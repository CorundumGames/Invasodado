from functools import partial
import math
import random

import pygame.display
import pygame.event
import pygame.sprite

import core.collisions     as collisions
import core.color          as color
import core.config         as config
import core.gamestate      as gamestate
import core.highscoretable as highscoretable

import balloflight
import bg
import block
import blockgrid
import enemy
import enemybullet
import enemysquadron
from highscore import HighScoreState
import hudobject
import mainmenu
import player
import shipbullet
import ufo

BG      = pygame.sprite.OrderedUpdates()
BLOCKS  = pygame.sprite.Group()
ENEMIES = pygame.sprite.Group()
HUD     = pygame.sprite.Group()
PLAYER  = pygame.sprite.Group()
UFO     = pygame.sprite.Group()

DEFAULT_MULTIPLIER = 10
multiplier         = DEFAULT_MULTIPLIER
COMBO_LENGTH        = 50

combo         = False
combo_counter = 0

score      = 0
prev_score = None

lives      = 3
prev_lives = None

class InGameState(gamestate.GameState):
    def __init__(self, *args, **kwargs):
        '''
        @ivar args: list of positional arguments that affect InGameState's execution
        @ivar collision_grid: Objects that collide with others
        @ivar game_running: True if we haven't gotten a Game Over
        @ivar group_list: list of pygame.Groups, rendered in ascending order
        @ivar hud_text: dict of HUD items that give info to the player
        @ivar key_actions: dict of functions to call when a given key is pressed
        @ivar kwargs: dict of keyword arguments that affect InGameState's execution
        @ivar mouse_actions: dict of Blocks to drop on mouse click, only in Debug mode
        @ivar ship: The player character
        @ivar time: Time limit for the game in seconds (no limit if 0)
        @ivar ufo: The UFO object that, when shot, can destroy many blocks
        '''

        f = hudobject.HudObject.make_text
        r = config.SCREEN_RECT
        self.args           = args
        self.collision_grid = collisions.CollisionGrid(4, 4, 1)
        self.game_running   = True
        self.group_list     = [bg.STARS_GROUP, BG, BLOCKS, UFO, ENEMIES, PLAYER, HUD]
        self.hud_text       = {
                               'score'     : f('', (16, 16)),
                               'lives'     : f('', (r.width - 160, 16)),
                               'game_over' : f("GAME OVER", (r.centerx - 64, r.centery - 64)),
                               'press_fire': f("Press fire to continue", (r.centerx - 192, r.centery)),
                               'time'      : f('', (r.centerx, 32))
                              }
        self.key_actions    = {
                               pygame.K_ESCAPE: partial(self.change_state, mainmenu.MainMenu),
                               pygame.K_F1    : config.toggle_fullscreen ,
                               pygame.K_SPACE : self.__ship_fire         ,
                               pygame.K_c     : blockgrid.clear          ,
                               pygame.K_f     : config.toggle_frame_limit,
                               pygame.K_p     : config.toggle_pause      ,
                               pygame.K_u     : self.__add_ufo           ,
                              }
        self.kwargs         = kwargs
        self.mouse_actions  = {1:color.RED, 2:color.YELLOW, 3:color.BLUE}
        self.ship           = player.Ship()
        self.time           = kwargs['time'] if 'time' in kwargs else 0
        self.ufo            = ufo.UFO()

        PLAYER.add(self.ship)
        HUD.add(self.hud_text['score'], self.hud_text['lives'])
        BG.add(bg.EARTH, bg.GRID)
        enemysquadron.reset()
        block.Block.block_full = False

        if not config.debug:
            for i in [pygame.K_u, pygame.K_c, pygame.K_f, pygame.K_F1]:
                del self.key_actions[i]
            del self.mouse_actions

    def __del__(self):
        global score, prev_score
        global lives, prev_lives
        global combo, combo_counter
        global multiplier
        map(pygame.sprite.Group.empty, self.group_list)

        for m in [balloflight, blockgrid, block, enemybullet, enemysquadron]:
            m.clean_up()

        del self.hud_text, self.ufo, self.group_list

        score, prev_score    = 0, None
        lives, prev_lives    = 3, None
        combo, combo_counter = False, 0
        multiplier           = DEFAULT_MULTIPLIER

    def events(self, events):
        ka = self.key_actions

        for e in events:
        #For all events passed in...
            if e.type == pygame.MOUSEBUTTONDOWN and config.debug:
            #If a mouse button is clicked...
                self.__make_block(e.pos[0], self.mouse_actions[e.button])
            elif e.type == pygame.KEYDOWN and e.key in ka:
            #If a key is pressed...
                if self.game_running or (not self.game_running and e.key == pygame.K_SPACE):
                #If we haven't gotten a game over...
                    ka[e.key]()

    def logic(self):
        global combo, combo_counter, multiplier
        self.collision_grid.update()
        map(pygame.sprite.Group.update, self.group_list)

        if len(ENEMIES) == 0:
        #If all enemies have been killed...
            enemysquadron.reset()
            enemy.Enemy.velocity[0] = abs(enemy.Enemy.velocity[0]) + 0.05

        if enemy.Enemy.should_flip:
        #If at least one enemy has touched the side of the screen...
            enemy.Enemy.velocity[0] *= -1
            enemysquadron.move_down()
            enemy.Enemy.should_flip = False

        if self.game_running and (lives == 0 or block.Block.block_full):
        #If we run out of lives or the blocks go past the top of the screen...
            self.__game_over()
            enemysquadron.celebrate()
            self.game_running = False

        if combo and combo_counter < COMBO_LENGTH:
            combo_counter += 1
        else:
            combo         = False
            combo_counter = 0
            multiplier    = DEFAULT_MULTIPLIER

    def render(self):
        global prev_score, prev_lives
        pd = pygame.display
        g = self.group_list

        if score != prev_score:
        #If our score has changed since the last frame...
            self.hud_text['score'].image = hudobject.HudObject.make_text("Score: %i" % score, surfaces = True)
            prev_score = score

        if lives != prev_lives:
        #If we've gained or lost lives since the last frame...
            self.hud_text['lives'].image = hudobject.HudObject.make_text("Lives: %i" % lives, surfaces = True)
            prev_lives = lives

        pd.get_surface().fill((0, 0, 0))
        bg.STARS.emit()

        map(pygame.sprite.Group.draw, g, [config.screen]*len(g))

        pd.flip()
        pd.set_caption("FPS: %f" % round(self.fps_timer.get_fps(), 3))

        self.fps_timer.tick_busy_loop(60 * config.limit_frame)


    def __make_block(self, pos, c):
        '''
        @param pos: Position to release the Block (it'll snap to the grid)
        @param c: Color of the Block that will be released
        '''
        BLOCKS.add(block.get_block([pos, 0], c))

    def __add_ufo(self):
        if self.ufo.state == ufo.UFO.STATES.IDLE:
        #If the UFO is not currently on-screen...
            UFO.add(self.ufo)
            self.ufo.state = ufo.UFO.STATES.APPEARING

    def __ship_fire(self):
        self.ship.on_fire_bullet()

    def __game_over(self):
        enemy.Enemy.velocity = [0, 0]
        self.key_actions[pygame.K_SPACE] = partial(self.change_state, HighScoreState, score=int(score))
        self.ship.kill()
        self.ship.flames.kill()
        self.ship.state      = player.Ship.STATES.IDLE

        HUD.add(self.hud_text['game_over'], self.hud_text['press_fire'])