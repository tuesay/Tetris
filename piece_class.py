from initialize import *
import random

class Piece(object): #using a class for pieces as many instances of the pieces will be used for tetris.
    def __init__(self,x,y,shape):
        #properties of a shape - x-axis, y-axis, what shape?, what color?, what rotation?
        self.x = x
        self.y = y
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]
        self.rotate = 0
        

def get_shape():
    #selecting a random shape from [shapes] list and creating a piece instance of it and returning.
    curr_shape = Piece(5,0,random.choice(shapes))
    return curr_shape