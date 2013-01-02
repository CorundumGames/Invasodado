import config
import game.gameobject as gameobject

class ParticleEmitter(gameobject.GameObject):
    '''
    ParticleEmitters...emit particles.  They inherit from GameObject,
    and thus can have things like motion, etc. but ParticleEmitters
    are not to be visible in and of themselves.  If you want a ParticleEmitter
    to be visible, attach it to an object that is.
    '''
    
    def __init__(self, rect, move_func, limit):
        '''
        @ivar active: True if currently emitting particles
        @ivar limit: Maximum number of particles visible on-screen
        @ivar move_func: The movement function this object's particles use
        @ivar particles: The particles; reuse, don't remake
        @ivar rect: The area that will emit particles
        @ivar take_oldest: True if new particles remove old ones if limit is hit
                           False if new particles are not drawn if limit is hit
        '''
        self.active      = False
        self.limit       = limit
        self.move_func   = move_func
        self.particles   = set()
        self.rect        = rect
        self.take_oldest = False
        
    def __del__(self):
        pass
    
    def toggle(self, state = None):
        '''
        Toggles this ParticleEmitter.
        
        @param state: Toggle self.active if None, else set to True/False as given
        '''
        
        if state == None:
            self.active = not self.active
        else:
            self.active = bool(state)
            
###############################################################################
    
class Particle(gameobject.GameObject):
    '''
    Tiny bits and pieces used for graphical effects.  Meant for things like
    explosions, sparkles, impacts, etc.
    
    Not meant to be instantiated alone; should only be held by ParticleEmitters.
    '''
    
    STATES = config.Enum('IDLE', 'APPEARING', 'ACTIVE', 'LEAVING')
    
    def __init__(self, image, move_func):
        '''
        @ivar move_func: The function that defines motion; called each update()
                         Does not take parameters!
        
        '''
        
        self.move_func = move_func
    
    def __del__(self):
        pass
    
    actions = {
               STATES.IDLE     : None          ,
               STATES.APPEARING: NotImplemented,
               STATES.ACTIVE   : self.move_func,
               STATES.LEAVING  : NotImplemented,
               }