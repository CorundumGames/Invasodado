import itertools

import pygame

import config
import block

CELL_SIZE  = (16, 16)
DIMENSIONS = (config.screen.get_width()/CELL_SIZE[0], 24)
LOCATION   = (0, 0)
RECT       = pygame.rect.Rect(LOCATION, (DIMENSIONS[0]*CELL_SIZE[0], DIMENSIONS[1]*CELL_SIZE[1]))

blocks = [[None for i in range(DIMENSIONS[0])] for j in range(DIMENSIONS[1])]
        
def clear(self):
    for i in blocks:
        for j in itertools(lambda x: x != None, j):
            j = None