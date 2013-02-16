'''
An interface for representing game screens.
'''

import pygame.time

class GameState:
    '''
    Consider GameState to be abstract; that is, do not instantiate it!

    GameState is meant to be derived from to represent different screens with
    different objects (e.g. the in-game state would have the player, the blocks,
    etc. while the main menu would have the buttons.

    @ivar fps_timer: Regulates the game's framerate
    @ivar group_list: List of game object groups to process
    @ivar next_state: If not None, the gsm switches to this state
    '''
    fps_timer  = pygame.time.Clock()
    group_list = []
    next_state = None

    def __init__(self, *args, **kwargs):
        '''
        Initialization logic is normally executed once here.
        We can pass in arguments so our game state can run a certain way.  This
        way, rather than creating a new object or subclass for a state that's
        slightly different than another, we can just pass in an argument.
        '''
        pass

    def events(self, events):
        '''
        Handles external input (mostly from the keyboard).
        
        @param events: List of events to process (filtered if necessary)
        '''
        pass

    def logic(self):
        '''
        Executes the next step in the game logic (collisions, etc.).
        '''
        pass

    def render(self):
        '''
        Blits all Sprites (or derived) to the screen.

        Remember, Group.blit() renders Sprites in arbitrary order, so we must
        assign Sprites to groups by layer, then call Group.blit() sequentially.
        '''
        pass

    def change_state(self, state_type, *args, **kwargs):
        '''
        Changes the game screen to the given type, with the given arguments.
        Primarily meant to be used with functools.partial.
        '''
        self.next_state = state_type(*args, **kwargs)
