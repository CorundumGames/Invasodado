from os.path   import join
from functools import partial
from string    import ascii_letters, digits

import pygame
from pygame.sprite import Group, OrderedUpdates

from core                import color
from core                import config
from core.gamestate      import GameState
from core.highscoretable import HighScoreTable, HighScoreEntry
from game                import bg
from game.hudobject      import HudObject

### Groups #####################################################################
BG   = OrderedUpdates()
MENU = Group()
################################################################################

### Constants ##################################################################
ALPHANUMERIC   = ''.join((ascii_letters, digits, '_-\'#<'))
CHAR_LIMIT     = 20
DEFAULTS       = ('norm_default.json', '2_default.json', '5_default.json')
ENTRY_NAME_POS = (0, config.SCREEN_HEIGHT - 32)
NO_ENTRY       = "Loser"
ROW_WIDTH      = 32
SCORE_FORMAT   = "{:.<24}.{:.>7}"
SCORE_TABLE_X  = (config.SCREEN_RECT.midtop[0] - 64, 16)
TABLE_CORNER   = (16, 64)
TITLES         = ("Normal Mode", "2 Minutes", "5 Minutes")
V_SPACE        = 24
################################################################################

### Globals ####################################################################
f = partial(join, 'save')
score_tables  = (
                 HighScoreTable(f('0.wtf'),  -1, 10, TITLES[0], f(DEFAULTS[0])),
                 HighScoreTable(f('2.wtf'), 120, 10, TITLES[1], f(DEFAULTS[1])),
                 HighScoreTable(f('5.wtf'), 300, 10, TITLES[2], f(DEFAULTS[2])),
                )
score_table_dict = {-1:0, 120:1, 300:2}
del f
################################################################################

### Functions ##################################################################
def make_score_table(table, pos, vspace, width, surfaces=False):
    '''
    Creates a visual representation of a high score table.
    @rtype: pygame.Surfaces if surfaces else HudObjects
    @return: Graphical representations of high scores

    @param table: The HighScoreTable to take the scores from
    @param pos: The position of the top-left corner
    @param vspace: The vertical space between each line in pixels
    @param width: The width of the table in characters
    '''
    scores = [SCORE_FORMAT.format(i.name, i.score) for i in table.get_scores()]
    return HudObject.make_text(scores, TABLE_CORNER, color.WHITE, config.FONT, V_SPACE, surfaces)
################################################################################

class HighScoreState(GameState):
    def __init__(self, *args, **kwargs):
        self.entering_name = False
        self.kwargs        = kwargs
        self.key_actions = {
                            pygame.K_LEFT  : partial(self.__switch_table, -1),
                            pygame.K_RIGHT : partial(self.__switch_table,  1),
                            pygame.K_UP    : partial(self.__char_move   ,  1),
                            pygame.K_DOWN  : partial(self.__char_move   , -1),
                            pygame.K_RETURN: self.__enter_char               ,
                            pygame.K_ESCAPE: partial(self.change_state, kwargs['next']),
                           }
        self.hud_titles = tuple(HudObject.make_text(score_tables[i].title, SCORE_TABLE_X) for i in range(3))
        self.hud_scores = tuple(make_score_table(score_tables[i], (0, 0), 8, ROW_WIDTH) for i in range(3))
        self.group_list = (bg.STARS_GROUP, BG, MENU)
        self._mode      = kwargs['mode'] if 'mode' in kwargs else -1
        self.current_table = score_table_dict[self._mode]
        if 'score' in self.kwargs:
        #If we just finished a game...
            if self.kwargs['score'] > score_tables[score_table_dict[self._mode]].lowest_score():
            #If we just got a high score...
                self.alphanum_index = 0
                self.entering_name  = True
                self.entry_name     = bytearray('A', config.ENCODING)
                self.hud_name       = HudObject.make_text(self.entry_name.decode(), ENTRY_NAME_POS)
                self.name_index     = 0
                MENU.add(self.hud_name)
            config.play_music('score.ogg')
            
        MENU.add(self.hud_scores[score_table_dict[self._mode]], self.hud_titles[score_table_dict[self._mode]])
        BG.add(bg.EARTH, bg.GRID)

    def render(self):  
        if self.entering_name:
        #If we're entering our name for a high score...
            self.hud_name.image = HudObject.make_text(self.entry_name.decode(config.ENCODING), surfaces=True)

        GameState.render(self)
        pygame.display.flip()

    def __char_move(self, index):
        if self.entering_name:
        #If we're entering our name for a high score...
            self.alphanum_index += index
            self.alphanum_index %= len(ALPHANUMERIC)
            self.entry_name[self.name_index] = ord(ALPHANUMERIC[self.alphanum_index])

    def __switch_table(self, index):
        '''
        Move between the three tables, but not if you're entering a high score.
        '''
        if not self.entering_name:
        #If we're not currently entering our name...
            scores, titles = self.hud_scores, self.hud_titles
            MENU.remove(scores[self.current_table], titles[self.current_table])
            self.current_table += index
            self.current_table %= len(self.hud_scores)
            MENU.add(scores[self.current_table], titles[self.current_table])

    def __enter_char(self):
        
        if self.entering_name and self.name_index < CHAR_LIMIT:
        #If we're entering our name for a high score and it's not too long...
            if ALPHANUMERIC[self.alphanum_index] == '<':
                if len(self.entry_name) > 1:              
                    self.entry_name.pop()
                self.entry_name.pop()
                self.name_index = max(self.name_index - 1, 0)
            elif ALPHANUMERIC[self.alphanum_index] == '_':
                self.entry_name[self.name_index] = ' '
                self.name_index = min(self.name_index + 1, CHAR_LIMIT - 1)
            elif ALPHANUMERIC[self.alphanum_index] == '#':
                if self.entry_name:
                    #Pops off the #
                    self.entry_name.pop()
                    self.__enter_score()
                else:
                    self.entry_name = bytearray(NO_ENTRY)
                return
            else:
                self.name_index = min(self.name_index + 1, CHAR_LIMIT - 1)
                
            self.alphanum_index = 0
            self.entry_name    += bytes('A', config.ENCODING)
        elif self.entering_name:
        #If we've finished entering our name...
            self.__enter_score()
            
    def __enter_score(self):
        self.entering_name = False
        self.hud_name.kill()#Get rid of the name entry characters
        score_tables[self.current_table].add_score(HighScoreEntry(self.entry_name.decode(), self.kwargs['score'], self._mode))#add the entry to the leaderboard
        MENU.remove(self.hud_scores)#remove the menu from the screen
        self.hud_scores = make_score_table(score_tables[self.current_table], (0, 0), 8, ROW_WIDTH)#update the menu with the new entry
        MENU.add(self.hud_scores)#add the menu back to the screen with the updated entry
