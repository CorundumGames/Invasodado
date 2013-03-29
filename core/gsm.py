'''
This module manages the game loop; it handles the flow from one game state (aka
game screen) to the next.

@var _current_state: The screen we're currently at.
'''
import pygame

from game.splash import SplashScreen

### Globals ####################################################################
_current_state = SplashScreen()
################################################################################

### Functions ##################################################################
def update():
    '''
    Moves us forward one frame.

    First it sees if we're changing states.  If not, we handle input, make
    decisions, then render the graphics.
    '''
    global _current_state
    
    if _current_state:
    #If we actually have a state...
        if not _current_state.next_state:
        #If we're not changing to another state...
            _current_state.events(pygame.event.get())
            _current_state.logic()
            _current_state.render()
        else:
            temp = _current_state.next_state
            _current_state.next_state = None
            _current_state.__del__()  #Dunno why 'del _current_state' doesn't work
            _current_state = temp

################################################################################