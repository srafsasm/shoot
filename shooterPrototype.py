from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import pygame
from pygame.locals import *
import numpy as np
import time

WIDTH = 800
HEIGHT = 400
DISPLAY = (WIDTH, HEIGHT)

class Player:

    def __init__(self, pos, size, angle, hp):
        self.pos = pos
        self.size = size * 0.01
        self.angle = angle
        self.direction = [0, 0]
        self.bulletDelay = 0
        self.hp = hp
    
    def move(self):
        self.pos[0] += 0.01 * (np.cos(self.angle) * self.direction[0] - np.sin(self.angle) * self.direction[1])
        self.pos[1] += 0.01 * (np.sin(self.angle) * self.direction[0] + np.cos(self.angle) * self.direction[1])

    def draw(self):
        glPushMatrix()
        glTranslatef(*self.pos)
        cylinder = gluNewQuadric()
        glColor3f(1.0, 1.0, 1.0)
        gluCylinder(cylinder, self.size, self.size, 0.1, 10, 1)
        glPopMatrix()

class Bullet:

    # Initializes starting point, bullet size, bullet speed, direction(+z or -z), and moving angle
    def __init__(self, start, size, speed, direction, angle):
        self.size = size * 0.01
        self.speed = speed
        self.direction = direction
        self.angle = angle * 2 * np.pi / 360
        self.distance = 0
        self.pos = start
    
    # Creates a bullet. Currently a red sphere is created.
    def draw(self):
        glPushMatrix()
        glTranslatef(*self.pos)
        sphere = gluNewQuadric()
        glColor3f(1.0, 1.0, 1.0)
        gluQuadricTexture(sphere, GL_TRUE)
        gluSphere(sphere, self.size, 100, 100)
        glPopMatrix()

    # Multiplies transform matrices.
    # A constant 0.01 may need a change if view is changed.
    def updatePos(self):
        self.distance += 0.01 * self.speed
        self.pos[0] += 0.01 * self.speed * self.direction * np.cos(self.angle)
        self.pos[1] += 0.01 * self.speed * self.direction * np.sin(self.angle)


class Game:
    def __init__(self):
        self.player1 = Player(pos = [-0.5, 0, 0], size=5, angle= 0, hp=200)
        self.player1bullets = []
        self.player2 = Player(pos = [0.5, 0, 0], size=5, angle= np.pi, hp=200)
        self.player2bullets = []
        self.numHits = 0

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
            bullet.updatePos()
            if abs(bullet.distance) >= 1:
                self.player1bullets.remove(bullet)
                # print("removed bullet " + str(bullet))
                del bullet
            elif self.isCollision(bullet, self.player2):
                self.player2.hp -= 1
                self.player1bullets.remove(bullet)
                del bullet
        for bullet in self.player2bullets:
            bullet.updatePos()
            if abs(bullet.distance) >= 1:
                self.player2bullets.remove(bullet)
                # print("removed bullet " + str(bullet))
                del bullet
            elif self.isCollision(bullet, self.player1):
                self.player1.hp -= 1
                self.player2bullets.remove(bullet)
                del bullet


    def isCollision(self, bullet, player):
        dist = 0
        for i in range(2):
            dist += (bullet.pos[i] - player.pos[i]) ** 2
        distance = np.sqrt(dist)
        return distance <= bullet.size + player.size

    def draw(self):
        # Visualize bullets
        for bullet in self.player1bullets:
            bullet.draw()
        for bullet in self.player2bullets:
            bullet.draw()
        # visualize players
        self.player1.draw()
        self.player2.draw()

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
        player1Shoot = False
        player2Shoot = False
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

                    elif event.key == pygame.K_RETURN:
                        player1Shoot = True
                    elif event.key == pygame.K_g:
                        player2Shoot = True

                    elif event.key == pygame.K_UP:
                        self.player1.direction[0] += 1
                    elif event.key == pygame.K_DOWN:
                        self.player1.direction[0] -= 1
                    elif event.key == pygame.K_LEFT:
                        self.player1.direction[1] += 1
                    elif event.key == pygame.K_RIGHT:
                        self.player1.direction[1] -= 1
                    elif event.key == pygame.K_w:
                        self.player2.direction[0] += 1
                    elif event.key == pygame.K_s:
                        self.player2.direction[0] -= 1
                    elif event.key == pygame.K_a:
                        self.player2.direction[1] += 1
                    elif event.key == pygame.K_d:
                        self.player2.direction[1] -= 1                    
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_RETURN:
                        player1Shoot = False
                    if event.key == pygame.K_g:
                        player2Shoot = False
                    
                    elif event.key == pygame.K_UP:
                        self.player1.direction[0] -= 1
                    elif event.key == pygame.K_DOWN:
                        self.player1.direction[0] += 1
                    elif event.key == pygame.K_LEFT:
                        self.player1.direction[1] -= 1
                    elif event.key == pygame.K_RIGHT:
                        self.player1.direction[1] += 1
                    elif event.key == pygame.K_w:
                        self.player2.direction[0] -= 1
                    elif event.key == pygame.K_s:
                        self.player2.direction[0] += 1
                    elif event.key == pygame.K_a:
                        self.player2.direction[1] -= 1
                    elif event.key == pygame.K_d:
                        self.player2.direction[1] += 1  

            if player1Shoot and self.player1.bulletDelay == 0:
                self.player1.bulletDelay += 11
                self.player1bullets.append(Bullet(start=self.player1.pos.copy(), size=1, speed=3, direction=1, angle=0))   # a straight bullet
                self.player1bullets.append(Bullet(start=self.player1.pos.copy(), size=1, speed=3, direction=1, angle=-10)) # a right sided bullet
                self.player1bullets.append(Bullet(start=self.player1.pos.copy(), size=1, speed=3, direction=1, angle=10))  # a left sided bullet
            
            if player2Shoot and self.player2.bulletDelay == 0:
                self.player2.bulletDelay += 11
                self.player2bullets.append(Bullet(start=self.player2.pos.copy(), size=1, speed=3, direction=-1, angle=0))   # a straight bullet
                self.player2bullets.append(Bullet(start=self.player2.pos.copy(), size=1, speed=3, direction=-1, angle=-10)) # a right sided bullet
                self.player2bullets.append(Bullet(start=self.player2.pos.copy(), size=1, speed=3, direction=-1, angle=10))  # a left sided bullet

            keypress = pygame.key.get_pressed()

            if self.player1.bulletDelay:
                self.player1.bulletDelay += 1
                if self.player1.bulletDelay == 50:
                    self.player1.bulletDelay = 0
            
            if self.player2.bulletDelay:
                self.player2.bulletDelay += 1
                if self.player2.bulletDelay == 50:
                    self.player2.bulletDelay = 0

            self.player1.move()
            self.player2.move()
            self.updateBullets()

            glViewport(0, 0, WIDTH // 2, HEIGHT)
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            # Perspective (tentative)
            gluPerspective(60, WIDTH/HEIGHT/2, 0.1, 50)

            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            # View (tentative)
            gluLookAt(-0.5+self.player1.pos[0], self.player1.pos[1], 0.5,   self.player1.pos[0]+0.5, self.player1.pos[1], 0,   0, 0, 1)

            self.draw()

            glViewport(WIDTH // 2, 0, WIDTH // 2, HEIGHT)
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            # Perspective (tentative)
            gluPerspective(60, WIDTH/HEIGHT / 2, 0.1, 50)
            # glOrtho(-1, 1, -1, 1, -10, 10)

            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            # View (tentative)
            gluLookAt(0.5+self.player2.pos[0], self.player2.pos[1], 0.5,   -0.5+self.player2.pos[0], self.player2.pos[1], 0,   0, 0, 1)

            self.draw()

            glViewport(0, 0, WIDTH, HEIGHT)

            glWindowPos2d(20, 350)
            glDrawPixels(player1hp_surface.get_width(), player1hp_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, player1hp_textdata)
            glWindowPos2d(420, 350)
            glDrawPixels(player2hp_surface.get_width(), player2hp_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, player2hp_textdata)

            pygame.display.flip()
            pygame.time.wait(10)


game = Game()
game.display()
