import sys

from pymongo import MongoClient
from src.MLEvaluation.features import WebsiteInfo

def build_features(target_url, keyword, phish_file, legit_file):
    client = MongoClient('localhost', 27017)
    db = client['phishing_training_data']
    websites = db.websites

    phish_url_data = os.path.join(os.getcwd(), phish_file)
    legit_url_data = os.path.join(os.getcwd(), legit_file)

    phish_urls = []
    with open(phish_url_data, 'r', encoding='utf8') as p:
        phish_urls = p.readlines()

    phish_urls = [url.strip() for url in phish_urls]

    legit_urls = []
    with open(legit_url_data, 'r', encoding='utf8') as l:
        legit_urls = l.readlines()

    legit_urls = [url.strip() for url in legit_urls]

    # iterate through urls, making url objects
    print('setting up urls')
    url_objs = [WebsiteInfo(target_url, u, keyword, 0).to_json() for u in phish_urls + \
        WebsiteInfo(target_url, u, keyword, u, 1).to_json() for u in legit_urls]

    # bulk save them into mongodb databases
    print('inserting urls')
    new_result = websites.insert_many(url_objs)


if __name__ == "__main__":
    arguments = sys.argv
    target_url, keyword, phish_file, legit_file = arguments[1], arguments[2], arguments[3], arguments[4]
    build_features(target_url, keyword, phish_file, legit_file)