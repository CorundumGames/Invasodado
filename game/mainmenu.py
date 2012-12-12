import random

import pygame.event
import pygame.display
import pygame.sprite

from core import color
from core import config
import hudobject

from core import gamestate
from core import config
import ingame

HUD  = pygame.sprite.RenderUpdates()
MENU = pygame.sprite.RenderUpdates()

class MainMenu(gamestate.GameState):    
    def __init__(self):
        self.group_list = [HUD, MENU]
        
        make_text = config.FONT.render
        middle_x  = config.SCREEN_WIDTH / 2
        middle_y  = config.SCREEN_HEIGHT / 2
        
        self.hud_invasodado = hudobject.HudObject(make_text("Invasodado", False, color.WHITE).convert(config.DEPTH, config.FLAGS),
                                                  (config.SCREEN_RECT.centerx - 96, 32)
                                                  )
        
        self.hud_selection  = hudobject.HudObject(make_text("->", False, color.WHITE).convert(config.DEPTH, config.FLAGS),
                                                  (0, 0)
                                                  )
        
        self.hud_normalmode = hudobject.HudObject(make_text("Normal Mode", False, color.WHITE).convert(config.DEPTH, config.FLAGS),
                                                  (config.SCREEN_RECT.centerx - 112, config.SCREEN_RECT.centery - 64)
                                                  )
        
        self.hud_quit       = hudobject.HudObject(make_text("Quit", False, color.WHITE).convert(config.DEPTH, config.FLAGS),
                                                  (config.SCREEN_RECT.centerx - 112, config.SCREEN_RECT.centery)
                                                  )
        
        
        
        self.frame_limit = True
        
        HUD.add(self.hud_invasodado, self.hud_selection)
        MENU.add(self.hud_normalmode, self.hud_quit)
        
        self.menu_entries = {
                             0 : self.hud_normalmode.rect.midleft,
                             1 : self.hud_quit.rect.midleft      ,
                             }
        
        self.menu_actions = {
                             self.hud_normalmode.rect.midleft : self.start_game,
                             self.hud_quit.rect.midleft       : quit           ,
                             }
        
        self.key_actions  = {
                             pygame.K_RETURN : self.enter_selection,
                             pygame.K_UP     : self.move_up        ,
                             pygame.K_DOWN   : self.move_down      ,
                             pygame.K_ESCAPE : quit                ,
                             }
        
        self.selection    = 0
        
    def __del__(self):
        pygame.display.get_surface().blit(config.BG, (0, 0))
        for g in self.group_list:
            g.empty()
        
        self.group_list = []
        
        self.next_state = None

    def events(self, events):
        #This could DEFINITELY use some improvement.
        for e in events:
        #For all input we've received...
            if e.type == pygame.KEYDOWN:
            #If a key was pressed...
                self.key_actions[e.key]()
                self.selection %= len(self.menu_entries)
            
    def logic(self):
        pass
    
    def render(self):
        pygame.display.get_surface().blit(config.BG, (0, 0))
        
        self.hud_selection.rect.midright = self.menu_entries[self.selection]
        
        for g in self.group_list:
        #For all Sprite groups...
            pygame.display.update(g.draw(pygame.display.get_surface()))
            
        pygame.display.flip()
        pygame.display.set_caption("FPS: %f" % round(self.fpsTimer.get_fps(), 3))
            
        self.fpsTimer.tick(60 * self.frame_limit)
        
    def start_game(self):
        self.next_state = ingame.InGameState()
        
    def enter_selection(self):
        if self.hud_selection.rect.midright in self.menu_actions:
            self.menu_actions[self.hud_selection.rect.midright]()
            
    def move_up(self):
        self.selection -= 1
        
    def move_down(self):
        self.selection += 1