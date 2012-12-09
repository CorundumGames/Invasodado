import math

import pygame.display
import pygame.event
import pygame.sprite

import core.collisions as collisions
import core.color      as color
import core.config     as config
import core.gamestate  as gamestate


import block
import blockgrid
import enemy
import enemysquadron
import hudobject
import player
import shipbullet
import ufo

PLAYER  = pygame.sprite.LayeredUpdates()
ENEMIES = pygame.sprite.LayeredUpdates()
BLOCKS  = pygame.sprite.LayeredUpdates()
HUD     = pygame.sprite.LayeredUpdates()

DEFAULT_MULTIPLIER = 10
multiplier         = DEFAULT_MULTIPLIER

global score
global prev_score
score = 0
prev_score = None

global lives
global prev_lives
lives = 3
prev_lives = None

class InGameState(gamestate.GameState):    
    def __init__(self):
        self.collision_grid = collisions.CollisionGrid(4, 4, 1)
        self.group_list    += [BLOCKS, ENEMIES, PLAYER, HUD]
        self.ship           = player.Ship()
        self.ufo            = ufo.UFO()
        
        self.hud_score       = hudobject.HudObject(pygame.Surface((0, 0)), pygame.Rect(16, 16, 0, 0))
        self.hud_lives       = hudobject.HudObject(pygame.Surface((0, 0)), pygame.Rect(config.SCREEN_WIDTH-160, 16, 0, 0))
        
        self.frame_limit  = True
        self.game_running = True

        
        PLAYER.add(self.ship)
        HUD.add(self.hud_score, self.hud_lives)
        enemysquadron.reset()
        
    
    def events(self,states):
        for e in states:
            if e.type == pygame.MOUSEBUTTONDOWN:
            #If a mouse button is clicked...
                if   e.button == 1:
                #If it was the left button...
                    BLOCKS.add(block.Block((e.pos[0], 0), color.RED))
                elif e.button == 2:
                #If it was the middle button...
                    BLOCKS.add(block.Block((e.pos[0], 0), color.YELLOW))
                elif e.button == 3:
                #If it was the right button...
                    BLOCKS.add(block.Block((e.pos[0], 0), color.BLUE))
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
                    if self.ufo.state == ufo.UFO.STATES.IDLE:
                        ENEMIES.add(self.ufo)
                        self.ufo.state = ufo.UFO.STATES.APPEARING
                elif e.key == pygame.K_c:
                    blockgrid.clear()
                elif e.key == pygame.K_p:
                    config.togglePause()
                     
    
    def logic(self):
        self.collision_grid.update()
        
        for g in self.group_list:
        #For all Sprite groups...
            g.update()
            
        if len(ENEMIES) == 0:
        #If all enemies have been killed...
            enemysquadron.reset()
            enemy.Enemy.velocity[0] += math.copysign(.05, enemy.Enemy.velocity[0])
            
        if enemy.Enemy.should_flip:
        #If at least one enemy has touched the side of the screen...
            enemy.Enemy.velocity[0] *= -1
            enemysquadron.move_down()
            enemy.Enemy.should_flip = False
            
        if lives == 0:
            self.game_running = False
            
        if not self.game_running:
            self.game_over()


    def render(self):
        global score
        global lives
        global prev_score
        global prev_lives
        pygame.display.get_surface().blit(config.BG, (0, 0))
        
        if score != prev_score:
            self.hud_score.image = config.FONT.render("Score: " + str(score), False, color.WHITE).convert(config.DEPTH, config.FLAGS)
            prev_score = score
            
        if lives != prev_lives:
            self.hud_lives.image = config.FONT.render("Lives: " + str(lives), False, color.WHITE).convert(config.DEPTH, config.FLAGS)
            prev_lives = lives
        
        for g in self.group_list:
        #For all Sprite groups...
            pygame.display.update(g.draw(pygame.display.get_surface()))
            
        pygame.display.flip()
        pygame.display.set_caption("Score: " + str(score) + "    FPS: " + str(round(self.fpsTimer.get_fps(), 3)))
            
        self.fpsTimer.tick(60 * self.frame_limit)


    def game_over(self):
        enemy.Enemy.velocity = [0, 0]
        gameovertext = hudobject.HudObject()
        gameovertext.image = config.FONT.render("GAME OVER", False, color.Colors.WHITE).convert(config.DEPTH, config.FLAGS)
        gameovertext.rect = pygame.Rect(config.SCREEN_WIDTH/2, config.SCREEN_HEIGHT/2, 0, 0)
        self.ship.state = player.STATES.DYING
        HUD.add(gameovertext)

