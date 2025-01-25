import pygame
import random

# Инициализация PyGame
pygame.init()

# Константы
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
GRID_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
SHADOW_GRAY = (50, 50, 50)
SHAPE_COLORS = {
    "I": (0, 255, 0),
    "O": (0, 0, 255),
    "T": (255, 0, 0),
    "L": (255, 255, 0),
    "J": (255, 165, 0),
    "S": (0, 255, 255),
    "Z": (128, 0, 128)
}
SHAPES = {
    "I": [[1, 1, 1, 1]],
    "O": [[1, 1], [1, 1]],
    "T": [[0, 1, 0], [1, 1, 1]],
    "L": [[0, 0, 1], [1, 1, 1]],
    "J": [[1, 0, 0], [1, 1, 1]],
    "S": [[1, 1, 0], [0, 1, 1]],
    "Z": [[0, 1, 1], [1, 1, 0]]
}

# Система подсчета очков
SCORE_TABLE = {
    1: 100,  # Очки за очистку 1 линии
    2: 300,  # Очки за очистку 2 линий
    3: 500,  # Очки за очистку 3 линий
    4: 800   # Очки за очистку 4 линий (Тетрис)
}

# Глобальные настройки
global_settings = {
    "initial_move_delay_horizontal": 100,
    "accelerated_move_delay_horizontal": 10,
    "initial_move_delay_vertical": 150,
    "accelerated_move_delay_vertical": 50,
    "acceleration_threshold": 50
}

# Создание экрана
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tetris")

# Класс InputBox (для меню настроек)
class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = GRAY
        self.text = text
        self.font = pygame.font.Font(None, 36)
        self.txt_surface = self.font.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = WHITE if self.active else GRAY
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    print(self.text)  # Для отладки, можно обработать ввод здесь
                    self.text = ''
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.txt_surface = self.font.render(self.text, True, self.color)

    def update(self):
        width = max(200, self.txt_surface.get_width() + 10)
        self.rect.w = width

    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(screen, self.color, self.rect, 2)

# Класс Grid
class Grid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[BLACK for _ in range(width)] for _ in range(height)]

    def clear_lines(self):
        new_grid = [row for row in self.grid if any(cell == BLACK for cell in row)]
        num_cleared_lines = self.height - len(new_grid)
        self.grid[:num_cleared_lines] = [[BLACK for _ in range(self.width)] for _ in range(num_cleared_lines)]
        self.grid[num_cleared_lines:] = new_grid
        return num_cleared_lines

    def place_shape(self, shape, x, y, color):
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    self.grid[y + i][x + j] = color

    def valid_move(self, shape, x, y):
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    if x + j < 0 or x + j >= self.width or y + i >= self.height or self.grid[y + i][x + j] != BLACK:
                        return False
        return True

    def draw(self, screen):
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                pygame.draw.rect(screen, cell, (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE), 0)
                pygame.draw.rect(screen, GRAY, (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE), 1)

# Класс Shape
class Shape:
    def __init__(self, shape, color):
        self.shape = shape
        self.color = color

    def rotate(self):
        return Shape([list(reversed(col)) for col in zip(*self.shape)], self.color)

    def draw(self, screen, x, y, alpha=255):
        surface = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)
        surface.fill((*self.color, alpha))
        for i, row in enumerate(self.shape):
            for j, cell in enumerate(row):
                if cell:
                    screen.blit(surface, ((x + j) * GRID_SIZE, (y + i) * GRID_SIZE))

# Класс TetrisGame
class TetrisGame:
    def __init__(self, initial_move_delay_horizontal=100, accelerated_move_delay_horizontal=10,
                 initial_move_delay_vertical=150, accelerated_move_delay_vertical=50, acceleration_threshold=50):
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
        self.grid.place_shape(self.current_shape.shape, self.current_x, self.current_y, self.current_shape.color)

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

    def draw_shadow(self, screen):
        shadow_y = self.current_y
        while self.grid.valid_move(self.current_shape.shape, self.current_x, shadow_y + 1):
            shadow_y += 1
        self.current_shape.draw(screen, self.current_x, shadow_y, alpha=128)

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

    def draw_info_window(self, screen):
        info_surface = pygame.Surface((SCREEN_WIDTH - GRID_WIDTH * GRID_SIZE, SCREEN_HEIGHT))
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
        screen.blit(info_surface, (GRID_WIDTH * GRID_SIZE, 0))

    def main_loop(self):
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
        result = self.show_game_over_screen()
        return result  # Возвращаем результат в run_game

    def show_game_over_screen(self):
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

# Меню настроек с InputBox
def show_settings_menu():
    # InputBox с значениями по умолчанию из global_settings
    input_boxes = [
        InputBox(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 8, 200, 40,
                 str(global_settings["initial_move_delay_horizontal"])),
        InputBox(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 8 + 80, 200, 40,
                 str(global_settings["accelerated_move_delay_horizontal"])),
        InputBox(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 8 + 160, 200, 40,
                 str(global_settings["initial_move_delay_vertical"])),
        InputBox(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 8 + 240, 200, 40,
                 str(global_settings["accelerated_move_delay_vertical"])),
        InputBox(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 8 + 320, 200, 40,
                 str(global_settings["acceleration_threshold"]))
    ]

    # Кнопка "Назад"
    back_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 150, 200, 40)

    while True:
        screen.fill(BLACK)
        font = pygame.font.Font(None, 36)

        # Заголовок настроек
        settings_title_text = font.render("Настройки", True, WHITE)
        screen.blit(settings_title_text,
                    (settings_title_text.get_width() // 2, SCREEN_HEIGHT // 8))

        # Текстовые пояснения для каждого InputBox
        explanations = [
            "Начальная задержка по горизонтали (мс):",
            "Ускоренная задержка по горизонтали (мс):",
            "Начальная задержка по вертикали (мс):",
            "Ускоренная задержка по вертикали (мс):",
            "Порог ускорения (мс):"
        ]

        # Рисуем пояснения для InputBox
        for i, box in enumerate(input_boxes):
            # Рисуем пояснительный текст
            explanation_text = font.render(explanations[i], True, WHITE)
            screen.blit(explanation_text, (SCREEN_WIDTH // 2 - 250, box.rect.y - 30))

            # Рисуем InputBox
            box.draw(screen)

        # Кнопка "Назад"
        pygame.draw.rect(screen, GRAY, back_button_rect)
        back_text = font.render("Назад", True, WHITE)
        screen.blit(back_text, (back_button_rect.x + 70, back_button_rect.y + 10))

        # Обработка наведения мыши на кнопку "Назад"
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]

        if back_button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, WHITE, back_button_rect, 2)
            if mouse_clicked:
                # Обновляем глобальные настройки новыми значениями
                global_settings["initial_move_delay_horizontal"] = int(input_boxes[0].text)
                global_settings["accelerated_move_delay_horizontal"] = int(input_boxes[1].text)
                global_settings["initial_move_delay_vertical"] = int(input_boxes[2].text)
                global_settings["accelerated_move_delay_vertical"] = int(input_boxes[3].text)
                global_settings["acceleration_threshold"] = int(input_boxes[4].text)
                return None  # Возврат в главное меню

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True

            for box in input_boxes:
                box.handle_event(event)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button_rect.collidepoint(event.pos):
                    # Обновляем глобальные настройки новыми значениями
                    global_settings["initial_move_delay_horizontal"] = int(input_boxes[0].text)
                    global_settings["accelerated_move_delay_horizontal"] = int(input_boxes[1].text)
                    global_settings["initial_move_delay_vertical"] = int(input_boxes[2].text)
                    global_settings["accelerated_move_delay_vertical"] = int(input_boxes[3].text)
                    global_settings["acceleration_threshold"] = int(input_boxes[4].text)

                    return None  # Возврат в главное меню

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None  # Возврат в главное меню

        pygame.display.flip()

# Главное меню
def show_menu():
    while True:
        screen.fill(BLACK)
        font = pygame.font.Font(None, 72)
        title_text = font.render("Тетрис", True, WHITE)
        start_text = font.render("Начать игру", True, WHITE)
        settings_text = font.render("Настройки", True, WHITE)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 2 - 150))
        screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(settings_text, (SCREEN_WIDTH // 2 - settings_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]

        # Определяем прямоугольники кнопок
        start_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50,
                                        start_text.get_width(), start_text.get_height())
        settings_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - settings_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50,
                                           settings_text.get_width(), settings_text.get_height())

        # Подсветка кнопок при наведении
        if start_button_rect.collidepoint(mouse_pos):
            start_text = font.render("Начать игру", True, GRAY)
            screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            if mouse_clicked:
                return None  # Начать игру

        if settings_button_rect.collidepoint(mouse_pos):
            settings_text = font.render("Настройки", True, GRAY)
            screen.blit(settings_text, (SCREEN_WIDTH // 2 - settings_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
            if mouse_clicked:
                return "settings"  # Перейти в меню настроек

        pygame.display.flip()

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True  # Выход из игры
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return None  # Начать игру

# Запуск игры
def run_game():
    while True:
        # Показываем главное меню и ждем ввода пользователя
        menu_result = show_menu()

        # Если пользователь выходит из главного меню, завершаем игру
        if menu_result is True:
            break

        # Если пользователь выбирает "Настройки" в главном меню
        elif menu_result == "settings":
            # Показываем меню настроек и ждем ввода пользователя
            settings_result = show_settings_menu()

            # Если пользователь выходит из меню настроек, завершаем игру
            if settings_result is True:
                break

            # Если пользователь выходит из меню настроек (без выхода), возвращаемся в главное меню
            elif settings_result is None:
                continue  # Возврат в главное меню

        # Если пользователь выбирает "Начать игру" в главном меню
        elif menu_result is None:
            # Инициализируем игру с глобальными настройками
            game = TetrisGame(
                initial_move_delay_horizontal=global_settings["initial_move_delay_horizontal"],
                accelerated_move_delay_horizontal=global_settings["accelerated_move_delay_horizontal"],
                initial_move_delay_vertical=global_settings["initial_move_delay_vertical"],
                accelerated_move_delay_vertical=global_settings["accelerated_move_delay_vertical"],
                acceleration_threshold=global_settings["acceleration_threshold"]
            )

            # Запускаем игровой цикл
            result = game.main_loop()

            # Обрабатываем результат игрового цикла
            if result is True:  # Если пользователь выходит из игры
                break
            elif result == "menu":  # Если пользователь возвращается в главное меню
                continue
            elif result == "restart":  # Если пользователь перезапускает игру
                continue  # Перезапускаем игру

if __name__ == "__main__":
    run_game()
    pygame.quit()