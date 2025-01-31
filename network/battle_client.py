# battle_client.py

import socket
import threading

import pygame
import pickle

from game.settings import *
from game.constants import *
from game.grid import Grid
from game.tetris_game import TetrisGame

from ui.error_handler import show_error_message

# Класс клиентского подключения
class BattleClient:
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.data = None
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
                length_prefix = self.client_socket.recv(10)
                if not length_prefix:
                    print("Сервер отключился.")
                    self.disconnect()
                    break


                data_length = int(length_prefix.decode('utf-8'))

                received_data = b""
                while len(received_data) < data_length:
                    chunk = self.client_socket.recv(data_length - len(received_data))
                    if not chunk:
                        break
                    received_data += chunk

                if len(received_data) != data_length:
                    raise ValueError("Incomplete data received")

                data = pickle.loads(received_data)

                # Обрабатываем сообщение о том, что ожидается второй игрок
                if data == "Ожидаем второго игрока...":
                    self.waiting_for_second_player = True
                elif data == 'Игра началась!':
                    self.game_started = True
                    self.waiting_for_second_player = False
                elif type(data) == type(dict()):
                    self.data = data

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
                serialized_data = pickle.dumps(data)
                data_length = len(serialized_data)
                length_prefix = f"{data_length:010}".encode('utf-8')
                self.client_socket.send(length_prefix + serialized_data)

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
        # op - Opponent
        self.op_grid = Grid(GRID_WIDTH, GRID_HEIGHT)
        self.op_game = TetrisGame()
        self.op_x_offset = 650


    def main_loop(self, screen):
        """Основной игровой цикл для режима сражения."""
        if self.client.connection_error:
            # Если есть ошибка подключения, показываем сообщение и возвращаемся в меню
            show_error_message(self.client.connection_error, screen)
            return "menu"

        while self.client.connected:  # Проверяем состояние подключения

            # Логика сражения

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

            # UPDATING THE OP GAME STATE

            received_data = self.client.data
            if received_data is not None:
                self.update_game_state(received_data)

            # CLIENT GAME
            self.game.handle_key_presses()
            self.game.update_falling_shape()
            self.game.grid.draw(screen)
            self.game.draw_shadow(screen)
            self.game.current_shape.draw(screen, self.game.current_x, self.game.current_y)
            self.game.draw_info_window(screen)

            # OP GAME

            self.op_game.grid.draw(screen, x_offset=self.op_x_offset)
            self.op_game.current_shape.draw(screen, self.op_game.current_x, self.game.current_y, x_offset=self.op_x_offset)
            self.op_game.draw_info_window(screen, x_offset=self.op_x_offset)

            # SENDING THE GAME STATE
            game_state = self.get_game_state()
            self.client.send_data(game_state)

            pygame.display.flip()
            clock.tick(120)
        # После проигрыша показываем экран Game Over

        result = self.game.show_game_over_screen(screen)
        return result  # Возвращаем результат в run_game

    def get_game_state(self):

        game_state = {
            "grid": self.game.grid.grid,
            "score": self.game.score,
            "level": self.game.level,
            "next_shapes": self.game.next_shapes,
            "held_shape": self.game.held_shape
        }

        return game_state

    def update_game_state(self, received):
        self.op_game.grid.grid = received["grid"]
        self.op_game.score = received["score"]
        self.op_game.level = received["level"]
        self.op_game.next_shapes = received["next_shapes"]
        self.op_game.held_shape = received["held_shape"]

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

