from functools import partial
from itertools import filterfalse
from random    import uniform

import pygame.time

from core            import config
from game.gameobject import GameObject

### Constants ##################################################################
PARTICLE_STATES = ('IDLE', 'APPEARING', 'ACTIVE', 'LEAVING')
################################################################################

class Particle(GameObject):
    '''
    Tiny bits and pieces used for graphical effects.  Meant for things like
    explosions, sparkles, impacts, etc.

    Not meant to be instantiated alone; should only be held by ParticleEmitters.

    Particles should have some randomization, particularly in initial direction.
    '''
    START_POS = (-100.0, -100.0)
    STATES    = config.Enum(*PARTICLE_STATES)
    GROUP     = None

    def __init__(self, image, move_func, appear_func):
        '''
        @ivar move_func: The function that defines motion; called each update()
                         Takes one parameter
        '''
        super().__init__()
        self.appear_func = partial(appear_func, self)
        self.image       = image
        self.move_func   = partial(move_func, self)
        self.position    = list(Particle.START_POS)
        self.rect        = pygame.Rect(self.position, self.image.get_size())
        self.state       = Particle.STATES.IDLE

    def appear(self):
        self.appear_func()
        self.change_state(Particle.STATES.ACTIVE)

    def move(self):
        self.move_func()

        if not self.rect.colliderect(config.SCREEN_RECT):
        #If we're no longer on-screen...
            self.change_state(Particle.STATES.LEAVING)

    def leave(self):
        self.kill()
        self.acceleration = [0.0, 0.0]
        self.velocity     = [0.0, 0.0]
        self.position     = list(Particle.START_POS)
        self.rect.topleft = self.position
        self.change_state(Particle.STATES.IDLE)

    actions = {
               STATES.IDLE     : None    ,
               STATES.APPEARING: 'appear',
               STATES.ACTIVE   : 'move'  ,
               STATES.LEAVING  : 'leave' ,
              }
    
################################################################################

class ParticleEmitter:
    '''
    ParticleEmitters...emit particles.  They are not to act independently;
    ParticleEmitters are to emit particles only when called by whatever
    object holds them.

    ParticleEmitters should not be in Pygame Groups; the objects that hold them
    should call emit().
    '''

    def __init__(self, pool, rect, period, group=Particle.GROUP):
        '''
        @ivar period: Frames between emits, e.g. 4 = 1 Particle per 4 frames
        @ivar pool: The ParticlePool where Particles are drawn from
        @ivar rate: Used to count to emits
        @ivar rect: The area that will emit Particles
        '''
        self.group  = group
        self.period = period
        self.pool   = pool
        self.rate   = 0
        self.rect   = rect

    def _release(self, particle):
        '''
        Actually releases a particle

        @param particle: The particle to release
        '''
        rect                  = self.rect
        particle.position     = [
                                 uniform(rect.left, rect.right),
                                 uniform(rect.top , rect.bottom)
                                ]
        particle.rect.topleft = particle.position
        particle.change_state(Particle.STATES.APPEARING)
        particle.add(self.group)

    def emit(self):
        '''
        Takes one step to release a particle.
        '''

        self.rate += 1
        self.rate %= self.period

        if not self.rate:
        #If we've gone a particle release cycle...
            self._release(self.pool.get_particle())
            self.pool.clean()

    def burst(self, amount):
        '''
        Releases a one-shot burst of particles.

        @param amount: No. of particles to release, max is self.pool.amount
        '''
        pool     = self.pool
        _release = self._release
        for i in range(amount):
            _release(pool.get_particle())

    actions    = None
    collisions = None

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
        '''
        Returns a spare Particle, or creates a new one if none exist.
        '''
        if not self.particles_in:
        #If we don't have any particles to spare...
            self.particles_in.add(Particle(self.image, self.move_func, self.appear_func))

        particle = self.particles_in.pop()
        self.particles_out.add(particle)
        return particle

    def clean(self):
        '''
        Removes all particles that are off-screen from the game, but not from
        memory.
        '''
        particles_to_remove = set()
        for i in filterfalse(config.SCREEN_RECT.colliderect, self.particles_out):
            particles_to_remove.add(i)

        self.particles_in.update(particles_to_remove)
        self.particles_out -= particles_to_remove