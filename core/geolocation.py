import json
import os.path
import urllib

API_KEY = 'affc0cf745509a400196c5b07d41d7bc7ad26bdfda5e2d9b1a289fc6c14d0b16'
FORMAT  = 'json'
PARAMS  = urllib.urlencode({'key': API_KEY, 'format': FORMAT})
URL     = 'http://api.ipinfodb.com/v3/ip-country/'

FILE    = os.path.join('save', 'country.wtf')
REQUEST = ''.join([URL, '?', PARAMS])

#TODO: Figure something out for if the connection failed or the server's down
def get_country(attribute = None):
    geoip_info = None

    try:
        geoip_info = json.load(open(FILE))
    except IOError:
        pass

    try:
        urllib.urlretrieve(REQUEST, FILE)
        geoip_info = json.load(open(FILE))
    except IOError:
        geoip_info = 'NA'

    return geoip_info[attribute] if attribute in geoip_info else geoip_info