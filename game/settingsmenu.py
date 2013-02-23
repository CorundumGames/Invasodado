from collections import namedtuple
from functools import partial

import pygame
from pygame.sprite import Group, OrderedUpdates

from core           import config
from core.gamestate import GameState
from core           import settings

from game           import bg
import game.mainmenu #Circular dependency; need to fix this
from game.hudobject import HudObject

'''
This is a menu that lets the user change settings within the game.
'''

HUD  = Group()
MENU = Group()
BG   = OrderedUpdates()

DIST_APART = 64
#How far apart, vertically, the menu entries are (in pixels)

DIST_APART_STATUS = 320
#How far apart, horizontally, the status of a menu entry is from the menu entry

MENU_CORNER    = (32, 64)
#The location of the top-left corner of the menu
MENU_KEYS      = namedtuple('Setttings', 'fullscreen colorblind difficulty back')
SETTINGS_NAMES = ("Full-Screen", "Colorblind Mode", "Difficulty", "Back")
TITLE_LOCATION = (config.SCREEN_RECT.centerx - 64, 32)

class SettingsMenu(GameState):
    def __init__(self):
        make_text = HudObject.make_text
        from game import mainmenu
        self.cursor_index = 0
        self.group_list = [bg.STARS_GROUP, BG, HUD, MENU]

        self.hud_title  = make_text("Settings", TITLE_LOCATION)
        self.hud_cursor = make_text("->", (0, 0))

        a = make_text(SETTINGS_NAMES, pos=MENU_CORNER, vspace=DIST_APART)

        b = make_text(
                      [config.on_off(settings.fullscreen), config.on_off(settings.color_blind), "Easy", ""],
                      pos=[MENU_CORNER[0] + DIST_APART_STATUS, MENU_CORNER[1]],
                      vspace=DIST_APART
                     )

        self.menu = MENU_KEYS(*zip(a, b))
        #first value is the menu entry, second value is its setting


        self.menu_actions = (
                             self.__toggle_fullscreen      ,
                             self.__toggle_color_blind_mode,
                             self.__toggle_difficulty      ,
                             partial(self.change_state, mainmenu.MainMenu),
                            )

        self.key_actions  = {
                             pygame.K_RETURN: self.__enter_selection         ,
                             pygame.K_UP    : partial(self.__move_cursor, -1),
                             pygame.K_DOWN  : partial(self.__move_cursor,  1),
                             pygame.K_ESCAPE: partial(self.change_state, mainmenu.MainMenu),
                            }

        HUD.add(self.hud_cursor, self.hud_title)
        MENU.add((a, b))
        BG.add(bg.EARTH, bg.GRID)

    def render(self):
        self.hud_cursor.rect.midright = self.menu[self.cursor_index][0].rect.midleft
        GameState.render(self)

    def __enter_selection(self):
        '''Go with the cursor_index the player made.'''
        self.menu_actions[self.cursor_index]()

    def __move_cursor(self, index):
        '''Move the cursor.'''
        #TODO: Put in some animation later
        self.cursor_index += index
        self.cursor_index %= len(self.menu)

    def __toggle_fullscreen(self):
        config.toggle_fullscreen()
        self.menu.fullscreen[1].image = HudObject.make_text(config.on_off(settings.fullscreen), surfaces=True)

    def __toggle_color_blind_mode(self):
        config.toggle_color_blind_mode();
        self.menu.colorblind[1].image = HudObject.make_text(config.on_off(settings.color_blind), surfaces=True)

    def __toggle_difficulty(self):
        pass