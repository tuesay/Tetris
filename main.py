import sys

from settings import *

from game import Game

class Main:
    def __init__(self):

        pygame.init()

        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Tetris2v2')

        self.clock = pygame.time.Clock()

        self.game = Game()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.screen.fill(BLACK)

            self.game.run()

            pygame.display.update()
            self.clock.tick(592)


if __name__ == '__main__':
    main = Main()
    main.run()
