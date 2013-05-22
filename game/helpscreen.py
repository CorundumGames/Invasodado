from functools import partial

import pygame.display
from pygame.constants import *
from pygame.sprite    import Group, OrderedUpdates

from core           import config
from core           import settings
from core import color
from game           import bg
from game.menustate import MenuState
from game.hudobject import make_text, HudObject
from game           import enemy
from game import player
from game import ufo
from game import block

### Groups #####################################################################
GRID_BG = OrderedUpdates()
TEXT    = Group()
SPRITES = Group()
################################################################################

### Constants ##################################################################
'''
@var DIST_APART: Vertical distance between text lines in pixels
@var TOP_LEFT: Coordinates of the top-left of the text, in pixels
'''
ALIEN_DIST = 12
DIST_APART = 24
TOP_LEFT   = (16, 32)
################################################################################

class HelpScreen(MenuState):
    def __init__(self, *args, **kwargs):
        ALIEN_FRAMES = enemy.ENEMY_FRAMES_COLOR_BLIND if settings.SETTINGS['color_blind'] else enemy.ENEMY_FRAMES
        BLOCK_FRAMES = block._block_frames_color_blind if settings.SETTINGS['color_blind'] else block._block_frames
        go_back = partial(self.change_state, kwargs['next'])
        
        self.group_list = (bg.STARS_GROUP, GRID_BG, TEXT, SPRITES)
        self.key_actions = {
                            K_ESCAPE : go_back,
                            K_SPACE  : go_back,
                            K_RETURN : go_back,
                           }
        self.aliens   = [HudObject(ALIEN_FRAMES[id(color.LIST[i])][0], [176 + (32 + ALIEN_DIST) * i, 24]) for i in range(len(color.LIST))]
        self.blocks   = [HudObject(BLOCK_FRAMES[id(color.LIST[i])][-1], [176 + (32 + ALIEN_DIST) * i, 72]) for i in range(len(color.LIST))]
        player.FRAMES[0].set_alpha(255)
        self.ship     = HudObject(player.FRAMES[0], (176, 120))

        self.hud_text = make_text(config.load_text('help', settings.get_language_code()), pos=TOP_LEFT, vspace=DIST_APART)
        self.hud_text[-1].center()
        SPRITES.add(self.aliens, self.blocks, self.ship)
        TEXT.add(self.hud_text)
        GRID_BG.add(bg.EARTH, bg.GRID)
        
    def render(self):
        super().render()
        pygame.display.flip()