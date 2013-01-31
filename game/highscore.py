from os.path import join
from functools import partial
import string

import pygame

import bg
import core.color          as color
import core.config         as config
from core.gamestate import GameState
from core.highscoretable import HighScoreTable, HighScoreEntry
import gameobject
from hudobject import HudObject
import mainmenu

BG   = pygame.sprite.OrderedUpdates()
MENU = pygame.sprite.Group()

ALPHANUMERIC   = ''.join([string.uppercase, string.lowercase, string.digits, '_-\' <'])
ENTRY_NAME_POS = (0, config.SCREEN_HEIGHT - 32)
ROW_WIDTH      = 32
TABLE_CORNER   = (16, 64)
V_SPACE        = 24

f = partial(join, 'save')
score_tables  = [
                 HighScoreTable(f('0.wtf'),   0, 10, "Normal Mode", f('norm_default.json')),
                 HighScoreTable(f('2.wtf'), 120, 10, "2 Minutes"  , f('2_default.json'   )),
                 HighScoreTable(f('5.wtf'), 300, 10, "5 Minutes"  , f('5_default.json'   )),
                ]
del f

def make_score_table(table, pos, vspace, width, surfaces = False):
    '''
    Creates a visual representation of a high score table.
    @rtype: pygame.Surfaces if surfaces else HudObjects
    @return: Graphical represntations of high scores

    @param table: The HighScoreTable to take the scores from
    @param pos: The position of the top-left corner
    @param vspace: The vertical space between each line in pixels
    @param width: The width of the table in characters
    '''

    b = ["{:.<24}.{:.>7}".format(i.name, i.score) for i in table.get_scores()]
    return HudObject.make_text(b, TABLE_CORNER, color.WHITE, config.FONT, V_SPACE, surfaces)

class HighScoreState(GameState):
    def __init__(self, *args, **kwargs):

        self.args          = args
        self.current_table = 0

        self.entering_name = False

        self.key_actions = {
                            pygame.K_LEFT   : partial(self.__switch_table, -1),
                            pygame.K_RIGHT  : partial(self.__switch_table,  1),
                            pygame.K_UP     : partial(self.__char_move   ,  1),
                            pygame.K_DOWN   : partial(self.__char_move   , -1),
                            pygame.K_RETURN : self.__enter_char               ,
                            pygame.K_ESCAPE : partial(self.change_state, mainmenu.MainMenu),
                           }

        self.hud_titles   = [HudObject.make_text(score_tables[i].title, (config.SCREEN_RECT.midtop[0] - 64, 16)) for i in range(3)]
        #The list of the titles of high score tables

        self.hud_scores   = [make_score_table(score_tables[i], (0, 0), 8, ROW_WIDTH) for i in range(3)]
        #The graphical display of the scores

        self.group_list   = [bg.STARS_GROUP, BG, MENU]
        self.kwargs = kwargs
        self.mode   = kwargs['mode'] if 'mode' in kwargs else 0

        MENU.add(self.hud_scores[self.mode], self.hud_titles[self.mode])
        BG.add(bg.EARTH, bg.GRID)
        if 'score' in args[0] and args[0]['score'] > score_tables[self.mode].lowest_score():
        #If we just got a high score...
            self.alphanum_index = 0
            self.char_limit     = 20
            self.entering_name  = True
            self.entry_name     = 'A'
            self.hud_name       = HudObject.make_text(self.entry_name, ENTRY_NAME_POS)
            self.name_index     = 0
            MENU.add(self.hud_name)


    def __del__(self):
        map(pygame.sprite.Group.empty, self.group_list)
        self.group_list = []

    def events(self, events):
        for e in events:
        #For all input we've received...
            if e.type == pygame.KEYDOWN and e.key in self.key_actions:
            #If a key was pressed...
                self.key_actions[e.key]()

    def logic(self):
        map(pygame.sprite.Group.update, self.group_list)

    def render(self):
        pd = pygame.display

        if self.entering_name:
        #If we're entering our name for a high score...
            self.hud_name.image = HudObject.make_text(self.entry_name, surfaces = True)

        pygame.display.get_surface().fill((0, 0, 0))
        bg.STARS.emit()
        map(pygame.sprite.Group.draw, self.group_list, [config.screen]*len(self.group_list))

        pd.flip()
        pd.set_caption("FPS: %f" % round(self.fps_timer.get_fps(), 3))

    def __char_move(self, index):
        if self.entering_name:
        #If we're entering our name for a high score...
            self.alphanum_index += index
            self.alphanum_index %= len(ALPHANUMERIC)
            self.entry_name = ''.join([self.entry_name[:self.name_index], ALPHANUMERIC[self.alphanum_index], self.entry_name[self.name_index+1:]])

    def __switch_table(self, index):
        '''
        Move between the three tables, but not if you're entering a high score.
        '''
        if not self.entering_name:
            MENU.remove(self.hud_scores[self.current_table], self.hud_titles[self.current_table])
            self.current_table += index
            self.current_table %= len(self.hud_scores)
            MENU.add(self.hud_scores[self.current_table], self.hud_titles[self.current_table])


    def __enter_char(self):
        self.name_index += 1
        if self.name_index > self.char_limit:
        #If we've finished entering our name...
            self.entering_name = False
            self.hud_name.kill()#Get rid of the name entry characters
            score_tables[self.current_table].add_score(HighScoreEntry(self.entry_name, self.args[0]['score'], self.mode))#add the entry to the leaderboard
            MENU.remove(self.hud_scores)#remove the menu from the screen
            self.hud_scores = make_score_table(score_tables[self.current_table], (0, 0), 8, ROW_WIDTH)#update the menu with the new entry
            MENU.add(self.hud_scores)#add the menu back to the screen with the updated entry
        else:
            self.alphanum_index = 0
            self.entry_name += 'A'