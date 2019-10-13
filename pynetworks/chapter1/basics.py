#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    NAME
        basics.py

    DESCRIPTION
        1. 利用 pygeocoder 库获取经度和纬度；
        2. 用 requests库 实现;
        3. 用 http库 实现

    MODIFIED  (MM/DD/YY)
        Na  10/02/2019

"""
__VERSION__ = "1.0.0.10022019"


# imports
from pygeocoder import Geocoder
import os, requests
import http.client, json
import socket, ssl
from urllib.parse import quote_plus

# configuration

# consts
# ADDRESS = '207 N. Defiance St, Archbold, OH'
#   result: {'lat': 41.5219761, 'lng': -84.3066486}
ADDRESS = 'Mountain View, CA'
#   result: {'lat': 37.3860517, 'lng': -122.0838511}
GOOGLE_MAPS_BASE = 'https://maps.google.com/maps/api/geocode/json?key={}'

# functions
def get_long_latitude():
    # print(Geocoder(os.environ['GOOGLE_API_KEY']).geocode(address=ADDRESS)[0].coordinates)
    print(Geocoder(api_key=os.environ['GOOGLE_API_KEY']).geocode(address=ADDRESS)[0].coordinates)

def geocode_via_googlemaps():
    from googlemaps import Client
    gmaps = Client(os.environ['GOOGLE_API_KEY'])
    address = '207 N. Defiance St, Archbold, OH'
    print(gmaps.geocode(address)[0]['geometry']['location'])

def geocode_via_requests(address):
    parameters = {'address': address, 'sensor': 'false'}
    base = GOOGLE_MAPS_BASE.format(os.environ['GOOGLE_API_KEY'])
    response = requests.get(base, params=parameters)
    answer = response.json()
    print(answer['results'][0]['geometry']['location'])

def geocode_via_http(address):
    path = '/maps/api/geocode/json?key={}&address={}&sensor=false'.format(
        os.environ['GOOGLE_API_KEY'], quote_plus(address))
    print('path:\n{}\n'.format(path))
    connection = http.client.HTTPSConnection('maps.google.com')
    connection.request('GET', path)
    rawreply = connection.getresponse().read()
    reply = json.loads(rawreply.decode('utf-8'))
    print(reply['results'][0]['geometry']['location'])

"""socket.socket(...) not working for https://maps.google.com/...

could be due to "Google IP ranges (except those whitelisted below), are blocked".  
ref: https://stackoverflow.com/questions/20879408/confusing-behavior-with-pygeocoder-and-google-app-engine-with-sockets?rq=1
"""
def geocode_via_socket2(address):
    request_text = """\
    GET /maps/api/geocode/json?key={}&address={}&sensor=false HTTP/1.1\r\n\
    Host: maps.google.com:443\r\n\
    User-Agent: search4.py (Foundation of Python Network Programming)\r\n\
    Connection: close\r\n\
    \r\n\
    """
    request_data = request_text.format(os.environ['GOOGLE_API_KEY'], quote_plus(address))

    # for website https://...
    hostname = 'maps.google.com'
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    with ssl.wrap_socket(sock, ssl_version=ssl.PROTOCOL_SSLv23) as ssock:
        ssock.connect((hostname, 443))
        print(ssock.version())

        ssock.sendall(request_data.encode('utf-8'))
        raw_reply = b''
        while True:
            more = ssock.recv(4096)
            if not more: break
            raw_reply += more
        if raw_reply:
            print(raw_reply.decode('utf-8'))
        else:
            print('No response data received.')

def geocode_via_socket(address):
    request_text = """\
    GET /maps/api/geocode/json?key={}&address={}&sensor=false HTTP/1.1\r\n\
    Host: maps.google.com:443\r\n\
    User-Agent: search4.py (Foundation of Python Network Programming)\r\n\
    Connection: close\r\n\
    \r\n\
    """
    request_data = request_text.format(os.environ['GOOGLE_API_KEY'], quote_plus(address))

    # for website https://...
    hostname = 'maps.google.com'
    context = ssl.create_default_context()
    # context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    with socket.create_connection((hostname, 443)) as sock:
    # socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # sock = socket1.connect((hostname, 443))
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            print(ssock.version())

            ssock.sendall(request_data.encode('utf-8'))
            raw_reply = b''
            while True:
                more = ssock.recv(4096)
                if not more: break
                raw_reply += more
            if raw_reply:
                print(raw_reply.decode('utf-8'))
            else:
                print('No response data received.')

def test_github_ssl():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # s.connect(('www.github.com', 443))
    ss = ssl.wrap_socket(s, keyfile=None, certfile=None, server_side=False,
                         cert_reqs=ssl.CERT_NONE, ssl_version=ssl.PROTOCOL_SSLv23)
    # s.connect(('www.github.com', 443)) and ss.connect(...) both work
    ss.connect(('www.github.com', 443))
    # ss.sendall(...) both / and https://github.com/liuna-liuna/pynetworks/tree/master/pynetworks works
    # ss.sendall('GET / HTTP/1.1\r\nHost:github.com\r\nConnection:close\r\n\r\n'.encode('utf-8'))
    ss.sendall('GET https://github.com/liuna-liuna/pynetworks/tree/master/pynetworks HTTP/1.1\r\n'
               'Host:github.com\r\nConnection:close\r\n\r\n'.encode('utf-8'))
    while True:
        new = ss.recv(4096)
        if not new:
            ss.close()
            break
        print(new)

# with nossl and no API key, maps.google.com API returns no data.
def test_socket_nossl():
    s = socket.socket()
    s.connect(('maps.google.com', 80))
    # both no response data: /maps/api/geocode/json?key=... and without key=...
    request_text = """\
    GET /maps/api/geocode/json?address={}&sensor=false HTTP/1.1\r\n\
    Host: maps.google.com:80\r\n\
    User-Agent: search4.py (Foundation of Python Network Programming)\r\n\
    Connection: close\r\n\
    \r\n\
    """.format(quote_plus(ADDRESS))
    print('s:\n{}\nurl:\n{}\n'.format(s, request_text))

    s.sendall(request_text.encode('ascii'))
    raw_reply = b''
    while True:
        new = s.recv(4096)
        if not new:
            s.close()
            break
        raw_reply += new
    print('Data received:\n{}'.format(raw_reply.decode('utf-8')))


# classes

# main entry
if __name__ == "__main__":
    # get_long_latitude()
    # geocode_via_requests(address=ADDRESS)
    # geocode_via_http(address=ADDRESS)
    # geocode_via_googlemaps()

    # geocode_via_socket(address=ADDRESS)

    test_socket_nossl()
