import random

import pygame

import core.config as config
from core.particles import ParticleEmitter, ParticlePool

from hudobject import HudObject

STARS_GROUP = pygame.sprite.RenderUpdates()

def star_appear(self):
    self.velocity[0] = random.randint(1, 5)

def star_move(self):
    self.position[0] += self.velocity[0]
    self.rect.left    = self.position[0]

star_image = config.SPRITES.subsurface(4, 170, 2, 2)

EARTH = HudObject(config.EARTH, [0, 0])
GRID  = HudObject(config.BG   , [0, 0])
STARS = ParticleEmitter(ParticlePool(star_image, star_move, star_appear),
                        pygame.Rect(0, 0, 0, config.SCREEN_HEIGHT),
                        8,
                        STARS_GROUP
                        )
EARTH.rect.center = config.SCREEN_RECT.midbottom