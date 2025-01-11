def create_grid(locked_pos={}):
    #iterate grid of 20 x 10 and set all grid as black
    grid = [[(0,0,0) for i in range(10)] for i in range(20)]
    
    #with respect to the positions in locked_pos, change those particular grid according to the color of the shape.
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j,i) in locked_pos:                      #change i j
                grid[i][j] = locked_pos[(j,i)]              #change i j
    
    return grid
 
def convert_shape_format(shape):
    positions = []
    format_shape = shape.shape[shape.rotate % len(shape.shape)]
    
    #collecting the positions of the particular shape at positions of '0'.
    for i in range(len(format_shape)):
        curr_row = list(format_shape[i])
        for j in range(len(curr_row)):
            if curr_row[j] == '0':
                positions.append((shape.x + j, shape.y + i))    #change i j
        
    #setting offset - moving the piece to the left and up to offset the space.       
    for i in range(len(positions)):
        positions[i] = (positions[i][0] - 2, positions[i][1] - 4)
    
    return positions