from math import log1p
import os.path
from operator import iadd
import random

import pygame.mixer
import pygame.rect

import core.color  as color
import core.config as config
import core.particles as particles

import balloflight
from gameobject import GameObject
import ingame

FRAMES    = [pygame.Rect(32 * i, 32, 32, 32) for i in range(4)]
START_POS = (32, 32)

enemy_frames = config.get_colored_objects(FRAMES)
hurt         = pygame.mixer.Sound(os.path.join('sfx', 'enemyhurt.wav'))



def increase_difficulty():
    '''
    Increases Enemy's fire rate and speed based on time elapsed
    '''
    Enemy.shoot_odds = log1p(pygame.time.get_ticks() - Enemy.start_time)/1000
    assert 0.0 <= Enemy.shoot_odds < 1.0, \
    "Expected a valid probability, got %f" % Enemy.shoot_odds

class Enemy(GameObject):
    STATES       = config.Enum('IDLE', 'APPEARING', 'LOWERING', 'ACTIVE', 'DYING', 'CHEERING')
    acceleration = [0.0, 0.0]
    anim         = 0.0
    base_speed   = 0.5
    shoot_odds   = 0.002
    should_flip  = False
    start_time   = None
    velocity     = [0.5, 0.0]
    #particles    = particles.ParticlePool(particles.Particle)

    def __init__(self, form_position):
        GameObject.__init__(self)
        self.color         = random.choice(color.LIST[:config.NUM_COLORS])
        self.form_position = form_position
        self.image         = enemy_frames[id(self.color)][0]
        self.position      = list(START_POS)
        self.rect          = pygame.Rect(START_POS, self.image.get_size())
        self.state         = Enemy.STATES.IDLE

        #self.emitter       = particles.ParticleEmitter(self.__class__.particles, self.rect, 4, ingame.ENEMIES)
        del self.acceleration, self.velocity


    def appear(self):
        self.add(ingame.ENEMIES)
        self.position     = [START_POS[0] * (self.form_position[0]+1)* 1.5,
                             START_POS[1] * (self.form_position[1]+1)* 1.5]
        self.rect.topleft = (self.position[0] + .5, self.position[1] + .5)
        self.color        = random.choice(color.LIST[0:config.NUM_COLORS])
        self.image        = enemy_frames[id(self.color)][0]
        self.state        = Enemy.STATES.ACTIVE

    def move(self):
        self.image        = enemy_frames[id(self.color)][int(-abs(Enemy.anim - 3) + 3) % 4]
        self.position[0] += Enemy.velocity[0]
        self.rect.topleft = (self.position[0] + .5, self.position[1] + .5)
        #self.emitter.rect = self.rect
        if random.uniform(0, 1) < Enemy.shoot_odds:
            b             = enemybullet.get_enemy_bullet()
            b.rect.midtop = self.rect.midbottom
            b.position    = list(b.rect.topleft)
            b.add(ingame.ENEMY_BULLETS)

        if not Enemy.should_flip:
        #If the squadron of enemies is marked to reverse direction...
            if self.rect.right > config.SCREEN_RECT.width or self.rect.left < 0:
            #If this enemy touches either end of the screen...
                Enemy.should_flip = True

    def die(self):
        balloflight.get_ball(self.position, self.color).add(ingame.ENEMIES)
        hurt.play()
        self.remove(ingame.ENEMIES)

        self.position     = [-300.0, -300.0]
        self.rect.topleft = self.position
        self.state        = Enemy.STATES.IDLE
        #increase the velocity of the squadron
        Enemy.velocity[0] += .1 if Enemy.velocity[0] > 0 else -.1

    def lower(self):  #Later we'll make this smoother.
        self.position[1] += 8
        self.rect.top     = self.position[1]
        self.state        = Enemy.STATES.ACTIVE

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

import enemybullet