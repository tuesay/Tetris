# error_handler.py
import pygame

from game.constants import BLACK, WHITE, SCREEN_WIDTH, SCREEN_HEIGHT


def show_error_message(message, screen):
    """Функция для отображения сообщения об ошибке."""
    screen.fill(BLACK)
    font = pygame.font.Font(None, 36)
    error_text = font.render(message, True, WHITE)
    screen.blit(error_text, (SCREEN_WIDTH // 2 - error_text.get_width() // 2, SCREEN_HEIGHT // 2))
    pygame.display.flip()
    pygame.time.delay(2000)  # Задержка для отображения сообщения