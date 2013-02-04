from functools import partial

from pygame import display
import pygame.event
import pygame.sprite
import pygame.time

from core            import collisions
from core.collisions import CollisionGrid
from core.gamestate  import GameState
from core            import color
from core            import config

from game import enemysquadron
#if __debug__: import core.vartracker

from game import balloflight
from game import bg
from game import block
#from game import blockgrid

from game           import gamedata
from game.hudobject import HudObject
from game           import enemy
from game           import player
from game           import shipbullet
from game           import blockgrid


BG            = pygame.sprite.OrderedUpdates()
BLOCKS        = pygame.sprite.Group()
ENEMIES       = pygame.sprite.Group()
ENEMY_BULLETS = pygame.sprite.Group()
HUD           = pygame.sprite.Group()
PARTICLES     = pygame.sprite.Group()
PLAYER        = pygame.sprite.Group()
UFO           = pygame.sprite.Group()

mode_vals = {-1: 0, -2: 0, 120: 1, 300: 2}  #FIXME: Quick hack

class InGameState(GameState):
    def __init__(self, *args, **kwargs):
        '''
        @ivar collision_grid: Objects that collide with others
        @ivar game_running: True if we haven't gotten a Game Over
        @ivar group_list: list of pygame.Groups, rendered in ascending order
        @ivar hud_text: dict of HUD items that give info to the player
        @ivar key_actions: dict of functions to call when a given key is pressed
        @ivar mouse_actions: dict of Blocks to drop on mouse click, only in Debug mode
        @ivar ship: The player character
        @ivar time: Time limit for the game in seconds (no limit if 0)
        @ivar ufo: The UFO object that, when shot, can destroy many blocks
        '''
        from core.particles import Particle, ParticleEmitter
        from game import mainmenu
        hud  = HudObject.make_text
        rect = config.SCREEN_RECT

        self.game_running   = True
        self.group_list     = [bg.STARS_GROUP, BG, BLOCKS, UFO, ENEMIES, ENEMY_BULLETS, PLAYER, PARTICLES, HUD]
        self.collision_grid = CollisionGrid(4, 4, 1, self.group_list)
        self.hud_text       = {
                               'score'     : hud('', (16, 16)),
                               'lives'     : hud('', (rect.width - 160, 16)),
                               'game_over' : hud("GAME OVER", (rect.centerx - 64, rect.centery - 64)),
                               'press_fire': hud("Press fire to continue", (rect.centerx - 192, rect.centery)),
                               'time'      : hud('', (rect.centerx, 32))
                              }
        self.key_actions    = {
                               pygame.K_ESCAPE: partial(self.change_state, mainmenu.MainMenu),
                               pygame.K_F1    : config.toggle_fullscreen ,
                               pygame.K_SPACE : self.__ship_fire         ,
                               pygame.K_c     : None          ,
                               pygame.K_f     : config.toggle_frame_limit,
                               pygame.K_p     : config.toggle_pause      ,
                               pygame.K_u     : self.__add_ufo           ,
                               pygame.K_e     : self.__game_over         ,
                              }
        self.mouse_actions  = {1:color.RED, 2:color.YELLOW, 3:color.BLUE}
        self.ship           = Ship()
        self.start_time     = pygame.time.get_ticks()
        self.time           = kwargs['time'] * 1000 + 1000 if 'time' in kwargs else -1
        self.end_time       = self.start_time + self.time
        self.ufo            = ufo.UFO()

        PLAYER.add(self.ship, self.ship.flames, self.ship.my_bullet)
        UFO.add(self.ufo)
        HUD.add(self.hud_text['score'], self.hud_text['lives'])
        if self.time > 0:
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
            del self.mouse_actions

        balloflight.BallOfLight.block_group = BLOCKS
        balloflight.BallOfLight.enemy_group = ENEMIES
        balloflight.BallOfLight.block_mod   = block
        block.Block.group                   = BLOCKS
        block.Block.particle_group          = PARTICLES  
        blockgrid.block_type                = block.Block
        collisions.dont_check_type(block.Block, balloflight.BallOfLight, HudObject, Particle, ParticleEmitter)
        enemysquadron.enemy_group           = ENEMIES
        enemy.Enemy.group                   = ENEMIES
        player.Ship.group                   = PLAYER
        shipbullet.ShipBullet.group = PLAYER
        ufo.UFO.ufo_group           = UFO
        ufo.UFO.block_group         = BLOCKS

        BG.add(bg.EARTH, bg.GRID)
        enemysquadron.reset()
        enemysquadron.start()

    def __del__(self):
        from game import blockgrid, enemybullet
        map(pygame.sprite.Group.empty, self.group_list)

        for m in [balloflight, blockgrid, block, enemybullet, enemysquadron, gamedata]:
            m.clean_up()

        #vartracker.output()
        #vartracker.clear()

    def events(self, events):
        key_actions = self.key_actions

        for e in events:
        #For all events passed in...
            if __debug__ and e.type == pygame.MOUSEBUTTONDOWN:
            #If a mouse button is clicked and we're in debug mode...
                self.__make_block(e.pos[0], self.mouse_actions[e.button])
            elif e.type == pygame.KEYDOWN and e.key in key_actions:
            #If a key is pressed...
                if self.game_running or (not self.game_running and e.key == pygame.K_SPACE):
                #If we haven't gotten a game over...
                    key_actions[e.key]()

    def logic(self):
        #if __debug__ and len(ENEMIES) == 0: vartracker.update()
        enemysquadron.update()
        self.collision_grid.update()
        map(pygame.sprite.Group.update, self.group_list)

        if self.time > -1 and self.game_running:
        #If this is a timed game...
            if pygame.time.get_ticks() >= self.end_time:
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

        if self.game_running and (not gamedata.lives or block.Block.block_full):
        #If we run out of lives or the blocks go past the top of the screen...
            self.__game_over()
            enemysquadron.celebrate()
            self.game_running = False



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

        if self.time >= 0:
        #If we haven't run out of time...
            milli = self.end_time - pygame.time.get_ticks()
            time  = [milli/1000/60, (milli/1000) % 60]
            self.hud_text['time'].image = hud("{}:{:0>2}".format(*time))

        config.screen.fill((0, 0, 0))
        bg.STARS.emit()

        map(pygame.sprite.Group.draw, self.group_list, [config.screen]*len(self.group_list))

        display.flip()
        display.set_caption("FPS: %hud" % round(self.fps_timer.get_fps(), 3))

        self.fps_timer.tick_busy_loop(60 * config.limit_frame)


    def __make_block(self, position, color):
        '''
        @param position: Position to release the Block (it'll snap to the grid)
        @param color: Color of the Block that will be released
        '''
        BLOCKS.add(block.get_block([position, 0], color))

    def __add_ufo(self):
        if self.ufo.state == ufo.UFO.STATES.IDLE:
        #If the UFO is not currently on-screen...
            UFO.add(self.ufo)
            self.ufo.state = ufo.UFO.STATES.APPEARING

    def __ship_fire(self):
        self.ship.on_fire_bullet()

    def __game_over(self):
        from game.highscore import HighScoreState

        self.key_actions[pygame.K_SPACE] = partial(self.change_state,
                                                   HighScoreState,
                                                   {'score': int(gamedata.score),
                                                    'mode': mode_vals[(self.time-1000)/1000]
                                                    })
        self.ship.kill()
        self.ship.flames.kill()
        self.ship.state      = Ship.STATES.IDLE

        HUD.add(self.hud_text['game_over'], self.hud_text['press_fire'])

    def __begin_tracking(self):
        pass

from game.player import Ship
from game import ufo
