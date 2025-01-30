# battle_client.py

import socket
import threading
import pygame

from game.settings import *
from game.constants import *
from game.tetris_game import TetrisGame

from ui.error_handler import show_error_message

# Класс клиентского подключения
class BattleClient:
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.client_socket = None
        self.connected = False
        self.receive_thread = None
        self.connection_error = None  # Флаг для ошибки подключения
        self.waiting_for_second_player = False  # Flag for second player waiting
        self.game_started = False  # Flag for GAME_STARTED event on the server

    def connect(self):
        """Подключение к серверу."""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.settimeout(30)  # Увеличиваем таймаут до 30 секунд
            self.client_socket.connect((self.server_ip, self.server_port))
            self.connected = True
            print(f"Подключено к серверу {self.server_ip}:{self.server_port}")

            # Запускаем поток для получения данных от сервера
            self.receive_thread = threading.Thread(target=self.receive_data)
            self.receive_thread.start()
        except socket.gaierror as e:
            self.connection_error = f"Ошибка подключения: Неверный IP-адрес или порт. ({e})"
        except socket.timeout:
            self.connection_error = "Ошибка подключения: Таймаут подключения."
        except ConnectionRefusedError:
            self.connection_error = "Ошибка подключения: Сервер недоступен."
        except Exception as e:
            self.connection_error = f"Ошибка подключения: {e}"
        finally:
            if not self.connected:
                self.disconnect()

    def receive_data(self):
        """Получение данных от сервера."""
        while self.connected:
            try:
                data = self.client_socket.recv(1024).decode()
                if not data:
                    print("Сервер отключился.")
                    self.disconnect()
                    break
                print(f"Получено от сервера: {data}")
                # Обрабатываем сообщение о том, что ожидается второй игрок
                if data == "Ожидаем второго игрока...":
                    self.waiting_for_second_player = True
                elif data == 'Игра началась!':
                    self.game_started = True
                    self.waiting_for_second_player = False
                # Здесь можно обрабатывать полученные данные (например, обновлять игровое состояние)
            except socket.timeout:
                print("Таймаут получения данных. Проверьте соединение.")
                self.disconnect()
                break
            except Exception as e:
                print(f"Ошибка получения данных: {e}")
                self.disconnect()
                break

    def send_data(self, data):
        """Отправка данных на сервер."""
        if self.connected:
            try:
                self.client_socket.send(data.encode())
            except Exception as e:
                print(f"Ошибка отправки данных: {e}")
                self.disconnect()

    def disconnect(self):
        """Отключение от сервера."""
        if self.connected:
            self.client_socket.close()
            self.connected = False
            print("Отключено от сервера.")

# Класс игры сражения
class BattleTetrisGame:
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.client = BattleClient(server_ip, server_port)
        self.client.connect()
        self.game = TetrisGame(
            initial_move_delay_horizontal=global_settings["initial_move_delay_horizontal"],
            accelerated_move_delay_horizontal=global_settings["accelerated_move_delay_horizontal"],
            initial_move_delay_vertical=global_settings["initial_move_delay_vertical"],
            accelerated_move_delay_vertical=global_settings["accelerated_move_delay_vertical"],
            acceleration_threshold=global_settings["acceleration_threshold"]
        )


    def main_loop(self, screen):
        """Основной игровой цикл для режима сражения."""
        if self.client.connection_error:
            # Если есть ошибка подключения, показываем сообщение и возвращаемся в меню
            show_error_message(self.client.connection_error, screen)
            return "menu"

        while self.client.connected:  # Проверяем состояние подключения

            # Здесь будет логика игры

            if self.client.waiting_for_second_player:
                result = self.show_waiting_for_second_player(screen)

                if result == "menu":
                    return "menu"

            elif self.client.game_started:
                result = self.game_loop(screen)
                if result == "menu":
                    return "menu"

        # Если клиент отключился, возвращаемся в меню
        show_error_message("Соединение с сервером потеряно.", screen)
        return "menu"

    def game_loop(self, screen):
        """Основной игровой цикл после начала игры."""
        clock = pygame.time.Clock()
        while not self.game.game_over:
            screen.fill(BLACK)
            result = self.game.handle_events()
            if result is not None:
                return result
            self.game.handle_key_presses()
            self.game.update_falling_shape()
            self.game.grid.draw(screen)
            self.game.draw_shadow(screen)
            self.game.current_shape.draw(screen, self.game.current_x, self.game.current_y)
            self.game.draw_info_window(screen)
            pygame.display.flip()
            clock.tick(60)
        # После проигрыша показываем экран Game Over
        result = self.game.show_game_over_screen(screen)
        return result  # Возвращаем результат в run_game

    def show_waiting_for_second_player(self, screen):
        """Отображение сообщения о том, что ожидается второй игрок."""
        while self.client.waiting_for_second_player:
            screen.fill(BLACK)
            font = pygame.font.Font(None, 36)
            waiting_text = font.render("Ожидаем второго игрока...", True, WHITE)
            screen.blit(waiting_text, (SCREEN_WIDTH // 2 - waiting_text.get_width() // 2, SCREEN_HEIGHT // 2))
            pygame.display.flip()
            result = self.handle_events()
            if result == "menu":
                self.client.disconnect()
                return "menu"
        return None

    def ok_debug(self):
        print("OK_debug()")

    def handle_events(self):
        """Обработка событий в режиме сражения."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "menu"
        return None

