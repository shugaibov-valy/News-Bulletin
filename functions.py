from bs4 import BeautifulSoup as BS
import requests
import sqlite3
import re
import json

con = sqlite3.connect('ParseNews.sqlite')
cur = con.cursor()


def completion_comboBox(comboBox):
    cities = cur.execute("""SELECT city_name FROM 'Список городов и стран'""").fetchall()
    for city in cities:
        comboBox.addItem(city[0])


def uploading_json(city_url, city, listWidget):
    html = requests.get(city_url)
    soup = BS(html.content, "html.parser")
    script = soup.find_all('script', type="application/ld+json")[-1]  # JSON
    my_json = str(script)[36:-10]
    cur.execute(f"""DELETE FROM '{city}'""")
    con.commit()
    listWidget.clear()
    return my_json


def uploading_post(index, my_json, city, listWidget):
    link_on_post = json.loads(my_json)['itemListElement'][index]['url']
    post = requests.get(link_on_post)
    html_post = BS(post.content, 'html.parser')
    html_post_title = html_post.find('meta', itemprop="name")
    html_post_text = html_post.find('meta', itemprop="articleBody")

    if str(html_post_text) == 'None' or str(html_post_title) == 'None':
        uploading_post(index, my_json, city, listWidget)
    else:
        title_post = re.sub(r'\<[^>]*\>', '',
                            str(html_post_title.attrs['content']))  # удаляем все лишние символы из текста
        text_post = re.sub(r'\<[^>]*\>', '', str(html_post_text.attrs['content']))
        cur.execute(f"""INSERT INTO '{city}' VALUES('{title_post}', '{text_post}')""")
        con.commit()
        listWidget.addItem(title_post)
        listWidget.update()

