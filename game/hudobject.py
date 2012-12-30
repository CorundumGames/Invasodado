import pygame.sprite

import core.config as config
import core.color  as color
import gameobject

class HudObject(gameobject.GameObject):
    '''HudObject is meant for displays like lives, score, etc.
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
    def make_text(text, pos, color = color.WHITE, font = fonts[0], vspace = 8):
        '''
        text is the text we want visible to the user.  If text is an iterable,
        each entry is on another line.
        
        pos is where the topleft corner of the pygame.Surface should be.
        
        color is the color of the text.
        
        font is the font used; it defaults to the first font entry
        
        vspace is the space between line in pixels.  Ignored if we only make one line.
        '''
        if isinstance(text, str):
            return HudObject(font.render(text, False, color).convert(config.DEPTH, config.FLAGS), pos)
        else:
            a = []
            for t in xrange(len(text)):
                a.append(HudObject(font.render(text[t], False, color).convert(config.DEPTH, config.FLAGS), (pos[0], pos[1] + vspace*t)))
            return a