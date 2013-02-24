'''
This is a simple module that's made to associate high scores by country.
Lets us use any aspect of the returned JSON response.
'''

from json           import loads
from os.path        import join
from urllib.error   import HTTPError, URLError
from urllib.parse   import urlencode
from urllib.request import urlopen

### Constants ##################################################################
API_KEY = 'affc0cf745509a400196c5b07d41d7bc7ad26bdfda5e2d9b1a289fc6c14d0b16'
FORMAT  = 'json'
PARAMS  = urlencode({'key': API_KEY, 'format': FORMAT})
URL     = 'http://api.ipinfodb.com/v3/ip-country/'

FILE    = join('save', 'country.wtf')
REQUEST = ''.join((URL, '?', PARAMS))
################################################################################

### Functions ##################################################################
#TODO: Figure something out for if the connection failed or the server's down
def get_country(attribute=None):
    '''
    Gets country info based on our IP address, then stores it for later.
    
    @param attribute: The attribute from the requested JSON file to return.
                      If None, returns the whole JSON response.
    '''
    geoip_info = None

    try:
    #See if the country info is stored on the file system...
        geoip_info = loads(urlopen(REQUEST, timeout=5).read().decode())
    except IOError:
    #Well, apparently not.
        pass

    try:
    #Let's try loading it online.
        geoip_info = loads(urlopen(REQUEST, timeout=5).read().decode())
    except URLError as e:
        print(e.reason)
        geoip_info = 'NA'
    except HTTPError as e:
        print("Error %s: %s" % (e.code, e.reason))
        geoip_info = 'NA'

    return geoip_info[attribute] if attribute in geoip_info else geoip_info

################################################################################