import itertools
import random

import enemy
import ingame

ROW_SIZE = 7
COL_SIZE = 4

global enemies
enemies = None

def reset():
    global enemies
    ingame.ENEMIES.empty()
    enemies = [[enemy.Enemy((i, j)) for i in range(ROW_SIZE)] for j in range(COL_SIZE)]
    
    for i in enemies:
    #For all rows of enemies...
        for j in range(ROW_SIZE/2):
        #For the first half of each row...
            if random.randint(0, 1):
            #With 50% odds...
                ingame.ENEMIES.add(i[j], i[ROW_SIZE-1-j])
                i[j].state            = enemy.Enemy.STATES.APPEARING
                i[ROW_SIZE-1-j].state = enemy.Enemy.STATES.APPEARING   
                
def move_down():
    global enemies
    for e in itertools.chain.from_iterable(enemies):
    #For all enemies...
        e.position[1] += 8