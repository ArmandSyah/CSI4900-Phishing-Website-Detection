import docker
import sys
import json

from urllib.parse import urlparse

client = docker.from_env()

def call_dnstwist(netloc: str):
    while True:
        try: 
            output = client.containers.run('elceef/dnstwist', f'--registered --format json {netloc}')
            output = output.decode('utf8').replace("'", '"')
            with open('out.json', 'w') as f:
                output = json.loads(output)
                json.dump(output, f, ensure_ascii=False, indent=4)
        except json.decoder.JSONDecodeError:
            print('Output got messed up, trying again')
            continue
        break

def create_candidate_list():
    with open('out.json', 'r') as f:
        output = json.load(f)
        with open('candidate_list.txt', 'w+') as extended_watchlist:
            for domain_object in output:
                if domain_object["domain-name"] != netloc:
                    extended_watchlist.write(f'{domain_object["domain-name"]}\n')

def create_candidate(url: str):
    url = urlparse(url)
    netloc = url.netloc
    call_dnstwist(netloc)
    create_candidate_list()

if __name__ == "__main__":
    url = sys.argv[1]
    url = urlparse(url)
    netloc = url.netloc
    call_dnstwist(netloc)
    create_candidate_list()
