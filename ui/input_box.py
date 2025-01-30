#input_box.py

import pygame

from game.constants import *

class InputBox:
    def __init__(self, x, y, w, h, text='', allowed_chars=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = GRAY
        self.text = text
        self.font = pygame.font.Font(None, 36)
        self.txt_surface = self.font.render(text, True, self.color)
        self.active = False
        self.allowed_chars = allowed_chars  # Список разрешенных символов

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
                    # Проверяем, разрешен ли символ
                    if self.allowed_chars is None or event.unicode in self.allowed_chars:
                        self.text += event.unicode
                self.txt_surface = self.font.render(self.text, True, self.color)

    def update(self):
        width = max(200, self.txt_surface.get_width() + 10)
        self.rect.w = width

    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(screen, self.color, self.rect, 2)