'''
This is where the user makes his decisions about what to do in the game.
Not really special compared to any other main menu.
'''

from functools import partial
from os.path import join

import pygame.event
from pygame        import display
from pygame.sprite import Group, OrderedUpdates

from core           import config
from core.gamestate import GameState

from game              import bg
from game.ingame       import InGameState
from game.highscore    import HighScoreState
from game.hudobject    import HudObject
from game.settingsmenu import SettingsMenu

### Groups #####################################################################
HUD  = Group()
MENU = Group()
BG   = OrderedUpdates()
################################################################################

### Constants ##################################################################
DIST_APART = 48
#How far apart, vertically, the menu entries are (in pixels)

MENU_CORNER  = (config.SCREEN_RECT.centerx-112, config.SCREEN_RECT.centery-64)
MENU_ENTRIES = ("Normal Mode", "2 Minutes", "5 Minutes", "High Scores", "Settings", "Quit")
TITLE_POS    = (config.SCREEN_RECT.centerx - 96, 32)
################################################################################

class MainMenu(GameState):
    def __init__(self):
        make_text = HudObject.make_text
        
        self.cursor_index = 0
        self.group_list   = (bg.STARS_GROUP, BG, HUD, MENU)

        self.hud_title  = make_text("Invasodado", TITLE_POS)

        self.hud_cursor = make_text("->", (0, 0))

        self.menu = make_text(MENU_ENTRIES, pos=MENU_CORNER, vspace=DIST_APART)

        self.menu_actions = (
                             partial(self.change_state, InGameState          ),
                             partial(self.change_state, InGameState, time=120),
                             partial(self.change_state, InGameState, time=300),
                             partial(self.change_state, HighScoreState, next = MainMenu),
                             partial(self.change_state, SettingsMenu         ),
                             quit                                             ,
                            )

        self.key_actions  = {
                             pygame.K_RETURN : self.__enter_selection         ,
                             pygame.K_UP     : partial(self.__move_cursor, -1),
                             pygame.K_DOWN   : partial(self.__move_cursor,  1),
                             pygame.K_ESCAPE : quit                           ,
                            }
        
        HUD.add(self.hud_title, self.hud_cursor)
        MENU.add(self.menu)
        BG.add(bg.EARTH, bg.GRID)
        
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
        self.menu_actions[self.cursor_index]()
