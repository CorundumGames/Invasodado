'''
ComboCounter is a number that briefly floats up whenever the player makes a
combo in clearing blocks.  This is a user feedback thing.
'''
from pygame import Rect

from core            import config
from game.gameobject import GameObject
from game            import hudobject
from game.hudobject  import HudObject

### Constants ##################################################################
TIME_MOVING   = 30
TIME_STANDING = 30
SPEED         = 2
STATE_NAMES   = ('IDLE', 'APPEARING', 'MOVING', 'STANDING', 'LEAVING')
################################################################################

### Globals ####################################################################
_counters = set()
################################################################################

### Functions ##################################################################
def get_combo_counter(num, pos):
    '''
    Returns a ComboCounter object, creating a new one if need be.
    
    @param num: The number to display
    @param pos: Position on-screen this ComboCounter should appear
    @type num: int
    @type pos: [float, float]
    @return: A new ComboCounter
    @rtype: ComboCounter
    '''
    if not _counters:
        _counters.add(ComboCounter(num, pos))
        
    counter           = _counters.pop()
    counter.position  = list(pos)
    counter.time_left = 0
    counter.image     = hudobject.make_text(str(num), pos=pos, surfaces=True)
    counter.rect      = Rect(pos, counter.image.get_size())
    return counter
################################################################################

class ComboCounter(HudObject):
    STATES = config.Enum(*STATE_NAMES)
    
    def __init__(self, num, pos):
        super().__init__(hudobject.make_text(str(num), pos=pos, surfaces=True), pos)
        self.next_state = None
        self.position   = list(pos)
        self.rect       = Rect(pos, self.image.get_size())
        self.time_left  = 0
        self.change_state(ComboCounter.STATES.IDLE)
        
    def update(self):
        GameObject.update(self)
        
    def move(self):
        self.position[1] -= SPEED
        self.rect.top     = self.position[1] + .5
        self.time_left -= 1
        if not self.time_left:
            self.change_state(ComboCounter.STATES.STANDING)
            self.time_left = TIME_STANDING
            
    def stand(self):
        self.time_left -= 1
        if not self.time_left:
            self.change_state(ComboCounter.STATES.LEAVING)
            self.time_left = 0
            
    def vanish(self):
        self.kill()
        self.change_state(ComboCounter.STATES.IDLE)
        
    def appear(self):
        self.time_left = TIME_MOVING
        self.change_state(ComboCounter.STATES.MOVING)
        
    actions = {
               STATES.IDLE      : None    ,
               STATES.APPEARING : 'appear',
               STATES.MOVING    : 'move'  ,
               STATES.STANDING  : 'stand' ,
               STATES.LEAVING   : 'vanish',
               }