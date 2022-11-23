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
from Chess.Board.board import *
from Chess.Board.piece import *
from Shoot.bullet import *
from Shoot.collision import *
from Shoot.particles import *
from Shoot.player import *
from Shoot.viewchange import *

WIDTH = 600
HEIGHT = 400
DISPLAY = (WIDTH * 2, HEIGHT)

class Game:
    def __init__(self):
        self.player1 = Player(pos = [-0.5, 0, 0.5], size=5, angle=0, hp=200)
        self.player1bullets = []
        self.player2 = Player(pos = [0.5, 0, 0.5], size=5, angle=180, hp=200)
        self.player2bullets = []
        self.numHits = 0
        self.particleSys = ParticleSystem()

        self.Pieces = []    # a list of chess pieces
        self.piece_x = 0
        self.piece_y = 0.45
        self.piece_z = 0

        self.chess = True   # chess mode
        self.shoot = False  # shooting mode

        self.view_p1 = View(1, [1, 0, 0, 0])    # player1's view
        self.view_p2 = View(2, [-1, 0, 0, 0])   # player2's view

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
    
    # Update bullets info
    def updateBullets(self):
        # Destroy the bullets after moving certain distance. Currently 1.
        for bullet in self.player1bullets:
            bullet.update()
            if abs(bullet.distance) >= 1:
                self.player1bullets.remove(bullet)
                del bullet
            elif isColliding(bullet, self.player2):
                self.particleSys.add(bullet.pos)
                self.player2.hp -= 1
                self.player1bullets.remove(bullet)
                del bullet
        for bullet in self.player2bullets:
            bullet.update()
            if abs(bullet.distance) >= 1:
                self.player2bullets.remove(bullet)
                del bullet
            elif isColliding(bullet, self.player1):
                self.particleSys.add(bullet.pos)
                self.player1.hp -= 1
                self.player2bullets.remove(bullet)
                del bullet

    def movePiece(self, piece, startplace, endplace):
        if piece.moving == True:
            result = [0, 0, 0]
            result[0] = (endplace[0] - startplace[0])/piece.movingSpeed
            result[1] = (endplace[1] - startplace[1])/piece.movingSpeed
            result[2] = (endplace[2] - startplace[2])/piece.movingSpeed
            piece.move(result[0], result[1], result[2])
        else:
            piece.show()

    def draw(self):

        # Visualize bullets
        glColor3f(1.0, 0.0, 0.0)
        self.player1.draw()
        for bullet in self.player1bullets:
            bullet.draw()
        glColor3f(0.0, 1.0, 0.0)
        self.player2.draw()
        for bullet in self.player2bullets:
            bullet.draw()
        # visualize players
        self.particleSys.draw()

        glPushMatrix()
        glScalef(1.7, 1.7, 1.7)
        drawChessBoard()
        glPopMatrix()

        # visualize chess pieces
        for piece in self.Pieces:
            if piece.moving:
                if self.chess:
                    self.movePiece(piece, piece.place, [piece.place[0], piece.height, -piece.place[2]])
                    # self.movePiece(piece, piece.place, [piece.box4, piece.height, -piece.box4])
                else:
                    self.movePiece(piece, piece.place, [piece.place[0], piece.height+self.piece_y, -piece.place[2]])
            else:
                self.piece_x = 0
                self.piece_y = 0.45
                self.piece_z = 0
                piece.show()

        # visualize a battlefield
        glPushMatrix()
        glScalef(2, 2, 2)
        drawBattlefield()
        glPopMatrix()

    # pygame-based interface
    def display(self):
        pygame.init()
        pygame.display.set_mode(DISPLAY, DOUBLEBUF|OPENGL)

        myfont = pygame.font.SysFont('Comic Sans MS', 30)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        tick = 0

        self.light()

        run = True

        while run:
            glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
            glClearColor(0, 0, 0, 1)
            player1hp_surface = myfont.render('Player1 HP: ' + str(self.player1.hp), False, (255, 255, 255, 255)).convert_alpha()
            player2hp_surface = myfont.render('Player2 HP: ' + str(self.player2.hp), False, (255, 255, 255, 255)).convert_alpha()
            player1hp_textdata = pygame.image.tostring(player1hp_surface, "RGBA", True)
            player2hp_textdata = pygame.image.tostring(player2hp_surface, "RGBA", True)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        run = False

                    elif event.key == pygame.K_t:
                        self.player1.isShoot = True
                    elif event.key == pygame.K_LEFTBRACKET:
                        self.player2.isShoot = True

                    elif event.key == pygame.K_i:
                        self.player2.acc[0] += 1
                    elif event.key == pygame.K_k:
                        self.player2.acc[0] -= 1
                    elif event.key == pygame.K_j:
                        self.player2.acc[1] += 1
                    elif event.key == pygame.K_l:
                        self.player2.acc[1] -= 1
                    
                    elif event.key == pygame.K_w:
                        self.player1.acc[0] += 1
                    elif event.key == pygame.K_s:
                        self.player1.acc[0] -= 1
                    elif event.key == pygame.K_a:
                        self.player1.acc[1] += 1
                    elif event.key == pygame.K_d:
                        self.player1.acc[1] -= 1

                    elif event.key == pygame.K_r:
                        self.player1.rotateDir += 2
                    elif event.key == pygame.K_y:
                        self.player1.rotateDir -= 2

                    elif event.key == pygame.K_p:
                        self.player2.rotateDir += 2
                    elif event.key == pygame.K_RIGHTBRACKET:
                        self.player2.rotateDir -= 2
                    
                    elif event.key == pygame.K_x:
                        for name in PIECENAMES:
                            self.Pieces.append(Piece(name))
                        for piece in self.Pieces:
                            piece.show()
                    elif event.key == pygame.K_q:
                        if self.chess:
                            self.chess = False
                            self.shoot = True
                            self.view_p1.changing = True
                            self.view_p2.changing = True
                        else:
                            self.chess = True
                            self.shoot = False
                            self.view_p1.changing = True
                            self.view_p2.changing = True
                    elif event.key == pygame.K_z:
                        p1 = self.Pieces[0]
                        p2 = self.Pieces[1]
                        p1.moving = True
                        p2.moving = True
                    elif event.key == pygame.K_c:
                        piece = self.Pieces[2]
                        piece.moving = True

                              
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_t:
                        self.player1.isShoot = False
                    elif event.key == pygame.K_LEFTBRACKET:
                        self.player2.isShoot = False
                    
                    elif event.key == pygame.K_i:
                        self.player2.acc[0] -= 1
                    elif event.key == pygame.K_k:
                        self.player2.acc[0] += 1
                    elif event.key == pygame.K_j:
                        self.player2.acc[1] -= 1
                    elif event.key == pygame.K_l:
                        self.player2.acc[1] += 1
                    
                    elif event.key == pygame.K_w:
                        self.player1.acc[0] -= 1
                    elif event.key == pygame.K_s:
                        self.player1.acc[0] += 1
                    elif event.key == pygame.K_a:
                        self.player1.acc[1] -= 1
                    elif event.key == pygame.K_d:
                        self.player1.acc[1] += 1

                    elif event.key == pygame.K_r:
                        self.player1.rotateDir -= 2
                    elif event.key == pygame.K_y:
                        self.player1.rotateDir += 2
                    
                    elif event.key == pygame.K_p :
                        self.player2.rotateDir -= 2
                    elif event.key == pygame.K_RIGHTBRACKET :
                        self.player2.rotateDir += 2

            if self.player1.isShoot and self.player1.bulletDelay == 0:
                pos = self.player1.pos.copy()
                pos[2] = 0.05+0.5
                self.player1.bulletDelay = 1
                self.player1bullets.append(Bullet(pos=pos, size=1, speed=3, angle=np.rad2deg(self.player1.angle)))   # a straight bullet
                self.player1bullets.append(Bullet(pos=pos, size=1, speed=3, angle=np.rad2deg(self.player1.angle)+10)) # a right sided bullet
                self.player1bullets.append(Bullet(pos=pos, size=1, speed=3, angle=np.rad2deg(self.player1.angle)-10))  # a left sided bullet
            
            if self.player2.isShoot and self.player2.bulletDelay == 0:
                pos = self.player2.pos.copy()
                pos[2] = 0.05+0.5
                self.player2.bulletDelay = 1
                self.player2bullets.append(Bullet(pos=pos, size=1, speed=3, angle=np.rad2deg(self.player2.angle)))   # a straight bullet
                self.player2bullets.append(Bullet(pos=pos, size=1, speed=3, angle=np.rad2deg(self.player2.angle)+10)) # a right sided bullet
                self.player2bullets.append(Bullet(pos=pos, size=1, speed=3, angle=np.rad2deg(self.player2.angle)-10))  # a left sided bullet

            keypress = pygame.key.get_pressed()

            if self.player1.bulletDelay:
                self.player1.bulletDelay += 1
                if self.player1.bulletDelay == 25:
                    self.player1.bulletDelay = 0
            
            if self.player2.bulletDelay:
                self.player2.bulletDelay += 1
                if self.player2.bulletDelay == 25:
                    self.player2.bulletDelay = 0

            self.player1.update()
            self.view_p1.update_start([self.player1.pos[0] - 0.5 * np.cos(self.player1.angle), self.player1.pos[1] - 0.5 * np.sin(self.player1.angle),
                                       self.player1.pos[0] + 0.5 * np.cos(self.player1.angle), self.player1.pos[1] + 0.5 * np.sin(self.player1.angle)])
            self.player2.update()
            self.view_p2.update_start([self.player2.pos[0] - 0.5 * np.cos(self.player2.angle), self.player2.pos[1] - 0.5 * np.sin(self.player2.angle),
                                       self.player2.pos[0] + 0.5 * np.cos(self.player2.angle), self.player2.pos[1] + 0.5 * np.sin(self.player2.angle)])
            if isColliding(self.player1, self.player2):
                handleCollision(self.player1, self.player2)
            handleBoundary(self.player1, 0.8)
            handleBoundary(self.player2, 0.8)
            self.updateBullets()
            self.particleSys.update()

            glViewport(0, 0, WIDTH, HEIGHT)
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()

            # Perspective
            gluPerspective(60, WIDTH/HEIGHT, 0.1, 50)


            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            # View - initial value: (-1.0, 0.0, 0.5,   0.0, 0.0, 0.0,   0.0, 0.0, 0.1)
            if self.chess:
                self.view_p1.shoot_to_chess()
            else:
                self.view_p1.chess_to_shoot()
            self.draw()
            glViewport(WIDTH, 0, WIDTH, HEIGHT)


            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            # View - initial value: (1.0, 0.0, 0.5,   0.0, 0.0, 0.0,   0.0, 0.0, 0.1)
            if self.chess:
                self.view_p2.shoot_to_chess()
            else:
                self.view_p2.chess_to_shoot()

            self.draw()

            glWindowPos2d(20, HEIGHT-50)
            glDrawPixels(player1hp_surface.get_width(), player1hp_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, player1hp_textdata)
            glWindowPos2d(WIDTH+20, HEIGHT-50)
            glDrawPixels(player2hp_surface.get_width(), player2hp_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, player2hp_textdata)

            pygame.display.flip()
            pygame.time.wait(10)


game = Game()
game.display()