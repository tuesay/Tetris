# grid.py

import pygame

from .constants import *


class Grid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[0 for _ in range(width)] for _ in range(height)]

    def clear_lines(self):
        new_grid = [row for row in self.grid if any(cell == 0 for cell in row)]
        num_cleared_lines = self.height - len(new_grid)
        self.grid[:num_cleared_lines] = [
            [0 for _ in range(self.width)] for _ in range(num_cleared_lines)]
        self.grid[num_cleared_lines:] = new_grid
        return num_cleared_lines

    def place_shape(self, shape, x, y):
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    self.grid[y + i][x + j] = 1

    def valid_move(self, shape, x, y):
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    if x + j < 0 or x + j >= self.width or y + \
                            i >= self.height or self.grid[y + i][x + j] != 0:
                        return False
        return True

    def draw(self, screen, x_offset=0):
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                color = BLACK if cell == 0 else WHITE
                pygame.draw.rect(
                    screen,
                    color,
                    (x *
                     GRID_SIZE +
                     x_offset,
                     y *
                     GRID_SIZE,
                     GRID_SIZE,
                     GRID_SIZE),
                    0)
                pygame.draw.rect(
                    screen,
                    GRAY,
                    (x *
                     GRID_SIZE +
                     x_offset,
                     y *
                     GRID_SIZE,
                     GRID_SIZE,
                     GRID_SIZE),
                    1)
