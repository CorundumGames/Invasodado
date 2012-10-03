import pygame

class GameObject(pygame.sprite.Sprite): 
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.acceleration = [0.0, 0.0]
        self.actions      = dict()
        self.position     = [0.0, 0.0]
        self.rect         = None
        self.state        = None
        self.velocity     = [0.0, 0.0]
        
    def on_collide(self, other):
        pass
    
    def update(self):
        self.previous_pos = list(self.position)
        
        if callable(self.actions[self.state]):
        #If this key has a function for its element...
            self.actions[self.state]()