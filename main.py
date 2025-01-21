import pygame
import random

# Initialize PyGame
pygame.init()

# Constants
SCREEN_WIDTH = 900  # Increased width for displaying next shapes and held shape
SCREEN_HEIGHT = 600
GRID_SIZE = 30
GRID_WIDTH = 10  # Width of the playing field
GRID_HEIGHT = 20  # Height of the playing field
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)  # Light gray color for grid lines
SHADOW_GRAY = (50, 50, 50)  # Dark gray color for shadow
# Colors for each shape
SHAPE_COLORS = {
    "I": (0, 255, 0),  # Green
    "O": (0, 0, 255),  # Blue
    "T": (255, 0, 0),  # Red
    "L": (255, 255, 0),  # Yellow
    "J": (255, 165, 0),  # Orange
    "S": (0, 255, 255),  # Cyan
    "Z": (128, 0, 128)  # Purple
}
# Shapes
SHAPES = {
    "I": [[1, 1, 1, 1]],  # I
    "O": [[1, 1], [1, 1]],  # O
    "T": [[0, 1, 0], [1, 1, 1]],  # T
    "L": [[0, 0, 1], [1, 1, 1]],  # L
    "J": [[1, 0, 0], [1, 1, 1]],  # J
    "S": [[1, 1, 0], [0, 1, 1]],  # S
    "Z": [[0, 1, 1], [1, 1, 0]]  # Z
}
# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tetris")

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
                pygame.draw.rect(screen, GRAY, (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE), 1)  # Light gray borders

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

class TetrisGame:
    def __init__(self):
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
        self.initial_move_delay_horizontal = 100 # Initial horizontal move delay (in milliseconds)
        self.accelerated_move_delay_horizontal = 10  # Accelerated horizontal move delay (in milliseconds)
        self.initial_move_delay_vertical = 150  # Initial vertical move delay (in milliseconds)
        self.accelerated_move_delay_vertical = 50  # Accelerated vertical move delay (in milliseconds)
        self.acceleration_threshold = 50  # Threshold time for acceleration (in milliseconds)
        self.last_time = pygame.time.get_ticks()

    def generate_bag(self):
        print("First creation of a bag")
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
                return True  # Return True to quit the entire program
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    rotated_shape = self.current_shape.rotate()
                    if self.grid.valid_move(rotated_shape.shape, self.current_x, self.current_y):
                        self.current_shape = rotated_shape
                if event.key == pygame.K_SPACE:
                    # Fast drop of the shape
                    while self.grid.valid_move(self.current_shape.shape, self.current_x, self.current_y + 1):
                        self.current_y += 1
                    self.place_current_shape()
                    self.clear_lines()
                    self.spawn_new_shape()
                    if not self.grid.valid_move(self.current_shape.shape, self.current_x, self.current_y):
                        self.game_over = True
                        break  # Break out of the event loop after fast drop
                if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                    if not self.held_used:
                        if self.held_shape is None:
                            self.held_shape = self.current_shape
                            self.held_color = self.current_shape.color  # Сохраняем цвет текущей фигуры
                            self.spawn_new_shape()
                        else:
                            # Обмениваем фигуры и их цвета
                            self.held_shape, self.current_shape = self.current_shape, self.held_shape
                            self.held_color, self.current_shape.color = self.current_shape.color, self.held_color
                        self.current_x = GRID_WIDTH // 2 - len(self.current_shape.shape[0]) // 2
                        self.current_y = 0
                        self.held_used = True  # Set the flag for using the held shape
                if event.key == pygame.K_r:
                    # Restart the current game
                    self.__init__()  # Reinitialize the game state
                    return None  # Continue the game
                if event.key == pygame.K_ESCAPE:
                    # Go back to the menu
                    return "menu"  # Return "menu" to go back to the menu
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
                    self.move_time_horizontal = 0  # Reset time to prevent instant movement
                if self.move_time_horizontal >= self.acceleration_threshold:
                    horizontal_move_delay = self.accelerated_move_delay_horizontal
        if keys[pygame.K_RIGHT]:
            if self.grid.valid_move(self.current_shape.shape, self.current_x + 1, self.current_y):
                if self.move_time_horizontal == 0 or self.move_time_horizontal >= horizontal_move_delay:
                    self.current_x += 1
                    self.move_time_horizontal = 0  # Reset time to prevent instant movement
                if self.move_time_horizontal >= self.acceleration_threshold:
                    horizontal_move_delay = self.accelerated_move_delay_horizontal
        if keys[pygame.K_DOWN]:
            if self.grid.valid_move(self.current_shape.shape, self.current_x, self.current_y + 1):
                if self.move_time_vertical == 0 or self.move_time_vertical >= vertical_move_delay:
                    self.current_y += 1
                    self.move_time_vertical = 0  # Reset time to prevent instant movement
                if self.move_time_vertical >= self.acceleration_threshold:
                    vertical_move_delay = self.accelerated_move_delay_vertical
        self.move_time_horizontal += time_passed
        self.move_time_vertical += time_passed
        self.fall_time += time_passed

    def place_current_shape(self):
        self.grid.place_shape(self.current_shape.shape, self.current_x, self.current_y, self.current_shape.color)

    def clear_lines(self):
        lines_cleared = self.grid.clear_lines()
        # Optionally, handle scoring based on lines cleared

    def spawn_new_shape(self):
        self.current_shape = self.next_shapes.pop(0)
        self.next_shapes.append(self.get_next_shape())
        self.current_x = GRID_WIDTH // 2 - len(self.current_shape.shape[0]) // 2
        self.current_y = 0
        self.held_used = False  # Reset the flag for using the held shape

    def update_falling_shape(self):
        if self.fall_time / 1000 >= 1:
            if self.grid.valid_move(self.current_shape.shape, self.current_x, self.current_y + 1):
                self.current_y += 1
            else:
                self.place_current_shape()
                self.clear_lines()
                self.spawn_new_shape()
            if not self.grid.valid_move(self.current_shape.shape, self.current_x, self.current_y):
                self.game_over = True
            self.fall_time = 0  # Reset time after falling

    def draw_shadow(self, screen):
        shadow_y = self.current_y
        while self.grid.valid_move(self.current_shape.shape, self.current_x, shadow_y + 1):
            shadow_y += 1
        self.current_shape.draw(screen, self.current_x, shadow_y, alpha=128)

    def draw_held_shape(self, screen):
        if self.held_shape is not None:
            for i, row in enumerate(self.held_shape.shape):
                for j, cell in enumerate(row):
                    if cell:
                        self.held_shape.draw(screen, 1, 1)

    def draw_next_shapes(self, screen):
        offset_x = GRID_SIZE # Offset from the playing field
        offset_y = 200
        spacing = int(GRID_SIZE) * 3  # Spacing between shapes
        for idx, shape in enumerate(self.next_shapes):
            max_height = max(len(row) for row in shape.shape)
            max_width = len(shape.shape[0])
            x = offset_x // 2  # Center the shape horizontally
            y = offset_y + idx * spacing + (5 - max_height) * GRID_SIZE // 2  # Center the shape vertically
            for i, row in enumerate(shape.shape):
                for j, cell in enumerate(row):
                    if cell:
                        shape.draw(screen, x // GRID_SIZE, y // GRID_SIZE)

    def draw_info_window(self, screen):
        info_surface = pygame.Surface((SCREEN_WIDTH - GRID_WIDTH * GRID_SIZE, SCREEN_HEIGHT))
        info_surface.fill(BLACK)
        # Draw headers
        font = pygame.font.Font(None, 36)
        held_text = font.render("Held", True, WHITE)
        next_text = font.render("Next", True, WHITE)
        info_surface.blit(held_text, (10, 10))
        info_surface.blit(next_text, (10, 150))
        # Draw held shape
        self.draw_held_shape(info_surface)
        # Draw next shapes
        self.draw_next_shapes(info_surface)
        # Draw info window on the main screen
        screen.blit(info_surface, (GRID_WIDTH * GRID_SIZE, 0))

    def main_loop(self):
        while not self.game_over:
            print("Main loop iteration")
            screen.fill(BLACK)
            # Handle events
            result = self.handle_events()
            if result is not None:
                return result
            # Handle key presses
            self.handle_key_presses()
            # Update falling shape
            self.update_falling_shape()
            # Draw grid
            self.grid.draw(screen)
            # Draw shadow
            self.draw_shadow(screen)
            # Draw current shape
            self.current_shape.draw(screen, self.current_x, self.current_y)
            # Draw info window
            self.draw_info_window(screen)
            pygame.display.flip()
            self.clock.tick(592)  # Limit frame rate to 592 frames per second
        return self.show_game_over_screen()

    def show_game_over_screen(self):
        while True:
            screen.fill(BLACK)
            # Display game over message
            game_over_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            game_over_surface.fill(BLACK)
            font = pygame.font.Font(None, 72)
            game_over_text = font.render("Game Over", True, WHITE)
            restart_text = font.render("Press R to Restart", True, WHITE)
            menu_text = font.render("Press ESC to Menu", True, WHITE)
            game_over_surface.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2,
                                                    SCREEN_HEIGHT // 2 - game_over_text.get_height() // 2 - 50))
            game_over_surface.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2,
                                                    SCREEN_HEIGHT // 2 - restart_text.get_height() // 2))
            game_over_surface.blit(menu_text, (SCREEN_WIDTH // 2 - menu_text.get_width() // 2,
                                                    SCREEN_HEIGHT // 2 - menu_text.get_height() // 2 + 50))
            screen.blit(game_over_surface, (0, 0))
            pygame.display.flip()
            # Wait for the R key to restart the game or ESC to go back to the menu
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return True  # Return True to quit the entire program
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.__init__()  # Reinitialize the game state
                        return None  # Continue the game
                    if event.key == pygame.K_ESCAPE:
                        return "menu"  # Return "menu" to go back to the menu

def show_settings_menu():
    while True:
        screen.fill(BLACK)
        # Draw settings text
        font = pygame.font.Font(None, 72)
        settings_title_text = font.render("Настройки", True, WHITE)
        back_text = font.render("Назад", True, WHITE)
        screen.blit(settings_title_text,
                    (SCREEN_WIDTH // 2 - settings_title_text.get_width() // 2, SCREEN_HEIGHT // 2 - 150))
        screen.blit(back_text, (SCREEN_WIDTH // 2 - back_text.get_width() // 2, SCREEN_HEIGHT // 2 + 200))
        # Check for button click
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]
        # Button rect
        back_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - back_text.get_width() // 2, SCREEN_HEIGHT // 2 + 200,
                                       back_text.get_width(), back_text.get_height())
        if back_button_rect.collidepoint(mouse_pos):
            back_text = font.render("Назад", True, GRAY)
            screen.blit(back_text, (SCREEN_WIDTH // 2 - back_text.get_width() // 2, SCREEN_HEIGHT // 2 + 200))
            if mouse_clicked:
                show_menu()
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Quit event detected in settings")
                return True  # Return True to quit the entire program
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button_rect.collidepoint(event.pos):
                    print("Back button clicked")
                    return None  # Возвращаем управление, чтобы вернуться в меню
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    print("Escape key pressed in settings")
                    return None  # Возвращаем управление, чтобы вернуться в меню

def run_game():
    while True:
        print("Entering menu...")
        menu_result = show_menu()
        if menu_result is True:
            break  # Quit the entire program
        elif menu_result == "settings":
            print("Entering settings menu...")
            settings_result = show_settings_menu()
            if settings_result is True:
                break  # Quit the entire program
            elif settings_result is None:
                continue  # Go back to the menu
        elif menu_result is None:
            print("Starting a new game...")
            game = TetrisGame()
            result = game.main_loop()
            if result is True:
                break  # Quit the entire программ
            elif result == "menu":
                continue  # Go back to the menu

def show_menu():
    while True:
        screen.fill(BLACK)
        # Draw menu text
        font = pygame.font.Font(None, 72)
        title_text = font.render("Tetris", True, WHITE)
        start_text = font.render("Start Game", True, WHITE)
        settings_text = font.render("Настройки", True, WHITE)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 2 - 150))
        screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(settings_text, (SCREEN_WIDTH // 2 - settings_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
        # Check for button click
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]
        # Button rects
        start_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50,
                                        start_text.get_width(), start_text.get_height())
        settings_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - settings_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50,
                                           settings_text.get_width(), settings_text.get_height())
        if start_button_rect.collidepoint(mouse_pos):
            start_text = font.render("Start Game", True, GRAY)
            screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            if mouse_clicked:
                print("Start Game clicked")  # Debug print
                return None

        if settings_button_rect.collidepoint(mouse_pos):
            settings_text = font.render("Настройки", True, GRAY)
            screen.blit(settings_text, (SCREEN_WIDTH // 2 - settings_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
            if mouse_clicked:
                print("Settings clicked")  # Debug print
                return "settings"

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Quit event detected")  # Debug print
                return True  # Return True to quit the entire program
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    print("Enter key pressed")  # Debug print
                    return None

if __name__ == "__main__":
    run_game()
    pygame.quit()