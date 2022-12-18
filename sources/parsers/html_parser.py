# create a type of parser which parses EPUB files
from django.conf import settings
from .source_parser import Source_parser
from bs4 import BeautifulSoup
from common.util.utils import div_txt_in_chunk, html_to_text
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
chrome_options = Options()
chrome_options.add_argument("--headless")


class Html_parser(Source_parser):
    def __init__(self):
        super().__init__("html", ["html"])

    def parse(source):
        print("Entered scrapper")
        # get textual content from html file
        link = source.link
        # load the url
        print("Loading Link: ", link)
        driver = webdriver.Chrome(options=chrome_options)
        print("Driver Loaded")
        driver.get(link)
        print("Scraping Link: ", link)
        # scrap the page
        html_content = driver.page_source
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            title = soup.find("meta", property="og:title")
            author_name = soup.find(
                "meta", attrs={'name': 'author'})
            source.name = title["content"]
            source.author = author_name["content"]
            source.save()
        except:
            pass
        text_content = html_to_text(html_content)
        txt_chunks = div_txt_in_chunk(
            text_content, settings.MAX_EMBEDDING_LENGTH)
        driver.quit()
        return [(txt_chunk, 0, 0) for txt_chunk in txt_chunks]
