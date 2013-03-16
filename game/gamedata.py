'''
This module contains common game data for things like lives, score, etc.  It
stores both the current values and the previous, so we can see if the score
changed at all.  This way we can save on creating new HUD graphics.
'''

### Constants ##################################################################
DEFAULT_LIVES = 3
MAX_COMBO_TIME = 60  #In frames
################################################################################

### Globals ####################################################################
alarm      = False

combo      = 0
combo_time = 0

score      = 0
prev_score = None

lives      = DEFAULT_LIVES
prev_lives = None
################################################################################

### Functions ##################################################################
def clean_up():
    '''
    Resets all the game data to the default values, in time for the next game.
    '''
    global score, prev_score
    global lives, prev_lives
    global combo
    global alarm

    score, prev_score =             0, None
    lives, prev_lives = DEFAULT_LIVES, None
    combo             = 0
    alarm             = False

################################################################################