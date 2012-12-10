import itertools
import random

import enemy
import ingame

ROW_SIZE = 7
COL_SIZE = 4

enemies = None

def reset():
    global enemies
    ingame.ENEMIES.empty()
    enemies = [[enemy.Enemy((i, j)) for i in xrange(ROW_SIZE)] for j in xrange(COL_SIZE)]
    
    for i in enemies:
    #For all rows of enemies...
        for j in xrange(ROW_SIZE/2):
        #For the first half of each row...
            if random.randint(0, 1):
            #With 50% odds...
                ingame.ENEMIES.add(i[j], i[ROW_SIZE-1-j])
                i[j].state            = enemy.Enemy.STATES.APPEARING
                i[ROW_SIZE-1-j].state = enemy.Enemy.STATES.APPEARING   
                
def move_down():
    global enemies
    for e in ingame.ENEMIES:
    #For all enemies...
        e.position[1] += 8
        e.rect.topleft = list(e.position)