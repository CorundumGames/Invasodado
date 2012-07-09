import enum
import pygame
import enemy

ROW_SIZE = 10
COL_SIZE = 8

enemies = [[enemy.Enemy((i, j)) for i in range(ROW_SIZE)] for j in range(COL_SIZE)]

