import sys
import json

from os import path
from evaluate_websites import evaluate_websites
from src.create_candidate_list import create_candidate
from src.create_cert_list import create_cert_list
from src.extend_cert_list import extend_cert_list
from src.create_probed_list import call_httprobe
from src.MLEvaluation.build_features import build_features, delete_urls
from src.MLEvaluation.train_model import build_model
from src.website_elasticsearch import Website
from elasticsearch import Elasticsearch
from elasticsearch_dsl.connections import connections

connections.create_connection(host=['localhost'])

es = Elasticsearch()

def run_pipeline():
    if not es.indices.exists(index="website"):
        Website.init()

    with open('config.json', 'r')  as config:
        data = json.load(config)
        url, primary_keyword, datasets = data['url'], data['primary_keyword'], data['datasets']
    
    # Setting up ML Model
    if not path.exists(path.join('.\\', 'models\\random_forest.pkl')):
        for dataset in datasets:
            keyword, file_path, is_legit = dataset['keyword'], dataset['file_path'], dataset['is_legit']
            build_features(keyword, file_path, is_legit)
        build_model()

    while True:
        create_candidate(url) # Step 2 - creating the candidate list
        create_cert_list() # Step 3 - creating the cert list
        extend_cert_list() # Step 4 - extending the cert list
        call_httprobe() # Step 5 - creating the probed list
        evaluate_websites('probed_list.txt', primary_keyword) # Step 6 - evaluating the websites

if __name__ == "__main__":
    run_pipeline()