import random

import pygame.event
import pygame.display
import pygame.sprite

from core import color
from core import config
from core import gamestate

import bg
import ingame
import highscore
import hudobject
import settingsmenu

'''
This is where the user makes his decisions about what to do in the game.
Not really special compared to any other main menu.
'''

HUD  = pygame.sprite.Group()
MENU = pygame.sprite.Group()
BG   = pygame.sprite.OrderedUpdates()

DIST_APART = 64
#How far apart, vertically, the menu entries are (in pixels)

MENU_CORNER = (config.SCREEN_RECT.centerx - 112, config.SCREEN_RECT.centery - 64)
#The location of the top-left corner of the menu

class MainMenu(gamestate.GameState):
    def __init__(self):
        self.frame_limit = True
        #True if we're limiting the frame rate to 60 FPS

        self.selection    = 0

        self.group_list = [bg.STARS_GROUP, BG, HUD, MENU]

        self.hud_title = hudobject.HudObject.make_text("Invasodado", [config.SCREEN_RECT.centerx - 96, 32])

        #Will be replaced with a logo (aka an actual image) later.
        self.hud_selection  = hudobject.HudObject.make_text("->", (0, 0))

        self.menu = hudobject.HudObject.make_text(["Normal Mode",
                                                   "High Scores",
                                                   "Settings"   ,
                                                   "Quit"       ,],
                                                  pos = MENU_CORNER,
                                                  vspace = DIST_APART)

        self.menu_actions = [
                             self.__start_game      ,
                             self.__view_high_scores,
                             self.__settings_menu   ,
                             quit                   ,
                             ]

        self.key_actions  = {
                             pygame.K_RETURN : self.__enter_selection,
                             pygame.K_UP     : self.__move_up        ,
                             pygame.K_DOWN   : self.__move_down      ,
                             pygame.K_ESCAPE : quit                  ,
                             }



        HUD.add(self.hud_title, self.hud_selection)
        MENU.add(self.menu)
        BG.add(bg.EARTH, bg.GRID)

    def __del__(self):
        map(pygame.sprite.Group.empty, self.group_list)

        self.group_list = []

    def events(self, events):
        for e in events:
        #For all input we've received...
            if e.type == pygame.KEYDOWN and e.key in self.key_actions:
            #If a key was pressed...
                self.key_actions[e.key]()
                self.selection %= len(self.menu_actions)

    def logic(self):
        map(pygame.sprite.Group.update, self.group_list)

    def render(self):
        self.hud_selection.rect.midright = self.menu[self.selection].rect.midleft
        pygame.display.get_surface().fill((0, 0, 0))
        bg.STARS.emit()
        map(pygame.sprite.Group.draw, self.group_list, [pygame.display.get_surface()]*len(self.group_list))

        pygame.display.flip()
        pygame.display.set_caption("FPS: %f" % round(self.fps_timer.get_fps(), 3))

        self.fps_timer.tick(60 * self.frame_limit)

    def __enter_selection(self):
        '''Go with the selection the player made.'''
        self.menu_actions[self.selection]()

    def __start_game(self):
        '''Begin the game.'''
        self.next_state = ingame.InGameState()

    def __view_high_scores(self):
        '''Bring the player to the high score table.'''
        self.next_state = highscore.HighScoreState()

    def __move_up(self):
        '''Move the cursor up.'''
        #There should probably be some animation here later.
        self.selection -= 1

    def __move_down(self):
        '''Move the cursor down.'''
        #Likewise here.
        self.selection += 1

    def __settings_menu(self):
        self.next_state = settingsmenu.SettingsMenu()
