import sys
import os

from pymongo import MongoClient
from src.hash_webpage import download_webpage
from src.MLEvaluation.features import WebsiteInfo

def build_features(target_url, keyword, phish_file, legit_file):
    # original_working_directory = os.getcwd()
    # download_webpage(target_url)
    # os.chdir(original_working_directory)

    client = MongoClient('localhost', 27017)
    db = client['phishing_training_data']
    websites = db.websites

    phish_url_data = os.path.join(os.getcwd(), phish_file)
    legit_url_data = os.path.join(os.getcwd(), legit_file)

    print(phish_url_data)
    print(legit_url_data)

    phish_urls = []
    with open(phish_url_data, 'r', encoding='utf8') as p:
        phish_urls = p.readlines()

    phish_urls = [url.strip() for url in phish_urls]
    print(phish_urls)

    legit_urls = []
    with open(legit_url_data, 'r', encoding='utf8') as l:
        legit_urls = l.readlines()

    legit_urls = [url.strip() for url in legit_urls]
    print(legit_urls)

    # iterate through urls, making url objects
    print('setting up urls')
    phish_website_info_objs = []
    legit_website_info_objs = []

    for phish_url in phish_urls:
        print(phish_url)
        phish_website_info_objs.append(WebsiteInfo(target_url, phish_url, keyword, 1).to_json())

    for legit_url in legit_urls:
        print(legit_url)
        legit_website_info_objs.append(WebsiteInfo(target_url, legit_url, keyword, 0).to_json())

    url_objs = phish_website_info_objs + legit_website_info_objs

    # bulk save them into mongodb databases
    print('inserting urls')
    new_result = websites.insert_many(url_objs)


if __name__ == "__main__":
    arguments = sys.argv
    target_url, keyword, phish_file, legit_file = arguments[1], arguments[2], arguments[3], arguments[4]
    build_features(target_url, keyword, phish_file, legit_file)