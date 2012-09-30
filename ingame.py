import pygame

import itertools

import block
import blockgrid
import collisions
import config
import color
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
        for e in pygame.event.get(pygame.MOUSEBUTTONDOWN):
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if blockgrid.RECT.collidepoint(pygame.mouse.get_pos()):
                    BLOCKS.add(block.Block(e.pos))  
                    
        for e in pygame.event.get(pygame.KEYDOWN):
            if e.key == pygame.K_g:
                for i in itertools.ifilter(lambda x: isinstance(x, block.Block) and x.color == color.Colors.GREEN, BLOCKS):
                        i.state = block.STATES.DYING
                        
            elif e.key == pygame.K_p:
                for i in itertools.ifilter(lambda x: isinstance(x, block.Block) and x.color == color.Colors.PURPLE, BLOCKS):
                        i.state = block.STATES.DYING
                        
            elif e.key == pygame.K_y:
                for i in itertools.ifilter(lambda x: isinstance(x, block.Block) and x.color == color.Colors.YELLOW, BLOCKS):
                        i.state = block.STATES.DYING
                        
            elif e.key == pygame.K_b:
                for i in itertools.ifilter(lambda x: isinstance(x, block.Block) and x.color == color.Colors.BLUE, BLOCKS):
                        i.state = block.STATES.DYING
                        
            elif e.key == pygame.K_r:
                for i in itertools.ifilter(lambda x: isinstance(x, block.Block) and x.color == color.Colors.RED, BLOCKS):
                        i.state = block.STATES.DYING
                        
            elif e.key == pygame.K_c:
                blockgrid.clear()
                             
    
    def logic(self):
        self.collision_grid.update()
        
        for g in self.group_list:
            g.update()
            
        blockgrid.update()
            
        pygame.event.clear()  #This is only temporary!
            
    
    def render(self):
        
        pygame.display.get_surface().fill((0, 0, 0))
        
        for g in self.group_list:
            pygame.display.update(g.draw(pygame.display.get_surface()))
        
        
        self.fpsTimer.tick(60)
        