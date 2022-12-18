from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from sources.parsers.epub_parser import Epub_parser
from sources.parsers.html_parser import Html_parser
from sources.parsers.pdf_parser import PDF_parser
from sources.parsers.youtube_parser import Youtube_parser
from django.conf import settings
from common.util.utils import doc_embed, get_transcription_results, div_txt_in_chunk
import time
import threading

# Create your models here.

# create a model source which contains the following fields:
# name, author, type, language, file, embeddings, created, updated, link, available, active, tags

Type_choices = (
    ('html', 'html'),
    ('epub', 'epub'),
    ('pdf', 'pdf'),
    ('youtube', 'youtube'),
)


class Source(models.Model):
    name = models.CharField(max_length=1000, default="", blank=True)
    author = models.CharField(max_length=1000, default="", blank=True)
    type = models.CharField(
        max_length=100, choices=Type_choices, default="text")
    language = models.CharField(max_length=100, default="en")
    file = models.FileField(upload_to='sources/', default="", blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    link = models.CharField(max_length=1000, default="", blank=True)
    available = models.BooleanField(default=True)
    active = models.BooleanField(default=False)
    tags = models.CharField(max_length=1000, default="", blank=True)

    def __str__(self):
        if self.name is not None:
            return self.name
        elif self.link is not None:
            return self.link
        elif self.file is not None:
            return self.file.name
        return "No Name"


# create a model embedding which contains the following fields:
# source, embedding, created, updated, content, start_location,end_location
class Embedding(models.Model):
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    embedding = models.BinaryField(default=b'', blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    content = models.CharField(max_length=3000, default="")
    start_location = models.CharField(max_length=1000, default="", blank=True)
    end_location = models.CharField(max_length=1000, default="", blank=True)
    embedding_type = models.CharField(
        max_length=100, default=settings.EMBEDDING_MODEL, blank=True)

    def __str__(self):
        return self.content


# post saving of source, parse the source and create embeddings
@receiver(post_save, sender=Source)
def create_embeddings(sender, instance, created, **kwargs):
    if created:
        # parse source and create embeddings
        instance.save()
        t = threading.Thread(target=parse_source,
                             args=(instance,))
        t.setDaemon(True)
        t.start()
    return


def parse_source(instance):
    results = []
    if instance.type == "epub":
        results = Epub_parser.parse(instance)
    elif instance.type == "html":
        results = Html_parser.parse(instance)
    elif instance.type == "pdf":
        results = PDF_parser.parse(instance)
    elif instance.type == "youtube":
        transcription_id_list = Youtube_parser.parse(instance)
        transcription_id = transcription_id_list[0]
        print("transcription_id", transcription_id)
        results = wait_for_transcription(transcription_id, instance)
    else:
        results = Epub_parser.parse(instance)
    print("Parsing completed for source: ", str(instance))
    for result in results:
        # calculate embeddings
        txt = result[0]
        start_location = result[1]
        end_location = result[2]
        if not Embedding.objects.filter(content=txt).exists():
            if len(txt) < 50:
                continue
            print("Embedding created for source: ", str(instance))
            txt = txt.replace(u'\xa0', u' ')
            embedding = doc_embed(txt, settings.EMBEDDING_MODEL)
            Embedding.objects.create(
                source=instance, embedding=embedding, content=txt, start_location=start_location, end_location=end_location)
    print("Embeddings created for source: ", str(instance))
    if instance.name == "":
        instance.name = str(instance)
    instance.active = True
    instance.save()


def wait_for_transcription(id, instance):
    transcription = get_transcription_results(id)
    while transcription == None:
        time.sleep(5)
        transcription = get_transcription_results(id)
    transcription_texts = div_txt_in_chunk(
        transcription, settings.MAX_EMBEDDING_LENGTH)
    for transcription_text in transcription_texts:
        embedding = doc_embed(transcription_text, settings.EMBEDDING_MODEL)
        Embedding.objects.create(
            source=instance, embedding=embedding, content=transcription_text)
