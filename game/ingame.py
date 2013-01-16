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
import highscore
import hudobject
import mainmenu
import player
import shipbullet
import ufo

PLAYER  = pygame.sprite.Group()
ENEMIES = pygame.sprite.Group()
BLOCKS  = pygame.sprite.Group()
HUD     = pygame.sprite.Group()
BG      = pygame.sprite.OrderedUpdates()

DEFAULT_MULTIPLIER = 10
multiplier         = DEFAULT_MULTIPLIER

score      = 0
prev_score = None

lives      = 3
prev_lives = None

class InGameState(gamestate.GameState):
    def __init__(self, *args):
        self.args           = args
        #The arguments we can use to change this gamestate

        self.collision_grid = collisions.CollisionGrid(4, 4, 1)
        #The collision-handling system

        self.group_list     = [bg.STARS_GROUP, BG, BLOCKS, ENEMIES, PLAYER, HUD]
        #The groups of sprites to process

        self.ship           = player.Ship()
        #The player

        self.ufo            = ufo.UFO()
        self.ufo_odds       = .0001
        #The UFO

        f = hudobject.HudObject.make_text
        r = config.SCREEN_RECT
        self.hud_text = {
                         'score'     : f('', (16, 16)),
                         'lives'     : f('', (r.width - 160, 16)),
                         'game_over' : f("GAME OVER", (r.centerx - 64, r.centery - 64)),
                         'press_fire': f("Press fire to continue", (r.centerx - 192, r.centery))
                         }
        #The components of our HUD; let the player know how he's doing!

        self.game_running = True
        #False if we've gotten a game over

        self.key_actions = {
                            pygame.K_ESCAPE: self.__return_to_menu    ,
                            pygame.K_SPACE : self.ship.on_fire_bullet ,
                            pygame.K_F1    : config.toggle_fullscreen ,
                            pygame.K_c     : self.__clear_blocks      ,
                            pygame.K_f     : config.toggle_frame_limit,
                            pygame.K_p     : config.toggle_pause      ,
                            pygame.K_u     : self.__add_ufo           ,
                            }
        #The keys available for use; key is keycode, element is a function

        self.mouse_actions = {
                              1: color.RED   ,
                              2: color.YELLOW,
                              3: color.BLUE  ,
                             }
        #What clicking the mouse can do: key is mouse button, element is color

        PLAYER.add(self.ship)
        HUD.add(self.hud_text['score'], self.hud_text['lives'])
        BG.add(bg.EARTH, bg.GRID)
        enemysquadron.reset()
        block.Block.block_full = False

    def __del__(self):
        global score, prev_score
        global lives, prev_lives
        global multiplier
        map(pygame.sprite.Group.empty, self.group_list)

        clean_up_crew = [balloflight,
                         blockgrid,
                         block,
                         enemybullet,
                         enemysquadron]

        for m in clean_up_crew: m.clean_up()

        self.group_list = []
        del self.hud_text, self.ufo

        score, prev_score = 0, None
        lives, prev_lives = 3, None
        multiplier        = DEFAULT_MULTIPLIER

    def events(self, events):
        for e in events:
        #For all events passed in...
            if e.type == pygame.MOUSEBUTTONDOWN and config.debug:
            #If a mouse button is clicked...
                self.__make_block(e.pos[0], self.mouse_actions[e.button])
            elif e.type == pygame.KEYDOWN and e.key in self.key_actions:
            #If a key is pressed...
                if self.game_running:
                #If we haven't gotten a game over...
                    self.key_actions[e.key]()
                elif e.key == pygame.K_SPACE:
                    self.next_state = highscore.HighScoreState(score = int(score))

    def logic(self):
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

        if (lives == 0 or block.Block.block_full) and self.game_running:
        #If we run out of lives or the blocks go past the top of the screen...
            self.__game_over()
            enemysquadron.celebrate()
            self.game_running = False

        if random.uniform(0, 1) < self.ufo_odds:
            self.__add_ufo()

    def render(self):
        global prev_score, prev_lives

        if score != prev_score:
        #If our score has changed since the last frame...
            self.hud_text['score'].image = hudobject.HudObject.make_text("Score: %i" % score, surfaces = True)
            prev_score = score

        if lives != prev_lives:
        #If we've gained or lost lives since the last frame...
            self.hud_text['lives'].image = hudobject.HudObject.make_text("Lives: %i" % lives, surfaces = True)
            prev_lives = lives

        pygame.display.get_surface().fill((0, 0, 0))
        bg.STARS.emit()

        map(pygame.sprite.Group.draw, self.group_list, [pygame.display.get_surface()]*len(self.group_list))

        pygame.display.flip()
        pygame.display.set_caption("FPS: %f" % round(self.fps_timer.get_fps(), 3))

        self.fps_timer.tick_busy_loop(60 * config.limit_frame)


    def __make_block(self, pos, c):
        BLOCKS.add(block.get_block([pos, 0], c))

    def __clear_blocks(self):
        if config.debug:
        #If we're in debug mode...
            blockgrid.blocks.clear()

    def __return_to_menu(self):
        self.next_state = mainmenu.MainMenu()

    def __add_ufo(self):
        if self.ufo.state == ufo.UFO.STATES.IDLE:
        #If the UFO is not currently on-screen...
            ENEMIES.add(self.ufo)
            self.ufo.state = ufo.UFO.STATES.APPEARING

    def __game_over(self):
        enemy.Enemy.velocity = [0, 0]

        self.ship.kill()
        self.ship.state      = player.STATES.IDLE

        HUD.add(self.hud_text['game_over'], self.hud_text['press_fire'])