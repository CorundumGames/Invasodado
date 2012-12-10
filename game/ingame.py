import math

import pygame.display
import pygame.event
import pygame.sprite

import core.collisions as collisions
import core.color      as color
import core.config     as config
import core.gamestate  as gamestate

import balloflight
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

score      = 0
prev_score = None

lives      = 3
prev_lives = None

class InGameState(gamestate.GameState):    
    def __init__(self):
        self.block_list     = []
        #The blocks available for use
        
        self.collision_grid = collisions.CollisionGrid(4, 4, 1)
        #The collision-handling system
        
        self.group_list    += [BLOCKS, ENEMIES, PLAYER, HUD]
        #The groups of sprites to process
        
        self.ship           = player.Ship()
        #The player
        
        self.ufo            = ufo.UFO()
        #The UFO
        
        self.hud_score = hudobject.HudObject(pygame.Surface((0, 0)), pygame.Rect(16, 16, 0, 0))
        self.hud_lives = hudobject.HudObject(pygame.Surface((0, 0)), pygame.Rect(config.SCREEN_WIDTH-160, 16, 0, 0))
        #The components of our HUD; let the player know how he's doing!
    
        self.game_running = True
        #False if we've gotten a game over
        
        self.key_actions = {
                            pygame.K_SPACE : self.ship.on_fire_bullet ,
                            pygame.K_F1    : config.toggle_fullscreen ,
                            pygame.K_c     : self.clear_blocks        ,
                            pygame.K_d     : config.toggle_debug      ,
                            pygame.K_f     : config.toggle_frame_limit,
                            pygame.K_p     : config.toggle_pause      ,
                            pygame.K_u     : self.add_ufo             ,
                            }
        #The keys available for use; key is keycode, element is a function
        
        self.mouse_actions = {
                              1: color.RED   ,
                              2: color.YELLOW,
                              3: color.BLUE  ,
                             }
        #What clicking the mouse can do: key is mouse button, element is color
        
        PLAYER.add(self.ship)
        HUD.add(self.hud_score, self.hud_lives)
        enemysquadron.reset()
        
    def __del__(self):
        for g in self.group_list:
            g.empty()
    
    def events(self, events):
        for e in events:
        #For all events passed in...
            if e.type == pygame.MOUSEBUTTONDOWN and config.debug:
            #If a mouse button is clicked...
                self.make_block(e.pos[0], self.mouse_actions[e.button])
            elif e.type == pygame.KEYDOWN and e.key in self.key_actions:
            #If a key is pressed...
                self.key_actions[e.key]()  
    
    def logic(self):
        self.collision_grid.update()
        
        for g in self.group_list:
        #For all Sprite groups...
            g.update()
            
        if len(ENEMIES) == 0:
        #If all enemies have been killed...
            enemysquadron.reset()
            enemy.Enemy.velocity[0] = abs(enemy.Enemy.velocity[0]) + 0.05
            
        if enemy.Enemy.should_flip:
        #If at least one enemy has touched the side of the screen...
            enemy.Enemy.velocity[0] *= -1
            enemysquadron.move_down()
            enemy.Enemy.should_flip = False
            
        if lives == 0:
        #If we run out of lives...
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
        #If our score has changed since the last frame...
            self.hud_score.image = config.FONT.render("Score: %i" % score, False, color.WHITE).convert(config.DEPTH, config.FLAGS)
            prev_score = score
            
        if lives != prev_lives:
        #If our lives have changed since the last frame...
            self.hud_lives.image = config.FONT.render("Lives: %i" % lives, False, color.WHITE).convert(config.DEPTH, config.FLAGS)
            prev_lives = lives
        
        for g in self.group_list:
        #For all Sprite groups...
            pygame.display.update(g.draw(pygame.display.get_surface()))
            
        pygame.display.flip()
        pygame.display.set_caption("Score: %i    FPS: %f" % (score, round(self.fpsTimer.get_fps(), 3)))
            
        self.fpsTimer.tick(60 * config.limit_frame)


    def add_ufo(self):
        if config.debug and self.ufo.state == ufo.UFO.STATES.IDLE:
        #If we're in debug mode and the UFO is not active...
            ENEMIES.add(self.ufo)
            self.ufo.state = ufo.UFO.STATES.APPEARING
            
    def make_block(self, pos, c):
        BLOCKS.add(block.Block((pos, 0), c))
        
    def clear_blocks(self):
        if config.debug:
        #If we're in debug mode...
            blockgrid.blocks.clear()

    def game_over(self):
        enemy.Enemy.velocity = [0, 0]
        gameovertext         = hudobject.HudObject(config.FONT.render("GAME OVER", False, color.WHITE).convert(config.DEPTH, config.FLAGS),
                                                   pygame.Rect(config.SCREEN_WIDTH/2, config.SCREEN_HEIGHT/2, 0, 0)
                                                   )
        self.ship.state      = player.STATES.DYING
        HUD.add(gameovertext)

