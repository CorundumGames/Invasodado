from math   import log1p
from random import randint

import pygame.time

from game.enemy import Enemy
from game       import gamedata

### Constants ##################################################################
ROW_SIZE       = 8
COL_SIZE       = 4
SPEED_INCREASE = .15 #In pixels per frame
################################################################################

### Globals ####################################################################
_enemies    = None
ENEMY_GROUP = None
################################################################################

def clean_up():
    '''
    Removes all Enemys from memory.
    '''
    global _enemies
    _enemies         = None
    Enemy.velocity   = [.5, 0.0]
    Enemy.start_time = None
    Enemy.shoot_odds = .002

def celebrate():
    '''
    Plays the Enemy celebration animation upon game over.
    '''
    Enemy.velocity = [0.0, 0.0]
    for e in (j for j in ENEMY_GROUP if isinstance(j, Enemy)):
    #For all enemies...
        e.change_state(Enemy.STATES.CHEERING)

def move_down():
    '''
    Moves the entire squadron down.
    '''
    for e in ENEMY_GROUP:
    #For all enemies on-screen...
        e.change_state(Enemy.STATES.LOWERING)
    Enemy.should_flip  = False

def reset():
    '''
    Brings out the next wave of Enemys (and recycles all the Enemy objects).
    '''
    global _enemies
    ENEMY_GROUP.empty()
    _enemies       = tuple([Enemy((i, j)) for i in range(ROW_SIZE)] for j in range(COL_SIZE))
    gamedata.wave += 1
    appearing      = Enemy.STATES.APPEARING

    for i in _enemies:
    #For all rows of _enemies...
        for j in range(ROW_SIZE // 2):
        #For the first half of each row...
            if randint(0, 1):
            #With 50% odds...
                ENEMY_GROUP.add(i[j], i[ROW_SIZE - 1 - j])
                i[j].change_state(appearing)
                i[ROW_SIZE - 1 - j].change_state(appearing)
    
    Enemy.velocity = [(12.50344*(len(ENEMY_GROUP)**-.94071))*log1p(gamedata.wave), 0.0]    
    if not ENEMY_GROUP:
    #If for some odd reason no enemies were created...
        reset()  #...then try again.

def start():
    '''
    Initializes the whole squadron of enemies.
    '''
    Enemy.start_time = pygame.time.get_ticks()

def update():
    '''
    Updates the Enemy class as a whole, rather than a particular instance.
    '''
    Enemy.anim += 1.0 / 3.0

    if Enemy.should_flip:
    #If at least one enemy has touched the side of the screen...
        Enemy.velocity[0] *= -1
        move_down()

    if not ENEMY_GROUP:
    #If all enemies have been killed...
        reset()

def increase_difficulty():
    '''
    Increases Enemy's fire rate and speed based on time elapsed
    '''
    Enemy.shoot_odds = log1p(pygame.time.get_ticks() - Enemy.start_time) / 5000
    assert 0.0 <= Enemy.shoot_odds < 1.0, \
    "Expected a valid probability, got %f" % Enemy.shoot_odds