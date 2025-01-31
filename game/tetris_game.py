#tetris_game.py

import pygame
import random

from .grid import Grid
from .shape import Shape
from .settings import global_settings
from .constants import *

class TetrisGame:
    def __init__(self, initial_move_delay_horizontal=global_settings["initial_move_delay_horizontal"], accelerated_move_delay_horizontal=global_settings["accelerated_move_delay_horizontal"],
                 initial_move_delay_vertical=global_settings["initial_move_delay_vertical"], accelerated_move_delay_vertical=global_settings["accelerated_move_delay_vertical"], acceleration_threshold=global_settings["acceleration_threshold"]):
        self.clock = pygame.time.Clock()
        self.grid = Grid(GRID_WIDTH, GRID_HEIGHT)
        self.bag = self.generate_bag()
        self.next_shapes = [self.get_next_shape() for _ in range(3)]
        self.current_shape = self.get_next_shape()
        self.current_x = GRID_WIDTH // 2 - len(self.current_shape.shape[0]) // 2
        self.current_y = 0
        self.held_shape = None
        self.held_color = None
        self.held_used = False
        self.game_over = False
        self.fall_time = 0
        self.move_time_horizontal = 0
        self.move_time_vertical = 0
        self.initial_move_delay_horizontal = initial_move_delay_horizontal
        self.accelerated_move_delay_horizontal = accelerated_move_delay_horizontal
        self.initial_move_delay_vertical = initial_move_delay_vertical
        self.accelerated_move_delay_vertical = accelerated_move_delay_vertical
        self.acceleration_threshold = acceleration_threshold
        self.last_time = pygame.time.get_ticks()
        self.score = 0
        self.level = 1
        self.lines_cleared = 0

    def generate_bag(self):
        shapes = list(SHAPES.keys())
        random.shuffle(shapes)
        return shapes

    def get_next_shape(self):
        if not self.bag:
            self.bag = self.generate_bag()
        shape_name = self.bag.pop(0)
        shape = SHAPES[shape_name]
        color = SHAPE_COLORS[shape_name]
        return Shape(shape, color)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    rotated_shape = self.current_shape.rotate()
                    if self.grid.valid_move(rotated_shape.shape, self.current_x, self.current_y):
                        self.current_shape = rotated_shape
                if event.key == pygame.K_SPACE:
                    while self.grid.valid_move(self.current_shape.shape, self.current_x, self.current_y + 1):
                        self.current_y += 1
                    self.place_current_shape()
                    self.clear_lines()
                    self.spawn_new_shape()
                    if not self.grid.valid_move(self.current_shape.shape, self.current_x, self.current_y):
                        self.game_over = True
                        break
                if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                    if not self.held_used:
                        if self.held_shape is None:
                            self.held_shape = self.current_shape
                            self.held_color = self.current_shape.color
                            self.spawn_new_shape()
                        else:
                            self.held_shape, self.current_shape = self.current_shape, self.held_shape
                            self.held_color, self.current_shape.color = self.current_shape.color, self.held_color
                        self.current_x = GRID_WIDTH // 2 - len(self.current_shape.shape[0]) // 2
                        self.current_y = 0
                        self.held_used = True
                if event.key == pygame.K_r:
                    self.__init__()
                    return None
                if event.key == pygame.K_ESCAPE:
                    return "menu"
        return None

    def handle_key_presses(self):
        keys = pygame.key.get_pressed()
        horizontal_move_delay = self.initial_move_delay_horizontal
        vertical_move_delay = self.initial_move_delay_vertical
        current_time = pygame.time.get_ticks()
        time_passed = current_time - self.last_time
        self.last_time = current_time
        if keys[pygame.K_LEFT]:
            if self.grid.valid_move(self.current_shape.shape, self.current_x - 1, self.current_y):
                if self.move_time_horizontal == 0 or self.move_time_horizontal >= horizontal_move_delay:
                    self.current_x -= 1
                    self.move_time_horizontal = 0
                if self.move_time_horizontal >= self.acceleration_threshold:
                    horizontal_move_delay = self.accelerated_move_delay_horizontal
        if keys[pygame.K_RIGHT]:
            if self.grid.valid_move(self.current_shape.shape, self.current_x + 1, self.current_y):
                if self.move_time_horizontal == 0 or self.move_time_horizontal >= horizontal_move_delay:
                    self.current_x += 1
                    self.move_time_horizontal = 0
                if self.move_time_horizontal >= self.acceleration_threshold:
                    horizontal_move_delay = self.accelerated_move_delay_horizontal
        if keys[pygame.K_DOWN]:
            if self.grid.valid_move(self.current_shape.shape, self.current_x, self.current_y + 1):
                if self.move_time_vertical == 0 or self.move_time_vertical >= vertical_move_delay:
                    self.current_y += 1
                    self.move_time_vertical = 0
                if self.move_time_vertical >= self.acceleration_threshold:
                    vertical_move_delay = self.accelerated_move_delay_vertical
        self.move_time_horizontal += time_passed
        self.move_time_vertical += time_passed
        self.fall_time += time_passed

    def place_current_shape(self):
        self.grid.place_shape(self.current_shape.shape, self.current_x, self.current_y)

    def clear_lines(self):
        lines_cleared = self.grid.clear_lines()
        if lines_cleared > 0:
            self.score += SCORE_TABLE.get(lines_cleared, 0)
            self.lines_cleared += lines_cleared
            # Увеличиваем уровень каждые 10 очищенных линий
            if self.lines_cleared >= self.level * 10:
                self.level += 1
                self.initial_move_delay_vertical = max(50, self.initial_move_delay_vertical - 20)  # Увеличиваем скорость

    def spawn_new_shape(self):
        self.current_shape = self.next_shapes.pop(0)
        self.next_shapes.append(self.get_next_shape())
        self.current_x = GRID_WIDTH // 2 - len(self.current_shape.shape[0]) // 2
        self.current_y = 0
        self.held_used = False

    def update_falling_shape(self):
        if self.fall_time / 1000 >= (1 / self.level):  # Регулируем скорость падения в зависимости от уровня
            if self.grid.valid_move(self.current_shape.shape, self.current_x, self.current_y + 1):
                self.current_y += 1
            else:
                self.place_current_shape()
                self.clear_lines()
                self.spawn_new_shape()
            if not self.grid.valid_move(self.current_shape.shape, self.current_x, self.current_y):
                self.game_over = True
            self.fall_time = 0

    def draw_shadow(self, screen, x_offset=0):
        shadow_y = self.current_y
        while self.grid.valid_move(self.current_shape.shape, self.current_x, shadow_y + 1):
            shadow_y += 1
        self.current_shape.draw(screen, self.current_x + x_offset // GRID_SIZE, shadow_y, alpha=128)

    def draw_held_info(self, screen):
        # Позиция для отрисовки удержанной фигуры
        offset_x = 10  # Отступ от игрового поля
        offset_y = 40  # Отступ сверху
        pygame.draw.rect(screen, GRAY, (offset_x, offset_y, GRID_SIZE * 4, GRID_SIZE * 4), 1)
        if self.held_shape is not None:

            # Рисуем удержанную фигуру
            for i, row in enumerate(self.held_shape.shape):
                for j, cell in enumerate(row):
                    if cell:
                        # Рассчитываем позицию каждого блока фигуры
                        block_x = offset_x + j * GRID_SIZE
                        block_y = offset_y + i * GRID_SIZE
                        pygame.draw.rect(screen, self.held_shape.color, (block_x, block_y, GRID_SIZE, GRID_SIZE))
                        pygame.draw.rect(screen, GRAY, (block_x, block_y, GRID_SIZE, GRID_SIZE), 1)

    def draw_next_shapes(self, screen):
        offset_x = (GRID_WIDTH * GRID_SIZE) // 2  # Отступ от игрового поля
        offset_y = 40  # Отступ сверху
        spacing = GRID_SIZE * 4  # Расстояние между фигурами

        for idx, shape in enumerate(self.next_shapes):
            # Рассчитываем позицию для каждой фигуры
            x = offset_x
            y = offset_y + idx * spacing

            # Рисуем фон для каждой фигуры (опционально)
            pygame.draw.rect(screen, GRAY, (x, y, GRID_SIZE * 4, GRID_SIZE * 4), 1)

            # Рисуем фигуру
            for i, row in enumerate(shape.shape):
                for j, cell in enumerate(row):
                    if cell:
                        # Рассчитываем позицию каждого блока фигуры
                        block_x = x + j * GRID_SIZE
                        block_y = y + i * GRID_SIZE
                        pygame.draw.rect(screen, shape.color, (block_x, block_y, GRID_SIZE, GRID_SIZE))
                        pygame.draw.rect(screen, GRAY, (block_x, block_y, GRID_SIZE, GRID_SIZE), 1)

    def draw_info_window(self, screen, x_offset=0):
        info_surface = pygame.Surface((SCREEN_WIDTH - GRID_WIDTH * GRID_SIZE + x_offset, SCREEN_HEIGHT))
        info_surface.fill(BLACK)
        font = pygame.font.Font(None, 36)
        held_text = font.render("Удержано", True, WHITE)
        next_text = font.render("Следующие", True, WHITE)
        score_text = font.render(f"Очки: {self.score}", True, WHITE)
        level_text = font.render(f"Уровень: {self.level}", True, WHITE)
        info_surface.blit(held_text, (10, 10))
        info_surface.blit(next_text, (150, 10))
        info_surface.blit(score_text, (10, 300))
        info_surface.blit(level_text, (10, 350))
        self.draw_held_info(info_surface)
        self.draw_next_shapes(info_surface)
        screen.blit(info_surface, (GRID_WIDTH * GRID_SIZE + x_offset, 0))


    def main_loop(self, screen):
        while not self.game_over:
            screen.fill(BLACK)
            result = self.handle_events()
            if result is not None:
                return result
            self.handle_key_presses()
            self.update_falling_shape()
            self.grid.draw(screen)
            self.draw_shadow(screen)
            self.current_shape.draw(screen, self.current_x, self.current_y)
            self.draw_info_window(screen)
            pygame.display.flip()
            self.clock.tick(60)

        # После проигрыша показываем экран Game Over
        result = self.show_game_over_screen(screen)
        return result  # Возвращаем результат в run_game

    def show_game_over_screen(self, screen):
        while True:
            screen.fill(BLACK)
            game_over_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            game_over_surface.fill(BLACK)
            font = pygame.font.Font(None, 72)
            game_over_text = font.render("Игра окончена", True, WHITE)
            restart_text = font.render("Нажмите R для перезапуска", True, WHITE)
            menu_text = font.render("Нажмите ESC для выхода в меню", True, WHITE)
            score_text = font.render(f"Финальный счет: {self.score}", True, WHITE)
            game_over_surface.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2,
                                                    SCREEN_HEIGHT // 2 - game_over_text.get_height() // 2 - 100))
            game_over_surface.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2,
                                                SCREEN_HEIGHT // 2 - score_text.get_height() // 2 - 50))
            game_over_surface.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2,
                                                  SCREEN_HEIGHT // 2 - restart_text.get_height() // 2 + 50))
            game_over_surface.blit(menu_text, (SCREEN_WIDTH // 2 - menu_text.get_width() // 2,
                                               SCREEN_HEIGHT // 2 - menu_text.get_height() // 2 + 100))
            screen.blit(game_over_surface, (0, 0))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return True  # Выход из игры
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        # Перезапуск игры
                        self.__init__(
                            initial_move_delay_horizontal=global_settings["initial_move_delay_horizontal"],
                            accelerated_move_delay_horizontal=global_settings["accelerated_move_delay_horizontal"],
                            initial_move_delay_vertical=global_settings["initial_move_delay_vertical"],
                            accelerated_move_delay_vertical=global_settings["accelerated_move_delay_vertical"],
                            acceleration_threshold=global_settings["acceleration_threshold"]
                        )
                        return "restart"  # Возвращаем "restart" для перезапуска
                    if event.key == pygame.K_ESCAPE:
                        return "menu"  # Возврат в главное меню