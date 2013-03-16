'''
This is where the user makes his decisions about what to do in the game.
Not really special compared to any other main menu.
'''

from functools import partial
from os.path import join
from sys import exit

import pygame.event
from pygame.constants import *
from pygame        import display
from pygame.sprite import Group, OrderedUpdates

from core           import config
from core.gamestate import GameState

from game              import bg
from game.ingame       import InGameState
from game.highscore    import HighScoreState
from game.hudobject    import make_text
from game.settingsmenu import SettingsMenu

### Groups #####################################################################
HUD  = Group()
MENU = Group()
GRID_BG   = OrderedUpdates()
################################################################################

### Constants ##################################################################
DIST_APART = 40
#How far apart, vertically, the menu entries are (in pixels)

MENU_CORNER  = (config.SCREEN_RECT.centerx-112, config.SCREEN_RECT.centery-80)
MENU_ENTRIES = config.load_text('menu')
TITLE_POS    = (config.SCREEN_RECT.centerx - 96, 32)
################################################################################

class MainMenu(GameState):
    def __init__(self):
        self.cursor_index = 0
        self.group_list   = (bg.STARS_GROUP, GRID_BG, HUD, MENU)

        self.hud_title  = make_text("Invasodado", TITLE_POS)
        self.cursor_moving = False
        self.hud_cursor = make_text("->", (0, 0))

        self.menu = make_text(MENU_ENTRIES, pos=MENU_CORNER, vspace=DIST_APART)

        self.menu_actions = (
                             partial(self.change_state, InGameState          ),
                             partial(self.change_state, InGameState, time=120),
                             partial(self.change_state, InGameState, time=300),
                             partial(self.change_state, HighScoreState, next = MainMenu),
                             lambda: None,
                             partial(self.change_state, SettingsMenu         ),
                             lambda: None,
                             exit                                             ,
                            )

        self.key_actions  = {
                             K_RETURN : self.__enter_selection         ,
                             K_SPACE  : self.__enter_selection         ,
                             K_UP     : partial(self.__move_cursor, -1),
                             K_DOWN   : partial(self.__move_cursor,  1),
                             K_ESCAPE : exit                           ,
                            }
        
        HUD.add(self.hud_title, self.hud_cursor)
        MENU.add(self.menu)
        GRID_BG.add(bg.EARTH, bg.GRID)
        
        config.play_music('title.ogg')

    def render(self):
        self.hud_cursor.rect.midright = self.menu[self.cursor_index].rect.midleft    
        super().render()
        pygame.display.flip()

    def __move_cursor(self, index):
        '''
        Move the cursor.
        
        @param index: How many menu positions the cursor should be moved by.
        '''
        #TODO: Throw in some animation
        self.cursor_index += index
        self.cursor_index %= len(self.menu_actions)
        config.CURSOR_BEEP.play()
        
    def __enter_selection(self):
        '''
        I can't just put "self.menu_actions[self.cursor_index]" in
        self.key_actions because it'll store self.menu_actions[0], and then only
        one menu item will actually be executed.
        '''
        config.CURSOR_SELECT.play()
        self.menu_actions[self.cursor_index]()
