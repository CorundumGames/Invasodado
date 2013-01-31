import pygame.sprite

from core import config
from core import color
from game import gameobject

class HudObject(gameobject.GameObject):
    '''
    HudObject is meant for displays like lives, score, etc.

    It is its own type so it can be in collisions.do_not_check, because we
    don't intend for these to collide with anything.
    '''
    actions    = None
    collisions = None
    fonts      = [config.FONT]

    def __init__(self, image, pos):
        pygame.sprite.Sprite.__init__(self)
        self.acceleration = None
        self.image        = image
        self.position     = None
        self.rect         = pygame.Rect(pos, image.get_size())
        self.state        = None
        self.velocity     = None

    def update(self):
        pass

    @staticmethod
    def make_text(text, pos = (0, 0), color = color.WHITE, font = fonts[0], vspace = 8, surfaces = False):
        '''
        @param text: The text we want visible to the user. If a list, one element per line
        @param pos: The topleft corner of the position rect
        @param color: The color of the text
        @param font: The font used; it defaults to the first font entry
        @param vspace: Space between lines in pixels. Ignored if only one line.
        @param surfaces: True if we want Surfaces instead of HudObjects (pos is then ignored)

        @return: list(pygame.Surface) if surfaces else list(HudObject)
        '''

        if isinstance(text, basestring):
        #If we were given a single string...
            a = font.render(text, False, color).convert(config.DEPTH, config.FLAGS)
            return a if surfaces else HudObject(a, pos)
        else:
            def d(t):
                c = font.render(text[t], False, color).convert(config.DEPTH, config.FLAGS)
                return c if surfaces else HudObject(c, (pos[0], pos[1] + vspace*t))

            return map(d, range(len(text)))