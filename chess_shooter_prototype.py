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
from Shoot.bullet import *
from Shoot.collision import *
from Shoot.particles import *
from Shoot.player import *
from Shoot.viewchange import *
from ChessSystem.chessRule import *
from ChessSystem.markingBoard import *

WIDTH = 600
HEIGHT = 400
DISPLAY = (WIDTH * 2, HEIGHT)

class Game:
    def __init__(self):
        self.player1 = Player(pos = [-0.5, 0, 0.5], size=5, angle=0, hp=2)
        self.player1bullets = []
        self.player2 = Player(pos = [0.5, 0, 0.5], size=5, angle=180, hp=2)
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

        ##### chess manage #####
        self.managedBoard = chessBoard()
        self.markedBoard = MarkingBoard(1.36)

        self.currentPlayer = -1
        self.currentPos = [0,0]

        ##### chess manage #####

        self.player1_piece = None
        self.player2_piece = None
        self.player1_win = False
        self.player2_win = False
        self.is_attacking = None
        self.isGameOver = False
        self.attacker = None
        self.save = None

    # Duplicated from assignment 2
    def light(self):
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_LIGHTING)
        glEnable(GL_DEPTH_TEST)

        # feel free to adjust light colors
        lightAmbient = [0.5, 0.5, 0.5, 1.0]
        lightDiffuse = [0.5, 0.5, 0.5, 1.0]
        lightSpecular = [0.5, 0.5, 0.5, 1.0]
        lightPosition = [0, 1.5, 0, 0]    # vector: point at infinity
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
            piece.movePiece(result[0], result[1], result[2])
        else:
            piece.draw()

    def draw(self):
        if self.shoot:
            # Visualize bullets
            glColor3f(1.0, 0.0, 0.0)
            self.player1.draw(self.player1_piece)
            for bullet in self.player1bullets:
                bullet.draw()
            glColor3f(0.0, 1.0, 0.0)
            self.player2.draw(self.player2_piece)
            for bullet in self.player2bullets:
                bullet.draw()
            # visualize players
            self.particleSys.draw()

        glPushMatrix()
        glScalef(1.7, 1.7, 1.7)
        drawChessBoard()
        glPopMatrix()

        # visualize chess pieces
        for piece in [block for rows in self.managedBoard.board for block in rows]:
            if piece is None:
                continue
            if piece.moving:
                if self.chess:
                    self.movePiece(piece, [self.managedBoard.xstart, piece.holdheight, self.managedBoard.ystart], [piece.moving_x_to, piece.height,piece.moving_z_to])
                else:
                    self.movePiece(piece, piece.place, [piece.place[0], piece.height+self.piece_y, piece.place[2]])
            elif piece.holding:
                piece.holdPiece()
            else:
                self.piece_x = 0
                self.piece_y = 0.45
                self.piece_z = 0
                piece.show()

        # visualize a battlefield
        if self.shoot:
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

                    # player 1 이동처리
                    if self.currentPlayer == -1:
                        if event.key == 97: # a
                            if self.currentPos[0] > 0:
                                self.currentPos[0] = self.currentPos[0] - 1
                        elif event.key == 119: # w
                            if self.currentPos[1] < 7:
                                self.currentPos[1] = self.currentPos[1] + 1
                        elif event.key == 100: # d
                            if self.currentPos[0] < 7:
                                self.currentPos[0] = self.currentPos[0] + 1
                        elif event.key == 115: # s
                            if self.currentPos[1] > 0:
                                self.currentPos[1] = self.currentPos[1] - 1
                    
                    # player -1 이동처리
                    elif self.currentPlayer == 1:
                        if event.key == 1073741903: # left
                            if self.currentPos[0] > 0:
                                self.currentPos[0] = self.currentPos[0] - 1
                        elif event.key == 1073741905: # up
                            if self.currentPos[1] < 7:
                                self.currentPos[1] = self.currentPos[1] + 1
                        elif event.key == 1073741904: # right
                            if self.currentPos[0] < 7:
                                self.currentPos[0] = self.currentPos[0] + 1
                        elif event.key == 1073741906: # down
                            if self.currentPos[1] > 0:
                                self.currentPos[1] = self.currentPos[1] - 1
                    
                    
                    # 칸 선택시 처리
                    if event.key == 13: # Enter
                        # 아직 어느 piece도 선택되지 않은 경우
                        if self.managedBoard.selected == None:
                            # 현재 칸에 piece가 없거나 상대 piece인 경우
                            if self.managedBoard.retPiece(self.currentPos[0], self.currentPos[1]) == None or self.managedBoard.retPiece(self.currentPos[0], self.currentPos[1]).group * self.currentPlayer == -1:
                                print("can't select")
                            # 현재 칸에 자신의 piece가 있는 경우
                            elif self.managedBoard.retPiece(self.currentPos[0], self.currentPos[1]).group * self.currentPlayer == 1:
                                self.managedBoard.selectPiece(self.currentPos[0], self.currentPos[1])
                        
                        # 어떤 piece가 선택되어 있는 경우
                        else:
                            # 현재 칸이 이동, 혹은 적 piece를 잡을 수 있는 칸인 경우
                            if self.managedBoard.checkMovable(self.currentPos[0], self.currentPos[1]) or self.managedBoard.checkCatchable(self.currentPos[0], self.currentPos[1]):
                                
                                # Change from chess mode to shooting mode
                                self.is_attacking = self.managedBoard.is_attacking(self.currentPos[0], self.currentPos[1])
                                if self.is_attacking[0]:
                                    self.chess = False
                                    self.shoot = True
                                    self.view_p1.changing = True
                                    self.view_p2.changing = True
                                    if self.is_attacking[1].name[:5] == 'White':
                                        self.player1_piece = self.is_attacking[1]
                                        self.player2_piece = self.is_attacking[2]
                                    else:
                                        self.player1_piece = self.is_attacking[2]
                                        self.player2_piece = self.is_attacking[1]
                                    self.attacker = self.currentPlayer
                                    self.save = [self.managedBoard.selected[0], self.managedBoard.selected[1], self.currentPos[0], self.currentPos[1]]

                                else:
                                    self.isGameOver = self.managedBoard.movePieces(self.currentPos[0], self.currentPos[1])
                                self.currentPlayer = self.currentPlayer * -1
                                
                            # select 해제
                            self.managedBoard.selectPiece(None, None)

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
            
            # Someone wins
            if self.player1.hp <= 0:
                self.player2_win = True
                self.chess = True
                self.shoot = False
                self.view_p1.changing = False
                self.view_p2.changing = False
                self.is_attacking = None
                self.player1.hp = 2
                self.player2.hp = 2
            elif self.player2.hp <= 0:
                self.player1_win = True
                self.chess = True
                self.shoot = False
                self.view_p1.changing = False
                self.view_p2.changing = False
                self.is_attacking = None
                self.player1.hp = 2
                self.player2.hp = 2
            
            if self.player1_win:
                if self.attacker == -1:
                    self.isGameOver = self.managedBoard.remove_lost(self.save[0], self.save[1], self.save[2], self.save[3])
                self.attacker = None
                self.save = None
                self.player1_win = False
                self.player2_win = False
                
            elif self.player2_win:
                if self.attacker == 1:
                    self.isGameOver = self.managedBoard.remove_lost(self.save[0], self.save[1], self.save[2], self.save[3])
                self.attacker = None
                self.save = None
                self.player1_win = False
                self.player2_win = False

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

            # chess play update
            self.managedBoard.updateColorBoard(self.currentPos)
            self.markedBoard.draw(self.managedBoard.colorBoard)
            self.managedBoard.drawPieces(1.36)

            glViewport(WIDTH, 0, WIDTH, HEIGHT)


            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            # View - initial value: (1.0, 0.0, 0.5,   0.0, 0.0, 0.0,   0.0, 0.0, 0.1)
            if self.chess:
                self.view_p2.shoot_to_chess()
            else:
                self.view_p2.chess_to_shoot()

            self.draw()

            # chess play update
            self.managedBoard.updateColorBoard(self.currentPos)
            self.markedBoard.draw(self.managedBoard.colorBoard)
            self.managedBoard.drawPieces(1.36)

            glWindowPos2d(20, HEIGHT-50)
            glDrawPixels(player1hp_surface.get_width(), player1hp_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, player1hp_textdata)
            glWindowPos2d(WIDTH+20, HEIGHT-50)
            glDrawPixels(player2hp_surface.get_width(), player2hp_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, player2hp_textdata)

            pygame.display.flip()
            pygame.time.wait(10)


game = Game()
game.display()
