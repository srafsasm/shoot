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

# 2D collision detection between two players
def isColliding(object1, object2):
    diff = np.subtract(object1.pos, object2.pos)
    d = np.sqrt(diff[0] ** 2 + diff[1] ** 2)
    return d <= object1.size + object2.size

# 2D dynamic-dynamic circle collision response handler
def handleCollision(object1, object2):
    diff = np.subtract(object2.pos, object1.pos)
    dist = np.sqrt(diff[0] ** 2 + diff[1] ** 2)
    n = diff[0:2] / dist
    # correct clipping
    correction = object1.size + object2.size - dist
    object1.pos[0:2] = np.subtract(object1.pos[0:2], n * correction / 2)
    object2.pos[0:2] = np.add(object2.pos[0:2], n * correction / 2)
    p = 2 * (np.dot(object1.velocity, n) - np.dot(object2.velocity, n)) / (object1.mass + object2.mass)
    object1.velocity = np.subtract(object1.velocity, p * object2.mass * n)
    object2.velocity = np.add(object2.velocity, p * object1.mass * n)

# 2D boundary collision response handler
def handleBoundary(object, bound):
    for i in range(2):
        if (abs(object.pos[i]) + object.size) > bound:
            object.pos[i] += -2 * np.sign(object.pos[i]) * (abs(object.pos[i]) + object.size - bound)
            object.velocity[i] *= -1
