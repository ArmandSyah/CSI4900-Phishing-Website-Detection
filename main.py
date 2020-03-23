import sys

from evaluate_websites import evaluate_websites
from src.create_candidate_list import create_candidate
from src.create_cert_list import create_cert_list
from src.extend_cert_list import extend_cert_list
from src.create_probed_list import call_httprobe
from src.MLEvaluation.build_features import build_features, delete_urls
from src.MLEvaluation.train_model import build_model

url = sys.argv[1]
keyword, legit_file, phish_file = sys.argv[2], sys.argv[3], sys.argv[4]
create_candidate(url) # Step 2 - creating the candidate list
create_cert_list() # Step 3 - creating the cert list
extend_cert_list() # Step 4 - extending the cert list
call_httprobe() # Step 5 - creating the probed list
# Step 6 ML Evaluation
build_features(keyword, legit_file, is_legit=1) # setting up features for legit file
build_features(keyword, phish_file, is_legit=0)
build_model()
evaluate_websites('probed_list.txt', keyword)