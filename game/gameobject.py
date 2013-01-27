import pygame.sprite

class GameObject(pygame.sprite.Sprite):
    actions    = dict()
    collisions = dict()

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.acceleration = [0.0, 0.0]
        self.position     = [0.0, 0.0]
        self.rect         = None
        self.state        = None
        self.velocity     = [0.0, 0.0]

    def on_collide(self, other):
        x   = other.__class__
        col = self.collisions
        if isinstance(col, dict):
        #If this object can interact with more than one other type...
            if x in col and callable(col[x]):
            #If we can interact with the other object...
                col[x](self, other)
        elif callable(col):
        #Else if we have any collisions...
            col(other)

    def update(self):
        assert self.state in type(self).actions, \
        "A {} tried to act on an invalid state {}!".format(type(self).__name__, self.state)

        method_name = self.__class__.actions[self.state]
        if method_name and callable(getattr(self, method_name)):
        #If this key has a function for its element...
            getattr(self, method_name)()