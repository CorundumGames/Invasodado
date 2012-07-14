import enum
import pygame

import config
import random
import gameobject

FRAMES = [pygame.Rect(0, 16, 16, 16), pygame.Rect(16, 16, 16, 16)]
START_POS = pygame.Rect(32, 32, 0, 0)
STATES = enum.Enum('APPEARING', 'LOWERING', 'ACTIVE', 'DYING', 'IDLE')

'''
Algorithm for storing one colored Enemy per color (with all animations)
1. Create as many copies of the Enemy frames (that is, properly animated) as there are colors for the desired difficulty
2: Paint them their respective colors
3: Store them in a dict<pygame.Color, pygame.Surface>
4: When an enemy's color is assigned, simply have it draw its Surface from the dict
'''

class Enemy(gameobject.GameObject):
    should_flip = False
    velocity = [1, 0]
    acceleration = [0, 0]
    
    def __init__(self, position):
        gameobject.GameObject.__init__(self)
        self.rect = pygame.Rect(START_POS.x * (position[0]+1),
                                START_POS.y * (position[1]+1)*.75,
                                16,
                                16)
        self.color = pygame.Color(0, 0, 255)
        self.image = config.SPRITES.subsurface(FRAMES[0]).copy() #@UndefinedVariable
        self.state = STATES.ACTIVE
        
        self.image.set_colorkey(config.COLOR_KEY)
        pygame.PixelArray(self.image).replace((255, 255, 255), self.color)  #TODO: Draw a random element from a dictionary
        
    def update(self):
        Enemy.acceleration[0] += Enemy.velocity[0]
        Enemy.acceleration[1] += Enemy.velocity[1]
        self.rect.move_ip(Enemy.velocity[0], Enemy.velocity[1])
       
        if (self.rect.right > config.screen.get_width() or \
           self.rect.left < 0) and \
           self.state == STATES.ACTIVE:
            Enemy.should_flip = True