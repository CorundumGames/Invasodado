import pygame.display
import pygame.sprite

from core import color
from core import config
from core import gamestate

import bg
import mainmenu
import hudobject

'''
This is a menu that lets the user change settings within the game.
'''

HUD  = pygame.sprite.RenderUpdates()
MENU = pygame.sprite.RenderUpdates()
BG   = pygame.sprite.LayeredUpdates()

DIST_APART_MENU = 64
#How far apart, vertically, the menu entries are (in pixels)
DIST_APART_STATUS = 32
#How far apart, horizontally, the status of a menu entry is from the menu entry

MENU_CORNER = (config.SCREEN_RECT.topleft[0] + 32 , config.SCREEN_RECT.topleft[1] + 64)
#The location of the top-left corner of the menu

def menu_text(text):
    '''Returns a text graphic in the menu's font style.'''
    return config.FONT.render(text, False, color.WHITE).convert(config.DEPTH, config.FLAGS)

class SettingsMenu(gamestate.GameState):    
    def __init__(self):
        self.group_list = [bg.STARS_GROUP, BG, HUD, MENU]
        
        self.hud_title = hudobject.HudObject(menu_text("Settings"),
                                             (config.SCREEN_RECT.centerx - 64, 32)
                                             )
        
        self.hud_fullscreen     = hudobject.HudObject(menu_text("Full Screen"), MENU_CORNER)
        
        self.hud_colorblindmode = hudobject.HudObject(menu_text("Color Blind mode"), (MENU_CORNER[0], MENU_CORNER[1] + DIST_APART_MENU))
        
        self.hud_difficulty     = hudobject.HudObject(menu_text("Difficulty"), (MENU_CORNER[0], MENU_CORNER[1] + 2*DIST_APART_MENU))
        
        self.hud_mainmenu       = hudobject.HudObject(menu_text("Return to Main Menu"), (config.SCREEN_RECT.centerx - 160, MENU_CORNER[1] + 3*DIST_APART_MENU))
        
        self.hud_selection              = hudobject.HudObject(menu_text("->"), (0, 0))
        
        if config.settings.fullscreen:
            self.hud_fullscreen_status = hudobject.HudObject(menu_text("On"), (MENU_CORNER[0] + self.hud_fullscreen.rect.width + DIST_APART_STATUS, MENU_CORNER[1]))
        else:
            self.hud_fullscreen_status = hudobject.HudObject(menu_text("Off"), (MENU_CORNER[0] + self.hud_fullscreen.rect.width + DIST_APART_STATUS, MENU_CORNER[1]))
        
        self.hud_colorblindmode_status  = hudobject.HudObject(menu_text("Off"), (MENU_CORNER[0] + self.hud_colorblindmode.rect.width + DIST_APART_STATUS, MENU_CORNER[1] + DIST_APART_MENU))#Add a conditional to display correct status
        
        self.hud_difficulty_status      = hudobject.HudObject(menu_text("Easy"), (MENU_CORNER[0] + self.hud_difficulty.rect.width + DIST_APART_STATUS, MENU_CORNER[1] + 2*DIST_APART_MENU))#Add a conditional to diplay correct status
        
        self.frame_limit = True
        #True if we're limiting the frame rate to 60 FPS
        
        
        
        self.menu_entries = {
                             0 : self.hud_fullscreen     ,
                             1 : self.hud_colorblindmode ,
                             2 : self.hud_difficulty     ,
                             3 : self.hud_mainmenu       ,
                             }
        
        self.menu_actions = {
                             self.hud_fullscreen.rect.midleft : self.__toggle_fullscreen            ,
                             self.hud_colorblindmode.rect.midleft  : self.__toggle_color_blind_mode ,
                             self.hud_difficulty.rect.midleft       : self.__toggle_difficulty      ,
                             self.hud_mainmenu.rect.midleft   : self.__return_to_main_menu          ,
                             }
        
        self.key_actions  = {
                             pygame.K_RETURN : self.__enter_selection,
                             pygame.K_UP     : self.__move_up        ,
                             pygame.K_DOWN   : self.__move_down      ,
                             }
        
        self.selection    = 0
        
        HUD.add(self.hud_title, self.hud_selection, self.hud_fullscreen_status, self.hud_colorblindmode_status, self.hud_difficulty_status)
        MENU.add(self.hud_fullscreen, self.hud_colorblindmode, self.hud_difficulty, self.hud_mainmenu)
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
        pygame.display.get_surface().fill((0, 0, 0))
        
        self.hud_selection.rect.midright = self.menu_entries[self.selection].rect.midleft
        
        bg.STARS.emit()
        for g in self.group_list:
        #For all Sprite groups...
            g.draw(pygame.display.get_surface())
            
        pygame.display.flip()
        pygame.display.set_caption("FPS: %f" % round(self.fps_timer.get_fps(), 3))
            
        self.fps_timer.tick(60 * self.frame_limit)
        
    def __enter_selection(self):
        '''Go with the selection the player made.'''
        if self.hud_selection.rect.midright in self.menu_actions:
        #If we're highlighting a valid menu entry...
            self.menu_actions[self.hud_selection.rect.midright]()
            
    def __move_up(self):
        '''Move the cursor up.'''
        #There should probably be some animation here later.
        self.selection -= 1
        
    def __move_down(self):
        '''Move the cursor down.'''
        #Likewise here.
        self.selection += 1
        
    def __toggle_fullscreen(self):
        config.toggle_fullscreen()
        if config.settings.fullscreen:
            self.hud_fullscreen_status.image = hudobject.HudObject.make_text("On", surfaces = True)
        else:
            self.hud_fullscreen_status.image = hudobject.HudObject.make_text("Off", surfaces = True)
    
    def __toggle_color_blind_mode(self):
        pass
    
    def __toggle_difficulty(self):
        pass
    
    def __return_to_main_menu(self):
        self.next_state = mainmenu.MainMenu()