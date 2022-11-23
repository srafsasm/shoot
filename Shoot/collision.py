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

# collision detection between two players
def isColliding(a, b):
    diff = np.subtract(a.pos, b.pos)
    d = np.sqrt(diff[0] ** 2 + diff[1] ** 2)
    return d <= a.size + b.size

# dynamic-dynamic circle collision response handler
def handleCollision(player1, player2):
    diff = np.subtract(player2.pos, player1.pos)
    dist = np.sqrt(diff[0] ** 2 + diff[1] ** 2)
    n = diff / dist
    correction = player1.size + player2.size - dist
    player1.pos = np.subtract(player1.pos, n * correction / 2)
    player2.pos = np.add(player2.pos, n * correction / 2)
    p = np.dot(player1.velocity, n[0:2]) - np.dot(player2.velocity, n[0:2])
    player1.velocity = np.subtract(player1.velocity, p * n[0:2])
    player2.velocity = np.add(player2.velocity, p * n[0:2])

def handleBoundary(player, bound):
    for i in range(2):
        if (abs(player.pos[i]) + player.size) > bound:
            player.pos[i] += - np.sign(player.pos[i]) * (abs(player.pos[i]) + player.size - bound)
            player.velocity[i] *= -1
