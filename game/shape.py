# shape.py

import pygame

from .constants import GRID_SIZE


class Shape:
    def __init__(self, shape, color):
        self.shape = shape
        self.color = color

    def rotate(self):
        return Shape([list(reversed(col))
                     for col in zip(*self.shape)], self.color)

    def draw(self, screen, x, y, alpha=255, x_offset=0):
        surface = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)
        surface.fill((*self.color, alpha))
        for i, row in enumerate(self.shape):
            for j, cell in enumerate(row):
                if cell:
                    screen.blit(
                        surface, (((x + j) * GRID_SIZE) + x_offset, (y + i) * GRID_SIZE))
