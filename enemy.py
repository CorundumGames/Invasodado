import random

import pygame

import color
import config
import gameobject
import gsm
import ingame
import shipbullet

FRAMES    = [pygame.Rect(0, 16, 16, 16), pygame.Rect(16, 16, 16, 16)]
START_POS = (32.0, 32.0)
STATES    = config.Enum('IDLE', 'APPEARING', 'LOWERING', 'ACTIVE', 'DYING')
SAFE_SPOT = (0, config.screen.get_height()*3)

'''
Algorithm for storing one colored Enemy per color (with all animations)
1. Create as many copies of the Enemy frames (that is, properly animated) as there are colors for the desired difficulty
2: Paint them their respective colors
3: Store them in a dict({pygame.Color : pygame.Surface})
4: When an enemy's color is assigned, simply have it draw its Surface from the dict
'''

hurt = pygame.mixer.Sound("./enemyhurt.wav")

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
        self.image         = config.SPRITES.subsurface(FRAMES[0]).copy() #@UndefinedVariable
        self.position      = list(START_POS)
        self.rect          = pygame.Rect(START_POS, (16, 16))
        self.state         = STATES.IDLE
        
        self.image.set_colorkey(color.COLOR_KEY)
        
        
    def appear(self):
        self.add(ingame.ENEMIES)
        self.position     = [START_POS[0] * (self.form_position[0]+1),
                             START_POS[1] * (self.form_position[1]+1)*.75]
        self.rect.topleft = self.position
        self.color        = random.choice(color.Colors.LIST)
        self.image        = color.blend_color(self.image, self.color)  #Quick fix; store all colors later
        self.image.set_colorkey(self.image.get_at((0, 0)))
        
        self.state = STATES.ACTIVE
        
    def move(self):
        self.position[0] += Enemy.velocity[0]
        self.position[1] += Enemy.velocity[1]
        self.rect.topleft = map(round, self.position)
       
        if self.rect.right > config.screen.get_width() or self.rect.left < 0:
        #If this enemy touches either end of the screen...
            Enemy.should_flip = True
            
    def on_collide(self, other):
        if isinstance(other, shipbullet.ShipBullet) and self.state == STATES.ACTIVE:
        #If we got hit by the player's bullet...
            pass
                
    def die(self):
        self.kill()
        self.position     = [-300.0, -300.0]
        self.velocity     = [0, 0]
        self.rect.topleft = self.position
        
        self.state = STATES.IDLE