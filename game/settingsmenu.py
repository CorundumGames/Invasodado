from functools import partial

import pygame.display
import pygame.sprite

from core import color
from core import config
from core import gamestate
from core import settings

import bg
import mainmenu
from hudobject import HudObject

'''
This is a menu that lets the user change settings within the game.
'''

HUD  = pygame.sprite.Group()
MENU = pygame.sprite.Group()
BG   = pygame.sprite.OrderedUpdates()

DIST_APART = 64
#How far apart, vertically, the menu entries are (in pixels)
DIST_APART_STATUS = 320
#How far apart, horizontally, the status of a menu entry is from the menu entry

MENU_CORNER = (32, 64)
#The location of the top-left corner of the menu

class SettingsMenu(gamestate.GameState):
    def __init__(self):
        f = HudObject.make_text
        self.group_list = [bg.STARS_GROUP, BG, HUD, MENU]

        self.hud_title     = f("Settings", (config.SCREEN_RECT.centerx - 64, 32))
        self.hud_selection = f("->", (0, 0))


        self.menu_keys = ['fullscreen', 'colorblind', 'difficulty', 'back']

        a = f(["Full-Screen", "Colorblind Mode", "Difficulty", "Back",],
              pos = MENU_CORNER,
              vspace = DIST_APART
              )

        b = f(["On" if settings.fullscreen else "Off", "Off", "Easy"],
               pos = [MENU_CORNER[0] + DIST_APART_STATUS, MENU_CORNER[1]],
               vspace = DIST_APART
               )

        self.menu          = dict(zip(self.menu_keys, a))
        self.menu_settings = dict(zip(self.menu_keys, b))

        self.frame_limit = True
        #True if we're limiting the frame rate to 60 FPS


        self.menu_actions = [
                             self.__toggle_fullscreen            ,
                             self.__toggle_color_blind_mode      ,
                             self.__toggle_difficulty            ,
                             partial(self.change_state, mainmenu.MainMenu),
                             ]

        self.key_actions  = {
                             pygame.K_RETURN : self.__enter_selection              ,
                             pygame.K_UP     : partial(self.__move_cursor, -1)     ,
                             pygame.K_DOWN   : partial(self.__move_cursor,  1)     ,
                             pygame.K_ESCAPE : partial(self.change_state, mainmenu.MainMenu),
                             }

        self.selection    = 0

        HUD.add(self.hud_selection, self.hud_title)
        MENU.add(self.menu.values(), self.menu_settings.values())
        BG.add(bg.EARTH, bg.GRID)

    def __del__(self):
        map(pygame.sprite.Group.empty, self.group_list)
        del self.group_list

    def events(self, events):
        for e in events:
        #For all input we've received...
            if e.type == pygame.KEYDOWN and e.key in self.key_actions:
            #If a key was pressed...
                self.key_actions[e.key]()
                self.selection %= len(self.menu)

    def logic(self):
        map(pygame.sprite.Group.update, self.group_list)

    def render(self):
        pygame.display.get_surface().fill((0, 0, 0))

        self.hud_selection.rect.midright = self.menu[self.menu_keys[self.selection]].rect.midleft

        bg.STARS.emit()
        map(pygame.sprite.Group.draw, self.group_list, [pygame.display.get_surface()]*len(self.group_list))

        pygame.display.flip()
        pygame.display.set_caption("FPS: %f" % round(self.fps_timer.get_fps(), 3))

        self.fps_timer.tick(60 * self.frame_limit)

    def __enter_selection(self):
        '''Go with the selection the player made.'''
        self.menu_actions[self.selection]()

    def __move_cursor(self, index):
        '''Move the cursor.'''
        #There should probably be some animation here later.
        self.selection += index

    def __toggle_fullscreen(self):
        config.toggle_fullscreen()
        self.menu_settings['fullscreen'].image = HudObject.make_text("On" if settings.fullscreen else "Off", surfaces = True)

    def __toggle_color_blind_mode(self):
        pass

    def __toggle_difficulty(self):
        pass