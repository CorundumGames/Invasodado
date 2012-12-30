import pygame

import core.config as config
import core.color  as color
import gameobject
import hudobject
import mainmenu
import core.highscoretable as highscoretable

MENU = pygame.sprite.RenderUpdates()

ROW_WIDTH = 32
V_SPACE   = 24
TABLE_CORNER = (16, 64)

score_tables  = [
                 highscoretable.HighScoreTable("normal.wtf", 1, 10, "Scores")
                 ]

def make_score_table(table, pos, vspace, width):
    '''
    Creates a visual representation of a high score table.
    Returns a list of pygame.HudObjects.
    
    table is the HighScoreTable
    pos is the position of the top-left corner
    vspace is the vertical space between each line
    width is the width of the table in characters
    
    '''
    
    b = []
    scores = table.get_scores()
    for i in scores:
        b.append(i.name + '.'*(width - len(i.name) - len(str(i.score))) + str(i.score))
        
    return hudobject.HudObject.make_text(b, TABLE_CORNER, vspace = V_SPACE)
    

class HighScoreState(gameobject.GameObject):
    def __init__(self, *args):
        global score_tables
        self.args = args
        
        self.key_actions = {
                            pygame.K_LEFT   : NotImplemented,
                            pygame.K_RIGHT  : NotImplemented,
                            pygame.K_UP     : NotImplemented,
                            pygame.K_DOWN   : NotImplemented,
                            pygame.K_RETURN : NotImplemented,
                            pygame.K_ESCAPE : self.__return_to_menu,
                            }
        
        self.hud_titles   = [hudobject.HudObject.make_text("Scores", (config.SCREEN_RECT.midtop[0], 16))]
        #The list of the titles of high score tables
        
        self.hud_scores   = make_score_table(score_tables[0], (0, 0), 8, ROW_WIDTH)
        #The graphical display of the scores
        
        self.next_state   = None
        
        self.group_list   = [MENU]
        
        MENU.add(self.hud_scores, self.hud_titles)
        
        if self.args:
        #If we were passed in any arguments...
            score_tables[0].add_score(highscoretable.HighScoreEntry("JesseTG", args[0], 1))
    
    def __del__(self):
        MENU.empty()
        pygame.display.get_surface().blit(config.BG, (0, 0))
    
    def events(self, events):
        for e in events:
        #For all input we've received...
            if e.type == pygame.KEYDOWN and e.key in self.key_actions:
            #If a key was pressed...
                self.key_actions[e.key]()
    
    def logic(self):
        pass
    
    def render(self):
        pygame.display.get_surface().blit(config.BG, (0, 0))
        for g in self.group_list:
            pygame.display.update(g.draw(pygame.display.get_surface()))
            
        pygame.display.flip()
    
    def __return_to_menu(self):
        self.next_state = mainmenu.MainMenu()