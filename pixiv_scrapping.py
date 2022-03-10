import requests
import json
from bs4 import BeautifulSoup
import os, shutil
from zipfile import ZipFile
import imageio
from PIL import Image
# link = "https://i.pximg.net/img-original/img/2021/04/07/20/24/43/88998885_p0.jpg"

def download(link, name, folder=""):
    if folder : 
        folder = str(folder)
        folder ="img_"+folder+"/"
        os.makedirs(folder, exist_ok=True)
    with open(folder+name+".png", 'wb') as f:
        im = requests.get(link, headers={'referer': 'https://www.pixiv.net/'})
        f.write(im.content)

# def download_gif(link, name):
    # with ZipFile('')

def zipextrac(artworkID,picturetype):
    with ZipFile(f'{artworkID}.{picturetype}', 'r') as zipObj:
        zipObj.extractall('temp_pixiv')

def get_img(id_img):
    link = f"https://www.pixiv.net/en/artworks/{id_img}"
    url = requests.get(link)
    soup = BeautifulSoup(url.content, 'html.parser')
    meta_tag = soup.find('meta', {'name':'preload-data'})
    js = json.loads(meta_tag['content'])
    img = js['illust'][id_img]['urls']['original']
    return img

def get_gif(id_gif):
    link = f"https://www.pixiv.net/ajax/illust/{id_gif}/ugoira_meta"
    url_raw = requests.get(link).json()
    url = url_raw['body']['originalSrc']
    duration = url_raw['body']['frames'][1]['delay']/10
    z = requests.get(url, headers={'referer': 'https://www.pixiv.net/'})
    with open(str(id_gif)+".zip", 'wb') as f:
        f.write(z.content)
    zipextrac(id_gif, 'zip')
    gifProcessing(id_gif, duration)
    print('success')

def gifProcessing(artworkID,delay):
    pregif = os.listdir('temp_pixiv')
    with imageio.get_writer(f'{artworkID}.gif', mode='I') as writer:
        for filename in pregif:
            image = imageio.imread('temp_pixiv/'+filename)
            writer.append_data(image)
        
    os.remove(f'{artworkID}.zip')
    shutil.rmtree('temp_pixiv')


def get_user_picture(id_user, num_of_pic):
    link = f"https://www.pixiv.net/ajax/user/{id_user}/profile/all?lang=en"
    f = requests.get(link)
    body = list(f.json()['body']['illusts'].keys())
    for id_img in body[:num_of_pic]:
        img = get_img(id_img)
        print(img) 
        download(img, id_img, id_user)

import urllib.request as ur
import re
def getpicfrompixiv(artworkID):
    url = 'https://www.pixiv.net/en/artworks/'+str(artworkID)
    r = requests.get(url)
    readhtml = r.content.decode("utf8")
    stf = re.find('"https:\/\/i\.pximg\.net\/img-original\/img\/\d+\/\d+\/\d+\/\d+\/\d+\/\d+\/.+_p0\.jpg"', readhtml)
    procurl = stf[0][1:-1]
    # pic = ur.Request(procurl)
    # pic.add_header('Referer', 'https://www.pixiv.net/')
    # picreq = ur.urlopen(pic).read()
    # with open('owo.png','wb') as file:
        # file.write(picreq)
    return procurl

if __name__ == '__main__':
    # get_user_picture(6357652)
    # get_gif(87841313)
    get_user_picture(31317880, -1)

