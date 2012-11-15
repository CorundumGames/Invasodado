import pygame.sprite

class GameObject(pygame.sprite.DirtySprite): 
    def __init__(self):
        pygame.sprite.DirtySprite.__init__(self)
        self.acceleration = [0.0, 0.0]
        self.actions      = dict()
        self.position     = [0.0, 0.0]
        self.rect         = None
        self.state        = None
        self.velocity     = [0.0, 0.0]
        self.dirty = 2
        
    def on_collide(self, other):
        pass
    
    def update(self):
        if callable(self.actions[self.state]):
        #If this key has a function for its element...
            self.actions[self.state]()