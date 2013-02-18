from os.path   import join
from functools import partial
from string    import uppercase, lowercase, digits

import pygame
from pygame.sprite import Group, OrderedUpdates

from game import bg
from core import color
from core import config
from core.gamestate import GameState
from core.highscoretable import HighScoreTable, HighScoreEntry
from game.hudobject import HudObject

BG             = OrderedUpdates()
MENU           = Group()

ALPHANUMERIC   = ''.join([uppercase, lowercase, digits, '_-\'#<'])
CHAR_LIMIT     = 20
DEFAULTS       = ['norm_default.json', '2_default.json', '5_default.json']
ENTRY_NAME_POS = (0, config.SCREEN_HEIGHT - 32)
NO_ENTRY       = "Loser"
ROW_WIDTH      = 32
SCORE_FORMAT   = "{:.<24}.{:.>7}"
SCORE_TABLE_X  = (config.SCREEN_RECT.midtop[0] - 64, 16)
TABLE_CORNER   = (16, 64)
TITLES         = ["Normal Mode", "2 Minutes", "5 Minutes"]
V_SPACE        = 24

f = partial(join, 'save')
score_tables  = [
                 HighScoreTable(f('0.wtf'),  -1, 10, TITLES[0], f(DEFAULTS[0])),
                 HighScoreTable(f('2.wtf'), 120, 10, TITLES[1], f(DEFAULTS[1])),
                 HighScoreTable(f('5.wtf'), 300, 10, TITLES[2], f(DEFAULTS[2])),
                ]
del f

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

class HighScoreState(GameState):
    def __init__(self, *args, **kwargs):
        self.current_table = 0
        self.entering_name = False
        print(kwargs)
        self.key_actions = {
                            pygame.K_LEFT  : partial(self.__switch_table, -1),
                            pygame.K_RIGHT : partial(self.__switch_table,  1),
                            pygame.K_UP    : partial(self.__char_move   ,  1),
                            pygame.K_DOWN  : partial(self.__char_move   , -1),
                            pygame.K_RETURN: self.__enter_char               ,
                            pygame.K_ESCAPE: partial(self.change_state, kwargs['next']),
                           }
        self.hud_titles = [HudObject.make_text(score_tables[i].title, SCORE_TABLE_X) for i in range(3)]
        self.hud_scores = [make_score_table(score_tables[i], (0, 0), 8, ROW_WIDTH) for i in range(3)]
        self.group_list = [bg.STARS_GROUP, BG, MENU]
        self._mode      = kwargs['mode'] if 'mode' in kwargs else -1
        
        if 'score' in kwargs and kwargs['score'] > score_tables[self._mode].lowest_score():
        #If we just got a high score...
            self.alphanum_index = 0
            self.entering_name  = True
            self.entry_name     = bytearray('A')
            self.hud_name       = HudObject.make_text(str(self.entry_name), ENTRY_NAME_POS)
            self.name_index     = 0
            MENU.add(self.hud_name)
            
        MENU.add(self.hud_scores[self._mode], self.hud_titles[self._mode])
        BG.add(bg.EARTH, bg.GRID)

    def __del__(self):
        map(Group.empty, self.group_list)
        self.group_list = []

    def events(self, events):
        for e in events:
        #For all input we've received...
            if e.type == pygame.KEYDOWN and e.key in self.key_actions:
            #If a key was pressed...
                self.key_actions[e.key]()

    def logic(self):
        map(Group.update, self.group_list)

    def render(self):
        display = pygame.display
        
        if self.entering_name:
        #If we're entering our name for a high score...
            self.hud_name.image = HudObject.make_text(str(self.entry_name), surfaces=True)

        display.get_surface().fill((0, 0, 0))
        bg.STARS.emit()
        map(Group.draw, self.group_list, [config.screen]*len(self.group_list))

        display.flip()
        assert not display.set_caption("FPS: %f" % round(self.fps_timer.get_fps(), 3))

    def __char_move(self, index):
        if self.entering_name:
        #If we're entering our name for a high score...
            self.alphanum_index += index
            self.alphanum_index %= len(ALPHANUMERIC)
            self.entry_name[self.name_index] = ALPHANUMERIC[self.alphanum_index]

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
            if ALPHANUMERIC[self.alphanum_index] == '<' and self.entry_name:              
                self.entry_name.pop()
                self.name_index = max(self.name_index - 1, 0)
            elif ALPHANUMERIC[self.alphanum_index] == '_':
                self.entry_name[self.name_index] = ' '
                self.name_index = min(self.name_index + 1, CHAR_LIMIT - 1)
            elif ALPHANUMERIC[self.alphanum_index] == '#':
                if self.entry_name:
                    self.__enter_score()
                else:
                    self.entry_name = bytearray(NO_ENTRY)
                return
            else:
                self.name_index = min(self.name_index + 1, CHAR_LIMIT - 1)
                
            self.alphanum_index = 0
            self.entry_name    += 'A'
        elif self.entering_name:
        #If we've finished entering our name...
            self.__enter_score()
            
    def __enter_score(self):
        self.entering_name = False
        self.hud_name.kill()#Get rid of the name entry characters
        score_tables[self.current_table].add_score(HighScoreEntry(str(self.entry_name), self.kwargs['score'], self._mode))#add the entry to the leaderboard
        MENU.remove(self.hud_scores)#remove the menu from the screen
        self.hud_scores = make_score_table(score_tables[self.current_table], (0, 0), 8, ROW_WIDTH)#update the menu with the new entry
        MENU.add(self.hud_scores)#add the menu back to the screen with the updated entry
