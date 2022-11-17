from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import pygame
from pygame.locals import *
import numpy as np


class Bullet:

    # Initializes starting point, bullet size, bullet speed, direction(+z or -z), and moving angle
    def __init__(self, start, size, speed, direction, angle):
        self.start = start
        self.size = size
        self.speed = speed
        self.direction = direction
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
        glTranslatef(self.start[0], self.start[1], self.start[2])
        glRotatef(self.angle, 0, 1, 0)
        glTranslatef(self.speed * self.move[0], self. speed * self.move[1], self.speed * self.move[2])

    # Multiplies transform matrices.
    # A constant 0.01 may need a change if view is changed.
    def forward(self):
        self.move[2] += self.direction * 0.01