import base64
import datetime
import platform
import re
import shelve

PATTERN = '%Y-%m-%d %H:%M:%S.%f'

class HighScoreEntry():  
    def __init__(self, name, score, mode, entry = None):

        if entry == None:
            self.name     = name
            self.score    = int(score)
            self.mode     = int(mode) #Can represent game modes or difficulty
            self.country  = 'US' #Temporary; will use a utility to find later
            self.platform = platform.platform(aliased = True, terse = True).split('-')[0]
            self.time     = datetime.datetime.today()
        
            if not re.match('\w+', self.name):
                raise ValueError("Name must be alphanumeric!")

        elif isinstance(entry, str):
            a = entry.split('|')
            self.name     = a[0]
            self.score    = int(a[1])
            self.mode     = int(a[2])
            self.country  = a[3]
            self.platform = a[4]
            self.time     = datetime.datetime.strptime(a[5], PATTERN)
        
    def __cmp__(self, other):
        return cmp(self.score, other.score)

    def __str__(self):
        
        a = '|'.join([self.name      ,
                         str(self.score),
                         str(self.mode) ,
                         self.country   ,
                         self.platform  ,
                         str(self.time)
                      ]
                     )
        return a

    def __repr__(self):
        return str(self)

    def scramble(self):
        self.name     = base64.b64encode(self.name)
        self.score   ^= hash(self.name)
        self.mode    ^= self.score
        self.country  = base64.b64encode(self.country)
        self.platform = base64.b64encode(self.platform)
        self.time     = base64.b64encode(str(self.time))

    def unscramble(self):
        self.time     = datetime.datetime.strptime(base64.b64decode(self.time), PATTERN)
        self.platform = base64.b64decode(self.platform)
        self.country  = base64.b64decode(self.country)
        self.mode    ^= self.score
        self.score   ^= hash(self.name)
        self.name     = base64.b64decode(self.name)
        
        

class HighScoreTable():
    def __init__(self, name, mode, size, title, db_flag = 'c'):
        self.filename  = name
        self.mode      = mode
        self.size      = size
        self.title     = title
        self.scorefile = shelve.open(self.filename, db_flag)

       
    def addScore(self, scoreobject):
        if not isinstance(scoreobject, HighScoreEntry):
            raise TypeError("HighScoreTables may only hold HighScoreEntry objects!")
        elif scoreobject.mode != self.mode:
            raise ValueError("HighScoreEntries must be the same mode as the table that holds them!")
        scoreobject.scramble()
        self.scorefile[base64.b64encode(str(scoreobject))] = scoreobject

    def addScores(self, iterable):
        for i in iterable:
            addscore(i)
        
    def getScores(self):
        a = self.scorefile.values()
        for i in a: i.unscramble()
        a.sort(reverse = True)
        return a
       
    def __len__(self):
        return self.size
