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
ENTRY_NAME_POS = (0,config.SCREEN_HEIGHT - 32)
ALPHANUMERIC = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 '

score_tables  = [
                 highscoretable.HighScoreTable("normal.wtf", 1, 10, "Scores", "./save/norm_default.json")
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
        
        self.enteringname = False
        
        self.key_actions = {
                            pygame.K_LEFT   : NotImplemented       ,
                            pygame.K_RIGHT  : NotImplemented       ,
                            pygame.K_UP     : self.__togglecharup  ,
                            pygame.K_DOWN   : self.__togglechardown,
                            pygame.K_RETURN : self.__confirmchar   ,
                            pygame.K_ESCAPE : self.__return_to_menu,
                            }
        
        self.hud_titles   = [hudobject.HudObject.make_text("Scores", (config.SCREEN_RECT.midtop[0] - 64, 16))]
        #The list of the titles of high score tables
        
        self.hud_scores   = make_score_table(score_tables[0], (0, 0), 8, ROW_WIDTH)
        #The graphical display of the scores
        
        self.next_state   = None
        
        self.group_list   = [MENU]
        
        MENU.add(self.hud_scores, self.hud_titles)
        
        if self.args:
        #If we were passed in any arguments...
            #score_tables[0].add_score(highscoretable.HighScoreEntry("Test", self.args[0], 1))
            print(score_tables[0].lowest_score())
            if self.args[0] > score_tables[0].lowest_score():
                print(args[0])
                self.enteringname = True
                self.charLimit = 9
                self.entryname = 'A'
                self.curnameindex = 0
                self.curalphanumericindex = 0
                self.hud_name  = hudobject.HudObject.make_text(self.entryname, ENTRY_NAME_POS)
                MENU.add(self.hud_name)
                    
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
        if self.enteringname:
            self.hud_name.kill()
            self.hud_name = hudobject.HudObject.make_text(self.entryname, ENTRY_NAME_POS)
            MENU.add(self.hud_name)
        for g in self.group_list:
            pygame.display.update(g.draw(pygame.display.get_surface()))
            
        pygame.display.flip()
        
    def __togglecharup(self):
        if self.enteringname:
            self.curalphanumericindex += 1
            self.updateName()
            
    def __togglechardown(self):
        if self.enteringname:
            self.curalphanumericindex -= 1
            self.updateName()
            
    def updateName(self):
        self.curalphanumericindex %= len(ALPHANUMERIC)
        self.entryname = self.entryname[0:self.curnameindex] + ALPHANUMERIC[self.curalphanumericindex] + self.entryname[self.curnameindex+1:]
    
    def __confirmchar(self):
        self.curnameindex += 1
        if self.curnameindex > self.charLimit:#Finished entering the name
            self.enteringname = False#End the entering name process
            self.hud_name.kill()#Get rid of the name entry characters
            score_tables[0].add_score(highscoretable.HighScoreEntry(self.entryname, self.args[0], 1))#add the entry to the leaderboard
            MENU.remove(self.hud_scores)#remove the menu from the screen
            self.hud_scores = make_score_table(score_tables[0], (0, 0), 8, ROW_WIDTH)#update the menu with the new entry
            MENU.add(self.hud_scores)#add the menu back to the screen with the updated entry
        else:
            self.curalphanumericindex = 0
            self.entryname += 'A'
            
    
    def __return_to_menu(self):
        self.next_state = mainmenu.MainMenu()
