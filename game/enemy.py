import random

import pygame.mixer
import pygame.rect

import core.color  as color
import core.config as config

import balloflight
import gameobject
import ingame

FRAMES    = [pygame.Rect( 0, 32, 32, 32),
             pygame.Rect(32, 32, 32, 32)]
START_POS = (32, 32)
SAFE_SPOT = (0, config.screen.get_height()*3)

enemy_frames = dict([(id(c), color.blend_color(config.SPRITES.subsurface(FRAMES[0]).copy(), c)) for c in color.LIST])

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
    
    def __init__(self, form_position):
        gameobject.GameObject.__init__(self)
        self.color         = random.choice(color.LIST[:config.NUM_COLORS])
        self.form_position = form_position
        self.image         = enemy_frames[id(self.color)]
        self.position      = list(START_POS)
        self.rect          = pygame.Rect(START_POS, self.image.get_size())
        self.state         = self.__class__.STATES.IDLE 
        self.shootRange    = 10
        
    def appear(self):
        self.add(ingame.ENEMIES)
        self.position     = [START_POS[0] * (self.form_position[0]+1)* 1.5,
                             START_POS[1] * (self.form_position[1]+1)* 1.5]
        self.rect.topleft = map(round, self.position)
        self.color        = random.choice(color.LIST[0:config.NUM_COLORS])
        self.image        = enemy_frames[id(self.color)]
        self.image.set_colorkey(self.image.get_at((0, 0)), config.FLAGS)
        
        self.state = self.__class__.STATES.ACTIVE
        
    def move(self):
        self.position[0] += Enemy.velocity[0]
        self.rect.topleft = (self.position[0] + .5, self.position[1] + .5)
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