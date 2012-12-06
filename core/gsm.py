import pygame.display
current_state = None

def update():
    '''Moves us forward a bit.
    
    First it sees if we're changing states.  If not, we handle input, make
    decisions, then render the graphics.
    '''
    states = pygame.event.get()
    current_state.events(states)
    current_state.logic()
    current_state.render()
    
    