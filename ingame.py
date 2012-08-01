import pygame

import block
import collisions
import enemysquadron
import enemy
import gsm
import player
import shipbullet

from gamestate import GameState

PLAYER  = None
ENEMIES = None
BLOCKS  = pygame.sprite.RenderUpdates()

class InGameState(GameState):    
    def __init__(self):
        self.collision_grid = collisions.CollisionGrid(4, 4, 1)
        self.group_list.append(BLOCKS)
    
    def events(self):
        for e in pygame.event.get():
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                BLOCKS.add(block.Block(e.pos))        
    
    def logic(self):
        self.collision_grid.update()
        
        for g in self.group_list:
            g.update()
    
    def render(self):
        pygame.display.get_surface().fill((0, 0, 0))
        
        for g in self.group_list:
            pygame.display.update(g.draw(pygame.display.get_surface()))
            
        self.fpsTimer.tick(60)