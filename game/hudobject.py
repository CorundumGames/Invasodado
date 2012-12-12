import pygame.sprite

import gameobject

class HudObject(gameobject.GameObject):
    '''HudObject is meant for displays like lives, score, etc.
    It is its own type so it can be in collisions.do_not_check, because we
    don't intend for these to collide with anything.
    '''
    actions    = None
    collisions = None
    
    def __init__(self, image, pos):
        pygame.sprite.Sprite.__init__(self)
        self.acceleration = None
        self.image        = image
        self.position     = None
        self.rect         = pygame.Rect(pos, self.image.get_size())
        self.state        = None
        self.velocity     = None
        
    def update(self):
        pass
    