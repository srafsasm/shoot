from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import pygame
from pygame.locals import *
import numpy as np
import time

WIDTH = 400
HEIGHT = 400
DISPLAY = (WIDTH, HEIGHT)

class Bullet:

    # Initializes bullet size, bullet speed, and moving angle
    def __init__(self, size, speed, angle):
        self.size = size
        self.speed = speed
        self.angle = angle
        self.move = [0, 0, 0]
    
    # Creates a bullet. Currently a red sphere is created.
    def create(self):
        sphere = gluNewQuadric()
        glColor3f(1.0, 0.0, 0.0)
        gluQuadricTexture(sphere, GL_TRUE)
        gluSphere(sphere, self.size * 0.01, 100, 100)

    # Multiplies transform matrices. No need to change unless you know what you are doing.
    def movement(self):
        glRotatef(self.angle, 0, 1, 0)
        glTranslatef(self.speed * self.move[0], self. speed * self.move[1], self.speed * self.move[2])

    # Multiplies transform matrices.
    # A constant 0.01 may need a change if view is changed.
    def forward(self):
        self.move[2] -= 0.01
        

class View:
    def __init__(self):
        self.Bullets = []   # List that stores bullet instances

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
                        self.Bullets.append(Bullet(size=1, speed=3, angle=0))   # a straight bullet
                        self.Bullets.append(Bullet(size=1, speed=3, angle=-10)) # a right sided bullet
                        self.Bullets.append(Bullet(size=1, speed=3, angle=10))  # a left sided bullet

            keypress = pygame.key.get_pressed()
            glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
            glClearColor(0, 0, 0, 1)

            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()

            # Perspective (tentative)
            gluPerspective(60, WIDTH/HEIGHT, 0.1, 50)

            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()

            # View (tentative)
            gluLookAt(0, 0, 0.5,   0, 0, 0,   0, 1, 0)

            # Visualize all the bullets
            for bullet in self.Bullets:
                glPushMatrix()
                bullet.forward()
                bullet.movement()
                bullet.create()
                glPopMatrix()

            pygame.display.flip()
            pygame.time.wait(10)

view = View()
view.display()
