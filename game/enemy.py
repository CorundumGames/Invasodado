import os.path
from math import copysign
from random import choice, uniform

import pygame.mixer
import pygame.rect

from core import color
from core import config
from core.particles import ParticlePool, ParticleEmitter
from core import settings

from game            import balloflight
from game.gameobject import GameObject

### Constants ##################################################################
ENEMY_STATES = ('IDLE', 'APPEARING', 'LOWERING', 'ACTIVE', 'DYING', 'CHEERING')
FRAMES       = [pygame.Rect(32 * i, 32, 32, 32) for i in range(4)]
START_POS    = (32.0, 32.0)

ENEMY_FRAMES = color.get_colored_objects(FRAMES)
ENEMY_FRAMES_COLOR_BLIND = color.get_colored_objects(FRAMES, True, True)
################################################################################

### Globals ####################################################################
_hurt = config.load_sound('enemyhit.wav')
_hurt.set_volume(.5)
################################################################################

class Enemy(GameObject):
    STATES       = config.Enum(*ENEMY_STATES)
    anim         = 0.0
    base_speed   = 0.5
    GROUP        = None
    shoot_odds   = 0.002
    should_flip  = False
    start_time   = None
    velocity     = [0.5, 0.0]
    #particles    = particles.ParticlePool(particles.Particle)

    def __init__(self, form_position):
        super().__init__()
        self.amount_lowered     = 0
        self.color              = choice(color.LIST[:config.NUM_COLORS])
        self.column             = None
        self._form_position     = form_position
        self.current_frame_list = ENEMY_FRAMES_COLOR_BLIND if settings.color_blind else ENEMY_FRAMES
        self.image              = self.current_frame_list[id(self.color)][0]
        self.position           = list(START_POS)
        self.rect               = pygame.Rect(START_POS, self.image.get_size())
        self.state              = Enemy.STATES.IDLE
        self.emitter            = ParticleEmitter(color.color_particles[id(self.color)], self.rect, 1)
        del self.acceleration, self.velocity

    def appear(self):
        self.add(Enemy.GROUP)
        self.position     = [
                             START_POS[0] * (self._form_position[0]+1)* 1.5,
                             START_POS[1] * (self._form_position[1]+1)* 1.5
                            ]
        self.rect.topleft = (self.position[0] + .5, self.position[1] + .5)
        self.color        = choice(color.LIST[0:config.NUM_COLORS])
        self.__animate()
        self.emitter.pool = color.color_particles[id(self.color)]
        self.change_state(Enemy.STATES.ACTIVE)

    def move(self):
        self.__animate()
        self.position[0] += Enemy.velocity[0]
        self.rect.topleft = (self.position[0] + .5, self.position[1] + .5)
        #self.emitter.rect = self.rect
        
        if uniform(0, 1) < Enemy.shoot_odds and not enemybullet.EnemyBullet.halt:
        #With Enemy.shoot_odds% of firing...
            b             = enemybullet.get_enemy_bullet()
            b.rect.midtop = self.rect.midbottom
            b.position    = list(b.rect.topleft)
            b.add(enemybullet.EnemyBullet.GROUP)

        if not Enemy.should_flip:
        #If the squadron of enemies is not marked to reverse direction...
            if self.rect.right > config.SCREEN_RECT.width or self.rect.left < 0:
            #If this enemy touches either end of the screen...
                Enemy.should_flip = True

    def die(self):
        balloflight.get_ball(self.position, self.column, self.color).add(Enemy.GROUP)
        _hurt.play()
        self.emitter.burst(20)
        self.kill()
        
        self.position      = [-300.0, -300.0]
        self.rect.topleft  = self.position
        self.change_state(Enemy.STATES.IDLE)
        Enemy.velocity[0] += copysign(0.1, Enemy.velocity[0])
        #^ Increase the enemy squadron's speed (copysign() considers direction)

    def lower(self):  #Later we'll make this smoother.
        self.amount_lowered += 1
        self.__animate()
        self.position[1] += 1
        self.rect.top     = self.position[1]
        if self.amount_lowered == 8:
            self.amount_lowered = 0
            self.change_state(Enemy.STATES.ACTIVE)

    def cheer(self):
        self.__animate()
    
    def __animate(self):
        self.image = self.current_frame_list[id(self.color)][int(-abs(Enemy.anim - 3) + 3) % 4]

    actions = {
                STATES.APPEARING: 'appear',
                STATES.LOWERING : 'lower' ,
                STATES.ACTIVE   : 'move'  ,
                STATES.DYING    : 'die'   ,
                STATES.IDLE     : None    ,
                STATES.CHEERING : 'cheer' ,
              }

from game import enemybullet
