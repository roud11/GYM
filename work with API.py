import requests
from bs4 import BeautifulSoup as bs
import datetime
import time

main_url = 'https://mobifitness.ru/widget/792082?colored=1&lines=1&club=0&clubs=1941&grid30min=0&desc=0&direction=0&group=0&trainer=0&room=0&age=&level=&activity=0&language=ru&custom_css=0&category_filter=2&activity_filter=2&ren'
reserve_url = 'https://mobifitness.ru/api/v6/account/reserve.json'
club_url = 'https://mobifitness.ru/api/v6/franchise/clubs.json'

soup_token = bs(requests.get(main_url).text, 'html.parser')
scripts = soup_token.find_all('script')

for script in scripts:
    if 'accesstok' in script.text:
        script_text = script.text
        access_start = script_text.find('accesstok') + len('accesstok') + 3
        access_end = script_text.find(',', access_start) - 1
        access_token = script_text[access_start:access_end]
        print(access_token)

headers = {'Authorization': 'Bearer ' + access_token}
print(headers)
req = requests.get(club_url, headers=headers)

clubs = {}
titels = []
for club in req.json():
    clubs[club['title']] = club['id']
    titels.append(club['title'])
print(titels)
print(clubs)

club = 'Mytimefitness Комендантский'
ID = str(clubs[club])
schedule_url = 'https://mobifitness.ru/api/v6/club/' + ID + '/schedule.json'
print(schedule_url)

schedule_json = requests.get(schedule_url, headers=headers).json()
print(schedule_json['schedule'])
schedule = {}
work_count = 0
for work in schedule_json['schedule']:
    work_count += 1
    schedule[work['id']] = {'Date and time': work['datetime'],
                            'Lesson': {'id': work['activity']['id'], 'Title of the lesson': work['activity']['title']},
                            'Trainer': {'id': work['trainers'][0]['id'], 'Name': work['trainers'][0]['title']},
                            'change': work['change']}
    if work['change'] == None:
        print(1)
    else:
        print(0)
#    print(schedule)
print(work_count)
user_lesson_id = '176024814112023'

#if
# zapros = requests.post(reserve_url, headers=header, data={'fio': 'Рогачева Кристина', 'phone': '79965298428', 'scheduleId': '197679514112023', 'clubId': '1941'})
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

