'''
This is where the user makes his decisions about what to do in the game.
Not really special compared to any other main menu.
'''

from functools import partial
from os.path import join
from math import sin
from time import time
from sys import exit

import pygame.transform
from pygame.constants import *
from pygame.sprite import Group, OrderedUpdates

from core import color
from core import config
from core import settings

from game              import bg
from game.about        import AboutScreen
from game.ingame       import InGameState
from game.helpscreen   import HelpScreen
from game.highscore    import HighScoreState
from game.hudobject    import make_text, HudObject
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
@var MENU_TOP: y-coordinate of the top of the menu graphic
@var TITLE_TOP: y-coordinate of the top of the title graphic

Since we're centering everything, we really don't need to store the corner
'''
DIST_APART = 36
INSTRUCTION_DIST = 24
MENU_TOP   = config.SCREEN_RECT.top + 144
TITLE_TOP  = 32
TITLE      = HudObject(config.load_image('gamelogo.png'), (0, 0))
################################################################################

### Preparation ################################################################
TITLE.image     = pygame.transform.scale(TITLE.image, (TITLE.image.get_width() // 2, TITLE.image.get_height() // 2))
TITLE.rect.size = TITLE.image.get_size()
TITLE.center().image.set_colorkey(color.BLACK, config.BLIT_FLAGS)
################################################################################

class MainMenu(MenuState):
    def __init__(self, *args, **kwargs):
        super().__init__()
        ### Local Variables ####################################################
        text      = config.load_text('menu', settings.get_language_code())
        to_game   = lambda a=-1: partial(self.change_state, InGameState, time=a)
        to_screen = lambda x   : partial(self.change_state, x, next=MainMenu)
        ########################################################################
        
        ### Object Attributes ##################################################
        self.group_list   = (bg.STARS_GROUP, GRID_BG, HUD, MENU)

        self.instructions = make_text(text[:2], pos=(0, config.SCREEN_HEIGHT - 48), vspace=INSTRUCTION_DIST)
        self.menu = make_text(text[2:], pos=(0, MENU_TOP), vspace=DIST_APART)

        self.menu_actions = (
                            to_game()                ,
                            to_game(120)             ,
                            to_game(300)             ,
                            to_screen(HighScoreState),
                            to_screen(HelpScreen    ),
                            to_screen(SettingsMenu  ),
                            to_screen(AboutScreen   ),
                            exit                     ,
                            )
        ########################################################################
        
        ### Preparation ########################################################
        TITLE.rect.top = TITLE_TOP
        HUD.add(TITLE, self.hud_cursor, (i.center() for i in self.instructions))
        MENU.add(j.center() for j in self.menu)
        GRID_BG.add(bg.EARTH, bg.GRID)
        config.play_music('title.ogg')
        ########################################################################

    def render(self):
        TITLE.rect.top += sin(10 * time()) + .5
        self.hud_cursor.rect.midright = self.menu[self.cursor_index].rect.midleft
        self.hud_cursor.rect.right -= 8
        super().render()
