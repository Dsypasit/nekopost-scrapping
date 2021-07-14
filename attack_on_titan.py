import requests
from bs4 import BeautifulSoup
import re
import json
import os

def download(link, chapter, page_name, title_name):
    folder = title_name+'/'+str(chapter)
    try:
        os.makedirs(folder)
    except:
        pass
    fi = folder+'/'+str(page_name)+".jpg"
    with open(fi, 'wb') as f:
        count = 0
        while True:
            im = requests.get(link)
            print(page_name, im.status_code)
            if im.status_code == 200:
                break
            if im.status_code == 404:
                count += 1
            if count >20:
                break
        f.write(im.content)

link = f'https://manga00.com/attack-on-titan/'
raw = requests.get(link)
soup = BeautifulSoup(raw.content, "html.parser")
sp = soup.find_all('span', {'class': 'lchx'})
links = [n.find('a')['href'] for n in sp]
links.reverse()

for i, link in enumerate(links, 1):
    raw = requests.get(link)
    soupc = BeautifulSoup(raw.content, "html.parser")
    img = soupc.find_all('img', {'id':'imagech'})
    for n ,page in enumerate(img):
        download(page['src'], str(link), n, 'attack on titan')
    print("-"*20)
