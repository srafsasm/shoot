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

class Player:

    def __init__(self, pos, size, angle, hp):
        self.pos = np.array(pos)
        self.size = size * 0.01
        self.angle = np.deg2rad(angle)
        self.rotateDir = 0
        self.acc = np.array([0.0, 0.0])
        self.velocity = np.array([0.0, 0.0])
        self.isShoot = False
        self.bulletDelay = 0
        self.hp = hp
    
    def update(self):
        self.angle += np.deg2rad(self.rotateDir)
        accnorm = np.linalg.norm(self.acc, 2)
        cosine = np.cos(self.angle)
        sine = np.sin(self.angle)
        rot = np.array([[cosine, -sine],
                        [sine, cosine]])
        # update velocity with acceleration
        if accnorm:
            nacc = self.acc / accnorm
            self.velocity = np.add(self.velocity, 0.001 * rot @ nacc)
            velonorm = np.linalg.norm(self.velocity, 2)
            if velonorm >= 0.02:
                self.velocity /= velonorm
                self.velocity *= 0.02
        # dynamic friction
        if np.linalg.norm(self.velocity, 2):
            friction = self.velocity / np.linalg.norm(self.velocity, 2) * 0.0005
            for i in range(2):
                if (abs(self.velocity[i]) < abs(friction[i])):
                    self.velocity[i] = 0
                else:
                    self.velocity[i] -= friction[i]
        # update position
        self.pos[0:2] = np.add(self.pos[0:2], self.velocity)

    def draw(self):
        glPushMatrix()
        glTranslatef(*self.pos)
        cylinder = gluNewQuadric()
        gluCylinder(cylinder, self.size, self.size, 0.1, 10, 1)
        glPopMatrix()