'''
bg.py contains common background elements in Invasodado.  Pretty much every
screen in the game has the same background.
'''

from random import randint

import pygame

from core           import config
from core.particles import ParticleEmitter, ParticlePool
from game.hudobject import HudObject

### Functions ##################################################################
def _star_appear(self):
    '''
    Stars appear on the left edge of the screen and travel right at one of five
    possible speeds.
    '''
    self.velocity[0] = randint(1, 5)

def _star_move(self):
    '''
    And this is the part where they actually move.
    '''
    self.position[0] += self.velocity[0]
    self.rect.left    = self.position[0]
    
################################################################################

STARS_GROUP = pygame.sprite.RenderUpdates()
_STAR_IMAGE = config.get_sprite(pygame.Rect(4, 170, 2, 2))

EARTH = HudObject(config.EARTH, [0, 0])
GRID  = HudObject(config.GRID_BG   , [0, 0])
STARS = ParticleEmitter(
                        ParticlePool(_STAR_IMAGE, _star_move, _star_appear),
                        pygame.Rect(0, 0, 0, config.SCREEN_HEIGHT),
                        8,
                        STARS_GROUP
                        )

EARTH.rect.midbottom = config.SCREEN_RECT.midbottom