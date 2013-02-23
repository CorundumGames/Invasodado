'''
The scoreretriever module abstracts away the details of connecting to the
Internet to retrieve the high score list.

It's meant as a sort of factory module to return new HighScoreTables.
'''

import json
import urllib
import urllib2

from core.highscoretable import HighScoreTable, HighScoreEntry

API_KEY  = '51f9db7bd942a109b32b477dc1058de588150640'
API_URL  = 'https://www.scoreoid.com/api/'
GAME_ID  = 'f6CoDo3mI'
ORDER    = 'desc'
ORDER_BY = 'score'
RESPONSE = 'JSON'

def test_connection():
    '''
    Ensures we can actually connect to Scoreoid.
    
    Returns an empty string if everything went OK.
    Returns an error message if not.
    '''
    params = urllib.urlencode({'api_key':API_KEY, 'game_id':GAME_ID})
    result_statement = ''
    try:
        urllib2.urlopen(params)
    except urllib2.URLError as e:
        result_statement = e.reason
    except urllib2.HTTPError as e:
        result_statement = "Error %s: %s" % (e.code, e.reason)
    except IOError as e:
        result_statement = str(e)
        
    return result_statement
    
def get_score_table():
    params = urllib.urlencode({'api_key' : API_KEY ,
                               'game_id' : GAME_ID ,
                               'response': RESPONSE,
                               'order_by': ORDER_BY,
                               'order'   : ORDER   ,
                              })
    url = ''.join([API_URL, 'getBestScores?', params])
    response = urllib.urlretrieve(url)
    data = json.load(open(response[0]))
    print data
    
def submit_score():
    pass