import config
from game import ingame
from game import mainmenu

current_state = mainmenu.MainMenu()

def update():
    '''Moves us forward a bit.
    
    First it sees if we're changing states.  If not, we handle input, make
    decisions, then render the graphics.
    '''
    current_state.events()
    current_state.logic()
    current_state.render()
    
    