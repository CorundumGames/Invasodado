import random

import pygame

import config
import gameobject
import gsm
import ingame
import shipbullet

FRAMES = [pygame.Rect(0, 16, 16, 16), pygame.Rect(16, 16, 16, 16)]
START_POS = pygame.Rect(32, 32, 16, 16)
STATES = config.Enum('IDLE', 'APPEARING', 'LOWERING', 'ACTIVE', 'DYING')
SAFE_SPOT = pygame.Rect(0, config.screen.get_height()*3, 16, 16)

'''
Algorithm for storing one colored Enemy per color (with all animations)
1. Create as many copies of the Enemy frames (that is, properly animated) as there are colors for the desired difficulty
2: Paint them their respective colors
3: Store them in a dict({pygame.Color : pygame.Surface})
4: When an enemy's color is assigned, simply have it draw its Surface from the dict
'''

class Enemy(gameobject.GameObject): 
    acceleration = [0, 0]
    count        = 0
    should_flip  = False
    velocity     = [1, 0]
    
    def __init__(self, position):
        gameobject.GameObject.__init__(self)
        
        self.actions = {
                        STATES.APPEARING: self.appear   ,
                        STATES.LOWERING : NotImplemented,
                        STATES.ACTIVE   : self.move     ,
                        STATES.DYING    : self.die      ,
                        STATES.IDLE     : self.move
                        }
        
        self.color         = pygame.Color(0, 0, 255)
        self.form_position = position
        self.image         = config.SPRITES.subsurface(FRAMES[0]).copy() #@UndefinedVariable
        self.rect          = pygame.Rect(START_POS.x * (self.form_position[0]+1),
                                START_POS.y * (self.form_position[1]+1)*.75,
                                16,
                                16)
        self.state         = STATES.IDLE
        
        self.image.set_colorkey(config.COLOR_KEY)
        pygame.PixelArray(self.image).replace((255, 255, 255), self.color)  #TODO: Draw a random element from a dictionary
        
    def appear(self):
        self.rect.topleft = (START_POS.x * (self.form_position[0]+1),
                             START_POS.y * (self.form_position[1]+1)*.75)
        self.add(ingame.ENEMIES)
        self.state = STATES.ACTIVE
        
    def move(self):
        Enemy.acceleration[0] += Enemy.velocity[0]
        Enemy.acceleration[1] += Enemy.velocity[1]
        self.rect.move_ip(Enemy.velocity[0], Enemy.velocity[1])
       
        if self.rect.right > config.screen.get_width() or self.rect.left < 0:
            Enemy.should_flip = True
            
    def on_collide(self, other):
        pass
                
    def die(self):
        self.kill()
        self.state = STATES.IDLE