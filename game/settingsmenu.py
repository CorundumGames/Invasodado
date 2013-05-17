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
from core           import settings

from game           import bg
from game.hudobject import make_text
from game.menustate import MenuState

### Groups #####################################################################
HUD  = Group()
MENU = Group()
GRID_BG   = OrderedUpdates()
################################################################################

### Constants ##################################################################
DIST_APART = 36
#How far apart, vertically, the menu entries are (in pixels)

DIST_APART_STATUS = 384
#How far apart, horizontally, the status of a menu entry is from the menu entry

MENU_CORNER    = (32, 64)

#The location of the top-left corner of the menu
SETTINGS_FIELDS = 'fullscreen colorblind settings musicvolume effectsvolume clearscores cleardata back'
SETTINGS_KEYS   = namedtuple('Settings', SETTINGS_FIELDS)
TITLE_LOCATION  = (config.SCREEN_RECT.centerx - 64, 32)
################################################################################

### Preparation ################################################################
del SETTINGS_FIELDS
################################################################################

class SettingsMenu(MenuState):
    def __init__(self):
        from game.mainmenu import MainMenu
        super().__init__()
        self.cursor_index = 0
        self.group_list   = (bg.STARS_GROUP, GRID_BG, HUD, MENU)
        self.hud_title    = None

        self.__make_text()

        self.menu_actions = (
                             self.__toggle_fullscreen            ,
                             self.__toggle_color_blind_mode      ,
                             self.__change_language,
                             self.__toggle_music_volume          ,
                             self.__toggle_sound_volume          ,
                             lambda x: None,
                             lambda x: None,
                             lambda x: self.change_state(MainMenu),
                            ) #The lambda is so we can throw away the toggle parameter

        self.key_actions  = {
                             K_RETURN: partial(self._enter_selection,   1),
                             K_LEFT  : partial(self._enter_selection, -.1),
                             K_RIGHT : partial(self._enter_selection,  .1),
                             K_UP    : partial(self._move_cursor    ,  -1),
                             K_w     : partial(self._move_cursor    ,  -1),
                             K_DOWN  : partial(self._move_cursor    ,   1),
                             K_s     : partial(self._move_cursor    ,   1),
                             K_ESCAPE: partial(self.change_state    , MainMenu),
                            }

        HUD.add(self.hud_cursor)

        GRID_BG.add(bg.EARTH, bg.GRID)
        
    def __del__(self):
        super().__del__()
        settings.save_settings(join(config.DATA_STORE, 'settings.wtf'))

    def render(self):
        self.hud_cursor.rect.midright = self.menu[self.cursor_index][0].rect.midleft
        super().render()
        
    def __make_text(self):
        MENU.empty()
        
        text = config.load_text("settings", settings.get_language_code())
        a = make_text(text[4:], pos=MENU_CORNER, vspace=DIST_APART)

        b = make_text(
                      (
                       config.on_off(settings.SETTINGS['fullscreen']),
                       config.on_off(settings.SETTINGS['color_blind']),
                       settings.get_language_name(),
                       config.percent_str(settings.SETTINGS['music_volume']),
                       config.percent_str(settings.SETTINGS['sound_volume']),
                       "",
                       "",
                       ""
                       ),
                      pos=(MENU_CORNER[0] + DIST_APART_STATUS, MENU_CORNER[1]),
                      vspace=DIST_APART
                     )
        a[-1].center()

        self.hud_title = make_text(text[0], TITLE_LOCATION).center()
        MENU.add(self.hud_title, a, b)
        self.menu = SETTINGS_KEYS(*zip(a, b))
        
        #first value is the menu entry, second value is its setting


    def __toggle_fullscreen(self, toggle):
        #toggle doesn't really matter because it's the same both ways
        config.toggle_fullscreen()
        self.__change_image(self.menu.fullscreen, config.on_off(settings.SETTINGS['fullscreen']))

    def __toggle_color_blind_mode(self, toggle=None):
        '''
        Turns Colorblind Mode on or off.  By default it inverts the current
        boolean value, pass in toggle to explicitly assign a value.
        
        @param toggle: The state to change Colorblind mode to.  If None, just
        '''
        settings.toggle_color_blind_mode();
        self.__change_image(self.menu.colorblind, config.on_off(settings.SETTINGS['color_blind']))

    def __toggle_music_volume(self, delta_volume):
        settings.SETTINGS['music_volume'] += delta_volume
        settings.SETTINGS['music_volume'] = round(settings.SETTINGS['music_volume'] % 1.1, 1)
        pygame.mixer.music.set_volume(settings.SETTINGS['music_volume'])
        self.__change_image(self.menu.musicvolume, config.percent_str(settings.SETTINGS['music_volume']))
        
    def __toggle_sound_volume(self, delta_volume):
        settings.SETTINGS['sound_volume'] += delta_volume
        settings.SETTINGS['sound_volume'] = round(settings.SETTINGS['sound_volume'] % 1.1, 1)
        config.set_volume()
        
        self.__change_image(self.menu.effectsvolume, config.percent_str(settings.SETTINGS['sound_volume']))
        
    def __change_language(self, lang_id):
        settings.SETTINGS['language_id'] = int(settings.SETTINGS['language_id'] + lang_id * 10)
        settings.SETTINGS['language_id'] %= len(settings.LANGUAGES)
        settings.set_language(settings.get_language_code())
        self.__make_text()
        
    def __confim_delete(self, position):
        pass
        
    def __change_image(self, menu_entry, new_text):
        '''
        Helper method to change a menu entry's text surface.
        
        @param menu_entry: The menu entry HudObject to change
        @param new_text: The text to change menu_entry to
        '''
        menu_entry[1].image = make_text(new_text, surfaces=True)
