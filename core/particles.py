import itertools
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
        r = self.rect
        p.position = [random.uniform(r.left, r.right), random.uniform(r.top , r.bottom)]
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
            self.pool.clean()

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

    def __init__(self, image, move_func, appear_func):
        '''
        @ivar move_func: The function that defines motion; called each update()
                         Takes one parameter
        '''
        gameobject.GameObject.__init__(self)
        self.appear_func = appear_func
        self.image       = image
        self.move_func   = move_func
        self.position    = list(self.__class__.START_POS)
        self.rect        = pygame.Rect(self.position, self.image.get_size())
        self.state       = self.__class__.STATES.IDLE

    def __del__(self):
        pass

    def appear(self):
        self.appear_func(self)
        self.state = Particle.STATES.ACTIVE

    def move(self):
        self.move_func(self)

        if not self.rect.colliderect(config.SCREEN_RECT):
            self.state = Particle.STATES.LEAVING

    def leave(self):
        self.kill()
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

    def __init__(self, image, move_func, appear_func):
        self.appear_func   = appear_func
        self.image         = image
        self.move_func     = move_func
        self.particles_in  = set()
        self.particles_out = set()

    def get_particle(self):
        if len(self.particles_in) == 0:
            self.particles_in.add(Particle(self.image, self.move_func, self.appear_func))

        p = self.particles_in.pop()
        self.particles_out.add(p)
        return p

    def clean(self):
        particles_to_remove = set()
        for i in itertools.ifilterfalse(config.SCREEN_RECT.colliderect, self.particles_out):
            particles_to_remove.add(i)

        self.particles_in.update(particles_to_remove)
        self.particles_out -= particles_to_remove