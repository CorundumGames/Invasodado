import config

class GameStateManager:
    '''Owns something derived from Gamestate.  Constantly updates it.'''
    
    #Which screen we're currently on.
    _current_state = None
    
    def __init__(self):
        '''GameStateManager is a singleton, so no instantiation!'''
        raise RuntimeError(__doc__)
    
    @staticmethod
    def update():
        '''Moves us forward a frame.
        
        First it sees if we're changing states.  If not, we handle input, make
        decisions, then render the graphics.
        '''
        if _current_state.next_state != None:
            _current_state =_current_state.next_state
        
        _current_state.events()
        _current_state.logic()
        _current_state.render()
        
        
    