'''
ComboCounter is a number that briefly floats up whenever the player makes a
combo in clearing blocks.  This is a user feedback thing.
'''
import pygame
from core import config
from game.gameobject import GameObject
from game import hudobject
from game.hudobject import HudObject

### Constants ##################################################################
TIME_MOVING = 30
TIME_STANDING = 30
SPEED = 2
STATE_NAMES = ('IDLE', 'APPEARING', 'MOVING', 'STANDING', 'LEAVING')
################################################################################

### Globals ####################################################################
_counters = set()
################################################################################

### Functions ##################################################################
def get_combo_counter(num, pos):
    if not _counters:
        _counters.add(ComboCounter(num, pos))
        
    counter = _counters.pop()
    counter.position = list(pos)
    counter.time_left = 0
    counter.image = hudobject.make_text(str(num), pos = pos, surfaces=True)
    counter.rect = pygame.Rect(pos[0], pos[1], counter.image.get_width(), counter.image.get_height())
    return counter
################################################################################

class ComboCounter(HudObject):
    STATES = config.Enum(*STATE_NAMES)
    
    def __init__(self, num, pos):
        super().__init__(hudobject.make_text(str(num), pos=pos, surfaces=True), pos)
        self.next_state = None
        self.position   = list(pos)
        self.rect       = pygame.Rect(pos[0], pos[1], self.image.get_width(), self.image.get_height())
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
               STATES.IDLE: None,
               STATES.APPEARING: 'appear',
               STATES.MOVING: 'move',
               STATES.STANDING: 'stand',
               STATES.LEAVING: 'vanish',
               }