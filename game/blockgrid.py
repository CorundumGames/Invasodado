import itertools

import pygame.rect
import pygame.mixer

from core import config
import block
import ingame

CELL_SIZE  = (16*config.SCALE_FACTOR, 16*config.SCALE_FACTOR)
DIMENSIONS = (12, config.screen.get_width()/CELL_SIZE[1]) #(row, column)
LOCATION   = (0, 0)
RECT       = pygame.rect.Rect(LOCATION, (config.screen.get_width(), DIMENSIONS[0]*CELL_SIZE[0]))
temp       = range(1, 3)

global blocks
blocks        = [[None for i in range(DIMENSIONS[1])] for j in range(DIMENSIONS[0])]
blockstocheck = set()
blockstoclear = set()

matchset = set()

blockclear = pygame.mixer.Sound("./sfx/clear.wav")
        
def clear():
    global blocks
    for i in itertools.ifilter(lambda x: x.state != block.STATES.IDLE, ingame.BLOCKS.sprites()):
    #For all blocks that are on-screen...
        i.state = block.STATES.DYING
        
    blocks        = [[None for i in range(DIMENSIONS[1])] for j in range(DIMENSIONS[0])]
    blockstocheck.clear()
    blockstoclear.clear()
            
def update():
    global blocks
    blocks = [[None for i in range(DIMENSIONS[1])] for j in range(DIMENSIONS[0])]
    
    for b in itertools.ifilter(lambda x: x.state == block.STATES.ACTIVE, ingame.BLOCKS.sprites()):
    #For all blocks that are on the grid and not moving...
        blocks[b.gridcell[0]][b.gridcell[1]] = b

    for b in blockstocheck:
    #For all blocks to check for matches...
        
        matchset.add(b)  #Start with a match of one
        
        nextblock = (
                    {blocks[min(DIMENSIONS[0]-1, b.gridcell[0]+j)][                     b.gridcell[1]   ] for j in temp}, #Down
                    {blocks[min(DIMENSIONS[0]-1, b.gridcell[0]+j)][min(DIMENSIONS[1]-1, b.gridcell[1]+j)] for j in temp}, #Down-right
                    {blocks[min(DIMENSIONS[0]-1, b.gridcell[0]+j)][                     b.gridcell[1]   ] for j in temp}, #Right
                    {blocks[min(DIMENSIONS[0]-1, b.gridcell[0]+j)][max(0              , b.gridcell[1]-j)] for j in temp}  #Up-right
                    )
        
        #TODO: Optimize this so the cells are pre-calculated
        for i in nextblock:
        #For all the sets of blocks above...
            if len([id(b) for x in i if            \
                    id(i) != id(x) and             \
                    isinstance(x, block.Block) and \
                    id(b.color) == id(x.color)]) >= 2:
            #If there are two blocks and they're both the same color as the first...
                matchset.update(i)  #Mark these blocks as matching
                    
            
        if len(matchset) >= 3:
        #If at least 3 blocks are aligned...
            blockstoclear.update(matchset)  #Mark the blocks in question for removal
            ingame.score += (len(matchset)**2)*ingame.multiplier
            
        matchset.clear()
            
    if blockstoclear != set():
    #If we're clearing any blocks...
        blockclear.play()
        for b in blockstoclear: 
        #For every block marked for clearing...
            b.state = block.STATES.DYING
        blockstoclear.clear()
        
    
