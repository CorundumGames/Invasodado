import itertools

import pygame

import config
import block
import ingame

CELL_SIZE  = (16, 16)
DIMENSIONS = (config.screen.get_width()/CELL_SIZE[0], 24) #(row, column)
LOCATION   = (0, 0)
RECT       = pygame.rect.Rect(LOCATION, (config.screen.get_width(), DIMENSIONS[1]*CELL_SIZE[1]))

blocks        = [[False for i in range(DIMENSIONS[0])] for j in range(DIMENSIONS[1])]
blockstocheck = []
blockstoclear = []
        
def clear():
    for i in itertools.ifilter(lambda x: x.state != block.STATES.IDLE, ingame.BLOCKS.sprites()):
        i.state = block.STATES.DYING
    blocks        = [[False for i in range(DIMENSIONS[0])] for j in range(DIMENSIONS[1])]
            
    blockstocheck = []
            
def update():
    blocks        = [[False for i in range(DIMENSIONS[0])] for j in range(DIMENSIONS[1])]
    for b in ingame.BLOCKS.sprites():
        blocks[b.gridcell[0]][b.gridcell[1]] = True
