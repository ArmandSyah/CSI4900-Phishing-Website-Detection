import requests, json 
import dateutil.parser
import censys.certificates

from datetime import date

now = date.today()


def search_crtsh(domain):
    url = f"https://crt.sh/?CN={domain}&output=json"

    ua = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1'
    req = requests.get(url, headers={'User-Agent': ua})

    if req.ok:
        try:
            content = req.content.decode('utf-8')
            data = json.loads("{}".format(content.replace('}{', '},{')))
        except Exception as err:
            print("Error retrieving information.")
            return False
        for cert in data:
            expiry_date = cert['not_after']
            expiry_date_object = dateutil.parser.parse(expiry_date)
            expiry_date_object = expiry_date_object.date()

            if (now < expiry_date_object):
                print(f'Found unexpired certificate in domain: {domain}')
                return True

    return False

def search_censys(domain, censys_uid, censys_secret):
    c = censys.certificates.CensysCertificates(api_id=censys_uid, api_secret=censys_secret)
    certs = c.search(f'{domain} and tags.raw: "unexpired"')
    return len(list(certs)) > 0

def create_cert_list():
    with open('config.json', 'r')  as config:
        data = json.load(config)
        censys_uid = data['censys_UID']
        censys_secret = data['censys_Secret']

    with open('cert_list.txt', 'w+') as cert_list, open('candidate_list.txt', 'r') as candidate_list:
        for _, candidate_domain in enumerate(candidate_list):
            print(f'searching: {candidate_domain.strip()}')
            if censys_uid and censys_secret:
                result = search_censys(candidate_domain.strip(), censys_uid, censys_secret)  
            else: 
                result = search_crtsh(candidate_domain.strip())
            if result:
                cert_list.write(f'{candidate_domain}')
    
