import config
import gamestate

current_state = None

def update():
    '''Moves us forward a frame.
    
    First it sees if we're changing states.  If not, we handle input, make
    decisions, then render the graphics.
    '''
    if isinstance(current_state, gamestate.GameState):
        current_state = current_state.next_state
    
    current_state.events()
    current_state.logic()
    current_state.render()