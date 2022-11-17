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

normal_valid_move = ([0.0, 0.0, -1.0])
chessBoard = ([[-0.40, -0.40, 0.05],
               [-0.40,  0.40, 0.05],
               [ 0.40,  0.40, 0.05],
               [ 0.40, -0.40, 0.05],
               [-0.45, -0.45, 0.05],
               [-0.45,  0.45, 0.05],
               [ 0.45,  0.45, 0.05],
               [ 0.45, -0.45, 0.05],
               [-0.50, -0.50, 0.00],
               [-0.50,  0.50, 0.00],
               [ 0.50,  0.50, 0.00],
               [ 0.50, -0.50, 0.00]])

def drawChessBoard():
    glPushMatrix()
    glNormal3fv(normal_valid_move)
    glBegin(GL_QUADS)
    glColor3f(1.0, 0.0, 0.0)
    for i in range(8, 12):
        glVertex3fv(chessBoard[i])
    glEnd()

    glColor3f(0, 0, 0)
    glBegin(GL_QUADS)
    glColor3f(0.55, 0.24, 0.09)
    glColor3f(0.803, 0.522, 0.247)
    glVertex3fv(chessBoard[0])
    glColor3f(0.545, 0.271, 0.075)
    glVertex3fv(chessBoard[4])
    glColor3f(0.545, 0.271, 0.075)
    glVertex3fv(chessBoard[5])
    glColor3f(0.803, 0.522, 0.247)
    glVertex3fv(chessBoard[1])
    glEnd()

    glBegin(GL_QUADS)
    glColor3f(0.803, 0.522, 0.247)
    glVertex3fv(chessBoard[1])
    glColor3f(0.545, 0.271, 0.075)
    glVertex3fv(chessBoard[5])
    glColor3f(0.545, 0.271, 0.075)
    glVertex3fv(chessBoard[6])
    glColor3f(0.803, 0.522, 0.247)
    glVertex3fv(chessBoard[2])
    glEnd()

    glBegin(GL_QUADS)
    glColor3f(0.803, 0.522, 0.247)
    glVertex3fv(chessBoard[2])
    glColor3f(0.545, 0.271, 0.075)
    glVertex3fv(chessBoard[6])
    glColor3f(0.545, 0.271, 0.075)
    glVertex3fv(chessBoard[7])
    glColor3f(0.803, 0.522, 0.247)
    glVertex3fv(chessBoard[3])
    glEnd()

    glBegin(GL_QUADS)
    glColor3f(0.803, 0.522, 0.247)
    glVertex3fv(chessBoard[3])
    glColor3f(0.545, 0.271, 0.075)
    glVertex3fv(chessBoard[7])
    glColor3f(0.545, 0.271, 0.075)
    glVertex3fv(chessBoard[4])
    glColor3f(0.803, 0.522, 0.247)
    glVertex3fv(chessBoard[0])
    glEnd()

    glBegin(GL_QUADS)
    glColor3f(1.0, 0.95, 0.9)
    glColor3f(0.545, 0.271, 0.075)
    glVertex3fv(chessBoard[4])
    glColor3f(1.000, 1.000, 1.000)
    glVertex3fv(chessBoard[8])
    glColor3f(1.000, 1.000, 1.000)
    glVertex3fv(chessBoard[9])
    glColor3f(0.545, 0.271, 0.075)
    glVertex3fv(chessBoard[5])
    glEnd()

    glBegin(GL_QUADS)
    glColor3f(0.545, 0.271, 0.075)
    glVertex3fv(chessBoard[5])
    glColor3f(1.000, 1.000, 1.000)
    glVertex3fv(chessBoard[9])
    glColor3f(1.000, 1.000, 1.000)
    glVertex3fv(chessBoard[10])
    glColor3f(0.545, 0.271, 0.075)
    glVertex3fv(chessBoard[6])
    glEnd()

    glBegin(GL_QUADS)
    glColor3f(0.545, 0.271, 0.075)
    glVertex3fv(chessBoard[6])
    glColor3f(1.000, 1.000, 1.000)
    glVertex3fv(chessBoard[10])
    glColor3f(1.000, 1.000, 1.000)
    glVertex3fv(chessBoard[11])
    glColor3f(0.545, 0.271, 0.075)
    glVertex3fv(chessBoard[7])
    glEnd()

    glBegin(GL_QUADS)
    glColor3f(0.545, 0.271, 0.075)
    glVertex3fv(chessBoard[7])
    glColor3f(1.000, 1.000, 1.000)
    glVertex3fv(chessBoard[11])
    glColor3f(1.000, 1.000, 1.000)
    glVertex3fv(chessBoard[8])
    glColor3f(0.545, 0.271, 0.075)
    glVertex3fv(chessBoard[4])
    glEnd()

    glPopMatrix()

    glColor3f(1, 1, 1)

    for j in range(1, 9):
        for i in range(1, 9):
            if j % 2 == 1 and i % 2 == 1:
                glColor3f(0, 0, 0)
            elif j % 2 == 1 and i % 2 == 0:
                glColor3f(1, 1, 1)
            elif j % 2 == 0 and i % 2 == 1:
                glColor3f(1, 1, 1)
            else:
                glColor3f(0, 0, 0)

            glPushMatrix()
            glBegin(GL_TRIANGLES)
            glVertex3f(-0.3705+0.092625*i, -0.42+0.0925*(j-1), 0.1)
            glVertex3f(-0.3705+0.092625*i,  -0.42+0.0925*j, 0.1)
            glVertex3f(-0.3705+0.092625*(i-1), -0.42+0.0925*(j-1), 0.1)
            glEnd()

            glBegin(GL_TRIANGLES)
            glVertex3f(-0.3705+0.092625*(i-1), -0.42+0.0925*(j-1), 0.1)
            glVertex3f(-0.3705+0.092625*i,  -0.42+0.0925*j, 0.1)
            glVertex3f(-0.3705+0.092625*(i-1), -0.42+0.0925*j, 0.1)
            glEnd()
            glPopMatrix()
