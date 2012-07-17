import pygame

class GameObject(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.acceleration = [0, 0]
        self.rect         = None
        self.state        = None
        self.velocity     = [0, 0]
        
        