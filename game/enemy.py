import os.path
from math import copysign
from random import choice, uniform

import pygame.mixer
import pygame.rect

from core import color
from core import config
from core import particles
from core import settings

from game import balloflight
from game.gameobject import GameObject


FRAMES    = [pygame.Rect(32 * i, 32, 32, 32) for i in range(4)]
START_POS = (32, 32)

ENEMY_FRAMES = color.get_colored_objects(FRAMES)
ENEMY_FRAMES_COLOR_BLIND = color.get_colored_objects(FRAMES,True,True)
_hurt        = pygame.mixer.Sound(os.path.join('sfx', 'enemyhit.wav'))


class Enemy(GameObject):
    STATES       = config.Enum('IDLE', 'APPEARING', 'LOWERING', 'ACTIVE', 'DYING', 'CHEERING')
    acceleration = [0.0, 0.0]
    anim         = 0.0
    base_speed   = 0.5
    GROUP        = None
    shoot_odds   = 0.002
    should_flip  = False
    start_time   = None
    velocity     = [0.5, 0.0]
    #particles    = particles.ParticlePool(particles.Particle)

    def __init__(self, form_position):
        GameObject.__init__(self)
        self.color              = choice(color.LIST[:config.NUM_COLORS])
        self._form_position     = form_position
        self.current_frame_list = ENEMY_FRAMES_COLOR_BLIND if settings.color_blind else ENEMY_FRAMES
        self.image              = self.current_frame_list[id(self.color)][0]
        self.position           = list(START_POS)
        self.rect               = pygame.Rect(START_POS, self.image.get_size())
        self.state              = Enemy.STATES.IDLE

        #self.emitter       = particles.ParticleEmitter(self.__class__.particles, self.rect, 4, ingame.ENEMIES)
        del self.acceleration, self.velocity

    def appear(self):
        self.add(Enemy.GROUP)
        self.position     = [START_POS[0] * (self._form_position[0]+1)* 1.5,
                             START_POS[1] * (self._form_position[1]+1)* 1.5]
        self.rect.topleft = (self.position[0] + .5, self.position[1] + .5)
        self.color        = choice(color.LIST[0:config.NUM_COLORS])
        self.image        = self.current_frame_list[id(self.color)][0]
        self.change_state(Enemy.STATES.ACTIVE)

    def move(self):
        self.image        = self.current_frame_list[id(self.color)][int(-abs(Enemy.anim - 3) + 3) % 4]
        self.position[0] += Enemy.velocity[0]
        self.rect.topleft = (self.position[0] + .5, self.position[1] + .5)
        #self.emitter.rect = self.rect
        
        if uniform(0, 1) < Enemy.shoot_odds:
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
        balloflight.get_ball(self.position, self.color).add(Enemy.GROUP)
        _hurt.play()
        self.kill()

        self.position      = [-300.0, -300.0]
        self.rect.topleft  = self.position
        self.change_state(Enemy.STATES.IDLE)
        Enemy.velocity[0] += copysign(0.1, Enemy.velocity[0])
        #^ Increase the enemy squadron's speed (copysign() considers direction)

    def lower(self):  #Later we'll make this smoother.
        self.position[1] += 8
        self.rect.top     = self.position[1]
        self.change_state(Enemy.STATES.ACTIVE)

    def cheer(self):
        pass

    actions = {
                STATES.APPEARING: 'appear',
                STATES.LOWERING : 'lower' ,
                STATES.ACTIVE   : 'move'  ,
                STATES.DYING    : 'die'   ,
                STATES.IDLE     : None    ,
                STATES.CHEERING : 'cheer' ,
              }

from game import enemybullet
