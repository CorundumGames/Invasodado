from itertools import chain
from math      import sin, cos, tan, pi
from random    import gauss, uniform

import pygame.key

from core            import color
from core            import config
from core.particles  import ParticleEmitter, ParticlePool, Particle
from game            import gamedata
from game.gameobject import GameObject
from game.shipbullet import ShipBullet
from game.combocounter import get_combo_counter



### Functions ##################################################################
def _burst_appear(self):
    self.acceleration[1] = GRAVITY
    self.velocity        = [gauss(0, 25), uniform(-10, -20)]
    
def _radius_appear(self):
    self.progress = 0
    distance_magnitude = gauss(300, 50)
    angle              = uniform(0, -pi)
    self.position[0]   = START_POS.centerx + distance_magnitude * cos(angle)
    self.position[1]   = START_POS.centery + distance_magnitude * sin(angle)
    self.startpos      = tuple(self.position)
    self.rect.topleft  = (self.position[0] + .5, self.position[1] + .5)
    
def _radius_move(self):
    self.progress += 1
    position = self.position
    percent  = self.progress / 30
    
    if percent == 1:
        #If we've reached our target location...
        self.change_state(Particle.STATES.LEAVING)
    else:
        dx                = (percent**2) * (3-2*percent)
        ddx               = 1 - dx
        position[0]       = (self.startpos[0] * ddx) + (START_POS.centerx * dx)
        position[1]       = (self.startpos[1] * ddx) + (START_POS.centery * dx)
        self.rect.topleft = (position[0] + .5, position[1] + .5)
    
    
################################################################################

### Constants ##################################################################
APPEAR      = config.load_sound('appear.wav')
APPEAR_POOL = ParticlePool(config.get_sprite(pygame.Rect(4, 170, 4, 4)), _radius_move, _radius_appear)
DEATH       = config.load_sound('death.wav')
GRAVITY     = 0.5
DEATH_POOL  = ParticlePool(config.get_sprite(pygame.Rect(4, 170, 4, 4)), appear_func=_burst_appear)
SHIP_STATES = ('IDLE', 'SPAWNING', 'ACTIVE', 'DYING', 'DEAD', 'RESPAWN')
SPEED       = 4
START_POS   = pygame.Rect(config.SCREEN_WIDTH/2, config.SCREEN_HEIGHT*.8, 32, 32)
################################################################################

class FlameTrail(GameObject):
    '''
    FlameTrail is the jet left by the Ship's engines.  This is purely a
    graphical effect.
    '''
    FRAMES = tuple(config.get_sprite(pygame.Rect(32*i, 0, 32, 32)) for i in range(6))
    GROUP  = None

    def __init__(self):
        super().__init__()
        self.anim  = 0.0
        self.image = FlameTrail.FRAMES[0]
        self.rect  = pygame.Rect([0, 0], self.image.get_size())
        self.state = 1
        del self.acceleration, self.velocity
        for i in self.__class__.FRAMES: i.set_colorkey(color.COLOR_KEY, config.FLAGS)

    def animate(self):
        self.anim += 1/3
        self.image = FlameTrail.FRAMES[int(3 * sin(self.anim / 2)) + 3]

    actions = {1 : 'animate'}
    
################################################################################

class LightColumn(GameObject):
    '''
    This class exists to let the player know where exactly he's aiming.
    '''
    def __init__(self):
        super().__init__()
        self.state = 1
        self.rect  = pygame.Rect(0, 0, 32, config.SCREEN_HEIGHT - 32 * 3)
        self.position = self.rect.topleft
        self.image = pygame.Surface(self.rect.size, config.FLAGS)
        self.image.fill(color.WHITE)
        self.image.set_alpha(128)
        del self.acceleration, self.velocity
        
    actions = {1 : None}
        
################################################################################

class Ship(GameObject):
    '''
    The Ship is the player character.  There's only going to be one instance of
    it, but it has to inherit from pygame.sprite.Sprite, so we can't make it a
    true Python singleton (i.e. a module).
    '''
    FRAMES = tuple(config.get_sprite(pygame.Rect(32 * i, 128, 32, 32)) for i in range(5))
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

        self.anim         = 0.0
        self.flames       = FlameTrail()
        self.image        = Ship.FRAMES[0]
        self.invincible   = 0
        self.light_column = LightColumn()
        self.my_bullet    = ShipBullet()
        self.position     = list(START_POS.topleft)
        self.rect         = START_POS.copy()
        self.respawn_time = 3 * 60
        self.emitter      = ParticleEmitter(DEATH_POOL, self.rect, 2)
        self.appear_emitter = ParticleEmitter(APPEAR_POOL, self.rect, 2)
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
        self.appear_emitter.burst(200)
        APPEAR.stop()
        APPEAR.play()
        for i in chain(Ship.FRAMES, FlameTrail.FRAMES, {self.light_column.image}): i.set_alpha(128)
        self.respawn_time = 3 * 60
        self.invincible = 250
        self.position   = list(START_POS.topleft)
        self.rect       = START_POS.copy()
        self.change_state(Ship.STATES.ACTIVE)

    def move(self):
        #Shorthand for which keys have been pressed
        keys = pygame.key.get_pressed()
        rect = self.rect
        width = self.image.get_width()

        if self.state not in {Ship.STATES.DYING, Ship.STATES.DEAD, Ship.STATES.IDLE}:
            if keys[pygame.K_LEFT] and rect.left > 0:
            #If we're pressing left and not at the left edge of the screen...
                self.position[0] -= SPEED
            elif keys[pygame.K_RIGHT] and rect.right < config.SCREEN_RECT.right:
            #If we're pressing right and not at the right edge of the screen...
                self.position[0] += SPEED

        rect.left = self.position[0] + 0.5
        self.flames.rect.midtop = (rect.midbottom[0], rect.midbottom[1] - 1)
        #Compensate for the gap in the flames                           ^^^
        self.light_column.rect.left = round(rect.left / width) * width

        if self.invincible:
        #If we're invincible...
            self.invincible -= 1
        elif self.image.get_alpha() == 128:
            for i in chain(Ship.FRAMES, FlameTrail.FRAMES): i.set_alpha(255)
            
        if self.anim != 4:
            self.anim  = self.anim + (0 < self.anim < len(Ship.FRAMES) - 1) / 3
        else:
            self.anim = 0.0
        self.image = Ship.FRAMES[int(self.anim)]
        
        if gamedata.combo_time == gamedata.MAX_COMBO_TIME and gamedata.combo > 1:
            counter = get_combo_counter(gamedata.combo, self.rect.topleft)
            counter.rect.midbottom = self.rect.midtop
            counter.position = list(counter.rect.topleft)
            counter.change_state(counter.__class__.STATES.APPEARING)
            Ship.GROUP.add(counter)
            

    def die(self):
        for i in chain(Ship.FRAMES, FlameTrail.FRAMES, (self.light_column.image,)): i.set_alpha(0)
        self.emitter.rect = self.rect
        DEATH.play()
        self.emitter.burst(100)
        self.change_state(Ship.STATES.DEAD)
            
    def wait_to_respawn(self):
        self.respawn_time -= 1
        if not self.respawn_time:
        #If we're done waiting to respawn...
            self.change_state(Ship.STATES.RESPAWN)
            

    actions = {
               STATES.IDLE      : None          ,
               STATES.SPAWNING  : 'respawn'     ,
               STATES.ACTIVE    : 'move'        ,
               STATES.DYING     : 'die'         ,
               STATES.DEAD      : 'wait_to_respawn',
               STATES.RESPAWN   : 'respawn'     ,
              }