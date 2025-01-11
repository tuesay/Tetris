from initialize import *
import pygame

#draw the horizontal and vertical lines of the grid to differentiate between the shapes.
def draw_grid_lines(surface, grid):
    x = top_left_x
    y = top_left_y
    
    for i in range(len(grid)):
        pygame.draw.line(surface,(0,0,0),(x , y + i*block_size),(x + play_width, y + i*block_size))
    
    for j in range(len(grid[0])):
        pygame.draw.line(surface,(0,0,0),(x + j*block_size, y),(x + j*block_size, y + play_height))
        


def draw_text_middle(text, size, color, surface):
    pass

        

def draw_next_shape(shape, surface):
    #drawing the next_piece with label.
    font = pygame.font.SysFont('comicsans',20,True)
    label = font.render('Next Piece:', 1, (255,255,30))
    
    sx = top_left_x + play_width
    sy = top_left_y + 30
    
    next_shape = shape.shape[shape.rotate % len(shape.shape)]
    for i,r in enumerate(next_shape):
        row = list(r)
        for j,col in enumerate(row):
            if col == '0':
                #drawing each grid of the shape using pygame.draw.rect on the side of the board.
                pygame.draw.rect(surface,shape.color,(sx + j*block_size, sy + i*block_size + 30, block_size, block_size), 1)
    
    surface.blit(label, (sx + 10, sy))
    
 
def draw_window(surface,grid,score):
    surface.fill((0,0,0)) #coloring the image surface blac
    #surface is an image placed over the play area
    
    #initializing the font
    pygame.font.init()
    
    #setting up the desired font in font variable
    font = pygame.font.SysFont('comicsans',60,True)
    font2 = pygame.font.SysFont('comicsans',30,True)
    font3 = pygame.font.SysFont('comicsans',20,True)
    
    #setting the heading "Tetris" and rendering it with color
    heading = font.render("Tetris",1,(255,0,255))
    score_heading = font2.render("Score",1,(254,205,64))
    points = font3.render(str(score),1,(254,175,64))
    
    #displaying the heading in the image surface (screen)
    surface.blit(heading,(top_left_x + play_width/2 - (heading.get_width()/2), 5))
    surface.blit(score_heading,(top_left_x/2 + play_width + 100, 310))
    surface.blit(points,(top_left_x/2 + play_width + 130, 350))
    
    #drawing the grids based on the tetris shapes
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface,grid[i][j],(top_left_x + j*block_size, top_left_y + i*block_size, block_size, block_size), 0)
    
    #drawing the border of the play area
    draw_grid_lines(surface,grid)
    
    pygame.draw.rect(surface,(0,255,0),(top_left_x,top_left_y,play_width+1,play_height+1),5)