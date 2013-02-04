from itertools import chain
from os.path   import join


from pygame.display import get_surface
import pygame.rect
import pygame.mixer
from game import gamedata

'''
The blockgrid module is responsible for handling interactions between multiple
blocks.  It's designed around Invasodado, but with a little work it could be
refitted for other match-3 games like Bejewelled or Puzzle League.
'''


CELL_SIZE   = (32, 32)
DIMENSIONS  = (12, 20) #(row, column)
RECT        = pygame.rect.Rect([0, 0], (get_surface().get_width(), DIMENSIONS[0] * CELL_SIZE[0]))

blocks          = [[None for i in range(DIMENSIONS[1])] for j in range(DIMENSIONS[0])]
block_type      = None
blocks_to_check = set()
blocks_to_clear = set()

match_set = set()

blockclear = pygame.mixer.Sound(join('sfx', 'clear.wav'))

def clean_up():
    '''
    Deletes all blocks that were created.

    @postcondition: No more objects of block_type exist in memory.
    '''
    global blocks
    blocks = [[None for i in range(DIMENSIONS[1])] for j in range(DIMENSIONS[0])]
    blocks_to_check.clear()
    blocks_to_clear.clear()
    match_set.clear()

def clear_color(target_color):
    '''
    Destroys all blocks of the specified color.

    @param target_color: Color of the blocks that should be deleted.
    @postcondition: No target_color-colored blocks exist on-screen.
    '''
    for i in (j for j in chain.from_iterable(blocks) if j and j.color is target_color):
    #For all blocks of the given color...
        i.state = block_type.STATES.DYING

def clear_row(row):
    '''
    Destroys all blocks in the specified row.

    @param row: The row of blocks to destroy, on [0, DIMENSIONS[0]).
    @postcondition: No blocks on-screen exist in the given row.
    '''

    assert 0 <= row < DIMENSIONS[0], \
    "Expected row value in 0 <= x < 20, but got %i" % row

    for i in (j for j in blocks[row] if j):
    #For all blocks in this row...
        i.state = block_type.STATES.DYING

def update():
    '''
    Checks if any blocks of the same color are lined up, clears them if so.

    @postcondition: Sets of 3+ like-colored blocks are removed from the game.
    '''
    global blocks

    blocks = [[None for i in xrange(DIMENSIONS[1])] for j in xrange(DIMENSIONS[0])]

    for i in (j for j in chain(block_type.group) if j and j.state == block_type.STATES.ACTIVE):
    #For all blocks that are on the grid and not moving...
        assert isinstance(i, block_type), "A %s got into the Block grid!" % i
        blocks[i.gridcell[0]][i.gridcell[1]] = i
        

    for b in blocks_to_check:
    #For all blocks to check for matches...
        match_set.add(b)    #Start with a match of one
        next_blocks = ([], [], [], []) #Respectively holds blocks down, down-right, right, up-right
        for j in (1, 2):
            if b.gridcell[0] + j < len(blocks):
            #If we're not out of bounds...
                next_blocks[0].append(blocks[b.gridcell[0]+j][ b.gridcell[1]]) #add the block below
            if b.gridcell[0] + j < len(blocks) and b.gridcell[1] + j < len(blocks[0]):
            #If we're not out of bounds...
                next_blocks[1].append(blocks[b.gridcell[0]+j][b.gridcell[1]+j])#add the block down and to the right
            if b.gridcell[1] + j < len(blocks[0]):
            #If we're not out of bounds...
                next_blocks[2].append(blocks[b.gridcell[0]][b.gridcell[1]+j])#add the block to the right
            if b.gridcell[0] - j >= 0 and b.gridcell[1] + j < len(blocks[0]):
            #If we're not out of bounds...
                next_blocks[3].append(blocks[b.gridcell[0]-j][b.gridcell[1]+j])#add the block up and to the right
        #TODO: Optimize this so the above chain of conditionals is done in one loop, if possible

        for i in next_blocks:
        #For all the lists of blocks above...
            if len([1 for j in i if j and i is not j and b.color is j.color]) >= 2:
            #If there are two blocks and they're both the same color as the first...
                match_set.update(i) #Mark these blocks as matching

        if len(match_set) >= 3:
        #If at least 3 blocks are aligned...
            blocks_to_clear.update(match_set) #Mark the blocks in question for removal
            gamedata.score     += (len(match_set) ** 2) * gamedata.multiplier
            gamedata.combo      = True
            gamedata.multiplier = gamedata.DEFAULT_MULTIPLIER * 2

        match_set.clear()

    if len(blocks_to_clear) >= 3:
    #If we're clearing any blocks...
        blockclear.play()
        for b in blocks_to_clear:
        #For every block marked for clearing...
            b.state = block_type.STATES.DYING
        blocks_to_clear.clear()
