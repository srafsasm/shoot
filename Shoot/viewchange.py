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

class View:
    def __init__(self, player_num, start):
        self.changing = False
        self.xchange = 0
        self.ychange = 0
        self.xchange2 = 0
        self.ychange2 = 0
        self.zchange = 0
        self.player = player_num - 1.5
        self.start = start

    def chess_to_shoot(self):
        if self.zchange >= 0.5: self.changing = False
        if self.changing:
            gluLookAt(2.0*self.player+self.xchange, 0.0+self.ychange, 1.5-self.zchange,   0.0+self.xchange2, 0.0+self.ychange2, 0.0,   0.0, 0.0, 0.1)
            self.xchange += (self.start[0]-2.0*self.player)/10
            self.ychange += (self.start[1])/10
            self.xchange2 += (self.start[2])/10
            self.ychange2 += (self.start[3])/10
            self.zchange += 0.05
        else:
            gluLookAt(self.start[0], self.start[1], 1,   self.start[2], self.start[3], 0.0,   0.0, 0.0, 0.1)
            self.xchange = 0
            self.ychange = 0
            self.xchange2 = 0
            self.ychange2 = 0
            self.zchange = 0


    def shoot_to_chess(self):
        if self.zchange >= 0.5: self.changing = False
        if self.changing:
            gluLookAt(self.start[0]+self.xchange, 0.0+self.start[1]+self.ychange, 1+self.zchange,   0.0+self.start[2]+self.xchange2, 0.0+self.start[3]+self.ychange2, 0.0,   0.0, 0.0, 0.1)
            self.xchange += (2.0*self.player-self.start[0])/10
            self.ychange += -(self.start[1])/10
            self.xchange2 += -(self.start[2])/10
            self.ychange2 += -(self.start[3])/10
            self.zchange += 0.05
        else:
            gluLookAt(2.0*self.player, 0.0, 1.5,   0.0, 0.0, 0.0,   0.0, 0.0, 0.1)
            self.xchange = 0
            self.ychange = 0
            self.xchange2 = 0
            self.ychange2 = 0
            self.zchange = 0
    
    def update_start(self, start):
        self.start = start
