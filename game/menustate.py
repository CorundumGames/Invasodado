from functools import partial
import sys

import pygame.display
from pygame.constants import *

from core           import config
from core.gamestate import GameState
from game.hudobject import make_text

class MenuState(GameState):
    def __init__(self, *args, **kwargs):
        super().__init__()
        ### Local Variables ####################################################
        cursor_up   = partial(self._move_cursor, -1)
        cursor_down = partial(self._move_cursor,  1)
        ########################################################################
        
        ### Object Attributes ##################################################
        self.cursor_index = 0
        self.hud_cursor   = make_text("->", (0, 0))
        self.menu_actions = ()
        self.key_actions  = {
                             K_RETURN : self._enter_selection ,
                             K_SPACE  : self._enter_selection ,
                             K_UP     : cursor_up             ,
                             K_w      : cursor_up             ,
                             K_DOWN   : cursor_down           ,
                             K_s      : cursor_down           ,
                             K_ESCAPE : sys.exit              ,
                             K_PRINT  : config.take_screenshot,
                             K_F12    : config.take_screenshot,
                             K_SYSREQ : config.take_screenshot,
                            }
        ########################################################################
        
    def render(self):
        super().render()
        pygame.display.flip()
        
    def _move_cursor(self, index):
        '''
        Move the cursor.
        
        @param index: How many menu positions the cursor should be moved by.
        '''
        #TODO: Throw in some animation
        self.cursor_index += index
        self.cursor_index %= len(self.menu_actions)
        config.CURSOR_BEEP.play()
        
    def _enter_selection(self, toggle=None):
        '''
        I can't just put "self.menu_actions[self.cursor_index]" in
        self.key_actions because it'll store self.menu_actions[0], and then only
        one menu item will actually be executed.
        '''
        config.CURSOR_SELECT.play()
        if toggle is None:
            self.menu_actions[self.cursor_index]()
        else:
            self.menu_actions[self.cursor_index](toggle)