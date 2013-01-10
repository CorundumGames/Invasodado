import random

import pygame

import core.config as config
import core.particles as particles

import hudobject

STARS_GROUP = pygame.sprite.RenderUpdates()

class Star(particles.Particle):
    image     = config.SPRITES.subsurface(4, 170, 2, 2)
    
    def appear(self):
        self.velocity[0] = random.randint(1, 5)
        self.state       = self.__class__.STATES.ACTIVE
        
    def move_func(self):
        self.position[0] += self.velocity[0]
        self.rect.left    = self.position[0]

EARTH = hudobject.HudObject(config.EARTH, [0, 0])
GRID  = hudobject.HudObject(config.BG   , [0, 0])
STARS = particles.ParticleEmitter(particles.ParticlePool(Star),
                                  pygame.Rect([0, 0], config.SCREEN_RECT.bottomleft),
                                  8,
                                  STARS_GROUP
                                  )
EARTH.rect.center = config.SCREEN_RECT.midbottom