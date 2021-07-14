import requests
import os
import time
from tqdm import tqdm

def get_img_link(fileName, chapter, title):
    return f"https://fs.nekopost.net/collectManga/{title}/{chapter}/{fileName}"

def cut_name(n):
    return ''.join([i for i in n if i != '/' ])

def download(link, chapter, page_name, title_name):
    folder = cut_name(title_name)+'/'+chapter
    try:
        os.makedirs(folder)
    except:
        pass
    fi = folder+'/'+str(page_name)+".jpg"
    with open(fi, 'wb') as f:
        while True:
            im = requests.get(link)
            if im.status_code == 200:
                break
            time.sleep(1)
        f.write(im.content)

def get_chapter(chapter, chapter_name, title, name):
    pages_raw = requests.get(chapter['link'])
    pages = list(pages_raw.json()['pageItem'])
    pbar = tqdm(total=len(pages))
    update = 1
    for page in pages:
        img_link = get_img_link(page['fileName'], chapter['id'], title)
        download(img_link, chapter_name, page['pageNo'], name)
        pbar.update(update)
    pbar.close()

def get_all_chapter_link(title):
    chapter_raw = requests.get(f'https://tuner.nekopost.net/ApiTest/getProjectDetailFull/{title}')
    data = chapter_raw.json()
    chapters = data['projectChapterList']
    name = data['projectInfo']['np_name']
    print(name)
    chapter_dict = {}
    for chapter in chapters:
        chapter_dict[chapter['nc_chapter_no']]= {'id': chapter['nc_chapter_id']}
        chapter_dict[chapter['nc_chapter_no']]['link'] = f'https://fs.nekopost.net/collectManga/{title}/{chapter["nc_chapter_id"]}/{title}_{chapter["nc_chapter_id"]}.json'
    chapter_keys = [int(i) for i in chapter_dict.keys()]
    chapter_keys.sort()
    chapter_need = input(f"Enter your chapter ({chapter_keys[0]} - {chapter_keys[-1]}): ")
    chapter_keys = [str(i) for i in chapter_keys]
    chapter_need = chapter_need.split()
    if len(chapter_need) == 0:
        for chapter in chapter_keys:
            print("chapter : " + chapter)
            get_chapter(chapter_dict[chapter], chapter, title, name)

    elif chapter_need[0] == ":":
        start = int(chapter_need[1])-1
        stop =  int(chapter_need[2])
        for chapter in chapter_keys[start:stop]:
            print("chapter : " + chapter)
            get_chapter(chapter_dict[chapter], chapter, title, name)

    else:
        for chapter in chapter_need:
            print("chapter : " + chapter)
            get_chapter(chapter_dict[chapter], chapter, title, name)

title = input('Enter name id: ')
get_all_chapter_link(title)
