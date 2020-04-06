import sys
import os

from pymongo import MongoClient
from src.MLEvaluation.features import WebsiteInfo

def build_features(keyword, url_file, is_legit):
    client = MongoClient('localhost', 27017)
    db = client['phishing_training_data']
    websites = db.websites

    url_data = os.path.join(os.getcwd(), url_file)

    urls = []
    with open(url_data, 'r', encoding='utf8') as l:
        urls = l.readlines()

    urls = [url.strip() for url in urls]

    # iterate through urls, making url objects
    print('setting up urls')
    url_objs = []

    for url in urls:
        print(url)
        url_objs.append(WebsiteInfo(url, keyword, is_legit).to_json())

    # bulk save them into mongodb databases
    print('inserting urls')
    new_result = websites.insert_many(url_objs)

def delete_urls():
    client = MongoClient('localhost', 27017)
    db = client['phishing_training_data']
    websites = db.websites
    websites.drop()
    print('Websites Deleted')


if __name__ == "__main__":
    arguments = sys.argv
    if arguments[1].lower() == 'delete':
        delete_urls()
    else: 
        keyword, url_file, is_legit = arguments[1], arguments[2], arguments[3]
        build_features(keyword, url_file, is_legit)