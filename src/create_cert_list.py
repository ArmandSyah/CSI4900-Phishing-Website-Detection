import requests, json, datetime

now = datetime.date.today()

def search(domain):
    url = f"https://crt.sh/?CN={domain}&output=json"

    ua = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1'
    req = requests.get(url, headers={'User-Agent': ua})

    if req.ok:
        try:
            content = req.content.decode('utf-8')
            data = json.loads("{}".format(content.replace('}{', '},{')))
            return data
        except Exception as err:
            print("Error retrieving information.")
    return None

if __name__ == "__main__": 
    with open('cert_list.txt', 'w+') as cert_list, open('candidate_list.txt', 'r') as candidate_list:
        for _, candidate_domain in enumerate(candidate_list):
            print(f'searching: {candidate_domain}')
            result = search(candidate_domain.strip())
            if result is not None and len(result) > 0:
                print('Certificates found')
                cert_list.write(f'{candidate_domain}')
