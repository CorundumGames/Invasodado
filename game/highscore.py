import pygame

import core.config as config
import gameobject
import mainmenu
import core.highscoretable as highscoretable

MENU = pygame.sprite.RenderUpdates()

score_tables  = [
                 highscoretable.HighScoreTable("Normal Mode", 1, 10, "Scores")
                 ]

class HighScoreState(gameobject.GameObject):
    def __init__(self):
        
        self.key_actions = {
                            pygame.K_LEFT   : NotImplemented,
                            pygame.K_RIGHT  : NotImplemented,
                            pygame.K_UP     : NotImplemented,
                            pygame.K_DOWN   : NotImplemented,
                            pygame.K_RETURN : NotImplemented,
                            pygame.K_ESCAPE : self.__return_to_menu,
                            }
        
        self.hud_titles   = []
        self.hud_scores   = []
        self.next_state   = None
    
    def __del__(self):
        pass
    
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
        pygame.display.flip()
    
    def __return_to_menu(self):
        self.next_state = mainmenu.MainMenu()