import requests
import sys
import shutil
import re
import os

from urllib import request, error, parse
from bs4 import BeautifulSoup as soup

def save_local_html_copy(url: str):
    try: 
        response = request.urlopen(url)
        web_content = response.read()

        netloc = parse.urlparse(url).netloc

        with open(f'saved_assets\{netloc}.html', 'wb') as f:
            f.write(web_content)
    except error.HTTPError:
        print('HTTP error occured, could not read html content')
        return
    except error.URLError:
        print('URL error occured, could not read html content')
        return 

def save_images(url: str):
    netloc = parse.urlparse(url).netloc
    if not os.path.exists(f"saved_assets\{netloc}_images"):
        os.makedirs(f"saved_assets\{netloc}_images")

    r = requests.get(url)
    if r.status_code == 200:
        html = soup(r.text, 'html.parser')
    else: 
        return

    tags = html.findAll("img")
    for tag in tags:
        src = tag.get("src")
        if src:
            src = re.match( r"((?:https?:\/\/.*)?\/(.*\.(?:png|jpg|svg)))", src )
            if src:
                (link, name) = src.groups()
                if not link.startswith("http"):
                    link = url + link
                r = requests.get( link, stream=True )
                if r.status_code == 200:
                    r.raw.decode_content = True
                    f = open( f"saved_assets\{netloc}_images\{name.split('/')[-1]}", "wb" )
                    shutil.copyfileobj(r.raw, f)
                    f.close()