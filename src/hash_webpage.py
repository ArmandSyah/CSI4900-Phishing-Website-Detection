import sys
import os
import hashlib
import filetype

from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from pywebcopy import WebPage, config, save_webpage
from urllib.parse import urlparse

engine = create_engine('sqlite:///test.sqlite') #Create test.sqlite automatically
Base = declarative_base()

class Web_Assets(Base): 
    __tablename__ = 'web_assets'

    id = Column(Integer, primary_key=True)
    netloc = Column(String)
    filename = Column(String)
    hexdigest = Column(String)
    extension = Column(String)

    def __init__(self, netloc, filename, hexdigest, extension):
        self.netloc = netloc
        self.filename = filename
        self.hexdigest = hexdigest
        self.extension = extension

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

def download_webpage(url: str):        
    parsed_url = urlparse(url)
    netloc = parsed_url.netloc
    print('netloc: ' + netloc)

    # download website page assets
    kwargs = {'bypass_robots': False, 'over_write': True, 'project_name': 'CSI4900'}
    save_webpage(url, './webpage_assets', **kwargs)
    print('finish extracting assets')
    return netloc

def hash_assets(netloc: str):
    print("Retrieving hash hexdigest of content")
    print(os.getcwd())
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
    session.commit()

# id, netloc, hash hexdigest, file_name, file extension 

if __name__ == "__main__":
    # print(os.path.exists('.\\webpage_assets\\CSI4900\\www.bell.ca'))
    print(os.getcwd())
    url = sys.argv[1]
    netloc = download_webpage(url)
    hash_assets(netloc)
    session.close()


