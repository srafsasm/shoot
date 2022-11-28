from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np

class MarkingBoard:
    # side에 체스판 한쪽 변 길이 입력
    def __init__(self, side):
        self.recSide = side / 8
        
        self.vertexPoints = []
        for i in range(8):
            for j in range(8):
                self.vertexPoints.append([[self.recSide * j, self.recSide * i],
                                          [self.recSide * (j+1), self.recSide * i],
                                          [self.recSide * (j+1), self.recSide * (i+1)],
                                          [self.recSide * j, self.recSide * (i+1)]])            
    
    # 보드 color 정보 받아서 그리는 함수
    def draw(self, movable):
        glPushMatrix()
        glRotatef(90, 1, 0, 0)
        glTranslatef(0, 0.0855, 0)
        glTranslatef(-4 * self.recSide, 0, -4 * self.recSide)
        for i in range(8):
            for j in range(8):
                k = i * 8 + j
                
                # 빈칸, 지금은 표시한다고 선을 그리게 했지만 실제 보드 오브젝트를 그린 후에는 선을 지우는게 좋을 것 같아요
                if movable[7-i][j] == 0:
                    # glColor3f(1.0, 1.0, 1.0)
                    # glBegin(GL_LINES)
                    # for vertice in self.vertexPoints[k]:
                    #     glVertex3f(vertice[1], 0.0, vertice[0])
                    # glEnd()
                    pass
                # 이동 가능한 칸
                elif movable[7-i][j] == 1:
                    glColor3f(0.0, 0.0, 1.0)
                    glBegin(GL_QUADS)
                    for vertice in self.vertexPoints[k]:
                        glVertex3f(vertice[1], 0, vertice[0])
                    glEnd()
                # 잡을 수 있는 칸
                elif movable[7-i][j] == 2:
                    glColor3f(1.0, 0.0, 0.0)
                    glBegin(GL_QUADS)
                    for vertice in self.vertexPoints[k]:
                        glVertex3f(vertice[1], 0, vertice[0])
                    glEnd()
                # 현재 고르고 있는 칸
                elif movable[7-i][j] == 3:
                    glColor3f(0.0, 1.0, 0.0)
                    glBegin(GL_QUADS)
                    for vertice in self.vertexPoints[k]:
                        glVertex3f(vertice[1], 0, vertice[0])
                    glEnd()
                # 선택된 말이 있는 칸
                elif movable[7-i][j] == 4:
                    glColor3f(0.8, 0.8, 0.0)
                    glBegin(GL_QUADS)
                    for vertice in self.vertexPoints[k]:
                        glVertex3f(vertice[1], 0, vertice[0])
                    glEnd()
        glPopMatrix()
