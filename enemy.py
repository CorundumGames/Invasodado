import enum
import pygame

import config
import random

FRAMES = [pygame.Rect(0, 16, 16, 16), pygame.Rect(16, 16, 16, 16)]
START_POS = pygame.Rect(32, 32, 0, 0)
STATES = enum.Enum('APPEARING', 'LOWERING', 'ACTIVE', 'DYING', 'IDLE')

'''
Algorithm for storing one colored Enemy per color (with all animations)
1. Create as many copies of the Enemy frames (that is, properly animated) as there are colors for the desired difficulty
2: Paint them their respective colors
3: Store them in a dict<pygame.Color, pygame.Surface>
4: When an enemy's color is assigned, simply have it draw its Surface from the dict

Must check GameDevExchange to see how Space Invaders formations are handled!
'''

class Enemy(pygame.sprite.Sprite):
    velocity = pygame.Rect(1, 0, 0, 0)
    
    def __init__(self, position):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(START_POS.x * (position[0]+1),
                                START_POS.y * (position[1]+1)*.75,
                                0,
                                0)
        self.color = pygame.Color(0, 0, 255)
        self.image = config.SPRITES.subsurface(FRAMES[0]).copy() #@UndefinedVariable
        self.state = STATES.APPEARING
        
        self.image.set_colorkey(config.COLOR_KEY)
        pygame.PixelArray(self.image).replace((255, 255, 255), self.color)  #TODO: Draw a random element from a dictionary
        
    def update(self):
        self.rect.move_ip(Enemy.velocity.x, Enemy.velocity.y)
        if self.rect.right > config.screen.get_width() or self.rect.left < 0:
            Enemy.velocity.x *= -1