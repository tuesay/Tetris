from mark_shapes import *

#This function checks if the shape is in a valid position in the grid. If the shape overlaps with another existing piece,
#it decrements its position by 1
def valid_space(shape, grid):
    valid_pos = [[(j,i) for j in range(10) if grid[i][j] == (0,0,0)] for i in range(20)]
    valid_pos = [j for sub in valid_pos for j in sub]
    
    #convert_shape_format func. sends the position of the shape's coordinates based on the grid matrix.
    formatted_shape = convert_shape_format(shape)
    for pos in formatted_shape:
        if pos not in valid_pos and pos[1]>-1:
            return False
    
    return True

#if y-axis of pos coordinates is less than 1, its outside the screen - meaning game lost.
def check_lost(positions):
    for pos in positions:
        x,y = pos
        if y<1:
            return True
    
    return False


def clear_rows(grid, locked):
    inc = 0
    for i in range(len(grid)):
        row = grid[i]
        #for every row, if no grid is black (all grids filled with shapes), increase inc by 1 and remember the index.
        if (0,0,0) not in row:
            inc+=1
            idx = i
            for j in range(len(grid[i])):
                #delete the corresponding position from {locked}
                if (j,i) in locked:
                    del locked[(j,i)]
    
    if inc>0:
        #update the {locked's key} with new coordinates and push the (entire row + inc) - condition: if the index is above last marked idx.
        for key in sorted(list(locked), key = lambda x: x[1])[::-1]:
            x,y = key
            if y<idx:
                newkey = (x,y+inc)
                locked[newkey] = locked.pop(key)
    
    return inc