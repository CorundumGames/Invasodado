from pygame.sprite import Sprite

state_changes = []

def update():
    global state_changes
    for i in state_changes:
        i.state = i.next_state
        i.next_state = None
    del state_changes[:]

class GameObject(Sprite, object):
    actions    = None
    collisions = None

    def __init__(self):
        Sprite.__init__(self)
        self.acceleration = [0.0, 0.0]
        self.next_state   = None
        self.position     = [0.0, 0.0]
        self.rect         = None
        self.state        = self.__class__.STATES.IDLE
        self.velocity     = [0.0, 0.0]

    def on_collide(self, other):
        '''
        Reacts based on the type of the other object.
        
        @param other: The object that we collided with.
        '''
        other_type = other.__class__
        collisions = self.collisions
        if isinstance(collisions, dict):
        #If this object can interact with more than one other type...
            if other_type in collisions and callable(collisions[other_type]):
            #If we can interact with the other object...
                collisions[other_type](self, other)
        elif callable(collisions):
        #Else if we have any collisions...
            collisions(other)

    def update(self):
        assert self.state in self.__class__.actions, \
        "A %s tried to act on an invalid state %s!" % (self, self.state)

        method_name = self.__class__.actions[self.state]
        if method_name and callable(getattr(self, method_name)):
        #If this key has a function for its element...
            getattr(self, method_name)()
            
    def change_state(self, next_state):
        self.next_state = next_state
        state_changes.append(self)