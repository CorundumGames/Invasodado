from functools import partial
import random

import pygame.event
import pygame.display
import pygame.sprite

from core import color
from core import config
from core import gamestate

import bg
from ingame import InGameState
from highscore import HighScoreState
from hudobject import HudObject
from settingsmenu import SettingsMenu

'''
This is where the user makes his decisions about what to do in the game.
Not really special compared to any other main menu.
'''

HUD  = pygame.sprite.Group()
MENU = pygame.sprite.Group()
BG   = pygame.sprite.OrderedUpdates()

DIST_APART = 48
#How far apart, vertically, the menu entries are (in pixels)

MENU_CORNER = (config.SCREEN_RECT.centerx - 112, config.SCREEN_RECT.centery - 64)
#The location of the top-left corner of the menu

class MainMenu(gamestate.GameState):
    def __init__(self):
        self.frame_limit = True
        #True if we're limiting the frame rate to 60 FPS

        self.selection    = 0

        self.group_list = [bg.STARS_GROUP, BG, HUD, MENU]

        self.hud_title = HudObject.make_text("Invasodado", [config.SCREEN_RECT.centerx - 96, 32])

        #Will be replaced with a logo (aka an actual image) later.
        self.hud_selection  = HudObject.make_text("->", (0, 0))

        self.menu = HudObject.make_text(["Normal Mode",
                                         "2 Minutes",
                                         "5 Minutes",
                                         "High Scores",
                                         "Settings"   ,
                                         "Quit"       ,],
                                         pos = MENU_CORNER,
                                         vspace = DIST_APART)

        self.menu_actions = [
                             partial(self.change_state, InGameState,   0),
                             partial(self.change_state, InGameState, 120),
                             partial(self.change_state, InGameState, 300),
                             partial(self.change_state, HighScoreState  ),
                             partial(self.change_state, SettingsMenu    ),
                             quit                                        ,
                            ]

        self.key_actions  = {
                             pygame.K_RETURN : self.__enter_selection         ,
                             pygame.K_UP     : partial(self.__move_cursor, -1),
                             pygame.K_DOWN   : partial(self.__move_cursor,  1),
                             pygame.K_ESCAPE : quit                           ,
                             }



        HUD.add(self.hud_title, self.hud_selection)
        MENU.add(self.menu)
        BG.add(bg.EARTH, bg.GRID)

    def __del__(self):
        map(pygame.sprite.Group.empty, self.group_list)

        self.group_list = []

    def events(self, events):
        ka = self.key_actions
        for e in events:
        #For all input we've received...
            if e.type == pygame.KEYDOWN and e.key in ka:
            #If a key was pressed...
                ka[e.key]()
                self.selection %= len(self.menu_actions)

    def logic(self):
        map(pygame.sprite.Group.update, self.group_list)

    def render(self):
        pd = pygame.display
        g = self.group_list

        self.hud_selection.rect.midright = self.menu[self.selection].rect.midleft
        pd.get_surface().fill((0, 0, 0))
        bg.STARS.emit()
        map(pygame.sprite.Group.draw, g, [config.screen]*len(g))

        pd.flip()
        pd.set_caption("FPS: %f" % round(self.fps_timer.get_fps(), 3))

        self.fps_timer.tick(60 * self.frame_limit)

    def __enter_selection(self):
        '''Go with the selection the player made.'''
        self.menu_actions[self.selection]()

    def __move_cursor(self, index):
        '''Move the cursor.'''
        #There should probably be some animation here later.
        self.selection += index
