import itertools

import pygame

from core import config
import block
import ingame

CELL_SIZE  = (16, 16)
DIMENSIONS = (24, config.screen.get_width()/CELL_SIZE[1]) #(row, column)
LOCATION   = (0, 0)
RECT       = pygame.rect.Rect(LOCATION, (config.screen.get_width(), DIMENSIONS[0]*CELL_SIZE[0]))
temp       = range(1, 3)

blocks        = [[None for i in range(DIMENSIONS[1])] for j in range(DIMENSIONS[0])]
blockstocheck = set()
blockstoclear = set()

blockclear = pygame.mixer.Sound("./sfx/clear.wav")
        
def clear():
    for i in itertools.ifilter(lambda x: x.state != block.STATES.IDLE, ingame.BLOCKS.sprites()):
        i.state = block.STATES.DYING
        
    blocks        = [[None for i in range(DIMENSIONS[1])] for j in range(DIMENSIONS[0])]
    blockstocheck = set()
    blockstoclear = set()
            
def update():
    blocks = [[None for i in range(DIMENSIONS[1])] for j in range(DIMENSIONS[0])]
    
    for b in itertools.ifilter(lambda x: x.state == block.STATES.ACTIVE, ingame.BLOCKS.sprites()):
    #For all blocks that are on the grid and still...
        blocks[b.gridcell[0]][b.gridcell[1]] = b

    for b in blockstocheck:
    #For all blocks to check for matches...
    
        if b in blockstoclear:
        #If it's already slated for removal...
            continue  #Skip this loop
        
        matchlist = {b}  #Start with a match of one
        
        nextblock = (
                    {blocks[       b.gridcell[0]   ][max(0              , b.gridcell[1]-j)] for j in temp}, #Up
                    {blocks[max(0, b.gridcell[0]-j)][max(0              , b.gridcell[1]-j)] for j in temp}, #Up-left
                    {blocks[max(0, b.gridcell[0]-j)][                     b.gridcell[1]   ] for j in temp}, #Left
                    {blocks[max(0, b.gridcell[0]-j)][min(DIMENSIONS[1]-1, b.gridcell[1]+j)] for j in temp}, #Down-left
                    {blocks[       b.gridcell[0]   ][min(DIMENSIONS[1]-1, b.gridcell[1]+j)] for j in temp}, #Down
                    {blocks[min(DIMENSIONS[0]-1, b.gridcell[0]+j)][min(DIMENSIONS[1]-1, b.gridcell[1]+j)] for j in temp}, #Down-right
                    {blocks[min(DIMENSIONS[0]-1, b.gridcell[0]+j)][                     b.gridcell[1]   ] for j in temp}, #Right
                    {blocks[min(DIMENSIONS[0]-1, b.gridcell[0]+j)][max(0              , b.gridcell[1]-j)] for j in temp}  #Up-right
                    )
        #TODO: Optimize this so the cells are pre-calculated
        for i in itertools.ifilter(lambda x: x != None, nextblock):
            #For all the matching blocks above...
            if len(filter(lambda x: isinstance(x, block.Block) and b.color == x.color, i)) > 1:
            #If there are two blocks and they're both the same color as the first...
                matchlist |= i  #Mark these blocks as matching
                    
            
        if len(matchlist) >= 3:
        #If at least 3 blocks are aligned...
            blockstoclear.update(matchlist)  #Mark the blocks in question for removal
            
    if len(blockstoclear) > 0:
        blockclear.play()
        for b in blockstoclear: b.state = block.STATES.DYING
        blockstoclear.clear()
    
