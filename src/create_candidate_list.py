import docker
import sys
import json
import censys.certificates
import censys
import tldextract

from urllib.parse import urlparse

client = docker.from_env()

def call_dnstwist(netloc: str):
    while True:
        try: 
            output = client.containers.run('elceef/dnstwist', f'--registered --banners --format json {netloc}')
            output = output.decode('utf8').replace("'", '"')
            with open('out_dnstwist.json', 'w') as f:
                output = json.loads(output)
                json.dump(output, f, ensure_ascii=False, indent=4)
        except json.decoder.JSONDecodeError:
            print('Output got messed up, trying again')
            continue
        break

def call_censys(domain: str, censys_uid: str, censys_secret: str):
    domain = f'{domain}*'
    certificates = censys.certificates.CensysCertificates(censys_uid, censys_secret)
    fields = ["parsed.subject_dn", "parsed.names"]
    censys_list = []
    try: 
        for c in certificates.search(f"parsed.names:({domain})", fields=fields):
            censys_list.append(c)
    except:
        print('Max limit of certs reached for this account')
    with open('out_censys.json', 'w') as f:
        json.dump(censys_list, f, ensure_ascii=False, indent=4)

def create_candidate_list(netloc: str, domain: str):
    with open('candidate_list.txt', 'w+') as candidate_list:
        with open('out_dnstwist.json', 'r') as f:
            output = json.load(f)
            for domain_object in output:
                if domain_object["domain-name"] != netloc:
                    candidate_list.write(f'{domain_object["domain-name"]}\n')
        with open('out_censys.json', 'r') as f:
            output = json.load(f)
            for entry in output:
                for parsed_domain in entry['parsed.names']:
                    if parsed_domain != netloc and domain in parsed_domain:
                        candidate_list.write(f'{parsed_domain}\n')

def create_candidate(url: str):
    with open('config.json', 'r')  as config:
        data = json.load(config)
        censys_uid = data['censys_UID']
        censys_secret = data['censys_Secret']

    domain = tldextract.extract(url).domain
    url = urlparse(url)
    netloc = url.netloc
    call_dnstwist(netloc)

    if censys_secret and censys_uid:
        call_censys(domain, censys_uid, censys_secret)

    create_candidate_list(netloc, domain)

if __name__ == "__main__":
    with open('config.json', 'r')  as config:
        data = json.load(config)
        censys_uid = data['censys_UID']
        censys_secret = data['censys_Secret']

    url = sys.argv[1]
    domain = tldextract.extract(url).domain
    url = urlparse(url)
    netloc = url.netloc
    call_dnstwist(netloc)

    if censys_secret and censys_uid:
        call_censys(domain, censys_uid, censys_secret)

    create_candidate_list(netloc, domain)
