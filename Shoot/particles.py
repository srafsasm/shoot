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

class Particles:

    def __init__(self, pos):
        self.initialpos = np.copy(pos)
        self.displacement = np.zeros((10, 3))
        self.velocity = (np.random.random_sample((10, 3)) - 0.5) / 500
        self.color = np.tile(np.array([np.random.random_sample(10)]).T, (1, 3))
        self.life = np.random.randint(40, 50, 10)
    
    def update(self):
        self.displacement = np.add(self.displacement, self.velocity)
        for i in range(10):
            if self.life[i]:
                self.life[i] -= 1

    def draw(self):
        size = 0.008
        glPushMatrix()
        glTranslatef(*self.initialpos)
        arr0 = np.array(glGetFloatv(GL_MODELVIEW_MATRIX))
        arr0[3, 0:3] = np.zeros(3)
        glMultMatrixf(arr0.T)
        glBegin(GL_QUADS)
        for i in range(10):
            if (self.life[i]):
                glColor3f(*self.color[i])
                glVertex3f(*(np.add(self.displacement[i], (size, size, 0))))
                glVertex3f(*(np.add(self.displacement[i], (size, -size, 0))))
                glVertex3f(*(np.add(self.displacement[i], (-size, -size, 0))))
                glVertex3f(*(np.add(self.displacement[i], (-size, size, 0))))
        glEnd()
        glPopMatrix()

class ParticleSystem:
    def __init__(self):
        self.particleList = []
        
    def add(self, pos):
        for i in range(1):
            self.particleList.append(Particles(pos))

    def update(self):
        for particles in self.particleList:
            particles.update()
            if not np.any(particles.life):
                self.particleList.remove(particles)
                del particles
    
    def draw(self):
        for particles in self.particleList:
            particles.draw()