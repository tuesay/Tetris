import socket
import threading
import time


class BattleServer:
    def __init__(self, host="0.0.0.0", port=5555):
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients = []  # Список подключенных клиентов
        self.lock = threading.Lock()  # Блокировка для потокобезопасности

    def start(self):
        """Запуск сервера."""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(2)  # Ожидаем подключения двух клиентов
            print(f"Сервер запущен на {self.host}:{self.port}. Ожидание подключений...")
            while len(self.clients) < 2:
                client_socket, client_address = self.server_socket.accept()
                print(f"Подключен клиент: {client_address}")
                self.clients.append(client_socket)
                # Отправляем подтверждение подключения
                client_socket.send("Подключено к серверу. Ожидаем второго игрока...".encode())
                # Если подключен только один клиент, отправляем ему сообщение о состоянии
                if len(self.clients) == 1:
                    threading.Thread(target=self.notify_waiting, args=(client_socket,)).start()
                # Запускаем поток для обработки клиента
                threading.Thread(target=self.handle_client, args=(client_socket,)).start()
            print("Оба игрока подключены. Начинаем игру!")
            # Отправляем сообщение обоим клиентам о начале игры
            time.sleep(1)

            self.broadcast("Игра началась!")
        except Exception as e:
            print(f"Ошибка при запуске сервера: {e}")
        finally:
            self.stop()

    def notify_waiting(self, client_socket):
        """Уведомление клиента о том, что сервер ожидает второго игрока."""
        try:
            while len(self.clients) < 2:
                client_socket.send("Ожидаем второго игрока...".encode())
                threading.Event().wait(5)  # Отправляем сообщение каждые 5 секунд
        except Exception as e:
            print(f"Ошибка при уведомлении клиента: {e}")

    def handle_client(self, client_socket):
        """Обработка данных от клиента."""
        try:
            while True:
                data = client_socket.recv(1024).decode()
                if not data:
                    break
                # Обрабатываем полученные данные (например, игровое состояние или атаку)
                self.broadcast(data, client_socket)
        except Exception as e:
            print(f"Ошибка при обработке клиента: {e}")
        finally:
            self.remove_client(client_socket)

    def broadcast(self, message, sender_socket=None):
        """Отправка сообщения всем клиентам, кроме отправителя."""
        with self.lock:
            for client in self.clients:
                if client != sender_socket:
                    try:
                        client.send(message.encode())
                    except Exception as e:
                        print(f"Ошибка при отправке сообщения клиенту: {e}")
                        self.remove_client(client)

    def remove_client(self, client_socket):
        """Удаление клиента из списка."""
        with self.lock:
            if client_socket in self.clients:
                self.clients.remove(client_socket)
                client_socket.close()
                print("Клиент отключен.")

    def stop(self):
        """Остановка сервера."""
        if self.server_socket:
            self.server_socket.close()
            print("Сервер остановлен.")


if __name__ == "__main__":
    server = BattleServer(host="127.0.0.1", port=5555)
    server.start()