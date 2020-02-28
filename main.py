import sys
from create_db import create_database
from hash_webpage import hash_webpage
from create_candidate_list import create_candidate
from create_cert_list import create_cert_list
from extend_cert_list import extend_cert_list

url = sys.argv[1]
create_database()
hash_webpage(url) # Step 1 - Hashing legit content
create_candidate(url) # Step 2 - creating the candidate list
create_cert_list() # Step 3 - creating the cert list
extend_cert_list() # Step 4 - extending the cert list
