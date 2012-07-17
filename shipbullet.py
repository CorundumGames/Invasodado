import enum
import pygame

import config
import gsm
import player
import gameobject


'''This is the bullet the ship has available.  It is not meant to be created
and deleted over and over, but to be reused by the ship (so we don't take as
much time creating and destroying bullets.'''

STATES       = enum.Enum('IDLE', 'FIRED', 'MOVING', 'COLLIDE', 'RESET')
FRAME        = pygame.Rect(23, 5, 5, 5)
START_POS    = pygame.Rect(0, config.screen.get_height()*2, 5, 5)
SPEED        = 8


class ShipBullet(gameobject.GameObject):
    def __init__(self):
        gameobject.GameObject.__init__(self)

        self.image = config.SPRITES.subsurface(FRAME) #@UndefinedVariable
        self.state = STATES.IDLE
        self.rect = START_POS.copy()
        
        self.actions = {
                        STATES.IDLE   : None             ,
                        STATES.FIRED  : self.start_moving,
                        STATES.MOVING : self.move        ,
                        STATES.COLLIDE: None             ,
                        STATES.RESET  : self.reset       ,
                        }
        
        self.velocity = [0, -SPEED]
        
    def update(self):
        '''Tells the bullet what to do this frame.'''
        try:
            self.actions[self.state]()
        except TypeError:
            pass
            
    def start_moving(self):
        '''Plays a sound and begins moving.'''
        #Play a sound here later
        self.state = STATES.MOVING
        self.velocity[1] = -SPEED
        
    def move(self):
        '''Moves up the screen, seeing if it's hit an enemy or exited.'''
        self.velocity[1] += self.acceleration[1]
        self.rect.move_ip(self.velocity[0], self.velocity[1])
        
        if self.rect.bottom < 0:
            self.state = STATES.RESET
        
    def reset(self):
        '''Resets the bullet back to its initial position.'''
        self.velocity[1] = 0
        self.kill()
        self.rect = START_POS.copy()
        self.state = STATES.IDLE  