import json
import socket
socket.setdefaulttimeout(10)
import mmh3
from shodan import Shodan

def extend_cert_list():
    with open('config.json', 'r') as config:
        data = json.load(config)
        shodan_key = data['shodan_key']

    shodan_api = Shodan(shodan_key)

    http_banners = []
    mmh3_hashes = set()

    with open('cert_list.txt', 'r') as cert_list:
        for _, target in enumerate(cert_list):
            try:
                target = target.strip()
                print(target)
                s = socket.socket()
                tport = 80
                s.connect((target, tport))
                head_request = str.encode('HEAD / HEAD/1.1\nHost: ' + target + '\n\n')
                s.send(head_request)
                http_banner = s.recv(1024).decode()
                http_banners.append(http_banner)
                s.close()
            except socket.error as socketerror:
                print("Error: ", socketerror)
                print('Continuing to next entry on cert list')
                s.close()
                continue
            

    for http_banner in http_banners:
        h = mmh3.hash(http_banner)
        mmh3_hashes.add(h)

    mmh3_hashes.remove(0)

    with open('extended_cert_list.txt', 'w+') as extended_cert_list:
        for h in mmh3_hashes:
            query = f'hash:{h}'
            results = shodan_api.search(query)
            print(f'Total for hash {h}: {results["total"]}')
            for result in results['matches']:
                hostnames = result['hostnames']
                for hostname in hostnames:
                    extended_cert_list.write(f'{hostname}\n')

if __name__ == "__main__":
    extend_cert_list()
        
