import pygame

import player
import gsm
import enemysquadron
import enemy
import collisiongrid

from gamestate import GameState

PLAYER = pygame.sprite.RenderUpdates()
ENEMIES = pygame.sprite.RenderUpdates()

class InGameState(GameState):    
    def __init__(self):
        ship = player.Ship()
        self.group_list += [PLAYER, ENEMIES]
    
        self.group_list[self.group_list.index(PLAYER)].add(ship)
        self.group_list[self.group_list.index(ENEMIES)].add(enemysquadron.enemies)
        self.collision_grid = collisiongrid.CollisionGrid(4, 4)
    
    def events(self):
        pass
    
    def logic(self):
        self.collision_grid.update()
        
        for g in self.group_list:
            g.update()
            
        if enemy.Enemy.should_flip == True:
            enemy.Enemy.velocity[0] *= -1
            enemy.Enemy.should_flip = False
    
    def render(self):
        pygame.display.get_surface().fill((0, 0, 0))
        
        for g in self.group_list:
            pygame.display.update(g.draw(pygame.display.get_surface()))
            
        self.fpsTimer.tick(60)