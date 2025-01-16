# импорты
from settings import *
from tetromino import Block, Tetromino
from game_mechanics import bag7
from timer import Timer


class Game:
    def __init__(self):

        self.surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
        self.screen = pygame.display.get_surface()

        self.danger_surface = self.surface.copy()
        self.danger_surface.fill((0, 255, 0))
        self.danger_surface.set_colorkey((0, 255, 0))
        self.danger_surface.set_alpha(200)

        self.grid_surface = self.surface.copy()
        self.grid_surface.fill((0, 255, 0))
        self.grid_surface.set_colorkey((0, 255, 0))
        self.grid_surface.set_alpha(90)

        # tetrominoes
        self.bag = None
        self.bag_next()
        self.tetrominoes = pygame.sprite.Group()
        self.field_data = [[0 for x in range(COLUMNS)] for y in range(ROWS)]
        self.tetromino = Tetromino(self.bag.pop(0), self.tetrominoes, self.field_data)


        # таймеры
        self.timers = {
            'vertical move': Timer(UPDATE_START_SPEED, True, self.move_down),
            'horizontal move': Timer(MOVE_WAIT_TIME),
            'input_downwards': Timer(MOVE_WAIT_TIME_DOWNWARDS),
            'rotate': Timer(ROTATE_WAIT)
        }

        self.timers['vertical move'].activate()

    def bag_next(self):
        if self.bag is None:
            self.bag = bag7()
            print('first creation of a bag')
        elif len(self.bag) == 0:
            self.bag = bag7()
            print('recreated a new bag')
        else:
            self.check_rows()
            self.tetromino = Tetromino(self.bag.pop(0), self.tetrominoes, self.field_data)

    def timer_update(self):
        for timer in self.timers.values():
            timer.update()

    def move_down(self):
        if self.tetromino.move_down() == 'already moved':
            self.bag_next()

    def danger_area(self):

        # коробка без крышки вокруг поля игрока (строится учитывая количество блоков до опасной зоны)

        pygame.draw.lines(self.danger_surface, WHITE, False,
                          [(0, BLOCK_SIZE * DANGER_AREA), (0, self.surface.get_height()),
                           (0, self.surface.get_height() - 1), (self.surface.get_width(), self.surface.get_height() - 1),
                           (self.surface.get_width() - 1, BLOCK_SIZE * DANGER_AREA),
                           (self.surface.get_width() - 1, self.surface.get_height())])

        self.surface.blit(self.danger_surface, (0, 0))

    def grid(self):

        # сетка поля

        for col in range(1, COLUMNS):
            x = BLOCK_SIZE * col
            pygame.draw.line(self.grid_surface, LIGHT_GRAY, (x, 0), (x, self.danger_surface.get_height()), 1)

        for row in range(1, ROWS):
            y = BLOCK_SIZE * row
            pygame.draw.line(self.grid_surface, LIGHT_GRAY, (0, y), (self.danger_surface.get_width(), y), 1)

        self.danger_surface.blit(self.grid_surface, (0, 0))

    def input(self):
        keys = pygame.key.get_pressed()

        if not self.timers['horizontal move'].active:
            if keys[pygame.K_LEFT]:
                self.tetromino.move_horizontal(-1)
                self.timers['horizontal move'].activate()

            if keys[pygame.K_RIGHT]:
                self.tetromino.move_horizontal(1)
                self.timers['horizontal move'].activate()

        if not self.timers['rotate'].active:
            if keys[pygame.K_z]:
                self.tetromino.rotate(-1)
                self.timers['rotate'].activate()

            if keys[pygame.K_x]:
                self.tetromino.rotate(1)
                self.timers['rotate'].activate()

        if not self.timers['input_downwards'].active:
            if keys[pygame.K_DOWN]:
                self.timers['vertical move'].deactivate()
                if self.tetromino.move_down() == 'already moved':
                    self.bag_next()
                self.timers['input_downwards'].activate()
                self.timers['vertical move'].activate()

    def check_rows(self):

        delete_rows = []
        for i, row in enumerate(self.field_data):
            if all(row):
                delete_rows.append(i)

        # delete full rows
        if delete_rows:
            for delete_row in delete_rows:
                for block in self.field_data[delete_row]:
                    block.kill()

                # move down blocks
                for row in self.field_data:
                    for block in row:
                        if block and block.pos.y < delete_row:
                            block.pos.y += 1

            self.field_data = [[0 for x in range(COLUMNS)] for y in range(ROWS)]
            for block in self.tetrominoes:
                self.field_data[int(block.pos.y)][int(block.pos.x)] = block

    def run(self):
        # update
        self.input()
        self.timer_update()
        self.tetrominoes.update()

        # move down timer active

        # draw section
        self.surface.fill(BLACK)
        self.danger_area()
        self.grid()
        self.tetrominoes.draw(self.surface)

        self.screen.blit(self.surface, (PADDING*2, PADDING*2))
