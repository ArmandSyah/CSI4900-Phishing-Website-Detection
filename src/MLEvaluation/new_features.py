from PIL import Image
import imagehash

import filetype

from urllib.parse import urlparse
from pywebcopy import WebPage, config, save_webpage

from OpenSSL import SSL
from cryptography import x509
from cryptography.x509.oid import NameOID
import idna

from socket import socket

from difflib import SequenceMatcher
from bs4 import BeautifulSoup

img_ext = ['jpg', 'jpx', 'png', 'gif', 'webp', 'cr2', 'tif', 'bmp', 'jxr', 'psd', 'ico', 'heic']
threshold_ratio = .6

class NewFeatures:
    def __init__(self, target_url: str, unknown_url: str, keyword: str):
        parsed_unknown_url = urlparse(unknown_url)
        unknown_netloc = parsed_unknown_url.netloc
        # # download website page assets
        # kwargs = {'bypass_robots': True, 'over_write': True, 'project_name': 'CSI4900'}
        # save_webpage(unknown_url, './webpage_assets', **kwargs)

        # print('Finished Saving Unknown URL assets')

        self.keyword_in_url = keyword in unknown_url
        self.keyword_in_domain = check_keyword_in_domain(target_url, unknown_url)
        # self.num_similar_images = check_num_similar_images(target_url, unknown_url)
        # self.num_similar_html_frags = check_num_similar_html_frags(target_url, unknown_url)
        self.cert_auth = check_cert_auth(unknown_url)

def check_keyword_in_domain(keyword: str, unknown_url: str):
    parsed_unknown_url = urlparse(unknown_url)
    unknown_url_netloc = parsed_unknown_url.netloc
    return keyword in unknown_url_netloc

# https://github.com/JohannesBuchner/imagehash
def check_num_similar_images(target_url: str, unknown_url: str):
    matching_images = 0
    target_image_hashes = set()
    unknown_url_image_hashes = set()

    parsed_target_url = urlparse(target_url)
    target_netloc = parsed_target_url.netloc

    parsed_unknown_url = urlparse(unknown_url)
    unknown_netloc = parsed_unknown_url.netloc
    
    for root, dirs, files in os.walk(os.path.join('./', unknown_netloc)):
        for f in files:
            f_name = os.path.join(root, f)
            f_guess = filetype.guess(f_name)
            f_ext_type = None if f_guess is None else f_guess.extension
            if f_ext_type in img_ext:
                image = Image.open(f_name)
                unknown_url_image_hashes.add(imagehash.average_hash(image))

    for root, dirs, files in os.walk(os.path.join('./', target_netloc)):
        for f in files:
            f_name = os.path.join(root, f)
            f_guess = filetype.guess(f_name)
            f_ext_type = None if f_guess is None else f_guess.extension
            if f_ext_type in img_ext:
                image = Image.open(f_name)
                target_image_hashes.add(imagehash.average_hash(image))

    for unknown_hash in unknown_url_image_hashes:
        matching_images = (matching_images + 1) if unknown_hash in target_image_hashes else matching_images

    return matching_images / len(target_image_hashes)

def check_num_similar_html_frags(target_url: str, unknown_url: str):
    match_ratios = []

    target_html_fragments = set()
    unknown_html_fragments = set()

    parsed_target_url = urlparse(target_url)
    target_netloc = parsed_target_url.netloc

    parsed_unknown_url = urlparse(unknown_url)
    unknown_netloc = parsed_unknown_url.netloc

    for root, dirs, files in os.walk(os.path.join('./', unknown_netloc)):
        for f in files:
            f_name = os.path.join(root, f)
            f_guess = filetype.guess(f_name)
            f_ext_type = None if f_guess is None else f_guess.extension
            if f_ext_type == "html":
                soup = BeautifulSoup(open(f_name), "html.parser")
                unknown_html_fragments.add(str(soup))


    for root, dirs, files in os.walk(os.path.join('./', target_netloc)):
        for f in files:
            f_name = os.path.join(root, f)
            f_guess = filetype.guess(f_name)
            f_ext_type = None if f_guess is None else f_guess.extension
            if f_ext_type == "html":
                soup = BeautifulSoup(open(f_name), "html.parser")
                target_html_fragments.add(str(soup))

    for target in target_html_fragments:
        for unknown in unknown_html_fragments:
            match_ratio = SequenceMatcher(None, target, unknown).ratio()
            match_ratios.append(match_ratio)

    return sum(match_ratios) / len(match_ratios)

# https://gist.github.com/gdamjan/55a8b9eec6cf7b771f92021d93b87b2c
def check_cert_auth(unknown_url: str):
    try:
        parsed_unknown_url = urlparse(unknown_url)
        unknown_netloc = parsed_unknown_url.netloc
        port = parsed_unknown_url.port

        if port is None:
            port = 443 if parsed_unknown_url.scheme == 'https' else 80

        hostname_idna = idna.encode(unknown_netloc)
        sock = socket()

        sock.connect((unknown_netloc, port))
        ctx = SSL.Context(SSL.SSLv23_METHOD) # most compatible
        ctx.check_hostname = False
        ctx.verify_mode = SSL.VERIFY_NONE

        sock_ssl = SSL.Connection(ctx, sock)
        sock_ssl.set_connect_state()
        sock_ssl.set_tlsext_host_name(hostname_idna)
        sock_ssl.do_handshake()
        cert = sock_ssl.get_peer_certificate()
        crypto_cert = cert.to_cryptography()
        sock_ssl.close()
        sock.close()

        try:
            import pprint
            pprint.pprint(crypto_cert.issuer.get_attributes_for_oid(NameOID.COMMON_NAME))
            names = crypto_cert.issuer.get_attributes_for_oid(NameOID.COMMON_NAME)
            return names[0].value
        except x509.ExtensionNotFound:
            print('Could not retrieve cert issuer')
            return None
    except:
        print('Could not retrieve cert issuer')
        return None

