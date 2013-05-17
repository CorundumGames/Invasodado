from functools import partial
from random    import choice
from string    import digits

import pygame
from pygame.constants import *
from pygame.sprite    import Group, OrderedUpdates

from core                import config
from core.highscoretable import HighScoreTable, HighScoreEntry
from core                import settings
from game                import bg
from game.default_scores import DEFAULT_HIGH_SCORES
from game.hudobject      import make_text
from game.menustate      import MenuState
from game.names          import NAMES

### Groups #####################################################################
GRID_BG = OrderedUpdates()
MENU    = Group()
################################################################################

### Constants ##################################################################
ALPHABET            = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
BACK_CHAR           = '\u2190' #Left arrow
UP_ARROW            = '\u2191' #Up arrow
DOWN_ARROW          = '\u2193' #Down arrow
BLANK_CHAR          = '\u2192' #Right arrow
DONE_CHAR           = '\u0180' #Normally a special b, but I modified it to say 'OK'
CHAR_LIMIT          = 20
DEFAULTS            = DEFAULT_HIGH_SCORES
ENTRY_NAME_POS      = (32, config.SCREEN_HEIGHT - 32)
OK_CHARS            = ''.join((ALPHABET, digits, BLANK_CHAR, '-\'', DONE_CHAR, BACK_CHAR))
ROW_WIDTH           = 32
SCORE_FORMAT        = "{:.<24}.{:.>7}"
SCORE_TABLE_X       = (config.SCREEN_RECT.midtop[0] - 64, 16)
INSTRUCTIONS_X      = (32 , 10 * 32)
INSTRUCT_DIST_APART = 40
TABLE_CORNER        = (16, 64)
V_SPACE             = 24
################################################################################

### Globals ####################################################################
score_tables  = (
                 HighScoreTable('0.wtf',  -1, 10, DEFAULTS[0]),
                 HighScoreTable('2.wtf', 120, 10, DEFAULTS[1]),
                 HighScoreTable('5.wtf', 300, 10, DEFAULTS[2]),
                )
score_table_dict = {-1:0, 120:1, 300:2}
del DEFAULTS
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
    scores = tuple(SCORE_FORMAT.format(i.name, i.score) for i in table.scores)
    return tuple(j.center() for j in make_text(scores, TABLE_CORNER, font=config.FONT, vspace=V_SPACE, surfaces=surfaces))

def _make_tables():
    return tuple(make_score_table(score_tables[i], (0, 0), 8, ROW_WIDTH) for i in range(3))
################################################################################

class HighScoreState(MenuState):
    def __init__(self, *args, **kwargs):
        super().__init__()
        titles = config.load_text('menu', settings.get_language_code())[2:5]
        
        self._mode         = kwargs['mode'] if 'mode' in kwargs else -1
        self.current_table = score_table_dict[self._mode]
        self.entering_name = False
        self.key_actions = {
                            K_LEFT  : partial(self.__switch_table, -1),
                            K_RIGHT : partial(self.__switch_table,  1),
                            K_UP    : partial(self.__char_move   ,  1),
                            K_w     : partial(self.__char_move   ,  1),
                            K_DOWN  : partial(self.__char_move   , -1),
                            K_s     : partial(self.__char_move   , -1),
                            K_RETURN: self.__enter_char               ,
                            K_SPACE : self.__enter_char               ,
                            K_ESCAPE: partial(self.change_state, kwargs['next']),
                           }
        self.group_list    = (bg.STARS_GROUP, GRID_BG, MENU)
        self.hud_titles    = tuple(make_text(i, SCORE_TABLE_X).center() for i in titles)
        self.hud_scores    = _make_tables()

        if 'score' in kwargs:
        #If we just finished a game...
            if kwargs['score'] > score_tables[score_table_dict[self._mode]].lowest_score():
            #If we just got a high score...
                self.instructions = make_text(
                                              config.load_text('highscore', settings.get_language_code()),
                                              pos=INSTRUCTIONS_X,
                                              vspace=INSTRUCT_DIST_APART
                                             )
                self._score          = kwargs['score']
                self.alphanum_index  = 0
                self.entering_name   = True
                self.entry_name      = ['A']
                self.hud_name        = make_text(''.join(self.entry_name), ENTRY_NAME_POS)
                self.last_entry_name = self.entry_name
                self.name_index      = 0
                MENU.add(self.instructions, self.hud_name)
            
            config.play_music('score.ogg')
            #Whether or not we got a high score, play the special music.
        
        m = score_table_dict[self._mode]
        MENU.add(self.hud_scores[m], self.hud_titles[m])
        GRID_BG.add(bg.EARTH, bg.GRID)

    def render(self):  
        if self.entering_name and (self.entry_name != self.last_entry_name):
        #If we're entering our name for a high score...
            self.hud_name.image = make_text(''.join(self.entry_name), surfaces=True)
        super().render()

    def __char_move(self, index):
        if self.entering_name:
        #If we're entering our name for a high score...
            config.CURSOR_BEEP.play()
            self.last_entry_name = list(self.entry_name)
            self.alphanum_index += index
            self.alphanum_index %= len(OK_CHARS)
            self.entry_name[self.name_index] = OK_CHARS[self.alphanum_index]

    def __switch_table(self, index):
        '''
        Move between the three tables, but not if you're entering a high score.
        '''
        if not self.entering_name:
        #If we're not currently entering our name...
            config.CURSOR_BEEP.play()
            scores, titles = self.hud_scores, self.hud_titles
            MENU.remove(scores[self.current_table], titles[self.current_table])
            self.current_table += index
            self.current_table %= len(score_tables)
            MENU.add(scores[self.current_table], titles[self.current_table])

    def __enter_char(self):
        if self.entering_name and self.name_index < CHAR_LIMIT:
        #If we're entering our name for a high score and it's not too long...
            config.CURSOR_SELECT.play()
            if OK_CHARS[self.alphanum_index] == BACK_CHAR:
            #If we're erasing a character...
                if len(self.entry_name) > 1:
                #If there are any characters to erase...           
                    self.entry_name.pop()
                self.entry_name.pop()
                self.name_index  = max(self.name_index - 1, 0)
                self.entry_name += [BACK_CHAR]
                return
            elif OK_CHARS[self.alphanum_index] == BLANK_CHAR:
            #Else if we want to mark down a space...
                self.entry_name[self.name_index] = ' '
                self.name_index = min(self.name_index + 1, CHAR_LIMIT - 1)
            elif OK_CHARS[self.alphanum_index] == DONE_CHAR:
            #Else if we're done...
                if len(self.entry_name) > 1:   
                    self.entry_name.pop() #Pops off the end character      
                else:
                    self.entry_name = list(choice(NAMES))
                self.__enter_score()
                return
            else:
            #Else if this character is an ordinary letter...
                self.name_index = min(self.name_index + 1, CHAR_LIMIT - 1)
                
            self.alphanum_index = 0
            self.entry_name    += ['A'] if len(self.entry_name) < CHAR_LIMIT else []
        elif self.entering_name:
        #If we've finished entering our name...
            self.__enter_score()
            
    def __enter_score(self):
        config.CURSOR_SELECT.play()
        score = [HighScoreEntry(''.join(self.entry_name), self._score, self._mode)]
        self.entering_name = False
        self.key_actions[K_SPACE] = self.key_actions[K_ESCAPE]
        self.hud_name.kill()  #Get rid of the name entry characters
        score_tables[self.current_table].add_scores(score)#add the entry to the leaderboard
        MENU.remove(self.hud_scores, self.instructions)
        self.hud_scores = _make_tables()
        MENU.add(self.hud_scores[self.current_table])#add the menu back to the screen with the updated entry
