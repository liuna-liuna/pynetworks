#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    NAME
        basics.py

    DESCRIPTION
        1. 利用 pygeocoder 库获取经度和纬度；

    MODIFIED  (MM/DD/YY)
        Na  10/02/2019

"""
__VERSION__ = "1.0.0.10022019"


# imports
from pygeocoder import Geocoder
import os, requests
import http.client, json
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

def geocode_via_requests(address):
    parameters = {'address': address, 'sensor': 'false'}
    base = GOOGLE_MAPS_BASE.format(os.environ['GOOGLE_API_KEY'])
    response = requests.get(base, params=parameters)
    answer = response.json()
    print(answer['results'][0]['geometry']['location'])

def geocode_via_http(address):
    path = '/maps/api/geocode/json?key={}&address={}&sensor=false'.format(
        os.environ['GOOGLE_API_KEY'], quote_plus(address))
    connection = http.client.HTTPSConnection('maps.google.com')
    connection.request('GET', path)
    rawreply = connection.getresponse().read()
    print('[DEBUG] rawreply.size={}'.format(len(rawreply)))
    reply = json.loads(rawreply.decode('utf-8'))
    print('[DEBUG] reply.size={}'.format(reply))

    print(reply['results'][0]['geometry']['location'])

# classes

# main entry
if __name__ == "__main__":
    # get_long_latitude()
    # geocode_via_requests(address=ADDRESS)
    geocode_via_http(address=ADDRESS)
    