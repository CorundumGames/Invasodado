from math import log1p
import itertools
import random

import pygame

from game.enemy import Enemy

ROW_SIZE = 7
COL_SIZE = 4

enemies = None
enemy_group = None

def clean_up():
    global enemies
    enemies          = None
    Enemy.velocity   = [.5, 0.0]
    Enemy.start_time = None
    Enemy.shoot_odds = .002

def celebrate():
    Enemy.velocity = [0, 0]
    for e in enemy_group:
    #For all enemies...
        e.state = Enemy.STATES.CHEERING

def move_down():
    for e in enemy_group:
    #For all enemies on-screen...
        e.state = Enemy.STATES.LOWERING
    Enemy.should_flip  = False

def reset():
    global enemies
    enemy_group.empty()
    enemies        = [[Enemy((i, j)) for i in xrange(ROW_SIZE)] for j in xrange(COL_SIZE)]
    Enemy.velocity = [.5, 0.0]
    a              = Enemy.STATES.APPEARING

    for i in enemies:
    #For all rows of enemies...
        for j in xrange(ROW_SIZE/2):
        #For the first half of each row...
            if random.randint(0, 1):
            #With 50% odds...
                enemy_group.add(i[j], i[ROW_SIZE-1-j])
                i[j].state            = a
                i[ROW_SIZE-1-j].state = a

def start():
    Enemy.start_time = pygame.time.get_ticks()

def update():
    Enemy.anim += 1.0/3.0

    if Enemy.should_flip:
    #If at least one enemy has touched the side of the screen...
        Enemy.velocity[0] *= -1
        move_down()

    if not enemy_group:
    #If all enemies have been killed...
        reset()
        Enemy.velocity[0] = abs(Enemy.velocity[0]) + 0.05

def increase_difficulty():
    '''
    Increases Enemy's fire rate and speed based on time elapsed
    '''
    Enemy.shoot_odds = log1p(pygame.time.get_ticks() - Enemy.start_time)/1000
    assert 0.0 <= Enemy.shoot_odds < 1.0, \
    "Expected a valid probability, got %f" % Enemy.shoot_odds