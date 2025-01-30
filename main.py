# main.py
import pygame

from game.constants import *
from game.tetris_game import TetrisGame
from ui.menu import show_menu, show_battle_connection_menu, show_settings_menu
from network.battle_client import BattleTetrisGame

def run_game():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Tetris")

    while True:
        menu_result = show_menu(screen)
        if menu_result == "quit":
            break
        elif menu_result == "single_player":
            game = TetrisGame()
            game.main_loop(screen)
        elif menu_result == "battle":
            battle_menu = show_battle_connection_menu(screen)
            if battle_menu == "quit":
                break
            server_ip, server_port = battle_menu
            if server_ip and server_port:
                battle_game = BattleTetrisGame(server_ip, server_port)
                battle_game.main_loop(screen)
        elif menu_result == "settings":
            show_settings_menu(screen)

if __name__ == "__main__":
    run_game()