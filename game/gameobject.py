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
        x = other.__class__
        if isinstance(self.collisions, dict):
        #If this object can interact with more than one other type...
            if x in self.collisions:
            #If we can interact with the other object...
                if callable(self.collisions[x]):
                    self.collisions[x](self, other)
        elif callable(self.collisions):
        #Else if we have any collisions...
            self.collisions(other)
    
    def update(self):
        method_name = self.__class__.actions[self.state]
        if method_name and callable(getattr(self, method_name)):
        #If this key has a function for its element...
            getattr(self, method_name)()