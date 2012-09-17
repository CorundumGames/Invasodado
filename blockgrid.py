import itertools

import pygame

import config
import block
import ingame

CELL_SIZE  = (16, 16)
DIMENSIONS = (config.screen.get_width()/CELL_SIZE[0], 24)
LOCATION   = (0, 0)
RECT       = pygame.rect.Rect(LOCATION, (config.screen.get_width(), DIMENSIONS[1]*CELL_SIZE[1]))

blocks        = [[False for i in range(DIMENSIONS[0])] for j in range(DIMENSIONS[1])]
blockstocheck = []
blockstoclear = []
        
def clear():
    for i in blocks:
        for j in itertools.ifilter(lambda x: x != False, i):
            j.kill()
            j = False
            
    blockstocheck = []
            
def update():
    blocks        = [[False for i in range(DIMENSIONS[0])] for j in range(DIMENSIONS[1])]
    for b in ingame.BLOCKS.sprites():
        if b.gridcell != None:
            blocks[b.gridcell[0]][b.gridcell[1]] = True
            
    '''for i in range(len(blockstocheck)):  #TODO: Check the eight cardinal directions for like-colored blocks.
        for j in range(i):
            temp_clear = []'''  #This block of code slows the game down because we're not
                                #removing anything from blockstocheck