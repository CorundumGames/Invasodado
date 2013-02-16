from random import choice

import pygame

from core import color
from core import config
from core import settings
from game.gameobject import GameObject

FRAMES       = [pygame.Rect(32 * i, 96, 32, 32) for i in range(5)]
TIME_TO_MOVE = 30 #In frames; remember, our target is 60FPS

ball_frames = color.get_colored_objects(FRAMES)
ball_frames_color_blind = color.get_colored_objects(FRAMES,True,True)

balls = set()

def clean_up():
    '''
    Removes all BallOfLights from memory.
    '''
    balls.clear()

def get_ball(startpos, newcolor):
    '''
    Returns a spare BallOfLight, or creates one if there are none.

    @param startpos: The starting position of this BallOfLight
    @param newcolor: The color this BallOfLight will appear as
    @rtype: BallOfLight
    '''

    if not balls:
    #If we don't have any spare BallsOfLight to give...
        balls.add(BallOfLight())

    ball          = balls.pop()  #Teehee
    ball.color    = newcolor
    ball.startpos = tuple(startpos)
    ball.state    = BallOfLight.STATES.APPEARING
    return ball

class BallOfLight(GameObject):
    collisions  = None
    STATES      = config.Enum('IDLE', 'APPEARING', 'MOVING', 'DYING', 'RESET')
    BLOCK_GROUP = None
    block_mod   = None
    ENEMY_GROUP = None

    def __init__(self, startpos=(-300.0, -300.0), newcolor=choice(color.LIST)):
        GameObject.__init__(self)

        self._anim              = 0
        self.color              = newcolor
        self.current_frame_list = ball_frames_color_blind if settings.color_blind else ball_frames
        self.image              = self.current_frame_list[id(newcolor)][0]
        size                    = self.image.get_size()
        self.rect               = pygame.Rect(startpos, size)
        self.position           = list(startpos)
        self.progress           = 0.0
        self._target            = [round(startpos[0] / size[0]) * size[1], 8.0]
        self.startpos           = startpos
        self.state              = BallOfLight.STATES.IDLE

        del self.acceleration, self.velocity

    def appear(self):
        self.image        = self.current_frame_list[id(self.color)][0]
        self.position     = list(self.startpos)
        self.progress     = 0.0
        self.rect.topleft = self.startpos
        self.state        = BallOfLight.STATES.MOVING
        self._target[0]   = round(self.position[0]/self.image.get_width())*self.image.get_height()
        
        assert config.SCREEN_RECT.collidepoint(self._target), \
        "BallOfLight's target should be on-screen, instead it's %s" % self._target

    def move(self):
        position = self.position
        startpos = self.startpos
        target   = self._target

        self.progress += 1
        percent        = self.progress/TIME_TO_MOVE

        if self._anim < len(FRAMES) - 1:
        #If we haven't finished animating...
            self._anim += 1
            self.image = self.current_frame_list[id(self.color)][self._anim]

        dx                = (percent**2)*(3-2*percent)
        ddx               = 1 - dx
        position[0]       = (startpos[0] * dx ) + (target[0] * ddx)
        position[1]       = (startpos[1] * ddx) + (target[1] * dx )
        self.rect.topleft = (position[0] + .5, position[1] + .5)

        if position[1] == target[1]:  #Only y-coordinate check is needed
        #If we've reached our target location...
            self.state = BallOfLight.STATES.DYING

        assert self.rect.colliderect(config.SCREEN_RECT), \
        "A BallOfLight at %s is trying to move off-screen!" % position

    def vanish(self):
        balls.add(self)
        BallOfLight.BLOCK_GROUP.add(BallOfLight.block_mod.get_block([self.rect.centerx, 0], self.color))
        self.remove(BallOfLight.enemy_group)
        self._anim        = 0
        self.position     = [-300.0, -300.0]
        self.rect.topleft = self.position
        self.state        = BallOfLight.STATES.IDLE

    actions = {
                STATES.IDLE     : None    ,
                STATES.APPEARING: 'appear',
                STATES.MOVING   : 'move'  ,
                STATES.DYING    : 'vanish',
              }