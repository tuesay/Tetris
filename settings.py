import pygame

DANGER_AREA = 3
COLUMNS = 10
ROWS = 20 + DANGER_AREA

BLOCK_SIZE = 40

GAME_WIDTH = COLUMNS * BLOCK_SIZE
GAME_HEIGHT = ROWS * BLOCK_SIZE

PADDING = 20

WINDOW_WIDTH = GAME_WIDTH + PADDING * 20
WINDOW_HEIGHT = GAME_HEIGHT + PADDING * 4

ACCELERATE = 20
ROTATE_WAIT = 200
MOVE_WAIT_TIME_DOWNWARDS = 50
MOVE_WAIT_TIME = 40
UPDATE_START_SPEED = 300
BLOCK_OFFSET = pygame.Vector2(COLUMNS // 2, -1)

WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
LIGHT_GRAY = (150, 150, 150)
BLACK = (0, 0, 0)
ORANGE = (255, 204, 153)
GREEN = (153, 255, 153)
LIGHT_BLUE = (153, 255, 255)
RED = (255, 153, 153)
PURPLE = (178, 102, 255)
BLUE = (51, 51, 255)
YELLOW = (255, 255, 51)

TETROMINOS = {
	'T': {'shape': [(0,0), (-1,0), (1,0), (0,-1)], 'color': PURPLE},
	'O': {'shape': [(0,0), (0,-1), (1,0), (1,-1)], 'color': YELLOW},
	'J': {'shape': [(0,0), (0,-1), (0,1), (-1,1)], 'color': BLUE},
	'L': {'shape': [(0,0), (0,-1), (0,1), (1,1)], 'color': ORANGE},
	'I': {'shape': [(0,0), (0,-1), (0,-2), (0,1)], 'color': LIGHT_BLUE},
	'S': {'shape': [(0,0), (-1,0), (0,-1), (1,-1)], 'color': GREEN},
	'Z': {'shape': [(0,0), (1,0), (0,-1), (-1,-1)], 'color': RED}
}