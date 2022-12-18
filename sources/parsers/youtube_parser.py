from .source_parser import Source_parser

from pytube import YouTube

from common.util.utils import start_assembly_session


class Youtube_parser(Source_parser):
    def __init__(self):
        super().__init__("youtube", ["youtube"])

    def parse(source):
        link = source.link
        yt = YouTube(link)
        print(yt.title)
        # get audio from youtube
        audio_stream = yt.streams.filter(only_audio=True).first()
        file_name = "youtube" + audio_stream.default_filename
        audio_stream.download(filename=file_name)
        transcription_id = start_assembly_session(file_name)['id']
        print(transcription_id)
        return [transcription_id]
