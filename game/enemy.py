import random

import pygame.mixer
import pygame.rect

import core.color  as color
import core.config as config
import core.particles as particles

import balloflight
import gameobject
import ingame

FRAMES    = [pygame.Rect(32*i, 32, 32, 32) for i in range(4)]
START_POS = (32, 32)
SAFE_SPOT = (0, config.screen.get_height()*3)

enemy_frames = config.get_colored_objects(FRAMES)

'''
Algorithm for storing one colored Enemy per color (with all animations)
1. Create as many copies of the Enemy frames (that is, properly animated) as there are colors for the desired difficulty
2: Paint them their respective colors
3: Store them in a dict({pygame.Color : pygame.Surface})
4: When an enemy's color is assigned, simply have it draw its Surface from the dict
'''

hurt = pygame.mixer.Sound("./sfx/enemyhurt.wav")

class Enemy(gameobject.GameObject):
    STATES    = config.Enum('IDLE', 'APPEARING', 'LOWERING', 'ACTIVE', 'DYING', 'SHOOTING', 'CHEERING')

    acceleration = [0.0, 0.0]
    count        = 0
    should_flip  = False
    velocity     = [0.5, 0.0]
    #particles    = particles.ParticlePool(particles.Particle)

    def __init__(self, form_position):
        gameobject.GameObject.__init__(self)
        self.anim          = 0.0
        self.color         = random.choice(color.LIST[:config.NUM_COLORS])
        self.form_position = form_position
        self.image         = enemy_frames[id(self.color)][0]
        self.position      = list(START_POS)
        self.rect          = pygame.Rect(START_POS, self.image.get_size())
        self.state         = self.__class__.STATES.IDLE
        self.shootRange    = 10

        #self.emitter       = particles.ParticleEmitter(self.__class__.particles, self.rect, 4, ingame.ENEMIES)
        del self.acceleration


    def appear(self):
        self.add(ingame.ENEMIES)
        self.position     = [START_POS[0] * (self.form_position[0]+1)* 1.5,
                             START_POS[1] * (self.form_position[1]+1)* 1.5]
        self.rect.topleft = map(round, self.position)
        self.color        = random.choice(color.LIST[0:config.NUM_COLORS])
        self.image        = enemy_frames[id(self.color)][0]

        self.state = self.__class__.STATES.ACTIVE

    def move(self):
        self.anim        += 1.0/3.0
        self.image        = enemy_frames[id(self.color)][int(-abs(self.anim - 3) + 3) % 4]
        self.position[0] += Enemy.velocity[0]
        self.rect.topleft = (self.position[0] + .5, self.position[1] + .5)
        #self.emitter.rect = self.rect
        if random.uniform(1, 5000) < self.shootRange:
            self.state = self.__class__.STATES.SHOOTING

        if not Enemy.should_flip:
        #If the squadron of enemies is marked to reverse direction...
            if self.rect.right > config.screen.get_width() or self.rect.left < 0:
            #If this enemy touches either end of the screen...
                Enemy.should_flip = True


    def shoot(self):
        b             = enemybullet.get_enemy_bullet()
        b.rect.midtop = self.rect.midbottom
        b.position    = list(b.rect.topleft)
        b.add(ingame.ENEMIES)
        self.state    = self.__class__.STATES.ACTIVE

    def die(self):
        balloflight.get_ball(self.position, self.color).add(ingame.ENEMIES)
        hurt.play()
        self.remove(ingame.ENEMIES)

        self.position     = [-300.0, -300.0]
        self.velocity     = [0, 0]
        self.rect.topleft = self.position

        self.state = self.__class__.STATES.IDLE
        #increase the velocity of the squadron
        Enemy.velocity[0] += .1 if Enemy.velocity[0] > 0 else -.1

    def cheer(self):
        pass

    actions = {
                STATES.APPEARING: 'appear'      ,
                STATES.LOWERING : NotImplemented,
                STATES.ACTIVE   : 'move'        ,
                STATES.DYING    : 'die'         ,
                STATES.IDLE     : None          ,
                STATES.SHOOTING : 'shoot'       ,
                STATES.CHEERING : 'cheer',
               }

import enemybullet