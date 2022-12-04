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
from Chess.Board.skybox import *
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

# FPS display
class FPS:
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Comic Sans MS', 20)
        
    def render(self):
        self.text = self.font.render(str(round(self.clock.get_fps(), 2)), False, (255, 255, 255, 255)).convert_alpha()
        self.data = pygame.image.tostring(self.text, "RGBA", True)

class Game:
    def __init__(self):
        self.player1 = None
        self.player1bullets = []
        self.player2 = None
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
        self.winner = None

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
    
    # update bullets of a regarding b
    def updateBullets(self, a, b):
        for bullet in a.bullets:
            bullet.update()
            if bullet.life == 0:
                a.bullets.remove(bullet)
                del bullet
            elif isColliding(bullet, b):
                handleCollision(bullet, b)
                self.particleSys.add(bullet.pos)
                b.hp -= a.bDamage
                if b.hp <= 0:
                    b.hp = 0
                a.bullets.remove(bullet)
                del bullet

    def movePiece(self, piece, startplace, endplace):
        if piece.moving == True:
            result = [0, 0, 0]
            result[0] = (endplace[0] - startplace[0])/piece.movingSpeed
            result[1] = (endplace[1] - startplace[1])/piece.movingSpeed
            result[2] = (endplace[2] - startplace[2])/piece.movingSpeed
            if piece.name[5:-1] == 'Knight':
                piece.moveKnight(result[0], result[1], result[2])
            else:
                piece.movePiece(result[0], result[1], result[2])
        else:
            piece.draw()

    def draw(self):
        if self.shoot:
            glColor3f(1.0, 0.0, 0.0)
            self.player1.draw(self.player1_piece)
            for bullet in self.player1bullets:
                bullet.draw()
            glColor3f(0.0, 1.0, 0.0)
            self.player2.draw(self.player2_piece)
            for bullet in self.player2bullets:
                bullet.draw()
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
                if not piece.shooting:
                    piece.show()

        # visualize a battlefield
        if self.shoot:
            glPushMatrix()
            glScalef(2, 2, 2)
            drawBattlefield()
            glPopMatrix()

    def drawHPbar(self):
        p1 = self.player1.hp / pieceStat[self.player1.type][0][1]
        p2 = self.player2.hp / pieceStat[self.player2.type][0][1]

        glClear(GL_DEPTH_BUFFER_BIT)
        glViewport(0, 0, WIDTH * 2, HEIGHT)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-2, 2, -1, 1, -1, 1)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glBegin(GL_QUADS)
        # player1 HP bar
        r = min(1, 2 * (1 - p1))
        g = min(1, 2 * p1)
        glColor3f(r, g, 0)
        glVertex3f(-1.8 * p1 - 0.1, 0.9, 0)
        glVertex3f(-0.1, 0.9, 0)
        glVertex3f(-0.1, 0.8, 0)
        glVertex3f(-1.8 * p1 - 0.1, 0.8, 0)
        # player2 HP bar
        r = min(1, 2 * (1 - p2))
        g = min(1, 2 * p2)
        glColor3f(r, g, 0)
        glVertex3f(1.8 * p2 + 0.1, 0.9, 0)
        glVertex3f(0.1, 0.9, 0)
        glVertex3f(0.1, 0.8, 0)
        glVertex3f(1.8 * p2 + 0.1, 0.8, 0)

        glEnd()
    
    def GameOver(self):
        font = pygame.font.SysFont('Comic Sans MS', 30)
        text = font.render(self.winner + "'s VICTORY!", False, (255, 255, 255, 255)).convert_alpha()
        data = pygame.image.tostring(text, 'RGBA', True)
        glWindowPos2f(160,200)
        glDrawPixels(text.get_width(), text.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, data)
        glWindowPos2f(760,200)
        glDrawPixels(text.get_width(), text.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, data)

    # pygame-based interface
    def display(self):
        pygame.init()
        screen = pygame.display.set_mode(DISPLAY, DOUBLEBUF|OPENGL)

        fps = FPS()
            
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        tick = 0

        self.skybox = Skybox()
        self.light()

        run = True

        while run:
            glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
            glClearColor(0, 0, 0, 1)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                
                if not self.isGameOver:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            run = False
                        if self.chess:
                            # player 1 이동처리
                            if self.currentPlayer == -1:
                                if event.key == pygame.K_f:
                                    if self.currentPos[0] > 0:
                                        self.currentPos[0] = self.currentPos[0] - 1
                                elif event.key == pygame.K_t:
                                    if self.currentPos[1] < 7:
                                        self.currentPos[1] = self.currentPos[1] + 1
                                elif event.key == pygame.K_h:
                                    if self.currentPos[0] < 7:
                                        self.currentPos[0] = self.currentPos[0] + 1
                                elif event.key == pygame.K_g:
                                    if self.currentPos[1] > 0:
                                        self.currentPos[1] = self.currentPos[1] - 1
                                
                                # 칸 선택시 처리
                                elif event.key == K_x: # Enter
                                    # 아직 어느 piece도 선택되지 않은 경우
                                    if self.managedBoard.selected == None:
                                        # 현재 칸에 piece가 없거나 상대 piece인 경우
                                        if self.managedBoard.retPiece(self.currentPos[0], self.currentPos[1]) == None or self.managedBoard.retPiece(self.currentPos[0], self.currentPos[1]).group * self.currentPlayer == -1:
                                            pass
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
                                                self.player1 = Player(pos = [-0.5, 0, 0.5], angle=0, type=self.player1_piece.name[5:-1])
                                                self.player2 = Player(pos = [0.5, 0, 0.5], angle=180, type=self.player2_piece.name[5:-1])
                                                self.attacker = self.currentPlayer
                                                self.save = [self.managedBoard.selected[0], self.managedBoard.selected[1], self.currentPos[0], self.currentPos[1]]
                                                self.managedBoard.board[7-self.save[1]][self.save[0]].shooting = True
                                                self.managedBoard.board[7-self.save[3]][self.save[2]].shooting = True

                                            else:
                                                self.isGameOver = self.managedBoard.movePieces(self.currentPos[0], self.currentPos[1])
                                            self.currentPlayer = self.currentPlayer * -1
                                            
                                        # select 해제
                                        self.managedBoard.selectPiece(None, None)

                                
                            
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
                                if event.key == K_PERIOD: # Enter
                                    # 아직 어느 piece도 선택되지 않은 경우
                                    if self.managedBoard.selected == None:
                                        # 현재 칸에 piece가 없거나 상대 piece인 경우
                                        if self.managedBoard.retPiece(self.currentPos[0], self.currentPos[1]) == None or self.managedBoard.retPiece(self.currentPos[0], self.currentPos[1]).group * self.currentPlayer == -1:
                                            pass
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
                                                self.player1 = Player(pos = [-0.5, 0, 0.5], angle=0, type=self.player1_piece.name[5:-1])
                                                self.player2 = Player(pos = [0.5, 0, 0.5], angle=180, type=self.player2_piece.name[5:-1])
                                                self.attacker = self.currentPlayer
                                                self.save = [self.managedBoard.selected[0], self.managedBoard.selected[1], self.currentPos[0], self.currentPos[1]]
                                                self.managedBoard.board[7-self.save[1]][self.save[0]].shooting = True
                                                self.managedBoard.board[7-self.save[3]][self.save[2]].shooting = True

                                            else:
                                                self.isGameOver = self.managedBoard.movePieces(self.currentPos[0], self.currentPos[1])
                                            self.currentPlayer = self.currentPlayer * -1
                                            
                                        # select 해제
                                        self.managedBoard.selectPiece(None, None)

                        else:
                            if event.key == pygame.K_x:
                                self.player1.isShoot = True
                            elif event.key == pygame.K_PERIOD:
                                self.player2.isShoot = True

                            elif event.key == pygame.K_UP:
                                self.player2.acc[0] += 1
                            elif event.key == pygame.K_DOWN:
                                self.player2.acc[0] -= 1
                            elif event.key == pygame.K_LEFT:
                                self.player2.acc[1] += 1
                            elif event.key == pygame.K_RIGHT:
                                self.player2.acc[1] -= 1
                            
                            elif event.key == pygame.K_t:
                                self.player1.acc[0] += 1
                            elif event.key == pygame.K_g:
                                self.player1.acc[0] -= 1
                            elif event.key == pygame.K_f:
                                self.player1.acc[1] += 1
                            elif event.key == pygame.K_h:
                                self.player1.acc[1] -= 1

                            elif event.key == pygame.K_z:
                                self.player1.rotateDir += 2
                            elif event.key == pygame.K_c:
                                self.player1.rotateDir -= 2

                            elif event.key == pygame.K_COMMA:
                                self.player2.rotateDir += 2
                            elif event.key == pygame.K_SLASH:
                                self.player2.rotateDir -= 2
                                
                    if event.type == pygame.KEYUP:
                        if self.shoot:
                            if event.key == pygame.K_x:
                                self.player1.isShoot = False
                            elif event.key == pygame.K_PERIOD:
                                self.player2.isShoot = False
                            
                            elif event.key == pygame.K_UP:
                                self.player2.acc[0] -= 1
                            elif event.key == pygame.K_DOWN:
                                self.player2.acc[0] += 1
                            elif event.key == pygame.K_LEFT:
                                self.player2.acc[1] -= 1
                            elif event.key == pygame.K_RIGHT:
                                self.player2.acc[1] += 1
                            
                            elif event.key == pygame.K_t:
                                self.player1.acc[0] -= 1
                            elif event.key == pygame.K_g:
                                self.player1.acc[0] += 1
                            elif event.key == pygame.K_f:
                                self.player1.acc[1] -= 1
                            elif event.key == pygame.K_h:
                                self.player1.acc[1] += 1

                            elif event.key == pygame.K_z:
                                self.player1.rotateDir -= 2
                            elif event.key == pygame.K_c:
                                self.player1.rotateDir += 2
                            
                            elif event.key == pygame.K_COMMA :
                                self.player2.rotateDir -= 2
                            elif event.key == pygame.K_SLASH :
                                self.player2.rotateDir += 2

            pygame.key.get_pressed()
            
            if self.shoot:
                self.player1.update()
                self.view_p1.update_start([self.player1.pos[0] - 0.5 * np.cos(np.deg2rad(self.player1.angle)), self.player1.pos[1] - 0.5 * np.sin(np.deg2rad(self.player1.angle)),
                      self.player1.pos[0] + 0.5 * np.cos(np.deg2rad(self.player1.angle)), self.player1.pos[1] + 0.5 * np.sin(np.deg2rad(self.player1.angle))])
                self.player2.update()
                self.view_p2.update_start([self.player2.pos[0] - 0.5 * np.cos(np.deg2rad(self.player2.angle)), self.player2.pos[1] - 0.5 * np.sin(np.deg2rad(self.player2.angle)),
                      self.player2.pos[0] + 0.5 * np.cos(np.deg2rad(self.player2.angle)), self.player2.pos[1] + 0.5 * np.sin(np.deg2rad(self.player2.angle))])
                self.player1.shoot()
                self.player2.shoot()
            
                if isColliding(self.player1, self.player2):
                    handleCollision(self.player1, self.player2)
                handleBoundary(self.player1, 0.8)
                handleBoundary(self.player2, 0.8)
                
                self.updateBullets(self.player1, self.player2)
                self.updateBullets(self.player2, self.player1)
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
                if self.view_p1.changing: self.view_p1.chess_to_shoot()
                else: gluLookAt(self.player1.pos[0] - 0.5 * np.cos(np.deg2rad(self.player1.angle)), self.player1.pos[1] - 0.5 * np.sin(np.deg2rad(self.player1.angle)), 1,
                      self.player1.pos[0] + 0.5 * np.cos(np.deg2rad(self.player1.angle)), self.player1.pos[1] + 0.5 * np.sin(np.deg2rad(self.player1.angle)), 0,
                      0, 0, 1)

            self.skybox.draw(1)
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
                if self.view_p2.changing: 
                    self.view_p2.chess_to_shoot()
                else: 
                    gluLookAt(self.player2.pos[0] - 0.5 * np.cos(np.deg2rad(self.player2.angle)), self.player2.pos[1] - 0.5 * np.sin(np.deg2rad(self.player2.angle)), 1,
                      self.player2.pos[0] + 0.5 * np.cos(np.deg2rad(self.player2.angle)), self.player2.pos[1] + 0.5 * np.sin(np.deg2rad(self.player2.angle)), 0,
                      0, 0, 1)
            self.skybox.draw(-1)
            self.draw()
            if self.isGameOver: self.GameOver()

            # chess play update
            self.managedBoard.updateColorBoard(self.currentPos)
            self.markedBoard.draw(self.managedBoard.colorBoard)
            self.managedBoard.drawPieces(1.36)

            if self.shoot:
                # Someone wins
                if self.player1.hp <= 0:
                    self.player2_win = True
                    self.chess = True
                    self.shoot = False
                    self.view_p1.changing = True
                    self.view_p2.changing = True
                    self.is_attacking = None
                    del self.player1
                    del self.player2
                    self.managedBoard.board[7-self.save[1]][self.save[0]].shooting = False
                    self.managedBoard.board[7-self.save[3]][self.save[2]].shooting = False
                elif self.player2.hp <= 0:
                    self.player1_win = True
                    self.chess = True
                    self.shoot = False
                    self.view_p1.changing = True
                    self.view_p2.changing = True
                    self.is_attacking = None
                    del self.player1
                    del self.player2
                    self.managedBoard.board[7-self.save[1]][self.save[0]].shooting = False
                    self.managedBoard.board[7-self.save[3]][self.save[2]].shooting = False

                
                if self.player1_win:
                    if self.attacker == -1:
                        self.isGameOver = self.managedBoard.remove_lost(self.save[0], self.save[1], self.save[2], self.save[3], attacker_won=True)
                        if self.isGameOver: self.winner = 'Player 1'
                    else:
                        self.isGameOver = self.managedBoard.remove_lost(self.save[0], self.save[1], self.save[2], self.save[3], attacker_won=False)
                        if self.isGameOver: self.winner = 'Player 2'
                    self.attacker = None
                    self.save = None
                    self.player1_win = False
                    self.player2_win = False
                    self.particleSys.init_particles()
                    
                elif self.player2_win:
                    if self.attacker == 1:
                        self.isGameOver = self.managedBoard.remove_lost(self.save[0], self.save[1], self.save[2], self.save[3], attacker_won=True)
                        if self.isGameOver: self.winner = 'Player 2'
                    else:
                        self.isGameOver = self.managedBoard.remove_lost(self.save[0], self.save[1], self.save[2], self.save[3], attacker_won=False)
                        if self.isGameOver: self.winner = 'Player 1'
                    self.attacker = None
                    self.save = None
                    self.player1_win = False
                    self.player2_win = False
                    self.particleSys.init_particles()

            if self.shoot:
                self.drawHPbar()
            
            # Show fps
            # fps.render()
            # glDrawPixels(fps.text.get_width(), fps.text.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, fps.data)

            pygame.display.flip()
            fps.clock.tick(60)


game = Game()
game.display()
