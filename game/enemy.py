import math
import random

import pygame.mixer
import pygame.rect

import block
from core import color
from core import config
import gameobject
import ingame
import shipbullet

FRAMES    = [pygame.Rect( 0*config.SCALE_FACTOR, 16*config.SCALE_FACTOR, 16*config.SCALE_FACTOR, 16*config.SCALE_FACTOR),
             pygame.Rect(16*config.SCALE_FACTOR, 16*config.SCALE_FACTOR, 16*config.SCALE_FACTOR, 16*config.SCALE_FACTOR)]
START_POS = (32, 32)
STATES    = config.Enum('IDLE', 'APPEARING', 'LOWERING', 'ACTIVE', 'DYING')
SAFE_SPOT = (0, config.screen.get_height()*3)

enemy_frames = dict([(id(c), color.blend_color(config.SPRITES.subsurface(FRAMES[0]).copy(), c)) for c in color.Colors.LIST])

'''
Algorithm for storing one colored Enemy per color (with all animations)
1. Create as many copies of the Enemy frames (that is, properly animated) as there are colors for the desired difficulty
2: Paint them their respective colors
3: Store them in a dict({pygame.Color : pygame.Surface})
4: When an enemy's color is assigned, simply have it draw its Surface from the dict
'''

hurt = pygame.mixer.Sound("./sfx/enemyhurt.wav")

class Enemy(gameobject.GameObject): 
    acceleration = [0.0, 0.0]
    count        = 0
    should_flip  = False
    velocity     = [1.0, 0.0]
    
    def __init__(self, form_position):
        gameobject.GameObject.__init__(self)
        
        self.actions = {
                        STATES.APPEARING: self.appear   ,
                        STATES.LOWERING : NotImplemented,
                        STATES.ACTIVE   : self.move     ,
                        STATES.DYING    : self.die      ,
                        STATES.IDLE     : None
                        }
        
        self.color         = random.choice(color.Colors.LIST)
        self.form_position = form_position
        self.image         = enemy_frames[id(self.color)]
        self.position      = list(START_POS)
        self.rect          = pygame.Rect(START_POS, (self.image.get_width(), self.image.get_height()))
        self.state         = STATES.IDLE
        
        self.image.set_colorkey(color.COLOR_KEY)   
        
    def appear(self):
        self.add(ingame.ENEMIES)
        self.position     = [START_POS[0] * (self.form_position[0]+1)*config.SCALE_FACTOR,
                             START_POS[1] * (self.form_position[1]+1)*.75*config.SCALE_FACTOR]
        self.rect.topleft = map(round, self.position)
        self.color        = random.choice(color.Colors.LIST)
        self.image        = enemy_frames[id(self.color)]
        self.image.set_colorkey(self.image.get_at((0, 0)))
        
        self.state = STATES.ACTIVE
        
    def move(self):
        self.position[0] += Enemy.velocity[0]
        self.rect.topleft = map(round, self.position)
       
        if not Enemy.should_flip:
            if self.rect.right > config.screen.get_width() or self.rect.left < 0:
            #If this enemy touches either end of the screen...
                Enemy.should_flip = True
            
    def on_collide(self, other):
        if isinstance(other, shipbullet.ShipBullet) and self.state == STATES.ACTIVE:
        #If we got hit by the player's bullet...
            pass
                
    def die(self):
        ingame.BLOCKS.add(block.Block([self.rect.centerx, 0], self.color))
        hurt.play()
        self.kill()
        
        self.position     = [-300.0, -300.0]
        self.velocity     = [0, 0]
        self.rect.topleft = self.position
        
        self.state = STATES.IDLE