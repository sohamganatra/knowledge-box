from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
chrome_options = Options()
chrome_options.add_argument("--headless")

link = "https://bensbites.beehiiv.com/p/openais-newest-model"
# load the url

driver = webdriver.Chrome(options=chrome_options)
driver.get(link)
# scrap the page
html_content = driver.page_source

soup = BeautifulSoup(html_content, "html.parser")
text = soup.get_text()
