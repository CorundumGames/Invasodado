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
        if callable(self.actions[self.state]):
            self.actions[self.state]()