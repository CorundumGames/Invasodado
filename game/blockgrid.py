import itertools

import pygame.rect
import pygame.mixer

from core import config
import block
import ingame

CELL_SIZE  = (16*config.SCALE_FACTOR, 16*config.SCALE_FACTOR)
DIMENSIONS = (12, 20) #(row, column)
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
    
def clear_color(targetcolor):
    global blocks
    for i in itertools.ifilter(lambda x: id(x.color) == id(targetcolor), ingame.BLOCKS.sprites()):
        i.state = block.STATES.DYING
            
def update():
    global blocks
    blocks = [[None for i in range(DIMENSIONS[1])] for j in range(DIMENSIONS[0])]
    
    for b in itertools.ifilter(lambda x: x.state == block.STATES.ACTIVE, ingame.BLOCKS.sprites()):
    #For all blocks that are on the grid and not moving...
        blocks[b.gridcell[0]][b.gridcell[1]] = b

    for b in blockstocheck:
    #For all blocks to check for matches...
        matchset.add(b)  #Start with a match of one
        listDown = list() #List of blocks below
        listDownRight = list() #List of blocks down and to the right
        listRight = list() #List of blocks to the right
        listUpRight = list() #List of blocks up and to the right
        for j in temp:
            if(b.gridcell[0] + j < len(blocks)): #check if index goes out of bounds
                listDown.append(blocks[b.gridcell[0]+j][ b.gridcell[1]])#add the block below if index isn't out of bounds
            if(b.gridcell[0] + j < len(blocks) and b.gridcell[1] + j < len(blocks[0])):#check if index goes out of bounds
                listDownRight.append(blocks[b.gridcell[0]+j][b.gridcell[1]+j])#add the block down and to the right if index isn't out of bounds
            if(b.gridcell[1] + j < len(blocks[0])):#check if index goes out of bounds
                listRight.append(blocks[b.gridcell[0]][b.gridcell[1]+j])#add the block to the right  if index isn't out of bounds
            if(b.gridcell[0] - j >= 0 and b.gridcell[1] + j < len(blocks[0])):#check if index goes out of bounds
                listUpRight.append(blocks[b.gridcell[0]-j][b.gridcell[1]+j])#add the block up and to the right if index isn't out of bounds
        nextblock = (listDown,listDownRight,listRight,listUpRight)#put the lists into a tuple to make iterating easier
        
        #TODO: Optimize this so the cells are pre-calculated
        
        for i in nextblock:
        #For all the lists of blocks above...
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
            
    if len(blockstoclear) >= 3:
    #If we're clearing any blocks...
        blockclear.play()
        for b in blockstoclear: 
        #For every block marked for clearing...
            b.state = block.STATES.DYING
        blockstoclear.clear()
