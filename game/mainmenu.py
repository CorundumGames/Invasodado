import random

import pygame.event
import pygame.display
import pygame.sprite

from core import color
from core import config
from core import gamestate

import bg
import ingame
import highscore
import hudobject
import settingsmenu

'''
This is where the user makes his decisions about what to do in the game.
Not really special compared to any other main menu.
'''

def menu_text(text):
    '''Returns a text graphic in the main menu's font style.'''
    return config.FONT.render(text, False, color.WHITE).convert(config.DEPTH, config.FLAGS)

HUD  = pygame.sprite.RenderUpdates()
MENU = pygame.sprite.RenderUpdates()
BG   = pygame.sprite.LayeredUpdates()

DIST_APART = 64
#How far apart, vertically, the menu entries are (in pixels)

MENU_CORNER = (config.SCREEN_RECT.centerx - 112, config.SCREEN_RECT.centery - 64)
#The location of the top-left corner of the menu

class MainMenu(gamestate.GameState):    
    def __init__(self):
        self.group_list = [bg.STARS_GROUP, BG, HUD, MENU]
        
        self.hud_title = hudobject.HudObject(menu_text("Invasodado"),
                                             (config.SCREEN_RECT.centerx - 96, 32)
                                             )
        #Will be replaced with a logo (aka an actual image) later.
        
        self.hud_selection  = hudobject.HudObject(menu_text("->"), (0, 0))
        
        self.hud_normalmode = hudobject.HudObject(menu_text("Normal Mode"), MENU_CORNER)
        
        self.hud_highscore  = hudobject.HudObject(menu_text("High Scores"), (MENU_CORNER[0], MENU_CORNER[1] + DIST_APART))

        self.hud_settings   = hudobject.HudObject(menu_text("Settings"), (MENU_CORNER[0], MENU_CORNER[1] + 2*DIST_APART))
        
        self.hud_quit       = hudobject.HudObject(menu_text("Quit"), (MENU_CORNER[0], MENU_CORNER[1] + 3*DIST_APART))
        
        self.frame_limit = True
        #True if we're limiting the frame rate to 60 FPS
        
        
        
        self.menu_entries = {
                             0 : self.hud_normalmode,
                             1 : self.hud_highscore ,
                             2 : self.hud_settings  ,
                             3 : self.hud_quit      ,
                             }
        
        self.menu_actions = {
                             self.hud_normalmode.rect.midleft : self.__start_game      ,
                             self.hud_highscore.rect.midleft  : self.__view_high_scores,
                             self.hud_quit.rect.midleft       : quit                   ,
                             self.hud_settings.rect.midleft   : self.__settings_menu   ,
                             }
        
        self.key_actions  = {
                             pygame.K_RETURN : self.__enter_selection,
                             pygame.K_UP     : self.__move_up        ,
                             pygame.K_DOWN   : self.__move_down      ,
                             pygame.K_ESCAPE : quit                ,
                             }
        
        self.selection    = 0
        
        HUD.add(self.hud_title, self.hud_selection)
        MENU.add(self.hud_normalmode, self.hud_highscore, self.hud_quit, self.hud_settings)
        BG.add(bg.EARTH, bg.GRID)
        
    def __del__(self):
        for g in self.group_list:
        #For all groups of sprites...
            g.empty()
        
        self.group_list = []
        
    

    def events(self, events):
        for e in events:
        #For all input we've received...
            if e.type == pygame.KEYDOWN and e.key in self.key_actions:
            #If a key was pressed...
                self.key_actions[e.key]()
                self.selection %= len(self.menu_entries)
            
    def logic(self):
        for g in self.group_list:
        #For all Sprite groups...
            g.update()
    
    def render(self):
        
        
        self.hud_selection.rect.midright = self.menu_entries[self.selection].rect.midleft
        pygame.display.get_surface().fill((0, 0, 0))
        bg.STARS.emit()
        for g in self.group_list:
        #For all Sprite groups...
            g.draw(pygame.display.get_surface())
            
        pygame.display.flip()
        pygame.display.set_caption("FPS: %f" % round(self.fps_timer.get_fps(), 3))
            
        self.fps_timer.tick(60 * self.frame_limit)
        
    def __start_game(self):
        '''Begin the game.'''
        self.next_state = ingame.InGameState()
        
    def __enter_selection(self):
        '''Go with the selection the player made.'''
        if self.hud_selection.rect.midright in self.menu_actions:
        #If we're highlighting a valid menu entry...
            self.menu_actions[self.hud_selection.rect.midright]()
            
    def __view_high_scores(self):
        '''Bring the player to the high score table.'''
        self.next_state = highscore.HighScoreState()
            
    def __move_up(self):
        '''Move the cursor up.'''
        #There should probably be some animation here later.
        self.selection -= 1
        
    def __move_down(self):
        '''Move the cursor down.'''
        #Likewise here.
        self.selection += 1

    def __settings_menu(self):
        self.next_state = settingsmenu.SettingsMenu()
