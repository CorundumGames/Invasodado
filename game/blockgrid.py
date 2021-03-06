'''
The blockgrid module is responsible for handling interactions between multiple
blocks.  It's designed around Invasodado, but with a little work it could be
refitted for other match-3 games like Bejewelled or Puzzle League.
'''

from pygame.display import get_surface
from pygame         import Rect
from pygame         import Surface
from pygame.sprite  import GroupSingle, Sprite

from core import config
from core import color
from game import gamedata

### Constants ##################################################################
ALARM_LINE = 2
BLOCK_TYPE = None
CELL_SIZE  = (32, 32)
COMBOS     = tuple(config.load_sound('combo%d.wav' % i) for i in range(1, 6))
SIZE       = (20, 12) #(width, height)
RECT       = Rect(0, 0, get_surface().get_width(), SIZE[1] * CELL_SIZE[1])
################################################################################

### Globals ####################################################################
blocks           = None
block_buffer     = GroupSingle(Sprite())
_blocks_to_check = set()
_blocks_to_clear = set()
_block_clear     = config.load_sound('clear.wav')


block_buffer.sprite.rect = Rect(0, 0, 0, 0)
################################################################################

def any_active():
    s = BLOCK_TYPE.STATES
    
    for i in BLOCK_TYPE.GROUP:
        if i.state not in {s.IDLE, s.ACTIVE}:
        #If this block is moving...
            return True
    return False

def cache_block_image():
    global block_buffer
    block_buffer.sprite.image = Surface((640, 384), config.BLIT_FLAGS, config.DEPTH)
    block_buffer.sprite.image.set_colorkey(color.BLACK, config.BLIT_FLAGS)
    BLOCK_TYPE.GROUP.draw(block_buffer.sprite.image)

def check_block(block, should_check=True):
    if should_check:
    #If we want to check this block for matches...
        _blocks_to_check.add(block)
    else:
        _blocks_to_check.discard(block)

def clean_up():
    '''
    Deletes all blocks that were created.

    @postcondition: No more objects of BLOCK_TYPE exist in memory.
    '''
    global blocks, block_buffer
    blocks = get_empty_block_array()
    block_buffer = GroupSingle(Sprite())
    block_buffer.sprite.rect = Rect(0, 0, 0, 0)
    _blocks_to_check.clear()
    _blocks_to_clear.clear()
    
def clear_color(color):
    '''
    Destroys all blocks of the specified color.

    @param color: Color of the blocks that should be deleted.
    @postcondition: No color-colored blocks exist on-screen.
    '''
    for i in (j for j in BLOCK_TYPE.GROUP if j and j.color is color):
    #For all blocks of the given color...
        i.change_state(BLOCK_TYPE.STATES.DYING)

def clear_row(row):
    '''
    Destroys all blocks in the specified row.

    @param row: The row of blocks to destroy, on [0, SIZE[1]).
    @postcondition: No blocks on-screen exist in the given row.
    '''

    assert 0 <= row < SIZE[1], \
    "Expected row value in 0 <= x < %i, but got %i" % (SIZE[1], row)

    for i in (j for j in blocks if any(j)):
    #For all blocks in this row...
        i[SIZE[1] - 1].change_state(BLOCK_TYPE.STATES.DYING)

def get_empty_block_array():
    '''
    Returns an empty 2D array to reset the block grid
    
    Outer list is the list of columns
    Inner list is the list of rows
    
    So (x, y)
    '''
    return tuple([None for i in range(SIZE[1])] for j in range(SIZE[0]))

def is_above_threshold():
    for i in blocks:
        for j in i[:3]:
            if j and j.gridcell[1] <= ALARM_LINE:
                return True
    return False

def update():
    '''
    Checks if any blocks of the same color are lined up, clears them if so.

    @postcondition: Sets of 3+ like-colored blocks are removed from the game.
    '''
    global blocks
    blocks = get_empty_block_array()

    for i in (j for j in BLOCK_TYPE.GROUP if j and j.state == BLOCK_TYPE.STATES.ACTIVE):
    #For all blocks that are on the grid and not moving...
        assert isinstance(i, BLOCK_TYPE), "A %s got into the Block grid!" % i
        blocks[i.gridcell[0]][i.gridcell[1]] = i
    
    for b in _blocks_to_check:
    #For all blocks to check for matches... 
        match_set = {b}  #Start with a match of one
        next_blocks = ([], [], [], []) #Respectively holds blocks down, down-right, right, up-right
        for j in (1, 2):
            if b.gridcell[1] + j < SIZE[1]:
            #If we're not out of bounds...
                next_blocks[0].append(blocks[b.gridcell[0]][b.gridcell[1] + j])
                #add the block below
            if b.gridcell[0] + j < SIZE[0] and b.gridcell[1] + j < SIZE[1]:
            #If we're not out of bounds...
                next_blocks[1].append(blocks[b.gridcell[0] + j][b.gridcell[1] + j])
                #add the block down and to the right
            if b.gridcell[0] + j < SIZE[0]:
            #If we're not out of bounds...
                next_blocks[2].append(blocks[b.gridcell[0] + j][b.gridcell[1]])
                #add the block to the right
            if b.gridcell[1] - j >= 0 and b.gridcell[0] + j < SIZE[0]:
            #If we're not out of bounds...
                next_blocks[3].append(blocks[b.gridcell[0]+j][b.gridcell[1]-j])
                #add the block up and to the right
        #TODO: Optimize this so the above mess is done in one loop, if possible

        for i in next_blocks:
        #For all the lists of blocks above...
            if len([1 for j in i if j and i is not j and b.color is j.color]) >= 2:
            #If there are 2+ blocks that are the same color as the first...
                match_set.update(i) #Mark these blocks as matching

        if len(match_set) >= 3:
        #If at least 3 blocks are aligned...
            _blocks_to_clear.update(match_set) #Mark these blocks for removal
            

    if gamedata.combo_time:
        gamedata.combo_time -= 1
    else:
        gamedata.combo = 0
        
    if len(_blocks_to_clear) >= 3:
    #If we're clearing any blocks...
        _block_clear.play()
        if gamedata.combo_time:
            COMBOS[min(gamedata.combo, len(COMBOS)) - 1].play()
        
        gamedata.combo_time     = gamedata.MAX_COMBO_TIME
        gamedata.combo += 1
        gamedata.score += len(_blocks_to_clear) * gamedata.combo * 10

        for k in _blocks_to_clear:
        #For every block marked for clearing...
            k.change_state(BLOCK_TYPE.STATES.DYING)
        
        _blocks_to_clear.clear()

