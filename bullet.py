from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import pygame
from pygame.locals import *
import numpy as np
import time
import os
import sys
from obj.chj.ogl import *
from obj.chj.ogl.objloader import CHJ_tiny_obj, OBJ
from obj.chj.ogl import light
from Chess.Board.board import *
from Chess.Board.piece import *
from Shoot.bullet import *

WIDTH = 800 
HEIGHT = 600
DISPLAY = (WIDTH, HEIGHT)

class View:
    def __init__(self):
        self.Bullets = []   # List that stores bullet instances
        self.Pieces = []
        self.Board = False

    # Duplicated from assignment 2
    def light(self):
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_LIGHTING)
        glEnable(GL_DEPTH_TEST)

        # feel free to adjust light colors
        lightAmbient = [0.5, 0.5, 0.5, 1.0]
        lightDiffuse = [0.5, 0.5, 0.5, 1.0]
        lightSpecular = [0.5, 0.5, 0.5, 1.0]
        lightPosition = [1, 1, -1, 0]    # vector: point at infinity
        glLightfv(GL_LIGHT0, GL_AMBIENT, lightAmbient)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, lightDiffuse)
        glLightfv(GL_LIGHT0, GL_SPECULAR, lightSpecular)
        glLightfv(GL_LIGHT0, GL_POSITION, lightPosition)
        glEnable(GL_LIGHT0)
    
    # Update bullets info
    def updateBullets(self):
        # Visualize all the bullets
        for bullet in self.Bullets:
            glPushMatrix()
            bullet.forward()
            bullet.movement()
            bullet.create()
            glPopMatrix()

        # Destroy the bullets after moving certain distance. Currently 1.
        for bullet in self.Bullets:
            if abs(bullet.move[2]) >= 1:
                self.Bullets = self.Bullets[2:]

    # pygame-based interface
    def display(self):
        pygame.init()
        pygame.display.set_mode(DISPLAY, DOUBLEBUF|OPENGL)

        self.light()

        run = True
        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                        run = False

                    # Press z to create a bullet(s)
                    if event.key == pygame.K_z:
                        self.Bullets.append(Bullet(start=[0.0,0.0,0.0], size=1, speed=3, direction=-1, angle=0))   # a straight bullet
                        self.Bullets.append(Bullet(start=[0.0,0.0,0.0], size=1, speed=3, direction=-1, angle=-10)) # a right sided bullet
                        self.Bullets.append(Bullet(start=[0.0,0.0,0.0], size=1, speed=3, direction=-1, angle=10))  # a left sided bullet
                    if event.key == pygame.K_x:
                        for name in PIECENAMES:
                            self.Pieces.append(Piece(name))
                    if event.key == pygame.K_c:
                        self.Board = True

                if event.type == pygame.MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    print(pos)


            keypress = pygame.key.get_pressed()
            glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
            glClearColor(0.6, 0.7, 0.6, 1)

            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()

            # Perspective (tentative)
            gluPerspective(60, WIDTH/HEIGHT, 0.1, 50)

            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()

            # View (tentative)
            gluLookAt(0, 0.3, 0.5,   0, 0, 0,   0, 1, 0)

            self.updateBullets()
            for piece in self.Pieces:
                glColor3f(1, 0.5, 1)
                piece.draw()
            if self.Board: 
                glPushMatrix()
                glTranslatef(0, 0, -0.1)
                glRotatef(-70, 1, 0, 0)
                glScalef(0.7, 0.7, 0.7)
                drawChessBoard()
                glPopMatrix()

            pygame.display.flip()
            pygame.time.wait(10)


view = View()
view.display()