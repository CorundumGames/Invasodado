import itertools

import pygame

import config
import block
import ingame

CELL_SIZE  = (16, 16)
DIMENSIONS = (24, config.screen.get_width()/CELL_SIZE[0]) #(row, column)
LOCATION   = (0, 0)
RECT       = pygame.rect.Rect(LOCATION, (config.screen.get_width(), DIMENSIONS[0]*CELL_SIZE[0]))

blocks        = [[None for i in range(DIMENSIONS[0])] for j in range(DIMENSIONS[1])]
blockstocheck = set()
blockstoclear = set()
        
def clear():
    for i in itertools.ifilter(lambda x: x.state != block.STATES.IDLE, ingame.BLOCKS.sprites()):
        i.state = block.STATES.DYING
    blocks        = [[None for i in range(DIMENSIONS[0])] for j in range(DIMENSIONS[1])]
    blockstocheck = set()
    blockstoclear = set()
            
def update():
    blocks = [[None for i in range(DIMENSIONS[0])] for j in range(DIMENSIONS[1])]
    for b in ingame.BLOCKS.sprites():
        blocks[b.gridcell[0]][b.gridcell[1]] = b

    for b in blockstocheck:  #Iterate over all blocks to check
        matchlist = [b]  #Start with a match of one
        blockdistance = 0
        while True:
            blockdistance += 1
            if b.gridcell[0] - blockdistance < 0:
                break
            else:
                nextblock = blocks[b.gridcell[0]-blockdistance][b.gridcell[1]]
                if isinstance(nextblock, block.Block) and b.color == nextblock.color:
                #If the adjacent cell has a block of the same color...
                    matchlist.append(nextblock)
                else:
                    break
            
        if len(matchlist) >= 3:
        #If at least 3 blocks are aligned...
            blockstoclear.update(matchlist)

    for b in blockstoclear:
        b.state = block.STATES.DYING
    