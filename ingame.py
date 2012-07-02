
import pygame

import player
import gsm

from gamestate import GameState

class InGameState(GameState):    
    def __init__(self):
        ship = player.Ship()
        self.group_list.append(pygame.sprite.RenderUpdates())
        self.group_list[0].add(ship, ship.bullet)
    
    def events(self):
        pass
    
    def logic(self):
        for g in self.group_list:
            g.update()
    
    def render(self):
        pygame.display.get_surface().fill((0, 0, 0))
        
        for g in self.group_list:
            pygame.display.update(g.draw(pygame.display.get_surface()))
            
        self.fpsTimer.tick(60)