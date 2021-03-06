from math   import copysign, pi, sin
from random import choice, uniform

from pygame import Rect

from core            import color
from core            import config
from core            import settings
from core.particles  import ParticleEmitter
from game            import balloflight
from game.gameobject import GameObject

### Constants ##################################################################
ENEMY_STATES    = ('IDLE', 'APPEARING', 'LOWERING', 'ACTIVE', 'DYING', 'CHEERING')
FRAMES          = tuple(Rect(32 * i, 32, 32, 32) for i in range(4))
LOWER_INCREMENT = 16
START_POS       = (32.0, 32.0)

ENEMY_FRAMES             = color.get_colored_objects(FRAMES, True, False, True)
ENEMY_FRAMES_COLOR_BLIND = color.get_colored_objects(FRAMES, True, True , True)
del FRAMES
################################################################################

### Globals ####################################################################
_hurt = config.load_sound('enemyhit.wav')
################################################################################

class Enemy(GameObject):
    STATES       = config.Enum(*ENEMY_STATES)
    anim         = 0.0
    base_speed   = 0.5
    GROUP        = None
    shoot_odds   = 0.002
    should_flip  = False
    start_time   = None
    velocity     = [0.5, 0.0]

    def __init__(self, form_position):
        super().__init__()
        ### Local variables ####################################################
        the_color = choice(color.LIST)
        the_id    = id(the_color)
        ########################################################################
        
        ### Object Attributes ##################################################
        self.amount_lowered     = 0
        self._anim              = 0.0
        self.color              = the_color
        self.column             = None
        self._form_position     = form_position
        self.current_frame_list = ENEMY_FRAMES_COLOR_BLIND if settings.SETTINGS['color_blind'] else ENEMY_FRAMES
        self.image              = self.current_frame_list[the_id][0]
        self.position           = list(START_POS)
        self.rect               = Rect(START_POS, self.image.get_size())
        self.state              = Enemy.STATES.IDLE
        self.emitter            = ParticleEmitter(color.color_particles[the_id], self.rect, 1)
        ########################################################################
        
        ### Preparation ########################################################
        del self.acceleration, self.velocity
        ########################################################################

    def appear(self):
        self.add(Enemy.GROUP)
        self.position     = [
                             START_POS[0] * (self._form_position[0] + 1) * 1.5,
                             START_POS[1] * (self._form_position[1] + 1) * 1.5,
                            ]
        self.rect.topleft = (self.position[0] + .5, self.position[1] + .5)
        self.color        = choice(color.LIST)
        self.__animate()
        self.emitter.pool = color.color_particles[id(self.color)]
        self.change_state(Enemy.STATES.ACTIVE)

    def move(self):
        self.__animate()
        self.position[0] += Enemy.velocity[0]
        self.rect.topleft = (self.position[0] + .5, self.position[1] + .5)
        
        if uniform(0, 1) < Enemy.shoot_odds and not enemybullet.EnemyBullet.halt:
        #With Enemy.shoot_odds% of firing...
        #TODO: Use another probability distribution
            b             = enemybullet.get_enemy_bullet()
            b.rect.midtop = self.rect.midbottom
            b.position    = list(b.rect.topleft)
            b.add(enemybullet.EnemyBullet.GROUP)

        if not Enemy.should_flip:
        #If the squadron of enemies is not marked to reverse direction...
            if self.rect.left < 0 or self.rect.right > config.SCREEN_WIDTH:
            #If this enemy touches either end of the screen...
                Enemy.should_flip = True

    def die(self):
        balloflight.get_ball(self.rect.topleft, self.column, self.color).add(Enemy.GROUP)
        _hurt.play()
        self.emitter.burst(20)
        self.kill()
        
        self.position      = [-300.0, -300.0]
        self.rect.topleft  = self.position
        self.change_state(Enemy.STATES.IDLE)
        Enemy.velocity[0] += copysign(0.1, Enemy.velocity[0])
        #^ Increase the enemy squadron's speed (copysign() considers direction)

    def lower(self):
        self.__animate()
        self.amount_lowered += 1
        self.position[1]    += 1
        self.rect.top        = self.position[1]
        if self.amount_lowered == LOWER_INCREMENT:
            self.amount_lowered = 0
            self.change_state(Enemy.STATES.ACTIVE)

    def cheer(self):
        self.__animate()
        self.position[1] -= 2 * sin((Enemy.anim/2) - (pi/4) * self._form_position[0])
        self.rect.top = self.position[1] + .5
    
    def __animate(self):
        self._anim = int(3 - abs(Enemy.anim - 3)) % 4
        self.image = self.current_frame_list[id(self.color)][self._anim]

    actions = {
                STATES.APPEARING: 'appear',
                STATES.LOWERING : 'lower' ,
                STATES.ACTIVE   : 'move'  ,
                STATES.DYING    : 'die'   ,
                STATES.IDLE     : None    ,
                STATES.CHEERING : 'cheer' ,
              }

from game import enemybullet
