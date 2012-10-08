import random

import enemy
import ingame

ROW_SIZE = 7
COL_SIZE = 4

enemies = None

def reset():
    ingame.ENEMIES.empty()
    enemies = [[enemy.Enemy((i, j)) for i in range(ROW_SIZE)] for j in range(COL_SIZE)]
    
    for i in enemies:
    #For all rows of enemies...
        for j in range(ROW_SIZE/2):
        #For the first half of each row...
            if random.randint(0, 1) == 1:
            #With 50% odds...
                ingame.ENEMIES.add(i[j], i[ROW_SIZE-1-j])
                i[j].state            = enemy.STATES.APPEARING
                i[ROW_SIZE-1-j].state = enemy.STATES.APPEARING   