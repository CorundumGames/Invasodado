import pygame.sprite

from core            import config
from core            import color
from game.gameobject import GameObject

class HudObject(GameObject):
    '''
    HudObject is meant for displays like lives, score, etc.

    It is its own type so it can be in collisions._do_not_check, because we
    don't intend for these to collide with anything.
    '''
    STATES = config.Enum('IDLE')
    fonts  = (config.FONT,)
    
    def __init__(self, image, pos):
        super().__init__()
        self.image = image#
        self.rect  = pygame.Rect(pos, image.get_size())
        del self.velocity, self.acceleration, self.position, self.next_state

    def update(self):
        '''
        Since HudObjects have no functionality, let's make update() do nothing!
        '''
        pass

    @staticmethod
    def make_text(text, pos=(0, 0), col=color.WHITE, font=fonts[0], vspace=8, surfaces=False):
        '''
        @param text: The text we want visible to the user. If a list, one element per line
        @param pos: The topleft corner of the position rect
        @param col: The color of the text
        @param font: The font used; it defaults to the first font entry
        @param vspace: Space between lines in pixels. Ignored if only one line.
        @param surfaces: True if we want Surfaces instead of HudObjects (pos is then ignored)

        @return: list(pygame.Surface) if surfaces else list(HudObject)
        '''

        if isinstance(text, str):
        #If we were given a single string...
            hud = font.render(text, False, col).convert(config.DEPTH, config.FLAGS)
            return hud if surfaces else HudObject(hud, pos)
        else:
            def d(t):
                hud = font.render(text[t], False, col).convert(config.DEPTH, config.FLAGS)
                return hud if surfaces else HudObject(hud, (pos[0], pos[1] + vspace * t))

            return [d(i) for i in range(len(text))]