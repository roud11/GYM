from requests_html import HTMLSession
session = HTMLSession()

r = session.get('https://mobifitness.ru/widget/792082?colored=1&lines=1&club=0&clubs=1941&grid30min=0&desc=0&direction=0&group=0&trainer=0&room=0&age=&level=&activity=0&language=ru&custom_css=0&category_filter=2&activity_filter=2&ren')
print(r)
#r.html.render()
#fitness-widget-club-tab-0 > div.fitness-widget-legend > span:nth-child(1)
rasp = r.html.find('#fitness-widget-popup > div > div.fitness-widget-popup-descr-in > div.fitness-widget-popup-title', first=True)
print(rasp.text)
