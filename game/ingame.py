from collections import namedtuple
from functools   import partial
from itertools import chain
from math        import log1p
from random      import choice

import pygame.mixer
from pygame.constants import *
from pygame.sprite import Group, OrderedUpdates

from core             import collisions
from core.collisions  import CollisionGrid
from core             import color
from core             import config
from core.gamestate   import GameState
from core.particles   import Particle, ParticleEmitter
from core import settings
from game             import balloflight
from game.balloflight import BallOfLight
from game             import bg
from game             import block
from game.block       import Block
from game             import blockgrid
from game.combocounter import ComboCounter
from game.enemy       import Enemy
from game             import enemybullet
from game.enemybullet import EnemyBullet
from game             import enemysquadron
from game             import gamedata
from game.highscore   import HighScoreState
from game.hudobject   import HudObject, make_text
from game.player      import Ship, FlameTrail, LightColumn
from game.shipbullet  import ShipBullet
from game.ufo         import UFO

#if config.DEBUG: import core.vartracker

### Groups #####################################################################
BG            = OrderedUpdates()
BLOCKS        = Group()
ENEMIES       = Group()
ENEMY_BULLETS = Group()
HUD           = Group()
PARTICLES     = Group()
PLAYER        = Group()
UFO_GROUP     = Group()
################################################################################

### Constants ##################################################################
rect = config.SCREEN_RECT
ALARM          = config.load_sound('alarm.wav')
DEBUG_KEYS     = (K_u, K_c, K_f, K_F1, K_e, K_k, K_i)
FADE_TIME      = 2500  #In milliseconds
FIRE_LOCATION  = (rect.centerx - 192, rect.centery     )
GAME_OVER_LOC  = (rect.centerx - 64 , rect.centery - 64)
HUD_TEXT       = namedtuple('Hud', 'score lives time game_over press_fire wave pause')
LIVES_LOCATION = (rect.width - 160, 16)
MODULE_CLEANUP = (balloflight, blockgrid, block, enemybullet, enemysquadron, gamedata)
MOUSE_ACTIONS  = {1:color.RED, 2:color.YELLOW, 3:color.BLUE}
MUSIC_PATHS    = {-1:'music.ogg', 120:'2.ogg', 300:'5.ogg'}
NULL_FUNC      = lambda: None
GAME_TEXT      = None
GAME_OVER_PATH = 'gameover.ogg'
SCORE_LOCATION = (16, 16)
TIME_FORMAT    = "{}:{:0>2}"
TIME_LOCATION  = (rect.centerx, 32)
TYPES_IGNORED  = (Block, BallOfLight, ComboCounter, FlameTrail, LightColumn, HudObject, Particle, ParticleEmitter)
TYPE_PAIRS_IGNORED = (
                      (Enemy, EnemyBullet),
                      (EnemyBullet, Enemy),
                      (Ship, ShipBullet),
                      (ShipBullet, Ship),
                      (Ship, UFO),
                      (UFO, Ship),
                      (EnemyBullet, EnemyBullet),
                      (Enemy, Enemy),
                      (ShipBullet, EnemyBullet),
                      (EnemyBullet, ShipBullet),
                      )
WAVE_LOCATION = (rect.centerx - 48, rect.height - 32)
del rect
################################################################################

### Functions ##################################################################
def null_if_debug(function):
    '''
    Returns function if we're in debug mode, returns the empty function (which
    does nothing) if we're not.
    '''
    return function if config.DEBUG else NULL_FUNC
################################################################################

### Preparation ################################################################
collisions.dont_check_type(*TYPES_IGNORED     )
collisions.dont_check_pair(*TYPE_PAIRS_IGNORED)

if not config.DEBUG:
    del MOUSE_ACTIONS

BallOfLight.BLOCK_GROUP   = BLOCKS
BallOfLight.enemy_group   = ENEMIES
BallOfLight.block_mod     = block
Block.GROUP               = BLOCKS
Particle.group            = PARTICLES
blockgrid.BLOCK_TYPE      = Block
Block.particle_group      = PARTICLES
enemysquadron.ENEMY_GROUP = ENEMIES
Enemy.GROUP               = ENEMIES
EnemyBullet.GROUP         = ENEMY_BULLETS
Ship.GROUP                = PLAYER
ShipBullet.GROUP          = PLAYER
UFO.GROUP                 = UFO_GROUP
UFO.BLOCK_GROUP           = BLOCKS
################################################################################

class InGameState(GameState):
    def __init__(self, *args, **kwargs):
        '''
        @ivar _collision_grid: Objects that collide with others
        @ivar _game_running: True if we haven't gotten a Game Over
        @ivar group_list: list of pygame.Groups, rendered in ascending order
        @ivar hud_text: dict of HUD items that give info to the player
        @ivar key_actions: dict of functions to call when a given key is pressed
        @ivar _mouse_actions: dict of Blocks to drop on mouse click, only if config.DEBUG
        @ivar _ship: The player character
        @ivar _time: Time limit for the game in seconds (no limit if 0)
        @ivar _ufo: The UFO_GROUP object that, when shot, can destroy many blocks
        '''
        from game.mainmenu import MainMenu
        ### Local Variables ####################################################
        global GAME_TEXT
        GAME_TEXT = config.load_text('ingame', settings.get_language_code())
        rect      = config.SCREEN_RECT
        ########################################################################
        
        ### Object Attributes ##################################################
        self._game_running   = True
        self.group_list      = [bg.STARS_GROUP, BG, BLOCKS, UFO_GROUP, ENEMIES, ENEMY_BULLETS, PLAYER, PARTICLES, HUD]
        self._collision_grid = CollisionGrid(4, 4, 1, self.group_list)
        self.hud_text        = HUD_TEXT(
                                        make_text(''          , SCORE_LOCATION),
                                        make_text(''          , LIVES_LOCATION),
                                        make_text(''          , TIME_LOCATION ).center(),
                                        make_text(GAME_TEXT[2], GAME_OVER_LOC ).center(),
                                        make_text(GAME_TEXT[3], FIRE_LOCATION ).center(),
                                        make_text(GAME_TEXT[4], WAVE_LOCATION ).center(),
                                        make_text(GAME_TEXT[5], GAME_OVER_LOC ).center(),
                                       )
        self._ship          = Ship()
        self.key_actions    = {
                               K_ESCAPE: partial(self.change_state, MainMenu)               ,
                               K_F1    : config.toggle_fullscreen                           ,
                               K_SPACE : self._ship.on_fire_bullet                          ,
                               K_c     : null_if_debug(blockgrid.clean_up)                  ,
                               K_e     : null_if_debug(partial(self._ship.instadie, None))  ,
                               K_f     : null_if_debug(config.toggle_frame_limit)           ,
                               K_i     : null_if_debug(self.__ship_life)                    ,
                               K_k     : partial(self._ship.change_state, Ship.STATES.DYING),
                               K_p     : self._pause_game                                   ,
                               K_u     : null_if_debug(self.__add_ufo)                      ,
                               K_PRINT : config.take_screenshot,
                               K_F12   : config.take_screenshot,
                               K_SYSREQ: config.take_screenshot,
                              }
        self._mode          = kwargs['time'] if 'time' in kwargs else -1
        self._time          = self._mode * 60 + 60 #In frames
        self._ufo           = UFO()
        ########################################################################

        ### Preparation ########################################################
        PLAYER.add(self._ship, self._ship.flames, self._ship.my_bullet, self._ship.light_column)
        UFO_GROUP.add(self._ufo)
        HUD.add(self.hud_text.score, self.hud_text.wave)
        if self._mode > -1:
        #If this is a time attack mode...
            HUD.add(self.hud_text.time)
            gamedata.lives = 1
        else:
            HUD.add(self.hud_text.lives)

        global DEBUG_KEYS
        if not config.DEBUG and DEBUG_KEYS:
        #If this is a release build...
            for i in DEBUG_KEYS:
            #For every debug action...
                del self.key_actions[i]
            DEBUG_KEYS = None

        BG.add(bg.EARTH, bg.GRID)
        enemysquadron.reset()
        enemysquadron.start()
        config.play_music(MUSIC_PATHS[self._mode])
        ########################################################################

    def __del__(self):
        super().__del__()
        BLOCKS.empty()
        pygame.mixer.stop()
        for i in MODULE_CLEANUP:
            i.clean_up()

        #vartracker.output()
        #vartracker.clear()

    def events(self, events):
        key_actions = self.key_actions

        for e in events:
        #For all events passed in...
            if e.type == KEYDOWN and e.key in key_actions:
            #If a key is pressed...
                if self._game_running or (not self._game_running and e.key == K_SPACE):
                #If we haven't gotten a game over...
                    key_actions[e.key]()
            elif config.DEBUG and e.type == MOUSEBUTTONDOWN:
            #If a mouse button is clicked and we're in debug mode...
                if e.button < 4:
                    self.__make_block(e.pos[0], MOUSE_ACTIONS[e.button])
                else:
                    self.__make_block(e.pos[0], None, True)

    def logic(self):
        enemysquadron.update()
        blockgrid.update()
        self._collision_grid.update()
        GameState.logic(self)

        if self._time > -1 and self._game_running:
        #If this is a timed game...
            self._time -= 1
            if not self._time:
            #If we run out of time...
                gamedata.lives = 0
            enemysquadron.increase_difficulty()
        
        if self._game_running:
            gamedata.alarm = blockgrid.is_above_threshold()
            config.loop_sound(ALARM if gamedata.alarm else None)
        else:
            config.loop_sound(None)

        if self._game_running and (not gamedata.lives or Block.block_full):
        #If we run out of lives or the blocks go past the top of the screen...
            pygame.mixer.music.fadeout(FADE_TIME)
            self._ship.change_state(Ship.STATES.DYING)
            self._ufo.change_state(UFO.STATES.GAMEOVER)
            self._ufo.kill()
            enemysquadron.celebrate()
            self._game_running = False
            gamedata.alarm = False
        elif not self._game_running:
        #If we've gotten a Game Over...
            if not self._ship.respawn_time:
            #Once the ship's been destroyed...
                for i in (self._ship, self._ship.flames, self._ship.light_column):
                    i.kill()
            if not pygame.mixer.music.get_busy():
            #If the song has faded out...
                HUD.add(self.hud_text.game_over, self.hud_text.press_fire)
                config.play_music(GAME_OVER_PATH)
                self.__game_over()
                

    def render(self):
        hud = partial(make_text, surfaces=True)
        
        if blockgrid.any_active():
            self.group_list[2] = BLOCKS
        else:
            blockgrid.cache_block_image()
            self.group_list[2] = blockgrid.block_buffer

        if gamedata.score != gamedata.prev_score:
        #If our score has changed since the last frame...
            self.hud_text.score.image = hud("%s: %i" % (GAME_TEXT[0], gamedata.score))
            gamedata.prev_score       = gamedata.score

        if gamedata.lives != gamedata.prev_lives and self.hud_text.lives.alive():
        #If we've gained or lost lives since the last frame...
            self.hud_text.lives.image = hud("%s: %i" % (GAME_TEXT[1], gamedata.lives))
            gamedata.prev_lives       = gamedata.lives
        
        if gamedata.wave != gamedata.prev_wave:
            self.hud_text.wave.image = hud("%s %i" % (GAME_TEXT[4], gamedata.wave))
            gamedata.prev_wave       = gamedata.wave

        if self._time >= 0:
        #If we haven't run out of time, and we're actually in timed mode...
            time_left  = ((self._time // 60 // 60), (self._time // 60) % 60)
            self.hud_text.time.image = hud(TIME_FORMAT.format(*time_left))

        GameState.render(self)
        
        if not self._ship.image.get_alpha():
        #If our ship is invisible...
            pygame.draw.circle(config.screen,
                               color.WHITE,
                               self._ship.rect.center,
                               int(150*log1p((3 * 60) - self._ship.respawn_time)) + 32,
                               16)
        
        pygame.display.flip()

    def __make_block(self, position, color=choice(color.LIST), special=False):
        '''
        @param position: Position to release the Block (it'll snap to the grid)
        @param color: Color of the Block that will be released
        '''

        if not special:
        #If we're not adding a special block...
            BLOCKS.add(block.get_block([position, 0.0], color))
        else:
            UFO.BLOCK_GROUP.add(block.get_block([position, 0.0], special=True))

    def __add_ufo(self):
        if self._ufo.state == UFO.STATES.IDLE:
        #If the UFO_GROUP is not currently on-screen...
            UFO_GROUP.add(self._ufo)
            self._ufo.change_state(UFO.STATES.APPEARING)
        
    def __ship_life(self):
        gamedata.lives += 30

    def __game_over(self):
        from game.mainmenu  import MainMenu
        kwargs={
                'next' : MainMenu      ,
                'score': gamedata.score,
                'mode' : self._mode    ,
                }
            
        self.key_actions[K_SPACE] = partial(self.change_state, HighScoreState, **kwargs)

    def _pause_game(self):
        HUD.add(self.hud_text.pause)
        for i in chain(BLOCKS, ENEMIES):
            i.image = i.current_frame_list[id(color.WHITE)][i._anim]

        self.render()
        config.toggle_pause()
        
        HUD.remove(self.hud_text.pause)
        for i in chain(BLOCKS, ENEMIES):
            i.image = i.current_frame_list[id(i.color)][i._anim]

    def __begin_tracking(self):
        pass
