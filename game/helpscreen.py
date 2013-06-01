from functools import partial
from random import choice

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
ALIEN_DIST = 12 + enemy.ENEMY_FRAMES[id(color.RED)][0].get_width()
ALIEN_Y    = 24
BLOCK_Y    = 72
DIST_APART = 24
TOP_LEFT   = (16, 32)
################################################################################

### Sprite Positions ###########################################################
'''
Due to the differences in language, different translations of this help screen
will have text of varying verbosity.
'''
ALIEN_BLOCK_POS = {
    'en' : lambda i: 176 + ALIEN_DIST * i,
    'es' : lambda i: 180 + ALIEN_DIST * i,
}

SHIP_POS = {
    'en' : (176, 120),
    'es' : (100, 120),
}

UFO_POS = {
    'en' : (400, 384),
    'es' : (100, 384),
}
################################################################################

class HelpScreen(MenuState):
    def __init__(self, *args, **kwargs):
        ### Local Variables ####################################################
        ALIEN_FRAMES = enemy.ENEMY_FRAMES_COLOR_BLIND if settings.SETTINGS['color_blind'] else enemy.ENEMY_FRAMES
        BLOCK_FRAMES = block._block_frames_color_blind if settings.SETTINGS['color_blind'] else block._block_frames
        go_back      = partial(self.change_state, kwargs['next'])
        langcode     = settings.get_language_code()
        AB           = ALIEN_BLOCK_POS[langcode]
        ########################################################################
        
        ### Object Attributes ##################################################
        self.group_list = (bg.STARS_GROUP, GRID_BG, TEXT, SPRITES)
        self.key_actions = {
                            K_ESCAPE : go_back,
                            K_SPACE  : go_back,
                            K_RETURN : go_back,
                           }
        
        self.aliens = (HudObject(ALIEN_FRAMES[id(color.LIST[i])][ 0], (AB(i), ALIEN_Y)) for i in range(len(color.LIST)))
        self.blocks = (HudObject(BLOCK_FRAMES[id(color.LIST[i])][-1], (AB(i), BLOCK_Y)) for i in range(len(color.LIST)))
        self.ship   = HudObject(player.FRAMES[0], SHIP_POS[langcode])
        self.ufo    = HudObject(ufo.UFO_FRAMES[id(choice(color.LIST))][0], UFO_POS[langcode])
        
        
        self._ufoanim = 0.0
        self.hud_text = make_text(config.load_text('help', langcode), pos=TOP_LEFT, vspace=DIST_APART)
        ########################################################################
        
        ### Preparation ########################################################
        player.FRAMES[0].set_alpha(255)
        self.hud_text[-1].center()
        SPRITES.add(self.aliens, self.blocks, self.ship, self.ufo)
        TEXT.add(self.hud_text)
        GRID_BG.add(bg.EARTH, bg.GRID)
        ########################################################################
        
    def render(self):
        super().render()
        self._ufoanim  += 0.5
        self.ufo.image  = ufo.UFO_FRAMES[id(choice(color.LIST))][int(self._ufoanim) % len(ufo.FRAMES)]
        
        pygame.display.flip()