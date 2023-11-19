import requests
from bs4 import BeautifulSoup as bs
import datetime
import time

reserve_url = 'https://mobifitness.ru/api/v6/account/reserve.json'

headers = {'Authorization': 'Bearer 0de079a2b23190df8026f699b7fb8a2c'}
stop = False

while not stop:
    if datetime.datetime.now().hour == 20:
        zapros = requests.post(reserve_url, headers=headers, data={'fio': 'Рогачева Кристина', 'phone': '79965298428', 'scheduleId': '197679521112023', 'clubId': '1941'})
        code = zapros.status_code
        print(code)
        print(zapros.content)
        if code == 200:
            stop = True
    time.sleep(2)
