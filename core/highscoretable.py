from base64   import b64encode, b64decode
import binascii
from datetime import datetime
from platform import platform
import json
import dbm.dumb as shelve

from core import geolocation
from core import config

PATTERN      = '%Y-%m-%d %H:%M:%S.%f'
SCORE_FORMAT = '{0.name}|{0.score}|{0.mode}|{0.country}|{0.platform}|{0.time}'

def encode(text):
    return b64encode(str(text).encode('utf-8','ignore')).decode('utf-8','ignore')

def decode(text):
    return b64decode(str(text).encode('utf-8','ignore')).decode('utf-8','ignore')

class HighScoreEntry:
    def __init__(self, name='', score=0, mode=0, entry=None):
        '''
        @ivar country: Two-letter country code for online high scores
        @ivar mode: Game mode this score was achieved in
        @ivar name: Name of the player
        @ivar platform: Platform the game was played on
        @ivar score: Score the player achieved
        @ivar time: Date and time the score was achieved

        @param entry: High score entry string to construct self from
        '''

        if not entry:
        #If we were not passed in fields high score entry string...
            self.country  = str(geolocation.get_country('countryCode'))
            self.mode     = int(mode) #Can represent game modes or difficulty
            self.name     = name
            self.platform = platform(True, True).split('-')[0]
            self.score    = int(score)
            self.time     = datetime.today()
        else:
        #Else if we were passed fields string for entry...
            fields        = str(entry).split('|')
            self.country  = fields[3]
            self.mode     = int(fields[2])
            self.name     = fields[0]
            self.platform = fields[4]
            self.score    = int(fields[1])
            try:
                self.time = datetime.strptime(fields[5], PATTERN)
            except ValueError:
                self.time = fields[5]
                
        try:
        #First see if our data is scrambled...
            self.unscramble()
        except binascii.Error:
        #Well apparently it's not.
            pass
        except ValueError:
            pass

    def scramble(self):
        '''
        @precondition: self is unscrambled and thus intelligible
        @postcondition: self is scrambled and thus cannot be changed

        @return: self
        '''
        self.name     = encode(self.name)
        self.score   ^= self.mode
        self.mode    ^= self.score
        self.country  = encode(self.country)
        self.platform = encode(self.platform)
        self.time     = encode(self.time)
        return self

    def unscramble(self):
        '''
        @precondition: self is scrambled and thus cannot be changed
        @postcondition: self is unscrambled and thus can be displayed

        @return: self
        '''
        self.time     = datetime.strptime(decode(self.time), PATTERN)
        self.platform = decode(self.platform)
        self.country  = decode(self.country)
        self.mode    ^= self.score
        self.score   ^= self.mode
        self.name     = decode(self.name)
        return self

    def __lt__(self, other):
        '''
        @param other: The other HighScoreEntry to compare to

        Allows us to sort all HighScoreEntrys in a table by score.
        '''
        return self.score < other.score

    def __str__(self):
        '''
        Returns this entry as a string for local storage.

        Example: Jesse|1492|1|US|Linux|1994-10-13 12:01:02.03
        '''
        return SCORE_FORMAT.format(self)

    def __repr__(self):
        return str(self)

###############################################################################

class HighScoreTable:
    def __init__(self, path, mode, size, title, default, db_flag='c'):
        '''
        @ivar mode: Game mode this HighScoreTable operates under
        @ivar path: Name and/or path of the database relative to the pwd
        @ivar scorefile: The actual entity that records high scores
        @ivar size: Number of entries this HighScoreTable must hold
        @ivar title: User-visible name of this high score table

        @param db_flag: Flags for the shelve module
        @param default: Location of default high scores if filename is new
        '''

        self.mode      = mode
        self.path      = path
        self.scorefile = shelve.open(path, db_flag)
        self.size      = size
        self.title     = title

        if len(self.scorefile) < size:
        #If our high score table has missing entries...
            a = self.set_to_default(default)
            self.add_scores([HighScoreEntry(i, a[i], mode) for i in a])

    def __del__(self):
        self.scorefile.close()

    def add_score(self, score_object):
        '''
        @param score_object: The score entry to add
        '''

        if not isinstance(score_object, HighScoreEntry):
        #If we weren't given a high score entry...
            raise TypeError("Expected HighScoreEntry, got %s" % score_object)
        elif score_object.mode != self.mode:
        #If this score entry is for the wrong game mode...
            raise ValueError("Expected mode %i, got mode %i" % (self.mode, score_object.mode))

        #TODO: This is kinda messy, I should fix it
        if len(self.scorefile) < self.size or score_object.score > self.lowest_score():
        #If our score doesn't rank out...
            if len(self.scorefile) >= self.size:
            #If we have more scores than we're allowed...
                lowest = self.get_scores()[-1].scramble()
                del self.scorefile[encode(lowest)]

            self.scorefile[encode(score_object)] = str(score_object.scramble())

    def add_scores(self, iterable):
        '''
        @param iterable: An iterable holding a bunch of HighScoreEntrys

        Adds all scores in iterable to self.scorefile, or at least tries
        '''
        for i in iterable:
            self.add_score(i)

    def get_scores(self):
        '''
        @return: sorted list of all HighScoreEntrys
        '''
        scores = [HighScoreEntry(entry=i.decode()) for i in self.scorefile.values()]
        scores.sort(reverse = True)
        return scores

    def highest_score(self):
        '''
        Returns the highest-valued score on this table.
        '''
        return self.get_scores()[0].score

    def lowest_score(self):
        '''
        Returns the lowest-valued score on this table.
        '''
        return self.get_scores()[-1].score

    def set_to_default(self, filename):
        '''
        @param filename: name/location of the default scores to load

        Takes in a JSON file and loads default scores from there.
        This is meant to be used for default high score tables, and NOT for storage.
        '''
        return json.load(open(filename))

    def __len__(self):
        return self.size
