"""Bounded, key-free network diagnostics for fixed public service endpoints."""
from concurrent.futures import ThreadPoolExecutor
import platform
import socket
import ssl
import time
import httpx

HOSTS=('opendart.fss.or.kr','dart.fss.or.kr','kosis.kr','github.com')


def endpoint(host,timeout=4):
    if host not in HOSTS:raise ValueError('Unsupported diagnostic target')
    result={'host':host,'stage':'DNS','dns_addresses':[]}
    started=time.monotonic()
    try:
        addresses=socket.getaddrinfo(host,443,family=socket.AF_INET,type=socket.SOCK_STREAM)
        result['dns_addresses']=sorted({r[4][0] for r in addresses})
        result['dns_seconds']=round(time.monotonic()-started,3)
        result['stage']='TCP 443'
        with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as connection:
            connection.settimeout(timeout)
            t=time.monotonic()
            connection.connect((result['dns_addresses'][0],443))
            result['tcp_seconds']=round(time.monotonic()-t,3)
            result['stage']='TLS'
            t=time.monotonic()
            with ssl.create_default_context().wrap_socket(connection,server_hostname=host) as secure:
                result['tls_seconds']=round(time.monotonic()-t,3)
                result['tls_version']=secure.version()
                result['stage']='HTTP'
                secure.sendall(('GET / HTTP/1.1\r\nHost: '+host+'\r\nUser-Agent: Namoneyberg-Diagnostics/1.0\r\nConnection: close\r\n\r\n').encode('ascii'))
                line=secure.recv(512).split(b'\r\n')[0].decode('ascii',errors='replace')
                result['http_status_line']=line
                result['result']='response received'
    except (OSError,ssl.SSLError) as exc:
        result['result']=type(exc).__name__
    result['total_seconds']=round(time.monotonic()-started,3)
    return result


def diagnostics():
    with ThreadPoolExecutor(max_workers=4) as pool:
        rows=list(pool.map(endpoint,HOSTS))
    return {'python':platform.python_version(),'httpx':httpx.__version__,
            'openssl':ssl.OPENSSL_VERSION,'targets':rows}
