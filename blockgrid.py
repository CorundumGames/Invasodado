import itertools

import pygame

import config
import block
import ingame

CELL_SIZE  = (16, 16)
DIMENSIONS = (config.screen.get_width()/CELL_SIZE[0], 24) #(row, column)
LOCATION   = (0, 0)
RECT       = pygame.rect.Rect(LOCATION, (config.screen.get_width(), DIMENSIONS[1]*CELL_SIZE[1]))

blocks        = [[None for i in range(DIMENSIONS[0])] for j in range(DIMENSIONS[1])]
blockstocheck = []
blockstoclear = set()
        
def clear():
    for i in itertools.ifilter(lambda x: x.state != block.STATES.IDLE, ingame.BLOCKS.sprites()):
        i.state = block.STATES.DYING
    blocks        = [[None for i in range(DIMENSIONS[0])] for j in range(DIMENSIONS[1])]
            
    blockstocheck = []
    blockstoclear = set()
            
def update():
    blocks        = [[None for i in range(DIMENSIONS[0])] for j in range(DIMENSIONS[1])]
    for b in ingame.BLOCKS.sprites():
        blocks[b.gridcell[0]][b.gridcell[1]] = b

    for b in blockstocheck:
        matchlist = [b]
        blockdistance = 0
        while True:
            blockdistance += 1
            if b.gridcell[0] - blockdistance < 0:
                break
            else:
                nextblock = blocks[b.gridcell[0]-blockdistance][b.gridcell[1]]
                if isinstance(nextblock, block.Block) and b.color == nextblock.color:
                    matchlist.append(nextblock)
                else:
                    break
                
        for i in matchlist:
            if i in blockstocheck: blockstocheck.remove(i)
            
        if len(matchlist) >= 3: blockstoclear.update(matchlist)
    
    