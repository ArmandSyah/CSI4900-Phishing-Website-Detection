import sys
import os
import pickle

from pymongo import MongoClient
from src.website_elasticsearch import Website
from src.MLEvaluation.train_model import RandomForest
from cert import get_hostinfo

def evaluate_websites(sites_to_evaluate_file: str, keyword: str):
    client = MongoClient('localhost', 27017)
    db = client['phishing_evaluation_results']
    evaluation_results = db.evaluation_results

    with open(os.path.join(os.getcwd(), 'models\\random_forest.pkl'), 'rb') as rf_pickle:
        rf = pickle.load(rf_pickle)

    url_data = os.path.join(os.getcwd(), sites_to_evaluate_file)

    urls = []
    with open(url_data, 'r', encoding='utf8') as l:
        urls = l.readlines()

    urls = [url.strip() for url in urls]

    for url in urls:
        (u, predicted_result, confidence_score) = rf.predict_url(url, keyword)
        u['is_legit'] = int(predicted_result)
        u['confidence_score'] = confidence_score
        evaluation_results.insert(u)
        hostinfo = get_hostinfo(url)
        import pprint
        pprint.pprint(hostinfo)
        url_es = Website(url=url,
                            domain=hostinfo['domain'],
                            hostname=hostinfo['hostname'], 
                            keyword=keyword, 
                            is_legit=bool(int(predicted_result)), 
                            certificate_authority_registrar=hostinfo['issuer'],
                            date_of_creation_ca=hostinfo['notvalidbefore'],
                            date_of_expiration_ca=hostinfo['notvalidafter'],
                            confidence_score=confidence_score)
        url_es.save()

if __name__ == "__main__":
    sites_to_evaluate_file, keyword = sys.argv[1], sys.argv[2]
    evaluate_websites(sites_to_evaluate_file)