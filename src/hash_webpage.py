import sys
import os
import hashlib
import filetype
import shutil

from create_db import Session, Web_Assets

from pywebcopy import WebPage, config, save_webpage
from urllib.parse import urlparse


def download_webpage(url: str):        
    parsed_url = urlparse(url)
    netloc = parsed_url.netloc
    print('netloc: ' + netloc)

    # download website page assets
    kwargs = {'bypass_robots': False, 'over_write': True, 'project_name': 'CSI4900'}
    save_webpage(url, './webpage_assets', **kwargs)

    file_gen_obj = os.walk('./')
    print('File gen: ', file_gen_obj)
    dirlist =  next(file_gen_obj)[1]
    print(dirlist)

    for folder in dirlist:
        if folder != netloc:
            shutil.rmtree(os.path.join('./', folder))

    print('finish extracting assets')
    return netloc

def hash_assets(netloc, session):
    print("Retrieving hash hexdigest of content")
    print(os.getcwd())
    print(os.path.join(os.getcwd(), netloc))
    for root, dirs, files in os.walk(os.path.join('./', netloc)):
        for f in files:
            md5_hash = hashlib.md5() 
            f_name = os.path.join(root, f)
            f_guess = filetype.guess(f_name)
            f_ext_type = None if f_guess is None else f_guess.extension
            with open(f_name, "rb") as f_b:
                for byte_block in iter(lambda: f_b.read(4096), b""):
                    md5_hash.update(byte_block)
            file_insert = Web_Assets(netloc, f_name, md5_hash.hexdigest(), f_ext_type)
            session.add(file_insert)
            print('Asset added')
    session.commit()

def hash_webpage(url: str):
    session = Session()
    netloc = download_webpage(url)
    hash_assets(netloc, session)
    session.close()

if __name__ == "__main__":
    session = Session()
    url = sys.argv[1]
    netloc = download_webpage(url)
    hash_assets(netloc, session)
    session.close()


