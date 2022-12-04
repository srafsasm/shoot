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


# bullet
class Bullet:

    # initialization
    def __init__(self, pos, size, mass, life, speed, angle):
        self.pos = np.copy(pos)
        self.size = 0.01 * size
        self.mass = mass
        self.life = life
        self.velocity = 0.01 * speed * np.array([np.cos(np.deg2rad(angle)), np.sin(np.deg2rad(angle))])
    
    # update life and position
    def update(self):
        self.life -= 1
        self.pos[0:2] = np.add(self.pos[0:2], self.velocity)
    
    # draw a bullet
    def draw(self):
        glPushMatrix()
        glTranslatef(*self.pos)
        sphere = gluNewQuadric()
        gluSphere(sphere, self.size, 10, 10)
        glPopMatrix()
