import requests
from bs4 import BeautifulSoup as bs
import datetime
import time

MainUrl = 'https://mobifitness.ru/widget/792082?colored=1&lines=1&club=0&clubs=1941&grid30min=0&desc=0&direction=0&group=0&trainer=0&room=0&age=&level=&activity=0&language=ru&custom_css=0&category_filter=2&activity_filter=2&ren'
url_rasp = 'https://mobifitness.ru/api/v6/account/reserve.json'

soup_token = bs(requests.get(MainUrl).text, 'html.parser')
scripts = soup_token.find_all('script')

for script in scripts:
    if 'accesstok' in script.text:
        script_text = script.text
        access_start = script_text.find('accesstok') + len('accesstok') + 3
        access_end = script_text.find(',', access_start) - 1
        access_token = script_text[access_start:access_end]
        print(access_token)

headers = {'Authorization': 'Bearer 0de079a2b23190df8026f699b7fb8a2c'}
# zapros = requests.post(url_rasp, headers=header, data={'fio': 'Рогачева Кристина', 'phone': '79965298428', 'scheduleId': '197679514112023', 'clubId': '1941'})
# print(zapros.status_code)
stop = False

# while not stop:
#     if datetime.datetime.now().hour == 20:
#         zapros = requests.post(url_rasp, headers=headers, data={'fio': 'Рогачева Кристина', 'phone': '79965298428', 'scheduleId': '197679514112023', 'clubId': '1941'})
#         code = zapros.status_code
#         print(code)
#         print(zapros.content)
#         if code == 200:
#             stop = True
#     time.sleep(2)

