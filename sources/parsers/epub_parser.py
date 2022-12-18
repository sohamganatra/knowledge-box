from .source_parser import Source_parser
import ebooklib
from ebooklib import epub
# create a type of parser which parses EPUB files
from bs4 import BeautifulSoup
from django.conf import settings
from common.util.utils import div_txt_in_chunk, html_to_text


class Epub_parser(Source_parser):
    def __init__(self):
        super().__init__("epub", ["epub"])

    def parse(source):
        # parse epub
        epub_file = source.file
        book = epub.read_epub(epub_file.path)
        author = book.get_metadata("DC", "creator")[0][0]
        title = book.get_metadata("DC", "title")[0][0]
        language = book.get_metadata("DC", "language")[0][0]
        if source.author == "":
            source.author = author
        if source.name == "":
            source.name = title
        if source.language == "":
            source.language = language
        source.save()

        # get textual content from epub file
        # parse epub file and extract text, author, title, language, etc
        items = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))
        all_txts = []
        for item in items:
            htmlContent = item.get_body_content()
            # use html parser
            text_content = html_to_text(htmlContent)
            # If the size of text content is more then te, then break it into multiple chunks and create embedding for each of them.
            txt_chunks = div_txt_in_chunk(
                text_content, settings.MAX_EMBEDDING_LENGTH)
            # create a thread to save the embeddings in the database
            all_txts += txt_chunks
        return [(all_txt, 0, 0) for all_txt in all_txts]
