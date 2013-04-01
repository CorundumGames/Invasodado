from contextlib import closing
from datetime   import datetime
from functools  import lru_cache
from json       import dumps, load, loads
from sys        import platform
from os         import mkdir
from os.path    import isdir  , join
import shelve

from core import config
from core import geolocation

### Constants ##################################################################
PATTERN      = '%Y-%m-%d %H:%M:%S.%f'
SCORE_FORMAT = '{0.name}|{0.score}|{0.mode}|{0.country}|{0.platform}|{0.time}'
################################################################################

### Functions ##################################################################
def load_defaults(scores):
    '''
    @param scores: Either a file-like object or a string, either of which must
                   hold JSON-formatted data.

    Takes in a JSON file and loads default scores from there.
    This is meant to be used for default high score tables, and NOT for storage.
    '''
    if not isinstance(scores, str):
        return load(open(scores))
    else:
        return loads(dumps(scores))

################################################################################

### Preparation ###############################################################
try:
#Let's try to make a directory...
    mkdir(config.DATA_STORE)
except OSError:
#Whoops, a file or directory with this name exists!
    if isdir(config.DATA_STORE):
    #Oh, it's a directory, we can use it
        pass
    else:
    #No, it's a file.  Abort!
        raise
###############################################################################

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
            self.platform = platform
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

    @lru_cache(maxsize=8)
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
        self.db_flag = db_flag
        self.mode    = mode
        self.path    = join(config.DATA_STORE, path)
        self.scores  = []
        self.size    = size
        self.title   = title
        
        a = None
        with closing(shelve.open(self.path)) as scorefile:
            if len(scorefile) < self.size:
            #If our high score table is the wrong size...
                a = load_defaults(default)
                
        if a is not None:
        #If we actually needed to load default scores...
            self.add_scores([HighScoreEntry(i, a[i], mode) for i in a])
        else:    
            self.read_scores()
        
    def __del__(self):
        self.write_scores()

    def add_scores(self, iterable):
        '''
        @param iterable: An iterable holding a bunch of HighScoreEntrys
        
        @raise TypeError: If any element in iterable is not a HighScoreEntry
        @raise ValueError: If any element in iterable has a different mode than self

        Adds all scores in iterable to self.scorefile, or at least tries
        '''

        for i in iterable:
        #For all scores to add...
            if not isinstance(i, HighScoreEntry):
            #If we weren't given a high score entry...
                raise TypeError("Expected HighScoreEntry, got %s" % i)
            elif i.mode != self.mode:
            #If this score entry is for the wrong game mode...
                raise ValueError("Expected mode %i, got mode %i" % (self.mode, i.mode))

            self.scores.append(i)
        
        self.scores.sort(reverse=True)
        while len(self.scores) > self.size:
        #While we have excess scores stored in the table...
            self.scores.pop()
            
        self.write_scores()
                    
    def write_scores(self):
        '''
        Writes all scores to the file
        '''
        with closing(shelve.open(self.path)) as scorefile:
            scorefile.clear()
            for i in self.scores:
                scorefile[str(i)] = i
        
    def read_scores(self):
        '''
        Reads scores from the file
        '''
        with closing(shelve.open(self.path)) as scorefile:
            self.scores = list(scorefile.values())
            self.scores.sort(reverse=True)

    def highest_score(self):
        '''
        Returns the highest-valued score on this table.
        '''
        return self.scores[0].score

    def lowest_score(self):
        '''
        Returns the lowest-valued score on this table.
        '''
        return self.scores[-1].score

    def __len__(self):
        return self.size
