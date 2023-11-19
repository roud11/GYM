import requests
from bs4 import BeautifulSoup as bs
from requests_html import HTMLSession
url = 'https://mobifitness.ru/widget/792082?colored=1&lines=1&club=0&clubs=1941&grid30min=0&desc=0&direction=0&group=0&trainer=0&room=0&age=&level=&activity=0&language=ru&custom_css=0&category_filter=2&activity_filter=2&ren'
r = requests.get(url)
soup = bs(r.text, 'html.parser')
#print(soup)
#a = soup.find_all(href, "/css/widget_responsive.css?v=f875f090f1")
#print(a)
#b = soup.find_all('accesstok')
#print(b)
session = HTMLSession()

s = session.get(url)
rasp = s.html.find('accesstok')
print(rasp.text)
