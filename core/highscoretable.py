import base64
import datetime
import json
import platform
import re
import shelve

import geolocation

PATTERN = '%Y-%m-%d %H:%M:%S.%f'

class HighScoreEntry:
    def __init__(self, name, score, mode, entry = None):
        '''
        @ivar country: Two-letter country code for online high scores
        @ivar mode: Game mode this score was achieved in
        @ivar name: Name of the player
        @ivar platform: Platform the game was played on
        @ivar score: Score the player achieved
        @ivar time: Date and time the score was achieved

        @param entry: High score entry string to construct self from
        '''

        if entry == None:
        #If we were not passed in a high score entry string...
            self.country  = str(geolocation.get_country('countryCode'))
            self.mode     = int(mode) #Can represent game modes or difficulty
            self.name     = name
            self.platform = platform.platform(True, True).split('-')[0]
            self.score    = int(score)
            self.time     = datetime.datetime.today()

            if not re.match('\w+', name):
                raise ValueError("Name must be alphanumeric!")

        elif isinstance(entry, basestring):
        #Else if we were passed a string for entry...
            a = entry.split('|')
            self.country  = a[3]
            self.mode     = int(a[2])
            self.name     = a[0]
            self.platform = a[4]
            self.score    = int(a[1])
            self.time     = datetime.datetime.strptime(a[5], PATTERN)

    def scramble(self):
        '''
        @precondition: self is unscrambled and thus intelligible
        @postcondition: self is scrambled and thus cannot be changed

        @return: self
        '''
        self.name     = base64.b64encode(self.name)
        self.score   ^= hash(self.name)
        self.mode    ^= self.score
        self.country  = base64.b64encode(self.country)
        self.platform = base64.b64encode(self.platform)
        self.time     = base64.b64encode(str(self.time))
        return self

    def unscramble(self):
        '''
        @precondition: self is scrambled and thus cannot be changed
        @postcondition: self is unscrambled and thus can be displayed

        @return: self
        '''
        self.time     = datetime.datetime.strptime(base64.b64decode(self.time), PATTERN)
        self.platform = base64.b64decode(self.platform)
        self.country  = base64.b64decode(self.country)
        self.mode    ^= self.score
        self.score   ^= hash(self.name)
        self.name     = base64.b64decode(self.name)
        return self

    def __cmp__(self, other):
        '''
        @param other: The other HighScoreEntry to compare to

        Allows us to sort all HighScoreEntrys in a table by score.
        '''
        return cmp(self.score, other.score)

    def __str__(self):
        '''
        Returns this entry as a string for local storage.

        Example: Jesse|1492|1|US|Linux|1994-10-13 12:01:02.03
        '''
        return '{0.name}|{0.score}|{0.mode}|{0.country}|{0.platform}|{0.time}'.format(self)

    def __repr__(self):
        return str(self)

###############################################################################

class HighScoreTable:
    def __init__(self, filename, mode, size, title, default, db_flag = 'c'):
        '''
        @ivar filename: Name and/or path of the database relative to the pwd
        @ivar mode: Game mode this HighScoreTable operates under
        @ivar scorefile: The actual entity that records high scores
        @ivar size: Number of entries this HighScoreTable must hold
        @ivar title: User-visible name of this high score table

        @param db_flag: Flags for the shelve module
        @param default: Location of default high scores if filename is new
        '''

        self.filename  = filename
        self.mode      = mode
        self.scorefile = shelve.open(filename, db_flag)
        self.size      = size
        self.title     = title

        if len(self.scorefile) < size:
        #If our high score table has missing entries...
            a = self.set_to_default(default)
            self.add_scores(map(HighScoreEntry, a, a.values(), [mode]*len(a)))

    def __del__(self):
        self.scorefile.close()

    def add_score(self, score_object):
        '''
        @param score_object: The score entry to add
        '''

        if not isinstance(score_object, HighScoreEntry):
        #If we weren't given a high score entry...
            raise TypeError("Expected HighScoreEntry, got {}".format(type(score_object)))
        elif score_object.mode != self.mode:
        #If this score entry is for the wrong game mode...
            raise ValueError("Expected mode {}, got mode {}".format(self.mode, score_object.mode))

        #TODO: This is kinda messy, I should fix it
        if len(self.scorefile) < self.size or score_object.score > self.lowest_score():
        #If our score doesn't rank out...
            if len(self.scorefile) >= self.size:
                a = self.get_scores()[-1].scramble()
                del self.scorefile[base64.b64encode(str(a))]
            self.scorefile[base64.b64encode(str(score_object))] = score_object.scramble()

    def add_scores(self, iterable):
        '''
        @param iterable: An iterable holding a bunch of HighScoreEntrys

        Adds all scores in iterable to self.scorefile, or at least tries
        '''
        map(self.add_score, iterable)

    def get_scores(self):
        '''
        @return: sorted list of all HighScoreEntrys
        '''
        a = map(HighScoreEntry.unscramble, self.scorefile.values())
        a.sort(reverse = True)
        return a

    def highest_score(self):
        return self.get_scores()[0].score

    def lowest_score(self):
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
