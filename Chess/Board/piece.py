from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import pygame
import os
import sys
import numpy as np
from obj.chj.ogl import *
from obj.chj.ogl.objloader import CHJ_tiny_obj, OBJ
from obj.chj.ogl import light

PIECESIZE = 5e-4

PIECENAMES = ["WhitePawn1", "WhitePawn2", "WhitePawn3", "WhitePawn4",
              "WhitePawn5", "WhitePawn6", "WhitePawn7", "WhitePawn8",
              "WhiteRook1", "WhiteRook2", "WhiteKnight1", "WhiteKnight2",
              "WhiteBishop1", "WhiteBishop2", "WhiteQueen1", "WhiteKing1",
              "BlackPawn1", "BlackPawn2", "BlackPawn3", "BlackPawn4",
              "BlackPawn5", "BlackPawn6", "BlackPawn7", "BlackPawn8",
              "BlackRook1", "BlackRook2", "BlackKnight1", "BlackKnight2",
              "BlackBishop1", "BlackBishop2", "BlackQueen1", "BlackKing1"]

class Piece:
    def __init__(self, piecename):
        self.obj = OBJ('Chess/Pieces/', piecename[:-1] + '.obj', swapyz=True)
        self.obj.create_bbox()
        self.obj.create_gl_list()
        self.name = piecename

        self.xmove = 0
        self.ymove = 0
        self.zmove = 0 

        self.c = 0.010625

        self.row1 = -0.270
        self.row2 = -0.205
        self.row3 = -0.140
        self.row4 = -0.080
        self.row5 = -0.015
        self.row6 = -0.050
        self.row7 =  0.115
        self.row8 =  0.175

        self.col1 = -0.225
        self.col2 = -0.160
        self.col3 = -0.095
        self.col4 = -0.030
        self.col5 =  0.030
        self.col6 =  0.095
        self.col7 =  0.160
        self.col8 =  0.225

    def draw(self):

        glPushMatrix()
        glRotatef(10, 1, 0, 0)

        if self.name ==   'WhitePawn1':   glTranslatef(self.col1, 0.005+self.c, self.row7)
        elif self.name == 'WhitePawn2':   glTranslatef(self.col2, 0.005+self.c, self.row7)
        elif self.name == 'WhitePawn3':   glTranslatef(self.col3, 0.005+self.c, self.row7)
        elif self.name == 'WhitePawn4':   glTranslatef(self.col4, 0.005+self.c, self.row7)
        elif self.name == 'WhitePawn5':   glTranslatef(self.col5, 0.005+self.c, self.row7)
        elif self.name == 'WhitePawn6':   glTranslatef(self.col6, 0.005+self.c, self.row7)
        elif self.name == 'WhitePawn7':   glTranslatef(self.col7, 0.005+self.c, self.row7)
        elif self.name == 'WhitePawn8':   glTranslatef(self.col8, 0.005+self.c, self.row7)        
        elif self.name == 'WhiteRook1':   glTranslatef(self.col1, 0.005, self.row8)
        elif self.name == 'WhiteRook2':   glTranslatef(self.col8, 0.005, self.row8)
        elif self.name == 'WhiteKnight1': glTranslatef(self.col2, 0.005, self.row8)
        elif self.name == 'WhiteKnight2': glTranslatef(self.col7, 0.005, self.row8)
        elif self.name == 'WhiteBishop1': glTranslatef(self.col3, 0.005, self.row8)
        elif self.name == 'WhiteBishop2': glTranslatef(self.col6, 0.005, self.row8)
        elif self.name == 'WhiteQueen1':  glTranslatef(self.col5, 0.005, self.row8)
        elif self.name == 'WhiteKing1':   glTranslatef(self.col4, 0.005, self.row8)
        
        elif self.name == 'BlackPawn1':   glTranslatef(self.col1, 0.090-self.c, self.row2)
        elif self.name == 'BlackPawn2':   glTranslatef(self.col2, 0.090-self.c, self.row2)
        elif self.name == 'BlackPawn3':   glTranslatef(self.col3, 0.090-self.c, self.row2)
        elif self.name == 'BlackPawn4':   glTranslatef(self.col4, 0.090-self.c, self.row2)
        elif self.name == 'BlackPawn5':   glTranslatef(self.col5, 0.090-self.c, self.row2)
        elif self.name == 'BlackPawn6':   glTranslatef(self.col6, 0.090-self.c, self.row2)
        elif self.name == 'BlackPawn7':   glTranslatef(self.col7, 0.090-self.c, self.row2)
        elif self.name == 'BlackPawn8':   glTranslatef(self.col8, 0.090-self.c, self.row2)        
        elif self.name == 'BlackRook1':   glTranslatef(self.col1, 0.090, self.row1)
        elif self.name == 'BlackRook2':   glTranslatef(self.col8, 0.090, self.row1)
        elif self.name == 'BlackKnight1': glTranslatef(self.col2, 0.090, self.row1)
        elif self.name == 'BlackKnight2': glTranslatef(self.col7, 0.090, self.row1)
        elif self.name == 'BlackBishop1': glTranslatef(self.col3, 0.090, self.row1)
        elif self.name == 'BlackBishop2': glTranslatef(self.col6, 0.090, self.row1)
        elif self.name == 'BlackQueen1':  glTranslatef(self.col5, 0.090, self.row1)
        elif self.name == 'BlackKing1':   glTranslatef(self.col4, 0.090, self.row1)

        if self.name[0:5] == 'Black':
            glRotatef(np.radians(10000), 0, 1, 0)

        glRotatef(-10, 1, 0, 0)
        glScale(PIECESIZE, PIECESIZE, PIECESIZE)
        glCallList(self.obj.gl_list)
        glPopMatrix()