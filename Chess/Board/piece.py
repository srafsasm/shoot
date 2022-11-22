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

PIECESIZE = 2e-3

# PIECENAMES = ["WhitePawn1", "WhitePawn2", "WhitePawn3", "WhitePawn4",
#               "WhitePawn5", "WhitePawn6", "WhitePawn7", "WhitePawn8",
#               "WhiteRook1", "WhiteRook2", "WhiteKnight1", "WhiteKnight2",
#               "WhiteBishop1", "WhiteBishop2", "WhiteQueen1", "WhiteKing1",
#               "BlackPawn1", "BlackPawn2", "BlackPawn3", "BlackPawn4",
#               "BlackPawn5", "BlackPawn6", "BlackPawn7", "BlackPawn8",
#               "BlackRook1", "BlackRook2", "BlackKnight1", "BlackKnight2",
#               "BlackBishop1", "BlackBishop2", "BlackQueen1", "BlackKing1"]
PIECENAMES = ["WhitePawn4", "BlackPawn4"]

class Piece:
    def __init__(self, piecename):
        self.obj = OBJ('Chess/Pieces/', piecename[:-1] + '.obj', swapyz=True)
        self.obj.create_bbox()
        self.obj.create_gl_list()
        self.name = piecename

        self.height = 0.084

        self.place = [0, 0, 0]

        self.box1 = 0.595
        self.box2 = 0.425
        self.box3 = 0.250
        self.box4 = 0.085
        self.box8 = -0.595
        self.box7 = -0.425
        self.box6 = -0.250
        self.box5 = -0.085

        self.moving = False
        self.movingCnt = 1
        self.movingSpeed = 40
        
        if self.name ==   'WhitePawn1':   self.place = [self.box7, self.height, -self.box1]
        elif self.name == 'WhitePawn2':   self.place = [self.box7, self.height, -self.box2]
        elif self.name == 'WhitePawn3':   self.place = [self.box7, self.height, -self.box3]
        elif self.name == 'WhitePawn4':   self.place = [self.box7, self.height, -self.box4]
        elif self.name == 'WhitePawn5':   self.place = [self.box7, self.height, -self.box5]
        elif self.name == 'WhitePawn6':   self.place = [self.box7, self.height, -self.box6]
        elif self.name == 'WhitePawn7':   self.place = [self.box7, self.height, -self.box7]
        elif self.name == 'WhitePawn8':   self.place = [self.box7, self.height, -self.box8]        
        elif self.name == 'WhiteRook1':   self.place = [self.box8, self.height, -self.box1]
        elif self.name == 'WhiteRook2':   self.place = [self.box8, self.height, -self.box8]
        elif self.name == 'WhiteKnight1': self.place = [self.box8, self.height, -self.box2]
        elif self.name == 'WhiteKnight2': self.place = [self.box8, self.height, -self.box7]
        elif self.name == 'WhiteBishop1': self.place = [self.box8, self.height, -self.box3]
        elif self.name == 'WhiteBishop2': self.place = [self.box8, self.height, -self.box6]
        elif self.name == 'WhiteQueen1':  self.place = [self.box8, self.height, -self.box4]
        elif self.name == 'WhiteKing1':   self.place = [self.box8, self.height, -self.box5]
        
        elif self.name == 'BlackPawn1':   self.place = [self.box2, self.height, -self.box1]
        elif self.name == 'BlackPawn2':   self.place = [self.box2, self.height, -self.box2]
        elif self.name == 'BlackPawn3':   self.place = [self.box2, self.height, -self.box3]
        elif self.name == 'BlackPawn4':   self.place = [self.box2, self.height, -self.box4]
        elif self.name == 'BlackPawn5':   self.place = [self.box2, self.height, -self.box5]
        elif self.name == 'BlackPawn6':   self.place = [self.box2, self.height, -self.box6]
        elif self.name == 'BlackPawn7':   self.place = [self.box2, self.height, -self.box7]
        elif self.name == 'BlackPawn8':   self.place = [self.box2, self.height, -self.box8]        
        elif self.name == 'BlackRook1':   self.place = [self.box1, self.height, -self.box1]
        elif self.name == 'BlackRook2':   self.place = [self.box1, self.height, -self.box8]
        elif self.name == 'BlackKnight1': self.place = [self.box1, self.height, -self.box2]
        elif self.name == 'BlackKnight2': self.place = [self.box1, self.height, -self.box7]
        elif self.name == 'BlackBishop1': self.place = [self.box1, self.height, -self.box3]
        elif self.name == 'BlackBishop2': self.place = [self.box1, self.height, -self.box6]
        elif self.name == 'BlackQueen1':  self.place = [self.box1, self.height, -self.box4]
        elif self.name == 'BlackKing1':   self.place = [self.box1, self.height, -self.box5]

    # Move a small amount and display
    def move(self, x, y, z):
        self.moving = True

        glPushMatrix()
        glRotatef(90, 1, 0, 0)
        glTranslatef(self.place[0]+x*self.movingCnt, self.place[1]+y*self.movingCnt, self.place[2]+z*self.movingCnt)

        if self.name[0:5] == 'Black':
            glRotatef(90, 0, 1, 0)
        else:
            glRotatef(-90, 0, 1, 0)

        glScale(PIECESIZE, PIECESIZE, PIECESIZE)
        glCallList(self.obj.gl_list)
        glPopMatrix()

        if self.movingCnt >= self.movingSpeed:
            self.moving = False
            self.place[0] += self.movingSpeed * x
            self.place[1] += self.movingSpeed * y
            self.place[2] += self.movingSpeed * z
            self.movingCnt = 1
        else:
            self.movingCnt += 1

    # Simply displaying
    def show(self):
        glPushMatrix()
        glRotatef(90, 1, 0, 0)
        glTranslatef(self.place[0], self.place[1], self.place[2])

        if self.name[0:5] == 'Black':
            glRotatef(90, 0, 1, 0)
        else:
            glRotatef(-90, 0, 1, 0)

        glScale(PIECESIZE, PIECESIZE, PIECESIZE)
        glCallList(self.obj.gl_list)
        glPopMatrix()

