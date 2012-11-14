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
import hudobject
import player
import shipbullet
import ufo

from core import gamestate

PLAYER  = pygame.sprite.LayeredUpdates()
ENEMIES = pygame.sprite.LayeredUpdates()
BLOCKS  = pygame.sprite.LayeredUpdates()
HUD     = pygame.sprite.LayeredUpdates()

DEFAULT_MULTIPLIER = 10
multiplier         = DEFAULT_MULTIPLIER

score = 0
lives = 3

class InGameState(gamestate.GameState):    
    def __init__(self):
        self.collision_grid = collisions.CollisionGrid(4, 4, 1)
        self.group_list    += [BLOCKS, ENEMIES, PLAYER, HUD]
        self.ship           = player.Ship()
        self.ufo            = ufo.UFO()
        
        self.hud_score       = hudobject.HudObject()
        self.hud_score.rect  = pygame.Rect(16, 16, 0, 0)
        
        
        self.frame_limit = True

        
        PLAYER.add(self.ship, shipbullet.ShipBullet())
        HUD.add(self.hud_score)
        enemysquadron.reset()
        
    
    def events(self):
        for e in pygame.event.get():
            if e.type == pygame.MOUSEBUTTONDOWN:
            #If a mouse button is clicked...
                if   e.button == 1:
                #If it was the left button...
                    BLOCKS.add(block.Block((e.pos[0], 0), color.Colors.RED))
                elif e.button == 2:
                #If it was the middle button...
                    BLOCKS.add(block.Block((e.pos[0], 0), color.Colors.YELLOW))
                elif e.button == 3:
                #If it was the right button...
                    BLOCKS.add(block.Block((e.pos[0], 0), color.Colors.BLUE))
            elif e.type == pygame.KEYDOWN:
            #If a key is pressed...
                if e.key == pygame.K_SPACE:
                #If the space bar is pressed...
                    self.ship.on_fire_bullet()
                elif e.key == pygame.K_f:
                #If the F key is pressed...
                    self.frame_limit = not self.frame_limit
                elif e.key == pygame.K_u:
                #If the U key is pressed...
                    if self.ufo.state == ufo.STATES.IDLE:
                        ENEMIES.add(self.ufo)
                        self.ufo.state = ufo.STATES.APPEARING
                     
    
    def logic(self):
        self.collision_grid.update()
        
        for g in self.group_list:
        #For all Sprite groups...
            g.update()
            
        if ENEMIES.sprites() == []:
        #If all enemies have been killed...
            enemysquadron.reset()
            
        if enemy.Enemy.should_flip:
        #If at least one enemy has touched the side of the screen...
            enemy.Enemy.velocity[0] *= -1
            enemysquadron.move_down()
            enemy.Enemy.should_flip = False
            
        

    
    def render(self):
        pygame.display.get_surface().blit(config.BG, (0, 0))
        
        self.hud_score.image = config.FONT.render("Score: " + str(score), False, (255, 255, 255))
        
        for g in self.group_list:
        #For all Sprite groups...
            pygame.display.update(g.draw(pygame.display.get_surface()))
            
        pygame.display.flip()
        pygame.display.set_caption("Score: " + str(score) + "    FPS: " + str(round(self.fpsTimer.get_fps(), 3)))
            
        self.fpsTimer.tick(60*self.frame_limit)