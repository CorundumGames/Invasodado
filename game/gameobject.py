'''
A class for pretty much any object in the game to inherit from.  Provides
facilities for motion, display, and the like.
'''

from pygame.sprite import Sprite

### Globals ####################################################################
'''
@var _state_changes: Module-private.  Set of all objects that will change state
                     on the next frame.
'''
_state_changes = set()
################################################################################

### Functions ##################################################################
def update():
    '''
    Handles all of the object state changes queued up before this frame's game
    logic is handled.  This way, it's much easier to predict when an object
    will be in what state.
    '''
    for i in _state_changes:
    #For all state changes we have lined up...
        i.state      = i.next_state
        i.next_state = None
        #Change the object's state.
        
    _state_changes.clear()

################################################################################

class GameObject(Sprite, object):
    '''
    @invariant: self.state in self.__class__.STATES
    @
    '''
    actions    = None
    collisions = None
    group      = None

    def __init__(self):
        Sprite.__init__(self)
        self.acceleration = [0.0, 0.0]
        self.next_state   = None
        self.position     = [-300.0, -300.0]
        self.rect         = None
        self.state        = None
        self.velocity     = [0.0, 0.0]

    def on_collide(self, other):
        '''
        Reacts based on the type of the other object.
        
        @param other: The object that we collided with.
        @type other: A subclass of GameObject
        '''
        other_type = other.__class__
        collisions = self.collisions
        if isinstance(collisions, dict):
        #If this object can interact with more than one other type...
            if other_type in collisions and callable(collisions[other_type]):
            #If we can interact with the other object...
                collisions[other_type](self, other)
        elif callable(collisions):
        #Else if we can collide with just one other type of object...
            collisions(other)

    def update(self):
        '''
        Acts on this object's current state.
        '''
        assert self.state in self.__class__.actions, \
        "A %s tried to act on an invalid state %s!" % (self, self.state)

        method_name = self.__class__.actions[self.state]
        if method_name and callable(getattr(self, method_name)):
        #If this key has a function for its element...
            getattr(self, method_name)()
            
    def change_state(self, next_state):
        '''
        Queues this object for a state change in the next frame.
        
        @param next_state: The state to switch to, in type(self).STATES.
        @type next_state: The values used in config.Enum to represent constants
        '''
        self.next_state = next_state
        _state_changes.add(self)
