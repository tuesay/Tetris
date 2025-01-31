#menu.py

import pygame

from .input_box import InputBox

from game.constants import *
from game.settings import global_settings

def show_settings_menu(screen):
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

def show_battle_connection_menu(screen):
    # Создаем InputBox для IP-адреса и порта
    ip_input = InputBox(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, 200, 40, allowed_chars="0123456789.")
    port_input = InputBox(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50, 200, 40, allowed_chars="0123456789")

    # Кнопка "Подключиться"
    connect_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 150, 200, 40)

    while True:
        screen.fill(BLACK)
        font = pygame.font.Font(None, 36)

        # Заголовок
        title_text = font.render("Подключение к серверу", True, WHITE)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 2 - 150))

        # Подписи для InputBox
        ip_label = font.render("IP-адрес:", True, WHITE)
        port_label = font.render("Порт:", True, WHITE)
        screen.blit(ip_label, (SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 - 50))
        screen.blit(port_label, (SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 + 50))

        # Рисуем InputBox
        ip_input.draw(screen)
        port_input.draw(screen)

        # Кнопка "Подключиться"
        pygame.draw.rect(screen, GRAY, connect_button_rect)
        connect_text = font.render("Подключиться", True, WHITE)
        screen.blit(connect_text, (connect_button_rect.x + 20, connect_button_rect.y + 10))

        # Обработка наведения мыши на кнопку "Подключиться"
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]

        if connect_button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, WHITE, connect_button_rect, 2)
            if mouse_clicked:
                # Возвращаем введенные данные
                try:
                    return ip_input.text, int(port_input.text)
                except ValueError:
                    print('UnexpectedError: Порт пуст/порт состоит из букв ')
                    return '127.0.0.1', 5555

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"  # Выход из меню

            ip_input.handle_event(event)
            port_input.handle_event(event)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None, None  # Выход из меню

        pygame.display.flip()

# Главное меню
def show_menu(screen):
    while True:
        screen.fill(BLACK)
        font = pygame.font.Font(None, 72)
        title_text = font.render("Тетрис", True, WHITE)
        battle_text = font.render("Сражение", True, WHITE)  # Новая кнопка "Сражение"
        single_player_text = font.render("Одиночная игра", True, WHITE)  # Переименованная кнопка
        settings_text = font.render("Настройки", True, WHITE)

        # Отображение текста на экране
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 2 - 200))
        screen.blit(battle_text,
                    (SCREEN_WIDTH // 2 - battle_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))  # Новая кнопка
        screen.blit(single_player_text, (
        SCREEN_WIDTH // 2 - single_player_text.get_width() // 2, SCREEN_HEIGHT // 2))  # Переименованная кнопка
        screen.blit(settings_text, (SCREEN_WIDTH // 2 - settings_text.get_width() // 2, SCREEN_HEIGHT // 2 + 100))

        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]

        # Определяем прямоугольники кнопок
        battle_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - battle_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100,
                                         battle_text.get_width(), battle_text.get_height())
        single_player_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - single_player_text.get_width() // 2,
                                                SCREEN_HEIGHT // 2,
                                                single_player_text.get_width(), single_player_text.get_height())
        settings_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - settings_text.get_width() // 2, SCREEN_HEIGHT // 2 + 100,
                                           settings_text.get_width(), settings_text.get_height())

        # Подсветка кнопок при наведении
        if battle_button_rect.collidepoint(mouse_pos):
            battle_text = font.render("Сражение", True, GRAY)
            screen.blit(battle_text, (SCREEN_WIDTH // 2 - battle_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
            if mouse_clicked:
                return "battle"  # Возвращаем "battle" для запуска режима сражения

        if single_player_button_rect.collidepoint(mouse_pos):
            single_player_text = font.render("Одиночная игра", True, GRAY)
            screen.blit(single_player_text,
                        (SCREEN_WIDTH // 2 - single_player_text.get_width() // 2, SCREEN_HEIGHT // 2))
            if mouse_clicked:
                return "single_player"  # Начать одиночную игру

        if settings_button_rect.collidepoint(mouse_pos):
            settings_text = font.render("Настройки", True, GRAY)
            screen.blit(settings_text, (SCREEN_WIDTH // 2 - settings_text.get_width() // 2, SCREEN_HEIGHT // 2 + 100))
            if mouse_clicked:
                return "settings"  # Перейти в меню настроек

        pygame.display.flip()

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"  # Выход из игры
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return None  # Начать одиночную игру