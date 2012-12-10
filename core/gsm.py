import pygame.display

import game.mainmenu as mainmenu

current_state = mainmenu.MainMenu()

def update():
    '''
    Moves us forward one frame.
    
    First it sees if we're changing states.  If not, we handle input, make
    decisions, then render the graphics.
    '''
    global current_state

    if current_state != None:
    #If we actually have a state...
        if current_state.next_state == None:
        #If we're not changing to another state...
            current_state.events(pygame.event.get())
            current_state.logic()
            current_state.render()
        else:
            current_state = current_state.next_state
    
    