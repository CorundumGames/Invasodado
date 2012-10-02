import pygame

import block
import blockgrid
import collisions
import enemysquadron
import enemy
import gsm
import player
import shipbullet

from gamestate import GameState

PLAYER  = pygame.sprite.RenderUpdates()
ENEMIES = pygame.sprite.RenderUpdates()
BLOCKS  = pygame.sprite.RenderUpdates()

class InGameState(GameState):    
    def __init__(self):
        self.collision_grid = collisions.CollisionGrid(4, 4, 1)
        self.group_list += [BLOCKS, ENEMIES, PLAYER]
        
        self.ship = player.Ship()
        PLAYER.add(self.ship, shipbullet.ShipBullet())
        ENEMIES.add(enemysquadron.enemies)
        enemysquadron.reset()
    
    def events(self):
        for e in pygame.event.get():
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                BLOCKS.add(block.Block(e.pos))   
            if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                self.ship.on_fire_bullet()
                     
    
    def logic(self):
        self.collision_grid.update()
        
        for g in self.group_list:
            g.update()
            
        if enemy.Enemy.should_flip:
            enemy.Enemy.should_flip = False
            enemy.Enemy.velocity[0] *= -1
            
        if ENEMIES.sprites() == []:
            enemysquadron.reset()
            
        blockgrid.update()
    
    def render(self):
        pygame.display.get_surface().fill((0, 0, 0))
        
        for g in self.group_list:
            pygame.display.update(g.draw(pygame.display.get_surface()))
            
        self.fpsTimer.tick(60)