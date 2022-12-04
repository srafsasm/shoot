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
from ChessSystem.chessRule import *
from Shoot.bullet import *

# ((mass, hp), (bSize, bMass, bLife, bDamage, bDelay, bSpeed), (bAngles))
pieceStat = {"Pawn":   ((1, 10), (2, 0.1, 40, 1, 10, 2), (0,)),
             "Knight": ((1, 10), (1, 0.1, 30, 1, 25, 3), (-10, 0, 10)),
             "Bishop": ((1, 10), (1, 0.1, 30, 1, 25, 3), (-135, -45, 45, 135)),
             "Rook":   ((1, 10), (1, 0.1, 30, 1, 25, 3), (-90, 0, 90, 180)),
             "Queen":  ((1, 10), (1, 0.1, 30, 2, 25, 3), (-135, -90, -45, 0, 45, 90, 135, 180)),
             "King":   ((1, 10), (2, 0.1, 30, 1, 25, 2), (-135, -90, -45, 0, 45, 90, 135, 180))}

# player
class Player:

    # initialization
    def __init__(self, pos, angle, type):
        # player parameters
        self.pos = np.array(pos)
        self.size = 0.05
        self.mass, self.hp = pieceStat[type][0]
        self.angle = angle
        self.rotateDir = 0
        self.acc = np.array([0.0, 0.0])
        self.velocity = np.array([0.0, 0.0])
        # shoot key pressed
        self.isShoot = False
        # bullet delay timer
        self.timer = 0
        # bullet parameters     
        self.bSize, self.bMass, self.bLife, self.bDamage, self.bDelay, self.bSpeed = pieceStat[type][1]
        self.bAngles = pieceStat[type][2]
        # bullet list
        self.bullets = []
        # model
        self.type = type

    def init_player(self, player):
        if player == 1: 
            self.pos = np.array([-0.5, 0, 0.5])
            self.angle = np.deg2rad(0)
        elif player == 2: 
            self.pos = np.array([0.5, 0, 0.5])
            self.angle = np.deg2rad(180)
        self.rotateDir = 0
        self.acc = np.array([0.0, 0.0])
        self.hp = 1

    def class_change(self, c):
        if c == 'Pawn': change = pieceStat['Pawn']
        elif c == 'Knight': change = pieceStat['Knight']
        elif c == 'Bishop': change = pieceStat['Bishop']
        elif c == 'Rook': change = pieceStat['Rook']
        elif c == 'Queen': change = pieceStat['Queen']
        elif c == 'King': change = pieceStat['King']
        self.mass, self.hp = change[0]
        self.bSize, self.bMass, self.bLife, self.bDamage, self.bDelay, self.bSpeed = change[1]
        self.bAngles = change[2]

    # update position
    def update(self):
        # update angle
        self.angle += self.rotateDir
        if self.angle < -180:
            self.angle += 360
        if self.angle > 180:
            self.angle -= 360
        accnorm = np.linalg.norm(self.acc, 2)
        cosine = np.cos(np.deg2rad(self.angle))
        sine = np.sin(np.deg2rad(self.angle))
        # rotation matrix for acceleration
        rot = np.array([[cosine, -sine],
                        [sine, cosine]])
        if accnorm:
            # normalize acceleration
            nacc = self.acc / accnorm
            # update velocity applying acceleration
            self.velocity = np.add(self.velocity, 0.001 * rot @ nacc)
        if np.linalg.norm(self.velocity, 2):
            # dynamic friction
            friction = self.velocity / np.linalg.norm(self.velocity, 2) * 0.0005
            # update velocity applying friction
            for i in range(2):
                if (abs(self.velocity[i]) < abs(friction[i])):
                    self.velocity[i] = 0
                else:
                    self.velocity[i] -= friction[i]
        # limit maximum velocity
        velonorm = np.linalg.norm(self.velocity, 2)
        if velonorm >= 0.02:
            self.velocity /= velonorm
            self.velocity *= 0.02
        # update position
        self.pos[0:2] = np.add(self.pos[0:2], self.velocity)

    # shoot bullets
    def shoot(self):
        if self.isShoot and self.timer == 0:
            self.timer = 1
            pos = self.pos.copy()
            pos[2] = 0.55
            # shoot bullets into bAngles
            for angle in self.bAngles:
                self.bullets.append(Bullet(pos, self.bSize, self.bMass, self.bLife, self.bSpeed, angle + self.angle))
        # update bullet delay timer
        if self.timer:
            self.timer += 1
            if self.timer == self.bDelay:
                self.timer = 0
    
    # draw bullets and player
    def draw(self, piece):
        # draw bullets
        for bullet in self.bullets:
            bullet.draw()
        # draw player
        self.pos[2] = 0.5
        glPushMatrix()
        glTranslatef(*self.pos)
        glRotatef(self.angle, 0, 0, 1)
        glScale(PIECESIZE, PIECESIZE, PIECESIZE)
        glCallList(piece.obj.gl_list)
        glPopMatrix()       
