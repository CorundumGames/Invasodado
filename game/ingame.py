from functools import partial

import pygame
from pygame import display
from pygame.sprite import Group, OrderedUpdates

from core            import collisions
from core.collisions import CollisionGrid
from core.gamestate  import GameState
from core            import color
from core            import config

from game import enemysquadron
#if __debug__: import core.vartracker

from game       import balloflight
from game.balloflight import BallOfLight
from game       import bg
from game       import block
from game.block import Block

from game           import gamedata
from game.hudobject import HudObject
from game           import enemy
from game.enemy     import Enemy
from game import enemybullet
from enemybullet import EnemyBullet
from game.player    import Ship
from game.shipbullet import ShipBullet
from game           import blockgrid
from core.particles import Particle, ParticleEmitter
from game.ufo       import UFO


BG            = OrderedUpdates()
BLOCKS        = Group()
ENEMIES       = Group()
ENEMY_BULLETS = Group()
HUD           = Group()
PARTICLES     = Group()
PLAYER        = Group()
UFO_GROUP     = Group()

rect = config.SCREEN_RECT

FIRE_LOCATION      = (rect.centerx - 192, rect.centery)
FIRE_MESSAGE       = "Press fire to continue"
GAME_OVER_LOCATION = (rect.centerx - 64, rect.centery - 64)
LIVES_LOCATION     = (rect.width - 160, 16)
SCORE_LOCATION     = (16, 16)
TIME_LOCATION      = (rect.centerx, 32)
TYPES_TO_IGNORE    = (Block, BallOfLight, HudObject, Particle, ParticleEmitter)

class InGameState(GameState):
    def __init__(self, *args, **kwargs):
        '''
        @ivar _collision_grid: Objects that collide with others
        @ivar _game_running: True if we haven't gotten a Game Over
        @ivar group_list: list of pygame.Groups, rendered in ascending order
        @ivar hud_text: dict of HUD items that give info to the player
        @ivar key_actions: dict of functions to call when a given key is pressed
        @ivar _mouse_actions: dict of Blocks to drop on mouse click, only if __debug__
        @ivar _ship: The player character
        @ivar _time: Time limit for the game in seconds (no limit if 0)
        @ivar _ufo: The UFO_GROUP object that, when shot, can destroy many blocks
        '''
        from game.mainmenu import MainMenu
        hud  = HudObject.make_text
        rect = config.SCREEN_RECT

        self._game_running   = True
        self.group_list     = [bg.STARS_GROUP, BG, BLOCKS, UFO_GROUP, ENEMIES, ENEMY_BULLETS, PLAYER, PARTICLES, HUD]
        self._collision_grid = CollisionGrid(4, 4, 1, self.group_list)
        self.hud_text       = {
                               'score'     : hud('', SCORE_LOCATION),
                               'lives'     : hud('', LIVES_LOCATION),
                               'time'      : hud('', TIME_LOCATION ),
                               'game_over' : hud("GAME OVER", GAME_OVER_LOCATION),
                               'press_fire': hud(FIRE_MESSAGE, FIRE_LOCATION),
                              }
        self.key_actions    = {
                               pygame.K_ESCAPE: partial(self.change_state, MainMenu),
                               pygame.K_F1    : config.toggle_fullscreen ,
                               pygame.K_SPACE : self.__ship_fire         ,
                               pygame.K_c     : blockgrid.clean_up       ,
                               pygame.K_f     : config.toggle_frame_limit,
                               pygame.K_p     : config.toggle_pause      ,
                               pygame.K_u     : self.__add_ufo           ,
                               pygame.K_e     : self.__game_over         ,
                              }
        self._mode          = kwargs['time'] * 100 + 100 if 'time' in kwargs else -1
        self._mouse_actions = {1:color.RED, 2:color.YELLOW, 3:color.BLUE}
        self._ship          = Ship()
        self._time          = self._mode
        self._ufo           = UFO()

        PLAYER.add(self._ship, self._ship.flames, self._ship.my_bullet)
        UFO_GROUP.add(self._ufo)
        HUD.add(self.hud_text['score'], self.hud_text['lives'])
        if self._time > -1:
        #If this is a time attack mode...
            HUD.add(self.hud_text['time'])
            gamedata.lives = 1
        else:
            del self.hud_text['time']

        if not __debug__:
        #If this is a release build...
            for i in [pygame.K_u, pygame.K_c, pygame.K_f, pygame.K_F1, pygame.K_e]:
            #For every debug action...
                del self.key_actions[i]
            del self._mouse_actions

        BallOfLight.BLOCK_GROUP   = BLOCKS
        BallOfLight.enemy_group   = ENEMIES
        BallOfLight.block_mod     = block
        Block.GROUP               = BLOCKS
        Particle.GROUP            = PARTICLES
        blockgrid.block_type      = Block
        Block.particle_group      = PARTICLES
        enemysquadron.ENEMY_GROUP = ENEMIES
        Enemy.GROUP               = ENEMIES
        EnemyBullet.GROUP         = ENEMY_BULLETS
        Ship.GROUP                = PLAYER
        ShipBullet.GROUP          = PLAYER
        UFO.GROUP                 = UFO_GROUP
        UFO.BLOCK_GROUP           = BLOCKS

        collisions.dont_check_type(*TYPES_TO_IGNORE)
        BG.add(bg.EARTH, bg.GRID)
        enemysquadron.reset()
        enemysquadron.start()

    def __del__(self):
        map(Group.empty, self.group_list)

        for i in [balloflight, blockgrid, block, enemybullet, enemysquadron, gamedata]:
            i.clean_up()

        #vartracker.output()
        #vartracker.clear()

    def events(self, events):
        key_actions = self.key_actions

        for e in events:
        #For all events passed in...
            if __debug__ and e.type == pygame.MOUSEBUTTONDOWN:
            #If a mouse button is clicked and we're in debug mode...
                self.__make_block(e.pos[0], self._mouse_actions[e.button])
            elif e.type == pygame.KEYDOWN and e.key in key_actions:
            #If a key is pressed...
                if self._game_running or (not self._game_running and e.key == pygame.K_SPACE):
                #If we haven't gotten a game over...
                    key_actions[e.key]()

    def logic(self):
        #if __debug__ and len(ENEMIES) == 0: vartracker.update()
        enemysquadron.update()
        self._collision_grid.update()
        map(Group.update, self.group_list)

        if self._time > -1 and self._game_running:
        #If this is a timed game...
            self._time -= 1
            if not self._time:
            #If we run out of time...
                gamedata.lives = 0
            enemysquadron.increase_difficulty()

        if gamedata.combo and gamedata.combo_counter < gamedata.COMBO_LENGTH:
        #If we made a combo...
            gamedata.combo_counter += 1
        else:
            gamedata.combo         = False
            gamedata.combo_counter = 0
            gamedata.multiplier    = gamedata.DEFAULT_MULTIPLIER

        if self._game_running and (not gamedata.lives or Block.block_full):
        #If we run out of lives or the blocks go past the top of the screen...
            self.__game_over()
            enemysquadron.celebrate()
            self._game_running = False

    def render(self):
        hud = partial(HudObject.make_text, surfaces=True)

        if gamedata.score != gamedata.prev_score:
        #If our score has changed since the last frame...
            self.hud_text['score'].image = hud("Score: %i" % gamedata.score)
            gamedata.prev_score          = gamedata.score

        if gamedata.lives != gamedata.prev_lives:
        #If we've gained or lost lives since the last frame...
            self.hud_text['lives'].image = hud("Lives: %i" % gamedata.lives)
            gamedata.prev_lives          = gamedata.lives

        if self._time >= 0:
        #If we haven't run out of time...
            time_left  = [self._time / 100 / 60, (self._time / 100) % 60]
            self.hud_text['time'].image = hud("{}:{:0>2}".format(*time_left))

        config.screen.fill((0, 0, 0))
        bg.STARS.emit()

        map(Group.draw, self.group_list, [config.screen] * len(self.group_list))

        display.flip()
        display.set_caption("FPS: %f" % round(self.fps_timer.get_fps(), 3))

        self.fps_timer.tick_busy_loop(60 * config._limit_frame)

    def __make_block(self, position, color):
        '''
        @param position: Position to release the Block (it'll snap to the grid)
        @param color: Color of the Block that will be released
        '''
        BLOCKS.add(block.get_block([position, 0], color))

    def __add_ufo(self):
        if self._ufo.state == UFO.STATES.IDLE:
        #If the UFO_GROUP is not currently on-screen...
            UFO_GROUP.add(self._ufo)
            self._ufo.state = UFO.STATES.APPEARING

    def __ship_fire(self):
        self._ship.on_fire_bullet()

    def __game_over(self):
        from game.highscore import HighScoreState
        from game.mainmenu  import MainMenu
        self.key_actions[pygame.K_SPACE] = partial(self.change_state,
                                                   HighScoreState,
                                                   kwargs={
                                                    'next' : MainMenu      ,
                                                    'score': gamedata.score,
                                                    'mode' : self._mode    ,
                                                   })
        for i in [self._ship, self._ship.flames]: i.kill()
        self._ship.state      = Ship.STATES.IDLE

        HUD.add(self.hud_text['game_over'], self.hud_text['press_fire'])

    def __begin_tracking(self):
        pass