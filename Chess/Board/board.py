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

board00 = chessBoard[2]
board08 = chessBoard[3]
board80 = chessBoard[1]
board88 = chessBoard[0]

def half(a, b):
    return [(a+b)/2 for a, b in zip(a, b)]

board04 = half(board00, board08)
board84 = half(board80, board88)
board02 = half(board00, board04)
board82 = half(board80, board84)
board06 = half(board04, board08)
board86 = half(board84, board88)
board01 = half(board00, board02)
board81 = half(board80, board82)
board03 = half(board04, board02)
board83 = half(board84, board82)
board05 = half(board06, board04)
board85 = half(board86, board84)
board07 = half(board06, board08)
board87 = half(board86, board88)

board40 = half(board00, board80)
board20 = half(board00, board40)
board60 = half(board40, board80)
board10 = half(board00, board20)
board30 = half(board20, board40)
board50 = half(board40, board60)
board70 = half(board60, board80)

board41 = half(board01, board81)
board21 = half(board01, board41)
board61 = half(board41, board81)
board11 = half(board01, board21)
board31 = half(board21, board41)
board51 = half(board41, board61)
board71 = half(board61, board81)

board42 = half(board02, board82)
board22 = half(board02, board42)
board62 = half(board42, board82)
board12 = half(board02, board22)
board32 = half(board22, board42)
board52 = half(board42, board62)
board72 = half(board62, board82)

board43 = half(board03, board83)
board23 = half(board03, board43)
board63 = half(board43, board83)
board13 = half(board03, board23)
board33 = half(board23, board43)
board53 = half(board43, board63)
board73 = half(board63, board83)

board44 = half(board04, board84)
board24 = half(board04, board44)
board64 = half(board44, board84)
board14 = half(board04, board24)
board34 = half(board24, board44)
board54 = half(board44, board64)
board74 = half(board64, board84)

board45 = half(board05, board85)
board25 = half(board05, board45)
board65 = half(board45, board85)
board15 = half(board05, board25)
board35 = half(board25, board45)
board55 = half(board45, board65)
board75 = half(board65, board85)

board46 = half(board06, board86)
board26 = half(board06, board46)
board66 = half(board46, board86)
board16 = half(board06, board26)
board36 = half(board26, board46)
board56 = half(board46, board66)
board76 = half(board66, board86)

board47 = half(board07, board87)
board27 = half(board07, board47)
board67 = half(board47, board87)
board17 = half(board07, board27)
board37 = half(board27, board47)
board57 = half(board47, board67)
board77 = half(board67, board87)

board48 = half(board08, board88)
board28 = half(board08, board48)
board68 = half(board48, board88)
board18 = half(board08, board28)
board38 = half(board28, board48)
board58 = half(board48, board68)
board78 = half(board68, board88)

# Define a board
board = [
         [board80, board81, board82, board83, board84, board85, board86, board87, board88],
         [board70, board71, board72, board73, board74, board75, board76, board77, board78],
         [board60, board61, board62, board63, board64, board65, board66, board67, board68],
         [board50, board51, board52, board53, board54, board55, board56, board57, board58],
         [board40, board41, board42, board43, board44, board45, board46, board47, board48],
         [board30, board31, board32, board33, board34, board35, board36, board37, board38],
         [board20, board21, board22, board23, board24, board25, board26, board27, board28],
         [board10, board11, board12, board13, board14, board15, board16, board17, board18],
         [board00, board01, board02, board03, board04, board05, board06, board07, board08],
        ]

# Draw a chess board
def drawChessBoard():
    glPushMatrix()
    glNormal3fv(normal_valid_move)
    glBegin(GL_QUADS)
    glColor3f(1.0, 0.0, 0.0)
    for i in range(8, 12):
        glVertex3fv(chessBoard[i])
    glEnd()

    for j in range(0, 8):
        for i in range(0, 8):
            if j % 2 == 1 and i % 2 == 0:
                glColor3f(1, 1, 1)
            elif j % 2 == 1 and i % 2 == 1:
                glColor3f(0, 0, 0)
            elif j % 2 == 0 and i % 2 == 0:
                glColor3f(0, 0, 0)
            else:
                glColor3f(1, 1, 1)

            glBegin(GL_TRIANGLES)
            glVertex3fv(board[i][j])
            glVertex3fv(board[i+1][j])
            glVertex3fv(board[i][j+1])
            glVertex3fv(board[i+1][j+1])
            glVertex3fv(board[i+1][j])
            glVertex3fv(board[i][j+1])
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

# Draw a battlefield
def drawBattlefield():
    glPushMatrix()
    glNormal3fv(normal_valid_move)

    for j in range(0, 8):
        for i in range(0, 8):
            if j % 2 == 1 and i % 2 == 0:
                glColor4f(1, 1, 1, 0.2)
            elif j % 2 == 1 and i % 2 == 1:
                glColor4f(0, 0, 0, 0.2)
            elif j % 2 == 0 and i % 2 == 0:
                glColor4f(0, 0, 0, 0.2)
            else:
                glColor4f(1, 1, 1, 0.2)

            glBegin(GL_TRIANGLES)
            glVertex3f(board[i][j][0]    , board[i][j][1]    , board[i][j][2]     + 0.2)
            glVertex3f(board[i+1][j][0]  , board[i+1][j][1]  , board[i+1][j][2]   + 0.2)
            glVertex3f(board[i][j+1][0]  , board[i][j+1][1]  , board[i][j+1][2]   + 0.2)
            glVertex3f(board[i+1][j+1][0], board[i+1][j+1][1], board[i+1][j+1][2] + 0.2)
            glVertex3f(board[i+1][j][0]  , board[i+1][j][1]  , board[i+1][j][2]   + 0.2)
            glVertex3f(board[i][j+1][0]  , board[i][j+1][1]  , board[i][j+1][2]   + 0.2)
            glEnd()
    glPopMatrix()
