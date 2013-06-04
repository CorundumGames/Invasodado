from functools import partial

import pygame.display
from pygame.constants import *
from pygame.sprite    import Group, OrderedUpdates

from core           import config
from core           import settings
from game           import bg
from game.menustate import MenuState
from game.hudobject import make_text

### Groups #####################################################################
GRID_BG = OrderedUpdates()
TEXT    = Group()
################################################################################

### Constants ##################################################################
'''
@var DIST_APART: Vertical distance between text lines in pixels
@var TOP_LEFT: Coordinates of the top-left of the text, in pixels
'''
DIST_APART = 24
TOP_LEFT   = (16, 16)
################################################################################

class AboutScreen(MenuState):
    def __init__(self, *args, **kwargs):
        go_back = partial(self.change_state, kwargs['next'])
        
        self.group_list = (bg.STARS_GROUP, GRID_BG, TEXT)
        self.key_actions = {
                            K_ESCAPE : go_back,
                            K_SPACE  : go_back,
                            K_RETURN : go_back,
                           }

        self.hud_text = make_text(config.load_text('about', settings.get_language_code()), pos=TOP_LEFT, vspace=DIST_APART)

        TEXT.add(self.hud_text)
        GRID_BG.add(bg.EARTH, bg.GRID)
        for i in (0, 1, -2, -1): self.hud_text[i].center()
        
    def render(self):
        super().render()
        pygame.display.flip()