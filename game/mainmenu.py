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

HUD = pygame.sprite.LayeredUpdates()

class MainMenu(gamestate.GameState):    
    def __init__(self):
        self.group_list += [HUD]
        
        make_text = config.FONT.render
        middle_x  = config.SCREEN_WIDTH / 2
        middle_y  = config.SCREEN_HEIGHT / 2
        
        self.hud_invasodado = hudobject.HudObject(make_text("Invasodado", False, color.WHITE).convert(config.DEPTH, config.FLAGS),
                                                  pygame.Rect(middle_x - 96, 32, 0, 0)
                                                  )
        
        self.hud_normalmode = hudobject.HudObject(make_text("Normal Mode", False, color.WHITE).convert(config.DEPTH, config.FLAGS),
                                                  pygame.Rect(middle_x - 112, middle_y - 64, 6 * 32, 16)
                                                  )
        
        self.hud_quit       = hudobject.HudObject(make_text("Quit", False, color.WHITE).convert(config.DEPTH, config.FLAGS),
                                                  pygame.Rect(middle_x - 112, middle_y, 6 * 32, 16)
                                                  )
        
        self.hud_selection  = hudobject.HudObject(make_text("->", False, color.WHITE).convert(config.DEPTH, config.FLAGS),
                                                  pygame.Rect(self.hud_normalmode.rect.x-32, self.hud_normalmode.rect.y, 6 * 32, 16)
                                                  )
        
        self.frame_limit = True
        
        HUD.add([self.hud_normalmode, self.hud_invasodado, self.hud_quit, self.hud_selection])
        
        self.menuLen        = 2
        self.curActionIndex = 0
        
    def __del__(self):
        HUD.empty()

    def events(self, states):
        #This could DEFINITELY use some improvement.
        for e in states:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN:
                    if self.curActionIndex == 0:
                        self.next_state = ingame.InGameState()
                    elif self.curActionIndex == 1:
                        quit()
                elif e.key == pygame.K_UP:
                        self.curActionIndex -= 1    
                elif e.key == pygame.K_DOWN:
                        self.curActionIndex += 1
                        
                self.curActionIndex %= self.menuLen
            
    def logic(self):
        pass
    
    def render(self):
        pygame.display.get_surface().blit(config.BG, (0, 0))
        
        #Note: We can store all possible menu entries in a list, then do
        #something like this (if the list is called menu_list):
        #self.hud_selection.rect.midright = self.menu_list[self.curActionIndex].rect.midright
        if self.curActionIndex == 0:
            self.hud_selection.rect.midright = self.hud_normalmode.rect.midleft
        elif self.curActionIndex == 1:
            self.hud_selection.rect.midright = self.hud_normalmode.rect.midleft
        
        for g in self.group_list:
        #For all Sprite groups...
            pygame.display.update(g.draw(pygame.display.get_surface()))
            
        pygame.display.flip()
        pygame.display.set_caption("FPS: " + str(round(self.fpsTimer.get_fps(), 3)))
            
        self.fpsTimer.tick(60 * self.frame_limit)