import pygame

class GameObject(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.velocity = [0, 0]
        self.acceleration = [0, 0]
        self.state = None
        self.rect = None