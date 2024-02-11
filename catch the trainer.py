import requests

url = 'https://mobifitness.ru/api/v6/club/1941/schedule.json'
headers = {'Authorization': 'Bearer 0de079a2b23190df8026f699b7fb8a2c'}

r = requests.get(url, headers=headers)

a = r.json()
print(a)
b = a['schedule']
print(b)
c = b[0]

for work in b:
    if work['trainers'][0]['title'] == 'Анастасия Багликова':
        print(work['activity'])
#    print(work["trainers"])
#    for key in work:
 #       if key == "trainers" and work[key][0]['title'] == 'Анастасия Багликова':
  #          print(1)

print(c)


