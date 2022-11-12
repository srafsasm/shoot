from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np


class Character:
    def __init__(self, initialPos, color):
        self.transformationMat = np.array([[1,0,0,initialPos[0]],[0,1,0,initialPos[1]],[0,0,1,initialPos[2]],[0,0,0,1]])
        self.color = color
        self.posX = 0
    def create(self, wtcMat):
        glLoadIdentity()
        if self.color == "blue":
            glColor3f(0.0, 0.0, 1.0)
        elif self.color == "red":
            glColor3f(1.0, 0.0, 0.0)
        print(self.color)
        print(self.transformationMat)
        glMultMatrixf((wtcMat @ self.transformationMat).T)
        glutSolidTeapot(0.5)
    def move(self, dir):
        if (self.posX == 200 and dir == 1) or (self.posX == -200 and dir == -1):
            return
        self.posX = self.posX + dir * 2 # 100배 해서 정수로 계산
        temp = np.array([[1,0,0,dir*0.02],[0,1,0,0],[0,0,1,0],[0,0,0,1]])
        self.transformationMat = temp @ self.transformationMat
        

class Viewer:
    def __init__(self):
        # 환경변수 설정
        self.fov = np.pi/4
        self.displayScale = 1
        self.cameraPos = np.array([[0,0.7,1,1],[0,0.5,0,1],[0,1,0,1]]) #cop, at, up
        
        # player 생성
        self.player1 = Character(np.array([0,0,1]), "blue")
        self.player2 = Character(np.array([0,0,-1]), "red")
        
        # 초기 카메라 위치 설정
        self.nearDist = 0
        self.worldToCameraMat = self.worldToCamera(self.cameraPos, self.player1.transformationMat, self.fov, self.displayScale)
        
        # 환경 scale mat
        self.envScaleMat = np.array([[4,0,0,0],[0,0.2,0,0],[0,0,0.2,0],[0,0,0,1]])
        self.envScaleMat2 = np.array([[6,0,0,0],[0,0.2,0,0],[0,0,6,0],[0,0,0,1]])
        

    # world coordinate to camera coordinate
    def worldToCamera(self, cameraPos, playerPosMat, fov, scale): # 플레이어 기준 카메라 위치(cop, at, up), 플레이어 위치(4*4 matrix), fov, 화면 스케일(?)
        # get cop, at, up
        cop = playerPosMat @ cameraPos[0]
        at = playerPosMat @ cameraPos[1]
        
        cop = cop[:3]
        at = at[:3]
        up = (cameraPos[2])[:3]
        
        # get world to camera matrix
        zVec = cop - at
        zVec = zVec / np.linalg.norm(zVec)
        xVec = np.cross(up, zVec)
        xVec = xVec / np.linalg.norm(xVec)
        yVec = np.cross(zVec, xVec)
        
        # consider proper frustum position
        halfAngle = fov / 2
        self.nearDist = scale / (np.tan(halfAngle)) # near dist 값 반영
        properCop = cop + self.nearDist * np.array([zVec[0], zVec[1], zVec[2]])
        
        # get matrix
        tMat = np.array([[xVec[0],yVec[0],zVec[0],properCop[0]], [xVec[1],yVec[1],zVec[1],properCop[1]], [xVec[2],yVec[2],zVec[2],properCop[2]], [0,0,0,1]])
        tMat = np.linalg.inv(tMat)
        
        return tMat

    def display(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(0, 0, 0, 1)

        # TPS 시점
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        self.worldToCameraMat = self.worldToCamera(self.cameraPos, self.player1.transformationMat, self.fov, self.displayScale)
        glFrustum(-self.displayScale, self.displayScale, -self.displayScale, self.displayScale, self.nearDist, 50)

        # player 배치
        glMatrixMode(GL_MODELVIEW)
        self.player1.create(self.worldToCameraMat)
        self.player2.create(self.worldToCameraMat)
        
        # 간이적인 환경
        glColor3f(1.0, 1.0, 1.0)
        
        glLoadIdentity()
        glMultMatrixf((self.worldToCameraMat @ np.array([[1,0,0,0],[0,1,0,-0.5],[0,0,1,1],[0,0,0,1]]) @ self.envScaleMat).T)
        glutSolidCube(1)
        
        glLoadIdentity()
        glMultMatrixf((self.worldToCameraMat @ np.array([[1,0,0,0],[0,1,0,-0.5],[0,0,1,-1],[0,0,0,1]]) @ self.envScaleMat).T)
        glutSolidCube(1)
        
        glColor3f(0.5, 0.5, 0.2)
        glLoadIdentity()
        glMultMatrixf((self.worldToCameraMat @ np.array([[1,0,0,0],[0,1,0,-1.5],[0,0,1,0],[0,0,0,1]]) @ self.envScaleMat2).T)
        glutSolidCube(1)

        glutSwapBuffers()

    def keyboard(self, key, x, y):
        print(f"keyboard event: key={key}, x={x}, y={y}")
        if glutGetModifiers() & GLUT_ACTIVE_SHIFT:
            print("shift pressed")
        if glutGetModifiers() & GLUT_ACTIVE_ALT:
            print("alt pressed")
        if glutGetModifiers() & GLUT_ACTIVE_CTRL:
            print("ctrl pressed")
            
        # moving player 1
        if key == b'a':
            self.player1.move(-1)
            print("1l")
        elif key == b'd':
            self.player1.move(1)
            print("1r")

        glutPostRedisplay()

    def special(self, key, x, y):
        print(f"special key event: key={key}, x={x}, y={y}")

        # moving player 2
        if key == 100:
            self.player2.move(1)
            print("2l")
        elif key == 102:
            self.player2.move(-1)
            print("2r")

        glutPostRedisplay()

    def mouse(self, button, state, x, y):
        # button macros: GLUT_LEFT_BUTTON, GLUT_MIDDLE_BUTTON, GLUT_RIGHT_BUTTON
        print(f"mouse press event: button={button}, state={state}, x={x}, y={y}")

        glutPostRedisplay()

    def motion(self, x, y):
        print(f"mouse move event: x={x}, y={y}")

        glutPostRedisplay()

    def reshape(self, w, h):
        self.currentWidth = w
        self.currentHeight = h
        glViewport(0, 0, w, h)

        glutPostRedisplay()
        
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

    def run(self):
        glutInit()
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
        glutInitWindowSize(800, 800)
        glutInitWindowPosition(0, 0)
        glutCreateWindow(b"CS471 Computer Graphics #2")

        glutDisplayFunc(self.display)
        glutKeyboardFunc(self.keyboard)
        glutSpecialFunc(self.special)
        glutMouseFunc(self.mouse)
        glutMotionFunc(self.motion)
        glutReshapeFunc(self.reshape)

        self.light()
        glutMainLoop()


if __name__ == "__main__":
    viewer = Viewer()
    viewer.run()
