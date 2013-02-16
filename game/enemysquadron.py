from math import log1p
from random import randint

import pygame

from game.enemy import Enemy

ROW_SIZE = 7
COL_SIZE = 4

_enemies    = None
ENEMY_GROUP = None

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
    Enemy.velocity = [0, 0]
    for e in ENEMY_GROUP:
    #For all enemies...
        e.state = Enemy.STATES.CHEERING

def move_down():
    '''
    Moves the entire squadron down.
    '''
    for e in ENEMY_GROUP:
    #For all enemies on-screen...
        e.state = Enemy.STATES.LOWERING
    Enemy.should_flip  = False

def reset():
    '''
    Brings out the next wave of Enemys (and recycles all the Enemy objects).
    '''
    global _enemies
    ENEMY_GROUP.empty()
    _enemies       = [[Enemy((i, j)) for i in xrange(ROW_SIZE)] for j in xrange(COL_SIZE)]
    Enemy.velocity = [0.5, 0.0]
    appearing      = Enemy.STATES.APPEARING

    for i in _enemies:
    #For all rows of _enemies...
        for j in xrange(ROW_SIZE/2):
        #For the first half of each row...
            if randint(0, 1):
            #With 50% odds...
                ENEMY_GROUP.add(i[j], i[ROW_SIZE - 1 - j])
                i[j].state                = appearing
                i[ROW_SIZE - 1 - j].state = appearing

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
        Enemy.velocity[0] = abs(Enemy.velocity[0]) + 0.05

def increase_difficulty():
    '''
    Increases Enemy's fire rate and speed based on time elapsed
    '''
    Enemy.shoot_odds = log1p(pygame.time.get_ticks() - Enemy.start_time) / 1000
    assert 0.0 <= Enemy.shoot_odds < 1.0, \
    "Expected a valid probability, got %f" % Enemy.shoot_odds