from itertools import chain
from math      import sin

import pygame.key

from core            import color
from core            import config
from game.gameobject import GameObject
from game.shipbullet import ShipBullet

'''
The Ship is the player character.  There's only going to be one instance of it,
but it has to inherit from pygame.sprite.Sprite, so we can't make it a true
Python singleton.
'''

### Constants ##################################################################
SHIP_STATES = ('IDLE', 'SPAWNING', 'ACTIVE', 'DYING', 'DEAD', 'RESPAWN')
SPEED       = 4
START_POS   = pygame.Rect(config.SCREEN_WIDTH/2, config.SCREEN_HEIGHT*.8, 32, 32)
################################################################################

class FlameTrail(GameObject):
    FRAMES = [config.SPRITES.subsurface(pygame.Rect(32*i, 0, 32, 32)) for i in range(6)]
    GROUP  = None

    def __init__(self):
        super().__init__()
        self.anim  = 0.0
        self.image = FlameTrail.FRAMES[0]
        self.rect  = pygame.Rect([0, 0], self.image.get_size())
        self.state = 1

        for i in self.__class__.FRAMES: i.set_colorkey(color.COLOR_KEY, config.FLAGS)

    def animate(self):
        self.anim += 1/3.0
        self.image = FlameTrail.FRAMES[int(3 * sin(self.anim / 2)) + 3]

    actions = {1 : 'animate'}

class Ship(GameObject):
    FRAMES = [config.SPRITES.subsurface(pygame.Rect(32 * i, 128, 32, 32)) for i in range(5)]
    STATES = config.Enum(*SHIP_STATES)
    GROUP  = None

    def __init__(self):
        '''
        @ivar anim: A counter for ship animation
        @ivar image: The graphic
        @ivar invincible: How many frames of invincibility the player has if any
        @ivar my_bullet: The single bullet this ship may fire
        '''
        super().__init__()

        self.anim       = 0.0
        self.flames     = FlameTrail()
        self.image      = Ship.FRAMES[0]
        self.invincible = 0
        self.my_bullet  = ShipBullet()
        self.position   = list(START_POS.topleft)
        self.rect       = START_POS.copy()
        self.change_state(Ship.STATES.RESPAWN)

        for i in Ship.FRAMES: i.set_colorkey(color.COLOR_KEY, config.FLAGS)

    def on_fire_bullet(self):
        bul = self.my_bullet
        if bul.state == ShipBullet.STATES.IDLE and self.state == Ship.STATES.ACTIVE:
        #If our bullet is not already on-screen...
            bul.add(Ship.GROUP)
            self.anim       = 1
            self.image      = Ship.FRAMES[self.anim]
            bul.rect.center = self.rect.center
            bul.position    = list(self.rect.topleft)
            bul.change_state(ShipBullet.STATES.FIRED)

    def respawn(self):
        for i in chain(Ship.FRAMES, FlameTrail.FRAMES): i.set_alpha(128)
        self.invincible = 250
        self.position   = list(START_POS.topleft)
        self.rect       = START_POS.copy()
        self.change_state(Ship.STATES.ACTIVE)

    def move(self):
        #Shorthand for which keys have been pressed
        keys = pygame.key.get_pressed()
        rect = self.rect

        if self.state not in (Ship.STATES.DYING, Ship.STATES.DEAD, Ship.STATES.IDLE):
            if keys[pygame.K_LEFT] and rect.left > 0:
            #If we're pressing left and not at the left edge of the screen...
                self.position[0] -= SPEED
            elif keys[pygame.K_RIGHT] and rect.right < config.SCREEN_RECT.right:
            #If we're pressing right and not at the right edge of the screen...
                self.position[0] += SPEED

        rect.left = self.position[0] + 0.5
        self.flames.rect.midtop = (rect.midbottom[0], rect.midbottom[1] - 1)
        #Compensate for the gap in the flames                           ^^^

        if self.invincible:
        #If we're invincible...
            self.invincible -= 1
        elif self.image.get_alpha() == 128:
            for i in chain(Ship.FRAMES, FlameTrail.FRAMES): i.set_alpha(255)
            
        if self.anim != 4:
            self.anim  = self.anim + 1.0/3 * (0 < self.anim < len(Ship.FRAMES) - 1)
        else:
            self.anim = 0.0
        self.image = Ship.FRAMES[int(self.anim)]

    def die(self):
        self.change_state(Ship.STATES.RESPAWN)

    actions = {
               STATES.IDLE      : None          ,
               STATES.SPAWNING  : 'respawn'     ,
               STATES.ACTIVE    : 'move'        ,
               STATES.DYING     : 'die'         ,
               STATES.DEAD      : NotImplemented,
               STATES.RESPAWN   : 'respawn'     ,
              }