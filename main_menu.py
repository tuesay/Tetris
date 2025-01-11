import pygame
import random
from pygame import mixer
from initialize import *
from piece_class import *
from draw import *
from checks import *
from mark_shapes import *

pygame.font.init()
mixer.init()

musics = ['interstellar.mp3','funky.mp3']
 
def main(window):
    locked_pos = {}
    grid = create_grid(locked_pos)
    change_piece = False
    run = True
    curr_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.27
    score = 0
    level_time = 0
    
    while run:
        grid = create_grid(locked_pos)
        fall_time += clock.get_rawtime()
        clock.tick()
        
        if fall_time/1000>=fall_speed:
            fall_time = 0
            curr_piece.y+=1
            if not valid_space(curr_piece,grid) and curr_piece.y > 0:
                curr_piece.y-=1
                change_piece=True
        
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    curr_piece.rotate+=1
                    if not valid_space(curr_piece,grid):
                        curr_piece.rotate-=1
                if event.key == pygame.K_DOWN:
                    curr_piece.y+=1
                    if not valid_space(curr_piece,grid):
                        curr_piece.y-=1
                if event.key == pygame.K_LEFT:
                    curr_piece.x-=1
                    if not valid_space(curr_piece,grid):
                        curr_piece.x+=1
                if event.key == pygame.K_RIGHT:
                    curr_piece.x+=1
                    if not valid_space(curr_piece,grid):
                        curr_piece.x-=1
                        
        final_piece_pos = convert_shape_format(curr_piece)
        for x,y in final_piece_pos:
            if y>-1:
                grid[y][x] = curr_piece.color         #change i j
                
        if change_piece:
            for x,y in final_piece_pos:
                locked_pos[(x,y)] = curr_piece.color  #change i j
            curr_piece = next_piece
            next_piece = get_shape()
            temp_score = clear_rows(grid,locked_pos)
            score+=(temp_score*10)
            change_piece = False
        
        draw_window(window,grid,score)
        draw_next_shape(next_piece,window)
        pygame.display.update()
        
        if check_lost(locked_pos):
            run = False
    
    pygame.display.quit()

def main_menu(window):
    run = True
    while run:
        mixer.music.set_volume(0.1)
        font_home = pygame.font.SysFont('comicsans', 40,True)
        text = font_home.render("Press any key to play", 1, (180,60,255))
        window.blit(text, [s_width/2 - 200, s_height/2 - 30])
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                mixer.music.stop()
                pygame.display.quit()
            if event.type == pygame.KEYDOWN:
                mixer.music.load(random.choice(musics))
                mixer.music.play(loops=-1)
                main(window)


window = pygame.display.set_mode((s_width,s_height))
pygame.display.set_caption("TETRIS")
main_menu(window)               
                
    


