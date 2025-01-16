from settings import *


class Block(pygame.sprite.Sprite):
    def __init__(self, group, pos, color):
        super().__init__(group)

        self.image = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
        self.image.fill(color)

        # позиция отдельного блока в определенной сетке
        self.pos = pygame.Vector2(pos) + BLOCK_OFFSET
        self.rect = self.image.get_rect(topleft = self.pos * BLOCK_SIZE)

    def update(self):
        # обновление квадратов тетромино
        self.rect.topleft = self.pos * BLOCK_SIZE

    def horizontal_collide(self, x, field_data):
        if not 0 <= x < COLUMNS:
            return True
        if field_data[int(self.pos.y)][x]:
            return True

    def vertical_collide(self, y, field_data):
        if not y < ROWS:
            return True
        if y >= 0 and field_data[y][int(self.pos.x)]:
            return True

    def rotate(self, pivot_pos, rotate_direction):
        distance = self.pos - pivot_pos
        rotated = distance.rotate(90 * rotate_direction)
        new_pos = pivot_pos + rotated
        return new_pos

class Tetromino:
    def __init__(self, shape, group, field_data):


        self.shape = shape
        self.block_pos = TETROMINOS[shape]['shape']
        self.color = TETROMINOS[shape]['color']

        self.field_data = field_data

        self.blocks = [Block(group, pos, self.color) for pos in self.block_pos]

    # movin
    def move_horizontal(self, change):
        if not self.next_move_horizontal_collide(self.blocks, change):
            for block in self.blocks:
                block.pos.x += change

    def move_down(self):
        if not self.next_move_vertical_collide(self.blocks, 1):
            for block in self.blocks:
                block.pos.y += 1
        else:
            for block in self.blocks:
                self.field_data[int(block.pos.y)][int(block.pos.x)] = block
            return 'already moved'

    def rotate(self, rotate_direction):
        if self.shape != 'O':
            pivot_pos = self.blocks[0].pos

            new_block_positions = [block.rotate(pivot_pos, rotate_direction) for block in self.blocks]

            for pos in new_block_positions:
                if pos.x < 0 or pos.x >= COLUMNS:
                    return
                if self.field_data[int(pos.y)][int(pos.x)]:
                    return
                if pos.y > ROWS:
                    return

            for i, block in enumerate(self.blocks):
                block.pos = new_block_positions[i]

    # collision
    def next_move_horizontal_collide(self, blocks, change):
        collision_list = [block.horizontal_collide(int(block.pos.x + change), self.field_data) for block in self.blocks]
        return True if any(collision_list) else False

    def next_move_vertical_collide(self, blocks, change):
        collision_list = [block.vertical_collide(int(block.pos.y + change), self.field_data) for block in self.blocks]
        return True if any(collision_list) else False
