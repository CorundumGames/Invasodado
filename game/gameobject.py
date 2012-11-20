import pygame.sprite

class GameObject(pygame.sprite.DirtySprite):
    actions    = dict()
    collisions = dict()
    
    def __init__(self):
        pygame.sprite.DirtySprite.__init__(self)
        self.acceleration = [0.0, 0.0]
        self.position     = [0.0, 0.0]
        self.rect         = None
        self.state        = None
        self.velocity     = [0.0, 0.0]
        self.dirty        = 2
        
    def on_collide(self, other):
        if isinstance(self.collisions, dict):
        #If this object can interact with more than one other types...
            if type(other) in self.collisions:
            #If we can interact with the other object...
                if callable(self.collisions[type(other)]):
                    self.collisions[type(other)](other)
        elif callable(self.collisions):
        #Else if we have any collisions...
            self.collisions(other)
    
    def update(self):
        if self.state in self.__class__.actions:
            if callable(self.__class__.actions[self.state]):
            #If this key has a function for its element...
                self.__class__.actions[self.state](self)