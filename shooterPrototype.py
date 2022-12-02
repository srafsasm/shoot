from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import pygame
from pygame.locals import *
import numpy as np
import time

from obj.chj.ogl import *
from obj.chj.ogl.objloader import CHJ_tiny_obj, OBJ
from obj.chj.ogl import light

WIDTH = 400
HEIGHT = 400
DISPLAY = (WIDTH * 2, HEIGHT)

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
            object.pos[i] += - np.sign(object.pos[i]) * (abs(object.pos[i]) + object.size - bound)
            object.velocity[i] *= -1

# FPS display
class FPS:
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Comic Sans MS', 20)
        
    def render(self):
        self.text = self.font.render(str(round(self.clock.get_fps(), 2)), False, (255, 255, 255, 255)).convert_alpha()
        self.data = pygame.image.tostring(self.text, "RGBA", True)


# ((mass, hp), (bSize, bMass, bLife, bDamage, bDelay, bSpeed), (bAngles))
pieceStat = {"pawn":   ((1, 20), (2, 0.1, 40, 1, 10, 2), (0,)),
             "knight": ((1, 20), (1, 0.1, 30, 1, 25, 3), (-10, 0, 10)),
             "bishop": ((1, 20), (1, 0.1, 30, 1, 25, 3), (-135, -45, 45, 135)),
             "rook":   ((1, 20), (1, 0.1, 30, 1, 25, 3), (-90, 0, 90, 180)),
             "queen":  ((1, 20), (1, 0.1, 30, 2, 25, 3), (-135, -90, -45, 0, 45, 90, 135, 180)),
             "king":   ((1, 20), (2, 0.1, 30, 1, 25, 2), (-135, -90, -45, 0, 45, 90, 135, 180))}

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
        self.obj = OBJ('vox/', type + '.obj', swapyz=True)
        self.obj.create_bbox()
        self.obj.create_gl_list()
    
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
            pos[2] = 0.05
            # shoot bullets into bAngles
            for angle in self.bAngles:
                self.bullets.append(Bullet(pos, self.bSize, self.bMass, self.bLife, self.bSpeed, angle + self.angle))
        # update bullet delay timer
        if self.timer:
            self.timer += 1
            if self.timer == self.bDelay:
                self.timer = 0
    
    # draw bullets and player
    def draw(self):
        # draw bullets
        for bullet in self.bullets:
            bullet.draw()
        # draw player
        glPushMatrix()
        glTranslatef(*self.pos)
        glRotatef(self.angle, 0, 0, 1)
        # cylinder = gluNewQuadric()
        # gluCylinder(cylinder, self.size, self.size, 0.1, 10, 1)
        glScalef(0.125, 0.125, 0.125)
        glCallList(self.obj.gl_list)
        glPopMatrix()

# bullet
class Bullet:

    # initialization
    def __init__(self, pos, size, mass, life, speed, angle):
        self.pos = np.copy(pos)
        self.size = 0.01 * size
        self.mass = mass
        self.life = life
        self.velocity = 0.01 * speed * np.array([np.cos(np.deg2rad(angle)), np.sin(np.deg2rad(angle))])
    
    # update life and position
    def update(self):
        self.life -= 1
        self.pos[0:2] = np.add(self.pos[0:2], self.velocity)
    
    # draw a bullet
    def draw(self):
        glPushMatrix()
        glTranslatef(*self.pos)
        sphere = gluNewQuadric()
        gluSphere(sphere, self.size, 10, 10)
        glPopMatrix()

# update bullets of a regarding b
def updateBullets(a, b, particle_system):
    for bullet in a.bullets:
        bullet.update()
        if bullet.life == 0:
            a.bullets.remove(bullet)
            del bullet
        elif isColliding(bullet, b):
            handleCollision(bullet, b)
            particle_system.add(bullet.pos)
            b.hp -= a.bDamage
            if b.hp <= 0:
                b.hp = 0
            a.bullets.remove(bullet)
            del bullet

# particles
class Particles:

    # initialization
    def __init__(self, pos):
        self.initialpos = np.copy(pos)
        self.displacement = np.zeros((10, 3))
        self.velocity = (np.random.random_sample((10, 3)) - 0.5) / 500
        self.color = np.tile(np.array([np.random.random_sample(10)]).T, (1, 3))
        self.life = np.random.randint(40, 50, 10)
    
    # update life and position
    def update(self):
        for i in range(10):
            if self.life[i]:
                self.life[i] -= 1
        self.displacement = np.add(self.displacement, self.velocity)

    # draw particles
    def draw(self):
        size = 0.008
        glPushMatrix()
        # translation to initial position
        glTranslatef(*self.initialpos)
        # make particles face the camera
        arr0 = np.array(glGetFloatv(GL_MODELVIEW_MATRIX))
        arr0[3, 0:3] = np.zeros(3)
        glMultMatrixf(arr0.T)
        glBegin(GL_QUADS)
        # draw particles
        for i in range(10):
            if (self.life[i]):
                glColor3f(*self.color[i])
                glVertex3f(*(np.add(self.displacement[i], (size, size, 0))))
                glVertex3f(*(np.add(self.displacement[i], (size, -size, 0))))
                glVertex3f(*(np.add(self.displacement[i], (-size, -size, 0))))
                glVertex3f(*(np.add(self.displacement[i], (-size, size, 0))))
        glEnd()
        glPopMatrix()

# particle system
class ParticleSystem:

    # initialization
    def __init__(self):
        self.particleList = []
        
    # add particles to system
    def add(self, pos):
        for i in range(1):
            self.particleList.append(Particles(pos))

    # update particles in a system
    def update(self):
        for particles in self.particleList:
            particles.update()
            if not np.any(particles.life):
                self.particleList.remove(particles)
                del particles
    
    # draw particles in a system
    def draw(self):
        for particles in self.particleList:
            particles.draw()

def drawBoard():
    glPushMatrix()
    squareSize = 0.2
    glBegin(GL_QUADS)
    glColor3f(1.0, 1.0, 1.0)
    x = -4
    y = -4
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
    glColor3f(0.2, 0.2, 0.2)
    x = -3
    y = -4
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
    
    def draw(self):
        glPushMatrix()
        glRotatef(90, 1, 0, 0)
        glCallList(self.list)
        glPopMatrix()


def drawHPbar(player1, player2):
    p1 = player1.hp / pieceStat[player1.type][0][1]
    p2 = player2.hp / pieceStat[player2.type][0][1]

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


class Game:
    def __init__(self):
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

    # draw objects
    def drawobjects(self):
        # draw player1
        glColor3f(0.2, 0.2, 0.2)
        self.player1.draw()
        # draw player2
        glColor3f(0.9, 0.9, 0.9)
        self.player2.draw()
        # draw particle system
        self.particleSys.draw()

    # pygame-based interface
    def display(self):
        ############################
        # game initialization here #
        ############################
        pygame.init()
        pygame.display.set_mode(DISPLAY, DOUBLEBUF|OPENGL)

        fps = FPS()

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self.skybox = Skybox()

        self.light()

        run = True

        while run:

            ####################
            # chess phase here #
            ####################

            phase_shoot = True
            
            self.player1 = Player(pos=[-0.5, 0, 0], angle=0, type="pawn")
            self.player2 = Player(pos=[0.5, 0, 0], angle=180, type="queen")

            # shoot-phase
            while phase_shoot:
                glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
                glClearColor(0, 0, 0, 1)

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        run = False
                        phase_shoot = False
                    
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            run = False
                            phase_shoot = False

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
                        
                        elif event.key == pygame.K_p:
                            self.player2.rotateDir -= 2
                        elif event.key == pygame.K_RIGHTBRACKET:
                            self.player2.rotateDir += 2
                
                self.player1.update()
                self.player2.update()
                if isColliding(self.player1, self.player2):
                    handleCollision(self.player1, self.player2)
                handleBoundary(self.player1, 0.8)
                handleBoundary(self.player2, 0.8)
                self.player1.shoot()
                self.player2.shoot()
                updateBullets(self.player1, self.player2, self.particleSys)
                updateBullets(self.player2, self.player1, self.particleSys)
                self.particleSys.update()

                if (self.player1.hp == 0 or self.player2.hp == 0):
                    phase_shoot = False

                glViewport(0, 0, WIDTH, HEIGHT)
                glMatrixMode(GL_PROJECTION)
                glLoadIdentity()
                # projection matrix
                gluPerspective(60, WIDTH/HEIGHT, 0.1, 50)
                glMatrixMode(GL_MODELVIEW)
                glLoadIdentity()
                # player 1 view
                gluLookAt(self.player1.pos[0] - 0.5 * np.cos(np.deg2rad(self.player1.angle)), self.player1.pos[1] - 0.5 * np.sin(np.deg2rad(self.player1.angle)), 0.5,
                        self.player1.pos[0] + 0.5 * np.cos(np.deg2rad(self.player1.angle)), self.player1.pos[1] + 0.5 * np.sin(np.deg2rad(self.player1.angle)), 0,
                        0, 0, 1)
                self.drawobjects()
                drawBoard()
                self.skybox.draw()

                glViewport(WIDTH, 0, WIDTH, HEIGHT)
                glMatrixMode(GL_MODELVIEW)
                glLoadIdentity()
                # player 2 view
                gluLookAt(self.player2.pos[0] - 0.5 * np.cos(np.deg2rad(self.player2.angle)), self.player2.pos[1] - 0.5 * np.sin(np.deg2rad(self.player2.angle)), 0.5,
                        self.player2.pos[0] + 0.5 * np.cos(np.deg2rad(self.player2.angle)), self.player2.pos[1] + 0.5 * np.sin(np.deg2rad(self.player2.angle)), 0,
                        0, 0, 1)

                self.drawobjects()
                drawBoard()
                self.skybox.draw()

                drawHPbar(self.player1, self.player2)

                glWindowPos2d(20, 20)
                fps.render()
                glDrawPixels(fps.text.get_width(), fps.text.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, fps.data)

                pygame.display.flip()
                fps.clock.tick(60)

            if not run:
                break

            # reset camera
            while self.player1.bullets:
                bullet = self.player1.bullets.pop()
                del bullet
            while self.player2.bullets:
                bullet = self.player2.bullets.pop()
                del bullet

            dx1 = (-0.5 - self.player1.pos[0]) / 60
            dy1 = (0.0 - self.player1.pos[1]) / 60
            da1 = (0 - self.player1.angle) / 60

            dx2 = (0.5 - self.player2.pos[0]) / 60
            dy2 = (0.0 - self.player2.pos[1]) / 60
            da2 = (180 - self.player2.angle) / 60

            p1x = self.player1.pos[0]
            p1y = self.player1.pos[1]
            p1a = self.player1.angle
            p2x = self.player2.pos[0]
            p2y = self.player2.pos[1]
            p2a = self.player2.angle
            for i in range(60):
                p1x += dx1 
                p1y += dy1
                p1a += da1
                p2x += dx2
                p2y += dy2
                p2a += da2

                self.particleSys.update()

                glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
                glClearColor(0, 0, 0, 1)

                glMatrixMode(GL_PROJECTION)
                glLoadIdentity()
                # projection matrix
                gluPerspective(60, WIDTH/HEIGHT, 0.1, 50)

                glViewport(0, 0, WIDTH, HEIGHT)
                glMatrixMode(GL_MODELVIEW)
                glLoadIdentity()
                gluLookAt(p1x - 0.5 * np.cos(np.deg2rad(p1a)), p1y - 0.5 * np.sin(np.deg2rad(p1a)), 0.5,
                        p1x + 0.5 * np.cos(np.deg2rad(p1a)), p1y + 0.5 * np.sin(np.deg2rad(p1a)), 0,
                        0, 0, 1)
                self.drawobjects()
                drawBoard()
                self.skybox.draw()

                glViewport(WIDTH, 0, WIDTH, HEIGHT)
                glMatrixMode(GL_MODELVIEW)
                glLoadIdentity()
                gluLookAt(p2x - 0.5 * np.cos(np.deg2rad(p2a)), p2y - 0.5 * np.sin(np.deg2rad(p2a)), 0.5,
                        p2x + 0.5 * np.cos(np.deg2rad(p2a)), p2y + 0.5 * np.sin(np.deg2rad(p2a)), 0,
                        0, 0, 1)
                self.drawobjects()
                drawBoard()
                self.skybox.draw()

                drawHPbar(self.player1, self.player2)

                glWindowPos2d(20, 20)
                fps.render()
                glDrawPixels(fps.text.get_width(), fps.text.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, fps.data)

                pygame.display.flip()
                fps.clock.tick(60)

            del self.player1
            del self.player2

            for event in pygame.event.get():
                pass


game = Game()
game.display()
