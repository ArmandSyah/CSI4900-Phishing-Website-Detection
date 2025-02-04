from PIL import Image
import imagehash

import filetype

from urllib.parse import urlparse
from pywebcopy import WebPage, config, save_webpage

from OpenSSL import SSL
from cryptography import x509
from cryptography.x509.oid import NameOID
import idna

from socket import socket, AF_INET, SOCK_STREAM

from difflib import SequenceMatcher

import tldextract

import os

class NewFeatures:
    def __init__(self, url: str, keyword: str):
        # cert_auth = check_cert_auth(url)

        self.keyword_in_url = keyword in url.lower() if keyword else False
        self.keyword_in_domain = check_keyword_in_domain(keyword, url) if keyword else False
        self.similar_keyword_in_url = check_similar_keyword_in_url(keyword, url) if keyword else False
        # self.cert_auth = cert_auth if cert_auth is not None else "No Certificate Authority Found"

def check_keyword_in_domain(keyword: str, unknown_url: str):
    parsed_unknown_url = urlparse(unknown_url)
    unknown_url_netloc = parsed_unknown_url.netloc.lower()
    return keyword in unknown_url_netloc

# check if there is a variant of the keyword hidden in url
# ex: paypai, paypa, ect.
def check_similar_keyword_in_url(keyword: str, unknown_url: str):
    for index in range(0, len(unknown_url) - len(keyword), len(keyword)):
        unknown_url_sub_str = unknown_url[index:index+6]
        if SequenceMatcher(None, unknown_url_sub_str, keyword).ratio() > .5:
            return True
    return False


# https://gist.github.com/gdamjan/55a8b9eec6cf7b771f92021d93b87b2c
def check_cert_auth(unknown_url: str):
    try:
        parsed_unknown_url = urlparse(unknown_url)
        hostname = parsed_unknown_url.netloc
        port = parsed_unknown_url.port

        if port is None:
            port = 443 if parsed_unknown_url.scheme == 'https' else 80

        hostname_idna = idna.encode(hostname)
        sock = socket(AF_INET, SOCK_STREAM)
        sock.settimeout(5)

        sock.connect((hostname, port))
        sock.setblocking(1)

        ctx = SSL.Context(SSL.SSLv23_METHOD) 
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
            names = crypto_cert.issuer.get_attributes_for_oid(NameOID.COMMON_NAME)
            return names[0].value
        except x509.ExtensionNotFound:
            return None
    except:
        return None
