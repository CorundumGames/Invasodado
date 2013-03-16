'''
This is a menu that lets the user change settings within the game.
'''

from collections import namedtuple
from functools import partial
from os.path import join

import pygame
from pygame.constants import *
from pygame.sprite import Group, OrderedUpdates

from core           import config
from core.gamestate import GameState
from core           import settings


from game           import bg
from game.hudobject import make_text

### Groups #####################################################################
HUD  = Group()
MENU = Group()
GRID_BG   = OrderedUpdates()
################################################################################

### Constants ##################################################################
DIST_APART = 64
#How far apart, vertically, the menu entries are (in pixels)

DIST_APART_STATUS = 320
#How far apart, horizontally, the status of a menu entry is from the menu entry

MENU_CORNER    = (32, 64)
#The location of the top-left corner of the menu
SETTINGS_FIELDS = 'fullscreen colorblind difficulty musicvolume effectsvolume back'
SETTINGS_KEYS   = namedtuple('Settings', SETTINGS_FIELDS)
SETTINGS_NAMES  = config.load_text('settings')
TITLE_LOCATION  = (config.SCREEN_RECT.centerx - 64, 32)
################################################################################

### Preparation ################################################################
del SETTINGS_FIELDS
################################################################################

class SettingsMenu(GameState):
    def __init__(self):
        from game.mainmenu import MainMenu
        
        self.cursor_index = 0
        self.group_list   = (bg.STARS_GROUP, GRID_BG, HUD, MENU)
        self.hud_title    = make_text("Settings", TITLE_LOCATION)
        self.hud_cursor   = make_text("->"      , (0, 0)        )

        a = make_text(SETTINGS_NAMES, pos=MENU_CORNER, vspace=DIST_APART)

        b = make_text(
                      (config.on_off(settings.fullscreen), config.on_off(settings.color_blind), config.difficulty_string(),
                       config.percent_str(settings.music_volume),
                       config.percent_str(settings.sound_volume), ""),
                      pos=(MENU_CORNER[0] + DIST_APART_STATUS, MENU_CORNER[1]),
                      vspace=DIST_APART
                     )

        self.menu = SETTINGS_KEYS(*zip(a, b))
        #first value is the menu entry, second value is its setting


        self.menu_actions = (
                             self.__toggle_fullscreen            ,
                             self.__toggle_color_blind_mode      ,
                             self.__toggle_difficulty            ,
                             self.__toggle_music_volume          ,
                             self.__toggle_sound_volume          ,
                             partial(self.change_state, MainMenu),
                            )

        self.key_actions  = {
                             K_RETURN: partial(self.__enter_selection,   1),
                             K_LEFT  : partial(self.__enter_selection, -.1),
                             K_RIGHT : partial(self.__enter_selection,  .1),
                             K_UP    : partial(self.__move_cursor    ,  -1),
                             K_DOWN  : partial(self.__move_cursor    ,   1),
                             K_ESCAPE: partial(self.change_state     , MainMenu),
                            }

        HUD.add(self.hud_cursor, self.hud_title)
        MENU.add(a, b)
        GRID_BG.add(bg.EARTH, bg.GRID)
        
    def __del__(self):
        super().__del__()
        settings.save_settings(join(config.DATA_STORE, 'settings.wtf'))

    def render(self):
        self.hud_cursor.rect.midright = self.menu[self.cursor_index][0].rect.midleft
        super().render()
        pygame.display.flip()

    def __enter_selection(self, toggle):
        '''Go with the cursor_index the player made.'''
        config.CURSOR_SELECT.play()
        if self.cursor_index != len(self.menu_actions) - 1:
            self.menu_actions[self.cursor_index](toggle)
        else:
            self.menu_actions[self.cursor_index]()

    def __move_cursor(self, index):
        '''Move the cursor.'''
        #TODO: Put in some animation later
        self.cursor_index += index
        self.cursor_index %= len(self.menu)
        config.CURSOR_BEEP.play()

    def __toggle_fullscreen(self, toggle):
        #toggle doesn't really matter because it's the same both ways
        config.toggle_fullscreen()
        self.menu.fullscreen[1].image = make_text(config.on_off(settings.fullscreen), surfaces=True)

    def __toggle_color_blind_mode(self, toggle=None):
        '''
        Turns Colorblind Mode on or off.  By default it inverts the current
        boolean value, pass in toggle to explicitly assign a value.
        
        @param toggle: The state to change Colorblind mode to.  If None, just
        '''
        config.toggle_color_blind_mode();
        self.menu.colorblind[1].image = make_text(config.on_off(settings.color_blind), surfaces=True)

    def __toggle_difficulty(self, toggle):
        config.toggle_difficulty(int(toggle * 10))
        self.menu.difficulty[1].image = make_text(config.difficulty_string(), surfaces=True)

    def __toggle_music_volume(self, delta_volume):
        settings.music_volume += delta_volume
        settings.music_volume = round(settings.music_volume % 1.1, 1)
        pygame.mixer.music.set_volume(settings.music_volume)
        self.menu.musicvolume[1].image = make_text(config.percent_str(settings.music_volume), surfaces=True)
        
    def __toggle_sound_volume(self, delta_volume):
        settings.sound_volume += delta_volume
        settings.sound_volume = round(settings.sound_volume % 1.1, 1)
        config.set_volume()
        
        self.menu.effectsvolume[1].image = make_text(config.percent_str(settings.sound_volume), surfaces=True)
