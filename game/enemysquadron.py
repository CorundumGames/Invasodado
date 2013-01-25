import itertools
import random

from enemy import Enemy
import ingame

ROW_SIZE = 7
COL_SIZE = 4

enemies = None

def clean_up():
    global enemies
    enemies        = None
    Enemy.velocity = [.5, 0.0]

def reset():
    global enemies
    ingame.ENEMIES.empty()
    enemies        = [[Enemy((i, j)) for i in xrange(ROW_SIZE)] for j in xrange(COL_SIZE)]
    Enemy.velocity = [.5, 0.0]
    a              = Enemy.STATES.APPEARING

    for i in enemies:
    #For all rows of enemies...
        for j in xrange(ROW_SIZE/2):
        #For the first half of each row...
            if random.randint(0, 1):
            #With 50% odds...
                ingame.ENEMIES.add(i[j], i[ROW_SIZE-1-j])
                i[j].state            = a
                i[ROW_SIZE-1-j].state = a

def move_down():
    for e in ingame.ENEMIES:
    #For all enemies on-screen...
        e.state = Enemy.STATES.LOWERING

def celebrate():
    for e in ingame.ENEMIES:
    #For all enemies...
        if e.state is not e.__class__.STATES.IDLE:
            e.state = Enemy.STATES.CHEERING