import random

import pygame.event
import pygame.display
import pygame.sprite

import block
import blockgrid
from core import collisions
from core import color
from core import config
import enemysquadron
import enemy
import player
import shipbullet

from core import gamestate



PLAYER  = pygame.sprite.RenderUpdates()
ENEMIES = pygame.sprite.RenderUpdates()
BLOCKS  = pygame.sprite.RenderUpdates()

class InGameState(gamestate.GameState):    
    def __init__(self):
        self.collision_grid = collisions.CollisionGrid(4, 4, 1)
        self.group_list    += [BLOCKS, ENEMIES, PLAYER]
        self.ship           = player.Ship()
        self.frame_limit = True

        
        PLAYER.add(self.ship, shipbullet.ShipBullet())
        enemysquadron.reset()
        
    
    def events(self):
        for e in pygame.event.get():
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            #If the mouse button is clicked...
                BLOCKS.add(block.Block(e.pos, random.choice(color.Colors.LIST)))   
            if e.type == pygame.KEYDOWN:
            #If a key is pressed...
                if e.key == pygame.K_SPACE:
                #If the space bar is pressed...
                    self.ship.on_fire_bullet()
                elif e.key == pygame.K_f:
                #If the F key is pressed...
                    self.frame_limit = not self.frame_limit    
                     
    
    def logic(self):
        self.collision_grid.update()
        
        for g in self.group_list:
        #For all Sprite groups...
            g.update()
            
        if len(ENEMIES.sprites()) == 0:
        #If all enemies have been killed...
            enemysquadron.reset()
            
        if enemy.Enemy.should_flip:
        #If at least one enemy has touched the side of the screen...
            enemy.Enemy.should_flip = False
            enemy.Enemy.velocity[0] *= -1
            
        

    
    def render(self):
        pygame.display.get_surface().blit(config.BG, (0, 0))
        
        for g in self.group_list:
        #For all Sprite groups...
            pygame.display.update(g.draw(pygame.display.get_surface()))
            
        pygame.display.flip()
        pygame.display.set_caption("FPS: " + str(round(self.fpsTimer.get_fps(), 3)))
            
        self.fpsTimer.tick(60*self.frame_limit)