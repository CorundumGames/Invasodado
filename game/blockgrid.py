from os.path import join
import pygame.rect
import pygame.mixer

import core.config as config
import block
import ingame

CELL_SIZE   = (32, 32)
DIMENSIONS  = (12, 20) #(row, column)
LOCATION    = (0, 0)
RECT        = pygame.rect.Rect(LOCATION, (config.screen.get_width(), DIMENSIONS[0]*CELL_SIZE[0]))

blocks        = [[None for i in xrange(DIMENSIONS[1])] for j in xrange(DIMENSIONS[0])]
blockstocheck = set()
blockstoclear = set()

matchset = set()

blockclear = pygame.mixer.Sound(join('sfx', 'clear.wav'))

def clean_up():
    global blocks, blockstocheck, blockstoclear, matchset

    blocks = [[None for i in xrange(DIMENSIONS[1])] for j in xrange(DIMENSIONS[0])]
    blockstocheck.clear()
    blockstoclear.clear()
    matchset.clear()

def clear():
    global blocks
    for i in (j for j in ingame.BLOCKS if j.state is not block.Block.STATES.IDLE):
    #For all blocks on-screen...
        i.state = block.Block.STATES.DYING

    blocks = [[None for i in xrange(DIMENSIONS[1])] for j in xrange(DIMENSIONS[0])]
    blockstocheck.clear()
    blockstoclear.clear()

def clear_color(targetcolor):
    for i in (x for x in ingame.BLOCKS if isinstance(x, block.Block) and x.color is targetcolor):
    #For all blocks of the given color...
        i.state = block.Block.STATES.DYING

def clear_row(row):
    if not 0 <= row < DIMENSIONS[0]:
        #If we're not in the row range...
        raise ValueError("Expected row value in 0 <= x < 20, but got %i" % row)

    for i in (x for x in blocks[row] if isinstance(x, block.Block)):
    #For all blocks in this row...
        i.state = block.Block.STATES.DYING

def update():
    global blocks
    blocks = [[None for i in xrange(DIMENSIONS[1])] for j in xrange(DIMENSIONS[0])]

    for b in (x for x in ingame.BLOCKS if x is not None and x.state is block.Block.STATES.ACTIVE and isinstance(x , block.Block)):
    #For all blocks that are on the grid and not moving...
        blocks[b.gridcell[0]][b.gridcell[1]] = b

    for b in blockstocheck:
    #For all blocks to check for matches...
        matchset.add(b)    #Start with a match of one
        nextblocks = ([], [], [], []) #Respectively holds blocks down, down-right, right, up-right
        for j in (1, 2):
            if b.gridcell[0] + j < len(blocks):
            #If we're not out of bounds...
                nextblocks[0].append(blocks[b.gridcell[0]+j][ b.gridcell[1]]) #add the block below
            if b.gridcell[0] + j < len(blocks) and b.gridcell[1] + j < len(blocks[0]):
            #If we're not out of bounds...
                nextblocks[1].append(blocks[b.gridcell[0]+j][b.gridcell[1]+j])#add the block down and to the right
            if b.gridcell[1] + j < len(blocks[0]):
            #If we're not out of bounds...
                nextblocks[2].append(blocks[b.gridcell[0]][b.gridcell[1]+j])#add the block to the right
            if b.gridcell[0] - j >= 0 and b.gridcell[1] + j < len(blocks[0]):
            #If we're not out of bounds...
                nextblocks[3].append(blocks[b.gridcell[0]-j][b.gridcell[1]+j])#add the block up and to the right

        #TODO: Optimize this so the above chain of conditionals is done in one loop, if possible

        for i in nextblocks:
        #For all the lists of blocks above...
            if len([id(b) for x in i if i is not x and x is not None and b.color is x.color]) >= 2:
            #If there are two blocks and they're both the same color as the first...
                matchset.update(i) #Mark these blocks as matching


        if len(matchset) >= 3:
        #If at least 3 blocks are aligned...
            blockstoclear.update(matchset) #Mark the blocks in question for removal
            ingame.score     += (len(matchset)**2)*ingame.multiplier
            ingame.combo      = True
            ingame.multiplier = ingame.DEFAULT_MULTIPLIER * 2

        matchset.clear()

    if len(blockstoclear) >= 3:
    #If we're clearing any blocks...
        blockclear.play()
        for b in blockstoclear:
        #For every block marked for clearing...
            b.state = block.Block.STATES.DYING
        blockstoclear.clear()
