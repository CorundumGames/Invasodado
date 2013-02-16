from functools import partial

import pygame.display
from pygame.sprite import Group, OrderedUpdates

from core           import config
from core.gamestate import GameState
from core           import settings

from game           import bg
import mainmenu  #Circular dependency; need to fix this
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
MENU_KEYS      = ['fullscreen', 'colorblind', 'difficulty', 'back']
SETTINGS_NAMES = ["Full-Screen", "Colorblind Mode", "Difficulty", "Back",]
TITLE_LOCATION = (config.SCREEN_RECT.centerx - 64, 32)

class SettingsMenu(GameState):
    def __init__(self):
        make_text = HudObject.make_text
        self.cursor_index = 0
        self.group_list = [bg.STARS_GROUP, BG, HUD, MENU]

        self.hud_title  = make_text("Settings", TITLE_LOCATION)
        self.hud_cursor = make_text("->", (0, 0))

        a = make_text(SETTINGS_NAMES, pos=MENU_CORNER, vspace=DIST_APART)

        b = make_text(
                      [self.__on_off(settings.fullscreen), self.__on_off(settings.color_blind), "Easy", ""],
                      pos=[MENU_CORNER[0] + DIST_APART_STATUS, MENU_CORNER[1]],
                      vspace=DIST_APART
                     )

        self.menu = dict(zip(MENU_KEYS, zip(a, b)))
        #first value is the menu entry, second value is its setting


        self.menu_actions = [
                             self.__toggle_fullscreen      ,
                             self.__toggle_color_blind_mode,
                             self.__toggle_difficulty      ,
                             partial(self.change_state, mainmenu.MainMenu),
                            ]

        self.key_actions  = {
                             pygame.K_RETURN: self.__enter_selection         ,
                             pygame.K_UP    : partial(self.__move_cursor, -1),
                             pygame.K_DOWN  : partial(self.__move_cursor,  1),
                             pygame.K_ESCAPE: partial(self.change_state, mainmenu.MainMenu),
                            }

        

        HUD.add(self.hud_cursor, self.hud_title)
        MENU.add((a, b))
        BG.add(bg.EARTH, bg.GRID)

    def __del__(self):
        map(Group.empty, self.group_list)
        del self.group_list

    def events(self, events):
        for e in events:
        #For all input we've received...
            if e.type == pygame.KEYDOWN and e.key in self.key_actions:
            #If a key was pressed...
                self.key_actions[e.key]()
                
    def logic(self):
        map(Group.update, self.group_list)

    def render(self):
        pygame.display.get_surface().fill((0, 0, 0))

        self.hud_cursor.rect.midright = self.menu[MENU_KEYS[self.cursor_index]][0].rect.midleft

        bg.STARS.emit()
        map(Group.draw, self.group_list, [config.screen]*len(self.group_list))

        pygame.display.flip()
        pygame.display.set_caption("FPS: %f" % round(self.fps_timer.get_fps(), 3))

        self.fps_timer.tick(60)

    def __on_off(self, condition):
        return "On" if condition else "Off"

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
        self.menu['fullscreen'][1].image = HudObject.make_text(self.__on_off(settings.fullscreen), surfaces=True)

    def __toggle_color_blind_mode(self):
        config.toggle_color_blind_mode();
        self.menu['colorblind'][1].image = HudObject.make_text(self.__on_off(settings.color_blind), surfaces=True)
        pass

    def __toggle_difficulty(self):
        pass