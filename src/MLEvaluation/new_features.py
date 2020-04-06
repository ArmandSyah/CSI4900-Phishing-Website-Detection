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

import os

class NewFeatures:
    def __init__(self, url: str, keyword: str):
        parsed_unknown_url = urlparse(url)
        unknown_netloc = parsed_unknown_url.netloc

        self.keyword_in_url = keyword in url.lower()
        self.keyword_in_domain = check_keyword_in_domain(keyword, url)
        self.similar_keyword_in_url = check_similar_keyword_in_url(keyword, url)
        self.cert_auth = check_cert_auth(url)

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
            names = crypto_cert.issuer.get_attributes_for_oid(NameOID.COMMON_NAME)
            return names[0].value
        except x509.ExtensionNotFound:
            print('Could not retrieve cert issuer')
            return None
    except:
        print('Could not retrieve cert issuer')
        return None

