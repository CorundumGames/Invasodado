import json
import urllib

URL     = 'http://api.ipinfodb.com/v3/ip-country/'
API_KEY = 'affc0cf745509a400196c5b07d41d7bc7ad26bdfda5e2d9b1a289fc6c14d0b16'
FORMAT  = 'json'
PARAMS  = urllib.urlencode({'key': API_KEY, 'format': FORMAT})

REQUEST = ''.join([URL, '?', PARAMS])
FILE    = './save/country.wtf'

#TODO: Figure something out for if the connection failed or the server's down
def get_country(attribute = None):
    b = None

    try:
        b = json.load(open(FILE))
    except IOError:
        pass

    try:
        urllib.urlretrieve(REQUEST, FILE)
        b = json.load(open(FILE))
    except IOError:
        b = 'NA'

    try:
        return b[attribute]
    except:
        return b