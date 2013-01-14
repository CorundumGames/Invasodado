import base64
import datetime
import json
import platform
import re
import shelve

PATTERN = '%Y-%m-%d %H:%M:%S.%f'

class HighScoreEntry:
    def __init__(self, name, score, mode, entry = None):

        if entry == None:
        #If we were not passed in a high score entry string...
            self.name     = name
            self.score    = int(score)
            self.mode     = int(mode) #Can represent game modes or difficulty
            self.country  = 'US' #Temporary; will use a utility to find later
            self.platform = platform.platform(aliased = True, terse = True).split('-')[0]
            self.time     = datetime.datetime.today()

            if not re.match('\w+', self.name):
                raise ValueError("Name must be alphanumeric!")

        elif isinstance(entry, str):
        #Else if we were passed a string for entry...
            a = entry.split('|')
            self.name     = a[0]
            self.score    = int(a[1])
            self.mode     = int(a[2])
            self.country  = a[3]
            self.platform = a[4]
            self.time     = datetime.datetime.strptime(a[5], PATTERN)

    def scramble(self):
        '''
        Scrambles the high score so users don't mess with the local
        high score database.
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
        Unscrambles the high score so we can retrieve and print
        the high score.
        '''
        self.time     = datetime.datetime.strptime(base64.b64decode(self.time), PATTERN)
        self.platform = base64.b64decode(self.platform)
        self.country  = base64.b64decode(self.country)
        self.mode    ^= self.score
        self.score   ^= hash(self.name)
        self.name     = base64.b64decode(self.name)
        return self

    def __cmp__(self, other):
        '''Allows us to sort by score.'''
        return cmp(self.score, other.score)

    def __str__(self):
        ''''Returns this entry as a string for local storage.'''
        return '|'.join([self.name      ,
                         str(self.score),
                         str(self.mode) ,
                         self.country   ,
                         self.platform  ,
                         str(self.time)
                        ]
                     )

    def __repr__(self):
        return str(self)

###############################################################################

class HighScoreTable:
    def __init__(self, name, mode, size, title, default, db_flag = 'c'):
        self.filename  = name
        self.mode      = mode
        self.size      = size
        self.title     = title
        self.scorefile = shelve.open(self.filename, db_flag)

        if len(self.scorefile.keys()) < self.size:
        #If our high score table has missing entries...
            a = self.set_to_default(default)
            for i in a:
                self.add_score(HighScoreEntry(i, a[i], self.mode))


    def __del__(self):
        self.scorefile.close()

    def add_score(self, scoreobject):
        if not isinstance(scoreobject, HighScoreEntry):
        #If we weren't given a high score entry...
            raise TypeError("HighScoreTables may only hold HighScoreEntry objects!")
        elif scoreobject.mode != self.mode:
        #If this score entry is for the wrong game mode...
            raise ValueError("HighScoreEntries must be the same mode as the table that holds them!")

        if len(self.scorefile.keys()) < self.size or scoreobject.score > self.lowest_score():
        #If our score doesn't rank out...
            self.scorefile[base64.b64encode(str(scoreobject))] = scoreobject.scramble()

    def add_scores(self, iterable):
        map(self.add_score, iterable)

    def get_scores(self):
        a = map(HighScoreEntry.unscramble, self.scorefile.values())
        a.sort(reverse = True)
        return a

    def highest_score(self):
        return self.get_scores()[0].score

    def lowest_score(self):
        return self.get_scores()[-1].score

    def set_to_default(self, filename):
        '''
        Takes in a JSON file and loads default scores from there.
        This is meant to be used for default high score tables, and NOT for storage.
        '''
        return json.load(open(filename))

    def __len__(self):
        return self.size
