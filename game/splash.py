from functools import partial
from os.path   import join

import pygame
from pygame.sprite import Group

from core import config
from core.config import screen, _limit_frame
from core.gamestate import GameState
from game.hudobject import HudObject
from game.mainmenu import MainMenu

### Groups #####################################################################
DIAMOND = Group()
LETTERS = Group()
################################################################################

### Constants ##################################################################
LOGO = pygame.image.load(join('gfx', 'logo.png'))
BOOT = pygame.mixer.Sound(join('sfx', 'boot.wav'))
################################################################################

### Preparation ################################################################

################################################################################

class SplashScreen(GameState):
    def __init__(self):
        self.group_list = (DIAMOND, LETTERS)
        self.logo       = HudObject(LOGO, [0, 0])
        self.start_time = 5 * 60
        self.alpha_percent = 0.0
        
        self.logo.rect.center = config.SCREEN_RECT.center
        self.logo.image.set_alpha(0)
        DIAMOND.add(self.logo)
        BOOT.play()
        
    def __del__(self):
        BOOT.stop()
        super().__del__()
        
    def events(self, events):
        for e in events:
            if e.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                self.change_state(MainMenu)
        
    def logic(self):
        self.start_time -= 1
        self.alpha_percent += 1
        self.logo.image.set_alpha(self.alpha_percent)
        if not self.start_time:
            self.change_state(MainMenu)
    
    def render(self):
        screen.fill((255, 255, 255))
        
        for i in self.group_list:
            i.draw(screen)

        pygame.display.flip()
        assert not config.show_fps(self.fps_timer.get_fps())
        #^ So this statement is stripped in Release mode.

        self.fps_timer.tick_busy_loop(60 * _limit_frame)