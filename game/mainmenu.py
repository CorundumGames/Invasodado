import random

import pygame.event
import pygame.display
import pygame.sprite

from core import color
from core import config
import hudobject

from core import gamestate
from core import config
from core import gsm
import ingame

HUD     = pygame.sprite.LayeredUpdates()

class MainMenu(gamestate.GameState):    
    def __init__(self):
        self.group_list    += [HUD]
        
        self.hud_invasodado  = hudobject.HudObject()
        #middle of screen minus the appropriate number of cells
        self.hud_invasodado.rect  = pygame.Rect((config.SCREEN_WIDTH/2) - 96,32,0,0)
        
        self.hud_normalmode  = hudobject.HudObject()
        #middle of screen minus the appropriate number of cells
        self.hud_normalmode.rect  = pygame.Rect((config.SCREEN_WIDTH/2) - 112,(config.SCREEN_HEIGHT/2) - 64, 6*32, 16)
        
        self.hud_quit = hudobject.HudObject()
        self.hud_quit.rect = pygame.Rect(config.SCREEN_WIDTH/2 - 112, config.SCREEN_HEIGHT/2, 6*32, 16)
        
        self.frame_limit = True
        
        self.hud_normalmode.image = config.FONT.render("Normal Mode", False, color.Colors.WHITE).convert(config.DEPTH, config.FLAGS)
        self.hud_invasodado.image = config.FONT.render("Invasodado", False, color.Colors.WHITE).convert(config.DEPTH, config.FLAGS)
        self.hud_quit.image       = config.FONT.render("Quit", False, color.Colors.WHITE).convert(config.DEPTH, config.FLAGS)

        HUD.add(self.hud_normalmode, self.hud_invasodado, self.hud_quit)
    
    def events(self):
        for e in pygame.event.get():
            if e.type == pygame.MOUSEBUTTONDOWN:
            #If a mouse button is clicked...
                if   e.button == 1:
                    if self.hud_normalmode.rect.collidepoint(e.pos):
                        gsm.current_state = ingame.InGameState()
                        HUD.empty()
                    elif self.hud_quit.rect.collidepoint(e.pos):
                        quit()
                                    
            
    def logic(self):
        pass
    
    def render(self):
        pygame.display.get_surface().blit(config.BG, (0, 0))
        
        
        
        for g in self.group_list:
        #For all Sprite groups...
            pygame.display.update(g.draw(pygame.display.get_surface()))
            
        pygame.display.flip()
        pygame.display.set_caption("FPS: " + str(round(self.fpsTimer.get_fps(), 3)))
            
        self.fpsTimer.tick(60*self.frame_limit)