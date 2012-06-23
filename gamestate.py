import config

#Every abstract method must raise an exception with this statement.
ERROR_STATEMENT = "GameState must be sub-classed, not instantiated!"

class GameState:
    '''Consider GameState to be abstract; that is, do not instantiate it!
    
    GameState is meant to be derived from to represent different screens with
    different objects (e.g. the in-game state would have the player, the blocks,
    etc. while the main menu would have the buttons.
    
    '''
    
    #The list of all pygame.Groups; left-most groups are blitted first.
    _group_list = []
    
    next_state = None
    
    def __init__(self):
        '''Initialization logic is normally executed once here.'''
        raise NotImplementedError(ERROR_STATEMENT)
        
    def events(self):
        '''Handles external input (mostly from the keyboard).'''
        raise NotImplementedError(ERROR_STATEMENT)
    
    def logic(self):
        '''Executes the next step in the game logic (collisions, etc.).'''
        raise NotImplementedError(ERROR_STATEMENT)
    
    def render(self):
        '''Blits all Sprites (or derived) to the screen.
        
        Remember, Group.blit() renders Sprites in arbitrary order, so we must
        assign Sprites to groups by layer, then call Group.blit() sequentially.
        '''
        raise NotImplementedError(ERROR_STATEMENT)
    
    