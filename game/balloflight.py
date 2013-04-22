from random import choice

import pygame
from pygame import Rect

from core            import color
from core            import config
from core            import settings
from game.gameobject import GameObject

### Constants ##################################################################
BALL_STATES  = ('IDLE', 'APPEARING', 'MOVING', 'DYING', 'RESET')
FRAMES       = tuple(Rect(32 * i, 96, 32, 32) for i in range(5))
TIME_TO_MOVE = 30  #In frames; remember, our target is 60FPS
################################################################################

### Globals ####################################################################
_ball_frames             = color.get_colored_objects(FRAMES)
_ball_frames_color_blind = color.get_colored_objects(FRAMES, True, True, True)
_balls                   = set()
################################################################################

### Functions ##################################################################
def clean_up():
    '''
    Removes all BallOfLights from memory.
    '''
    _balls.clear()

def get_ball(startpos, target, newcolor):
    '''
    Returns a spare BallOfLight, or creates one if there are none.

    @param startpos: The starting position of this BallOfLight
    @param newcolor: The color this BallOfLight will appear as
    @rtype: BallOfLight
    '''

    if not _balls:
    #If we don't have any spare BallsOfLight to give...
        _balls.add(BallOfLight())

    ball            = _balls.pop()  #Teehee
    ball.color      = newcolor
    ball.startpos   = tuple(startpos)

    ball._target[0] = target
    ball.change_state(BallOfLight.STATES.APPEARING)
    return ball

################################################################################

class BallOfLight(GameObject):
    STATES      = config.Enum(*BALL_STATES)
    BLOCK_GROUP = None
    block_mod   = None
    ENEMY_GROUP = None

    def __init__(self, startpos=(-300.0, -300.0), newcolor=choice(color.LIST)):
        GameObject.__init__(self)

        self._anim              = 0
        self.color              = newcolor
        self.current_frame_list = _ball_frames_color_blind if settings.SETTINGS['color_blind'] else _ball_frames
        self.image              = self.current_frame_list[id(newcolor)][0]
        size                    = self.image.get_size()
        self.rect               = Rect(startpos, size)
        self.position           = list(self.rect.topleft)
        self.progress           = 0
        self._target            = [None, 0]
        self.startpos           = startpos
        self.state              = BallOfLight.STATES.IDLE

        del self.acceleration, self.velocity

    def appear(self):
        self.image        = self.current_frame_list[id(self.color)][0]
        self.position     = list(self.startpos)
        self.progress     = -1
        self.rect.topleft = (self.startpos[0] + .5, self.startpos[1] + .5) 
        self.change_state(BallOfLight.STATES.MOVING)
        
        assert config.SCREEN_RECT.collidepoint(self._target), \
        "BallOfLight's target should be on-screen, but it's %s" % self._target

    def move(self):
        position = self.position
        startpos = self.startpos
        target   = self._target
        
        self.progress += 1
        percent        = self.progress / TIME_TO_MOVE

        if self._anim < len(FRAMES) - 1:
        #If we haven't finished animating...
            self._anim += 1
            self.image  = self.current_frame_list[id(self.color)][self._anim]

        if percent >= 1:
        #If we've reached our target location...
            self.change_state(BallOfLight.STATES.DYING)
        else:
            dx                = (percent * percent) * (3 - 2 * percent)
            dp                = 1 - dx
            position[0]       = (startpos[0] * dx) + (target[0] * self.image.get_width() * dp)
            position[1]       = (startpos[1] * dp) + (target[1] * dx)
            self.rect.topleft = (position[0] + .5, position[1] + .5)

        assert self.rect.colliderect(config.SCREEN_RECT), \
        "A BallOfLight at %s is trying to move off-screen!" % position

    def vanish(self):
        _balls.add(self)
        BallOfLight.BLOCK_GROUP.add(BallOfLight.block_mod.get_block([self._target[0] * 32, 8.0], self.color))
        self.kill()
        self._anim        = 0
        self.position     = [-300.0, -300.0]
        self.rect.topleft = (self.position[0] + .5, self.position[1] + .5)
        
        self.change_state(BallOfLight.STATES.IDLE)

    actions = {
                STATES.IDLE     : None    ,
                STATES.APPEARING: 'appear',
                STATES.MOVING   : 'move'  ,
                STATES.DYING    : 'vanish',
              }