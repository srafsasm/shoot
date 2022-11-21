from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import pygame
from pygame.locals import *
import numpy as np
import time

WIDTH = 400
HEIGHT = 400
DISPLAY = (WIDTH * 2, HEIGHT)

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

class Bullet:

    # Initializes position, size, speed, and angle
    def __init__(self, pos, size, speed, angle):
        self.pos = np.copy(pos)
        self.size = 0.01 * size
        self.speed = 0.01 * speed
        self.velocity = self.speed * np.array([np.cos(np.deg2rad(angle)), np.sin(np.deg2rad(angle))])
        self.distance = 0
    
    # update position
    def update(self):
        self.distance += self.speed
        self.pos[0:2] = np.add(self.pos[0:2], self.velocity)
    
    # create a bullet
    def draw(self):
        glPushMatrix()
        glTranslatef(*self.pos)
        sphere = gluNewQuadric()
        gluSphere(sphere, self.size, 10, 10)
        glPopMatrix()
    


class Particles:

    def __init__(self, pos):
        self.initialpos = np.copy(pos)
        self.displacement = np.zeros((10, 3))
        self.velocity = (np.random.random_sample((10, 3)) - 0.5) / 500
        self.color = np.tile(np.array([np.random.random_sample(10)]).T, (1, 3))
        self.life = np.random.randint(40, 50, 10)
    
    def update(self):
        self.displacement = np.add(self.displacement, self.velocity)
        for i in range(10):
            if self.life[i]:
                self.life[i] -= 1

    def draw(self):
        size = 0.008
        glPushMatrix()
        glTranslatef(*self.initialpos)
        arr0 = np.array(glGetFloatv(GL_MODELVIEW_MATRIX))
        arr0[3, 0:3] = np.zeros(3)
        glMultMatrixf(arr0.T)
        glBegin(GL_QUADS)
        for i in range(10):
            if (self.life[i]):
                glColor3f(*self.color[i])
                glVertex3f(*(np.add(self.displacement[i], (size, size, 0))))
                glVertex3f(*(np.add(self.displacement[i], (size, -size, 0))))
                glVertex3f(*(np.add(self.displacement[i], (-size, -size, 0))))
                glVertex3f(*(np.add(self.displacement[i], (-size, size, 0))))
        glEnd()
        glPopMatrix()

class ParticleSystem:
    def __init__(self):
        self.particleList = []
        
    def add(self, pos):
        for i in range(1):
            self.particleList.append(Particles(pos))

    def update(self):
        for particles in self.particleList:
            particles.update()
            if not np.any(particles.life):
                self.particleList.remove(particles)
                del particles
    
    def draw(self):
        for particles in self.particleList:
            particles.draw()


class Game:
    def __init__(self):
        self.player1 = Player(pos = [-0.5, 0, 0], size=5, angle=0, hp=200)
        self.player1bullets = []
        self.player2 = Player(pos = [0.5, 0, 0], size=5, angle=180, hp=200)
        self.player2bullets = []
        self.numHits = 0
        self.particleSys = ParticleSystem()

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

    def draw(self):
        self.drawBoard()
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


    def drawBoard(self):
        glPushMatrix()
        squareSize = 0.2
        x = -4
        y = -4
        glColor3f(1.0, 1.0, 1.0)
        glBegin(GL_QUADS)
        for i in range(8):
            for j in range(4):
                glVertex3f(x * squareSize, y * squareSize, 0)
                glVertex3f((x + 1) * squareSize, y * squareSize, 0)
                glVertex3f((x + 1) * squareSize, (y + 1) * squareSize, 0)
                glVertex3f(x * squareSize, (y + 1) * squareSize, 0)
                x += 2
            if x == 4:
                x = -3
            elif x == 5:
                x = -4
            y += 1
        glEnd()
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
                pos[2] = 0.05
                self.player1.bulletDelay = 1
                self.player1bullets.append(Bullet(pos=pos, size=1, speed=3, angle=np.rad2deg(self.player1.angle)))   # a straight bullet
                self.player1bullets.append(Bullet(pos=pos, size=1, speed=3, angle=np.rad2deg(self.player1.angle)+10)) # a right sided bullet
                self.player1bullets.append(Bullet(pos=pos, size=1, speed=3, angle=np.rad2deg(self.player1.angle)-10))  # a left sided bullet
            
            if self.player2.isShoot and self.player2.bulletDelay == 0:
                pos = self.player2.pos.copy()
                pos[2] = 0.05
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
            self.player2.update()
            if isColliding(self.player1, self.player2):
                handleCollision(self.player1, self.player2)
            handleBoundary(self.player1, 0.8)
            handleBoundary(self.player2, 0.8)
            self.updateBullets()
            self.particleSys.update()

            glViewport(0, 0, WIDTH, HEIGHT)
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            # Perspective (tentative)
            gluPerspective(60, WIDTH/HEIGHT, 0.1, 50)
            # glOrtho(-0.5, 0.5, -0.5, 0.5, -10, 10)
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            # View (tentative)
            gluLookAt(self.player1.pos[0] - 0.5 * np.cos(self.player1.angle), self.player1.pos[1] - 0.5 * np.sin(self.player1.angle), 0.5,
                      self.player1.pos[0] + 0.5 * np.cos(self.player1.angle), self.player1.pos[1] + 0.5 * np.sin(self.player1.angle), 0,
                      0, 0, 1)
            self.draw()
            glViewport(WIDTH, 0, WIDTH, HEIGHT)

            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            # View (tentative)
            gluLookAt(self.player2.pos[0] - 0.5 * np.cos(self.player2.angle), self.player2.pos[1] - 0.5 * np.sin(self.player2.angle), 0.5,
                      self.player2.pos[0] + 0.5 * np.cos(self.player2.angle), self.player2.pos[1] + 0.5 * np.sin(self.player2.angle), 0,
                      0, 0, 1)
            self.draw()

            glWindowPos2d(20, HEIGHT-50)
            glDrawPixels(player1hp_surface.get_width(), player1hp_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, player1hp_textdata)
            glWindowPos2d(WIDTH+20, HEIGHT-50)
            glDrawPixels(player2hp_surface.get_width(), player2hp_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, player2hp_textdata)

            pygame.display.flip()
            pygame.time.wait(10)


game = Game()
game.display()
