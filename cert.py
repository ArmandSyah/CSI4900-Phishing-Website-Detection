# -*- encoding: utf-8 -*-
# requires a recent enough python with idna support in socket
# pyopenssl, cryptography and idna

from urllib.parse import urlparse

from OpenSSL import SSL
from cryptography import x509
from cryptography.x509.oid import NameOID
import idna

from socket import socket
from collections import namedtuple

import tldextract

HostInfo = namedtuple(field_names='cert hostname peername', typename='HostInfo')

HOSTS = [
    ('www.canadat.ca', 80),
    ('www.canala.ca', 80),
    ('lp.canadacustomautoworks.com', 443),
    ('www.sankakucomplex.com', 443),
    ('zuriadelfines.com', 443),
    ('expired.badssl.com', 443),
    ('wrong.host.badssl.com', 443),
    ('ca.ocsr.nl', 443),
    ('faß.de', 443),
    ('самодеј.мкд', 443),
]

def verify_cert(cert, hostname):
    # verify notAfter/notBefore, CA trusted, servername/sni/hostname
    cert.has_expired()
    # service_identity.pyopenssl.verify_hostname(client_ssl, hostname)
    # issuer

def get_certificate(hostname, port):
    hostname_idna = idna.encode(hostname)
    sock = socket()
    sock.settimeout(5)

    sock.connect((hostname, 443))
    sock.setblocking(1)

    
    peername = sock.getpeername()
    ctx = SSL.Context(SSL.SSLv23_METHOD) # most compatible
    ctx.check_hostname = False
    ctx.verify_mode = SSL.VERIFY_NONE

    sock_ssl = SSL.Connection(ctx, sock)
    sock_ssl.set_connect_state()
    sock_ssl.set_tlsext_host_name(hostname_idna)
    sock_ssl.do_handshake()
    cert = sock_ssl.get_peer_certificate()
    crypto_cert = cert.to_cryptography()

    import pprint
    pprint.pprint(crypto_cert)

    sock_ssl.close()
    sock.close()

    return HostInfo(cert=crypto_cert, peername=peername, hostname=hostname)

def get_alt_names(cert):
    try:
        ext = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
        return ext.value.get_values_for_type(x509.DNSName)
    except x509.ExtensionNotFound:
        return None

def get_common_name(cert):
    try:
        names = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)
        return names[0].value
    except x509.ExtensionNotFound:
        return None

def get_issuer(cert):
    try:
        names = cert.issuer.get_attributes_for_oid(NameOID.COMMON_NAME)
        return names[0].value
    except x509.ExtensionNotFound:
        return None


def print_basic_info(hostinfo):
    s = '''» {hostname} « … {peername}
    \tcommonName: {commonname}
    \tSAN: {SAN}
    \tissuer: {issuer}
    \tnotBefore: {notbefore}
    \tnotAfter:  {notafter}
    '''.format(
            hostname=hostinfo.hostname,
            peername=hostinfo.peername,
            commonname=get_common_name(hostinfo.cert),
            SAN=get_alt_names(hostinfo.cert),
            issuer=get_issuer(hostinfo.cert),
            notbefore=hostinfo.cert.not_valid_before,
            notafter=hostinfo.cert.not_valid_after
    )
    print(s)

def check_it_out(hostname, port):
    hostinfo = get_certificate(hostname, port)
    print_basic_info(hostinfo)

def get_hostinfo(url: str):
    ext = tldextract.extract(url)
    parsed_url = urlparse(url)
    hostname = parsed_url.netloc
    port = parsed_url.port
    domain = ext.domain

    if port is None:
        port = 443 if parsed_url.scheme == 'https' else 80

    try:
        hostinfo = get_certificate(hostname, port)

        info_dict = {
            'hostname': hostname,
            'domain': domain,
            'issuer' :get_issuer(hostinfo.cert),
            'notvalidbefore': hostinfo.cert.not_valid_before,
            'notvalidafter': hostinfo.cert.not_valid_after
        }
    except:
        info_dict = {
            'hostname': hostname,
            'domain': domain,
            'issuer' : 'Unknown',
            'notvalidbefore': None,
            'notvalidafter': None
        }

    return info_dict

import concurrent.futures
if __name__ == '__main__':
    for host in HOSTS:
        hostinfo = get_certificate(host[0], host[1])
        print_basic_info(hostinfo)
    # with concurrent.futures.ThreadPoolExecutor(max_workers=4) as e:
    #     for hostinfo in e.map(lambda x: get_certificate(x[0], x[1]), HOSTS):
    #         print_basic_info(hostinfo)