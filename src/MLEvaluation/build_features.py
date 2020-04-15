import sys
import os
import csv

from pymongo import MongoClient
from src.MLEvaluation.features import WebsiteInfo

def build_features(keyword, url_file, is_legit, file_type, num_rows = None, csv_url_pos = 0):
    client = MongoClient('localhost', 27017)
    db = client['phishing_training_data']
    websites = db.websites

    url_data = os.path.join(os.getcwd(), url_file)

    urls = []
    url_objs = []

    if file_type == 'txt': 
        if not num_rows:
            with open(url_data, 'r', encoding='utf8') as l:
                urls = l.readlines()
        else:
            with open(url_data, 'r', encoding='utf8') as l:
                urls = [next(l) for x in range(num_rows)]

        urls = [url.strip() for url in urls]
    elif file_type == 'csv':
        with open(url_data, 'r', encoding="utf8") as legit_file:
            csvreader = csv.reader(legit_file)

            data_list = list(csvreader)

            for row in data_list[:num_rows if num_rows else len(data_list)]:
                urls.append(row[csv_url_pos])

    # iterate through urls, making url objects
    print('setting up urls')

    for url in urls:
        print(f'Setting up: {url}')
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