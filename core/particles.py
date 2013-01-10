import random

import pygame.time

import config
import game.gameobject as gameobject

class ParticleEmitter:
    '''
    ParticleEmitters...emit particles.  They are not to act independently;
    ParticleEmitters are to emit particles only when called by whatever
    object holds them.
    
    ParticleEmitters should not be in Pygame Groups; the objects that hold them
    should call emit().
    '''
    
    def __init__(self, pool, rect, period, group):
        '''
        @ivar period: Frames between emits, e.g. 4 = 1 Particle per 4 frames
        @ivar pool: The ParticlePool where Particles are drawn from
        @ivar rate: Used to count to emits
        @ivar rect: The area that will emit Particles
        '''
        self.group     = group
        self.period    = period
        self.pool      = pool
        self.rate      = 0
        self.rect      = rect
        
    def __del__(self):
        pass
    
    def __release(self, p):
        '''
        Actually releases a particle
        
        @param p: The particle to release
        '''
        p.position = [
                      random.uniform(self.rect.left, self.rect.right ),
                      random.uniform(self.rect.top , self.rect.bottom)
                     ]
        p.rect.topleft = p.position
        p.state        = p.__class__.STATES.APPEARING
        p.add(self.group) 
            
    def emit(self):
        '''
        Takes one step to release  particle.
        '''

        self.rate += 1
        self.rate %= self.period
        
        if self.rate == 0:
            self.__release(self.pool.get_particle())
            
    def burst(self, amount):
        '''
        Releases a one-shot burst of particles.
        
        @param amount: No. of particles to release, max is self.pool.amount
        '''
        for i in xrange(amount):
            self.__release(self.pool.get_particle())
    
    actions    = None
    collisions = None
        
            
###############################################################################
    
class Particle(gameobject.GameObject):
    '''
    Tiny bits and pieces used for graphical effects.  Meant for things like
    explosions, sparkles, impacts, etc.
    
    Not meant to be instantiated alone; should only be held by ParticleEmitters.
    And Particle is meant to be a base class; you should make subclasses with
    their own images and move functions.
    
    Particles should have some randomization to them, particularly in initial direction.
    '''
    
    START_POS = [-100.0, -100.0]
    STATES    = config.Enum('IDLE', 'APPEARING', 'ACTIVE', 'LEAVING')
    image     = config.SPRITES.subsurface(4, 170, 8, 8)
    
    def __init__(self, pool):
        '''
        @ivar move_func: The function that defines motion; called each update()
                         Takes one parameter
        '''
        gameobject.GameObject.__init__(self)
        self.image     = self.__class__.image
        self.pool      = pool
        self.position  = list(self.__class__.START_POS)
        self.rect      = pygame.Rect(self.position, self.image.get_size())
        self.state     = self.__class__.STATES.IDLE
    
    def __del__(self):
        pass
    
    def appear(self):
        self.state = self.__class__.STATES.ACTIVE
        
    def move(self):
        self.move_func()
        
        if not self.rect.colliderect(config.SCREEN_RECT):
            self.state = self.__class__.STATES.LEAVING
            
    def move_func(self):
        self.velocity[0] += self.acceleration[0]
        self.velocity[1] += self.acceleration[1]
        self.position[0] += self.velocity[0]
        self.position[1] += self.velocity[1]
        self.rect.topleft = (self.position[0] + .5, self.position[1] + .5)
            
    def leave(self):
        self.kill()
        self.pool.particles_in.add(self)
        self.pool.particles_out.remove(self)
        self.acceleration = [0.0, 0.0]
        self.velocity     = [0.0, 0.0]
        self.position     = list(self.__class__.START_POS)
        self.rect.topleft = self.position
        self.state        = self.__class__.STATES.IDLE
        
    actions = {
               STATES.IDLE     : None    ,
               STATES.APPEARING: 'appear',
               STATES.ACTIVE   : 'move'  ,
               STATES.LEAVING  : 'leave' ,
               }
    
###############################################################################

class ParticlePool:
    '''
    A pool of particles that multiple emitters can draw from.
    Each pool may hold one type of particle.
    
    @ivar particles_in: Particles not visible on-screen
    @ivar particles_out: Particles visible on-screen
    '''
    
    def __init__(self, particle_type):
        '''
        @param particle_type: The type data of the Particle we want.
        '''
        self.particle_type = particle_type
        self.particles_in  = set()
        self.particles_out = set()
        
    def get_particle(self):
        if len(self.particles_in) == 0:
            self.particles_in.add(self.particle_type(self))
            
        p = self.particles_in.pop()
        self.particles_out.add(p)
        return p