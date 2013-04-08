'''
This is where the user makes his decisions about what to do in the game.
Not really special compared to any other main menu.
'''

from functools import partial
from os.path import join
from sys import exit

from pygame.constants import *
import pygame
from pygame.sprite import Group, OrderedUpdates

from core           import config
from core import settings

from game              import bg
from game.about        import AboutScreen
from game.ingame       import InGameState
from game.highscore    import HighScoreState
from game.hudobject    import make_text
from game.menustate    import MenuState
from game.settingsmenu import SettingsMenu

### Groups #####################################################################
HUD     = Group()
MENU    = Group()
GRID_BG = OrderedUpdates()
################################################################################

### Constants ##################################################################
'''
@var DIST_APART: Vertical distance between menu entries, in pixels
@var MENU_CORNER: Location of top-left corner of the main menu graphic
@var TITLE_POS: Top-left corner of the title on-screen
'''
DIST_APART = 40
MENU_CORNER  = (config.SCREEN_RECT.centerx-112, config.SCREEN_RECT.centery-80)
TITLE_POS    = (config.SCREEN_RECT.centerx - 96, 32)
################################################################################

class MainMenu(MenuState):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.group_list   = (bg.STARS_GROUP, GRID_BG, HUD, MENU)

        self.hud_title  = make_text("Invasodado", TITLE_POS)
        self.cursor_moving = False
        self.menu = make_text(config.load_text('menu', settings.get_language_code()), pos=MENU_CORNER, vspace=DIST_APART)

        self.menu_actions = (
                            partial(self.change_state, InGameState          ),
                            partial(self.change_state, InGameState, time=120),
                            partial(self.change_state, InGameState, time=300),
                            partial(self.change_state, HighScoreState, next=MainMenu),
                            lambda: None,
                            partial(self.change_state, SettingsMenu         ),
                            partial(self.change_state, AboutScreen, next=MainMenu),
                            exit                                             ,
                            )
        
        
        HUD.add(self.hud_title, self.hud_cursor)
        MENU.add(self.menu)
        GRID_BG.add(bg.EARTH, bg.GRID)
        
        config.play_music('title.ogg')

    def render(self):
        self.hud_cursor.rect.midright = self.menu[self.cursor_index].rect.midleft
        super().render()
