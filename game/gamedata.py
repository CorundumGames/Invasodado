### Constants ##################################################################
DEFAULT_MULTIPLIER = 10
################################################################################

### Globals ####################################################################
multiplier         = DEFAULT_MULTIPLIER
COMBO_LENGTH       = 50

combo              = False
combo_counter      = 0

score              = 0
prev_score         = None

lives              = 3
prev_lives         = None
################################################################################

### Functions ##################################################################
def clean_up():
    global score, prev_score
    global lives, prev_lives
    global combo, combo_counter
    global multiplier

    score, prev_score    = 0, None
    lives, prev_lives    = 3, None
    combo, combo_counter = False, 0
    multiplier           = DEFAULT_MULTIPLIER

################################################################################