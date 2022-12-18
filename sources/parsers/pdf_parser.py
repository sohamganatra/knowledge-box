import PyPDF2
from common.util.utils import div_txt_in_chunk
from django.conf import settings
from .source_parser import Source_parser
import time


class PDF_parser(Source_parser):
    def __init__(self):
        super().__init__("pdf", ["pdf"])

    def parse(source):
        # parse pdf
        print("Parsing PDF")
        pdf_file = source.file
        pdfReader = PyPDF2.PdfFileReader(pdf_file.path)
        num_pages = pdfReader.numPages
        count = 0
        text = ""
        # The while loop will read each page
        results = []
        while count < num_pages:
            print("PDF for Page: ", count)
            pageObj = pdfReader.getPage(count)
            count += 1
            text = pageObj.extractText()
            text = text.replace("\n", " ")
            text = text.replace("\t", " ")
            text = text.replace("\r", " ")
            text = text.replace("  ", " ")
            print("PDF text: ", text)
            # This if statement exists to check if the above library returned #words. It's done because PyPDF2 cannot read scanned files.
            if text == "":
                continue
            # add textchunks, start location, end location
            results.append((text, count, count))
        return results
