from pygame.constants import *
from pygame           import display
from pygame.sprite    import Group

from core import color
from core import config

from core.config    import screen, _limit_frame
from core.gamestate import GameState
from game.hudobject import HudObject
from game.mainmenu  import MainMenu

### Groups #####################################################################
DIAMOND = Group()
################################################################################

### Constants ##################################################################
LOGO = config.load_image('logo.png')
BOOT = config.load_sound('boot.ogg')
################################################################################

### Preparation ################################################################

################################################################################

class SplashScreen(GameState):
    def __init__(self):
        self.alpha_percent = 0.0
        self.group_list    = (DIAMOND,)
        self.logo          = HudObject(LOGO, [0, 0])
        self.start_time    = 5 * 60  #In frames
        
        BOOT.play()
        self.logo.rect.center = config.SCREEN_RECT.center
        self.logo.image.set_alpha(0)
        DIAMOND.add(self.logo)
        
    def __del__(self):
        BOOT.stop()
        super().__del__()
        
    def events(self, events):
        for e in events:
        #For all input events received...
            if e.type in {KEYDOWN, MOUSEBUTTONDOWN}:
            #If the user presses any button...
                self.change_state(MainMenu)
        
    def logic(self):
        self.start_time    -= 1
        self.alpha_percent += 1
        self.logo.image.set_alpha(self.alpha_percent)
        if not self.start_time:
        #Once the logo's finished fading in...
            self.change_state(MainMenu)
    
    def render(self):
        screen.fill(color.WHITE)
        
        for i in self.group_list:
            i.draw(screen)

        display.flip()
        assert not config.show_fps()
        #^ So this statement is stripped in Release mode.

        config.fps_timer.tick_busy_loop(60 * _limit_frame)
