import json
import urllib

import highscoretable

'''
Scoreoid_HighScoreTable uses the same interface as HighScoreTable, except it
uses the Scoreoid online high score service.

www.scoreoid.net
'''

class Scoreoid_HighScoreTable(highscoretable.HighScoreTable):
    def __init__(self):
        pass