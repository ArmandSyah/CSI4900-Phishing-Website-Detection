import sys
import json
from collections import defaultdict

from os import path, getcwd, remove
from evaluate_websites import evaluate_websites

from src.create_candidate_list import create_candidate
from src.create_cert_list import create_cert_list
from src.extend_cert_list import extend_cert_list
from src.create_probed_list import call_httprobe
from src.MLEvaluation.build_features import build_features, delete_urls
from src.MLEvaluation.train_model import build_model, RandomForest
from src.website_elasticsearch import Website

from elasticsearch import Elasticsearch
from elasticsearch_dsl.connections import connections

import time

es = Elasticsearch()
connections.create_connection()

def reset():
    if path.exists(path.join(getcwd(), 'models\\random_forest.pkl')):
        remove(path.join(getcwd(), 'models\\random_forest.pkl'))

    if es.indices.exists(index="website"):
        es.indices.delete(index='website', ignore=[400, 404])

    delete_urls()

def run_pipeline():
    if not es.indices.exists(index="website"):
        body = {"index.blocks.read_only_allow_delete": None}
        es.indices.put_settings(index="_all", body=body)
        Website.init()

    with open('config.json', 'r')  as config:
        data = json.load(config)
        url, primary_keyword, datasets = data['url'], data['primary_keyword'], data['datasets']
    
    # Setting up ML Model
    if not path.exists(path.join(getcwd(), 'models\\random_forest.pkl')):
        print("Setting up random forest")
        for dataset in datasets:
            keyword = dataset.get('keyword') 
            file_path = dataset.get('file_path') 
            is_legit = dataset.get('is_legit') 
            file_type = dataset.get('file_type')
            num_rows = dataset.get('num_rows', None)
            csv_url_pos = dataset.get('csv_url_pos', 0) 
            build_features(keyword, file_path, is_legit, file_type, num_rows, csv_url_pos)
        build_model()
        print("finished setting up random forest")
        
    print("Beginning Pipeline")

    while True:
        print('Beggining the loop')
        print('Creating the candidate list')
        create_candidate(url) # Step 2 - creating the candidate list
        print('Creating the cert list')
        create_cert_list() # Step 3 - creating the cert list
        print('Extending the cert list')
        extend_cert_list() # Step 4 - extending the cert list
        print('Finding websites with active HTTP servers')
        call_httprobe() # Step 5 - creating the probed list
        print('Evalutating website with RF')
        evaluate_websites('probed_list.txt', primary_keyword) # Step 6 - evaluating the websites
        print('Evaluation loop complete, redoing from the start')
        time.sleep(3600)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1].lower() == 'fresh':
            print('Reseting all json, mongodb and elasticsearch for fresh run')
            reset()
    run_pipeline()