import itertools
import random

import pygame

import enemy
import ingame


ROW_SIZE = 10
COL_SIZE = 8

enemies = [[enemy.Enemy((i, j)) for i in range(ROW_SIZE)] for j in range(COL_SIZE)]

def reset():
    for i in enemies:
        for j in i:
            j.add(ingame.ENEMIES)
    
    for i in enemies:
        for j in i[:len(i)/2]:
            if random.randint(0, 1) == 1:
                j.state = enemy.STATES.APPEARING       
            
    for i in enemies:
        for j in range(ROW_SIZE/2):
            i[ROW_SIZE-1-j].state = i[j].state
            
    for i in enemies:
        for j in itertools.ifilter(lambda x: x.state == enemy.STATES.IDLE, i):
            j.kill()