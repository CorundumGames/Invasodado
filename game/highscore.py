import string

import pygame

import bg
import core.color          as color
import core.config         as config
import core.gamestate      as gamestate
import core.highscoretable as highscoretable
import gameobject
import hudobject
import mainmenu

BG   = pygame.sprite.OrderedUpdates()
MENU = pygame.sprite.Group()

ALPHANUMERIC   = ''.join([string.letters, string.digits, '_-\' <'])
ENTRY_NAME_POS = (0, config.SCREEN_HEIGHT - 32)
ROW_WIDTH      = 32
TABLE_CORNER   = (16, 64)
V_SPACE        = 24

score_tables  = [
                 highscoretable.HighScoreTable("./save/normal.wtf", 1, 10, "Scores", "./save/norm_default.json")
                 ]

def make_score_table(table, pos, vspace, width, surfaces = False):
    '''
    Creates a visual representation of a high score table.
    Returns a list of HudObjects, or pygame.Surfaces if surfaces is True

    @param table: The HighScoreTable to take the scores from
    @param pos: The position of the top-left corner
    @param vspace: The vertical space between each line in pixels
    @param width: The width of the table in characters
    '''

    b = ["{:.<24}.{:.>7}".format(i.name, i.score) for i in table.get_scores()]
    return hudobject.HudObject.make_text(b, TABLE_CORNER, color.WHITE, config.FONT, V_SPACE, surfaces)

class HighScoreState(gamestate.GameState):
    def __init__(self, *args, **kwargs):

        self.args   = args
        self.kwargs = kwargs

        self.entering_name = False

        self.key_actions = {
                            pygame.K_LEFT   : NotImplemented       ,
                            pygame.K_RIGHT  : NotImplemented       ,
                            pygame.K_UP     : self.__char_up       ,
                            pygame.K_DOWN   : self.__char_down     ,
                            pygame.K_RETURN : self.__enter_char    ,
                            pygame.K_ESCAPE : self.__return_to_menu,
                           }

        self.hud_titles   = [hudobject.HudObject.make_text(score_tables[0].title, (config.SCREEN_RECT.midtop[0] - 64, 16))]
        #The list of the titles of high score tables

        self.hud_scores   = make_score_table(score_tables[0], (0, 0), 8, ROW_WIDTH)
        #The graphical display of the scores

        self.next_state   = None

        self.group_list   = [bg.STARS_GROUP, BG, MENU]

        MENU.add(self.hud_scores, self.hud_titles)
        BG.add(bg.EARTH, bg.GRID)

        try:
        #If we were passed in any arguments...
            if self.kwargs['score'] > score_tables[0].lowest_score():
                self.alphanum_index = 0
                self.char_limit     = 9
                self.entering_name  = True
                self.entry_name     = 'A'
                self.hud_name       = hudobject.HudObject.make_text(self.entry_name, ENTRY_NAME_POS)
                self.name_index     = 0
                MENU.add(self.hud_name)
        except KeyError:
            pass

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
        if self.entering_name:
        #If we're entering our name for a high score...
            self.hud_name.image = hudobject.HudObject.make_text(self.entry_name, surfaces = True)

        pygame.display.get_surface().fill((0, 0, 0))
        bg.STARS.emit()
        map(pygame.sprite.Group.draw, self.group_list, [pygame.display.get_surface()]*len(self.group_list))

        pygame.display.flip()
        pygame.display.set_caption("FPS: %f" % round(self.fps_timer.get_fps(), 3))

    def __char_up(self):
        if self.entering_name:
        #If we're entering our name for a high score...
            self.alphanum_index += 1
            self.__update_name()

    def __char_down(self):
        if self.entering_name:
        #If we're entering our name for a high score...
            self.alphanum_index -= 1
            self.__update_name()

    def __update_name(self):
        self.alphanum_index %= len(ALPHANUMERIC)
        self.entry_name = ''.join([self.entry_name[:self.name_index], ALPHANUMERIC[self.alphanum_index], self.entry_name[self.name_index+1:]])

    def __enter_char(self):
        self.name_index += 1
        if self.name_index > self.char_limit:
        #If we've finished entering our name...
            self.entering_name = False
            self.hud_name.kill()#Get rid of the name entry characters
            score_tables[0].add_score(highscoretable.HighScoreEntry(self.entry_name, self.args[0], 1))#add the entry to the leaderboard
            MENU.remove(self.hud_scores)#remove the menu from the screen
            self.hud_scores = make_score_table(score_tables[0], (0, 0), 8, ROW_WIDTH)#update the menu with the new entry
            MENU.add(self.hud_scores)#add the menu back to the screen with the updated entry
        else:
            self.alphanum_index = 0
            self.entry_name += 'A'


    def __return_to_menu(self):
        self.next_state = mainmenu.MainMenu()
