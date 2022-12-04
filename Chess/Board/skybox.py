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

class Skybox:

    def __init__(self):
        images = []
        images.append(pygame.image.load('textures/front.jpg'))
        images.append(pygame.image.load('textures/back.jpg'))
        images.append(pygame.image.load('textures/left.jpg'))
        images.append(pygame.image.load('textures/right.jpg'))
        images.append(pygame.image.load('textures/top.jpg'))
        images.append(pygame.image.load('textures/bottom.jpg'))

        for i in range(4, 6):
            images[i] = pygame.transform.rotate(images[i], 90)

        self.texturedata = []

        width = 2048
        height = 2048

        for i in range(6):
            data = pygame.image.tostring(images[i], "RGBA", 1)
            texture = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, texture)
            glPixelStorei(GL_UNPACK_ALIGNMENT,1)
            glTexEnvf( GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE )
            glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR )
            glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR )
            glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
            glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0,GL_RGBA,GL_UNSIGNED_BYTE, data)
            self.texturedata.append(texture)

        length = 10
        x = - (length / 2)
        y = - (length / 2)
        z = - (length / 2)
        self.list = glGenLists(1)
        glNewList(self.list, GL_COMPILE)

        glColor3f(1.0, 1.0, 1.0)
        glEnable(GL_TEXTURE_2D)

        glBindTexture(GL_TEXTURE_2D, self.texturedata[0])
        glBegin(GL_QUADS)
        glTexCoord2f(1, 0)
        glVertex3f(x, y, z+length)
        glTexCoord2f(1, 1)
        glVertex3f(x, y+length, z+length)
        glTexCoord2f(0, 1)
        glVertex3f(x+length, y+length, z+length)
        glTexCoord2f(0, 0)
        glVertex3f(x+length, y, z+length)
        glEnd()

        glBindTexture(GL_TEXTURE_2D, self.texturedata[1])
        glBegin(GL_QUADS)
        glTexCoord2f(1, 0)
        glVertex3f(x+length, y, z)
        glTexCoord2f(1, 1)
        glVertex3f(x+length, y+length, z)
        glTexCoord2f(0, 1)
        glVertex3f(x, y+length, z)
        glTexCoord2f(0, 0)
        glVertex3f(x, y, z)
        glEnd()

        glBindTexture(GL_TEXTURE_2D, self.texturedata[2])
        glBegin(GL_QUADS)
        glTexCoord2f(1, 1)
        glVertex3f(x, y+length, z)
        glTexCoord2f(0, 1)
        glVertex3f(x, y+length, z+length)
        glTexCoord2f(0, 0)
        glVertex3f(x, y, z+length)
        glTexCoord2f(1, 0)
        glVertex3f(x, y, z)
        glEnd()

        glBindTexture(GL_TEXTURE_2D, self.texturedata[3])
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0)
        glVertex3f(x+length, y, z)
        glTexCoord2f(1, 0)
        glVertex3f(x+length, y, z+length)
        glTexCoord2f(1, 1)
        glVertex3f(x+length, y+length, z+length)
        glTexCoord2f(0, 1)
        glVertex3f(x+length, y+length, z)
        glEnd()

        glBindTexture(GL_TEXTURE_2D, self.texturedata[4])
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0)
        glVertex3f(x+length, y+length, z)
        glTexCoord2f(1, 0)
        glVertex3f(x+length, y+length, z+length)
        glTexCoord2f(1, 1)
        glVertex3f(x, y+length, z+length)
        glTexCoord2f(0, 1)
        glVertex3f(x, y+length, z)
        glEnd()

        glBindTexture(GL_TEXTURE_2D, self.texturedata[5])
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0)
        glVertex3f(x, y, z)
        glTexCoord2f(1, 0)
        glVertex3f(x, y, z+length)
        glTexCoord2f(1, 1)
        glVertex3f(x+length, y, z+length)
        glTexCoord2f(0, 1)
        glVertex3f(x+length, y, z)
        glEnd()

        glBindTexture(GL_TEXTURE_2D,0)
        glDisable(GL_TEXTURE_2D)

        glEndList()

    def draw(self, player):
        glPushMatrix()
        glRotatef(player * 20, 0, 1, 0)
        glRotatef(90, 1, 0, 0)
        glCallList(self.list)
        glPopMatrix()