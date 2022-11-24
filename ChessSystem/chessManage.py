import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np

import markingBoard
import chessRule

def main():
    pygame.init()
    display = (1680, 1050)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)


    # 셋팅
    gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)
    
    managedBoard = chessRule.chessBoard()
    markedBoard = markingBoard.MarkingBoard(2)
    
    # 현재 차례표시 변수 (1, -1)
    currentPlayer = -1
    # 첫 선택 위치
    currentPos = [0,0] # [0,0] ~ [7,7]
    # game 종료 처리 변수
    isGameOver = False
    
    while not isGameOver:
        # 이벤트 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            elif event.type == KEYDOWN:
                # player 1 이동처리
                if currentPlayer == -1:
                    if event.key == 97: # a
                        if currentPos[0] > 0:
                            currentPos[0] = currentPos[0] - 1
                    elif event.key == 119: # w
                        if currentPos[1] < 7:
                            currentPos[1] = currentPos[1] + 1
                    elif event.key == 100: # d
                        if currentPos[0] < 7:
                            currentPos[0] = currentPos[0] + 1
                    elif event.key == 115: # s
                        if currentPos[1] > 0:
                            currentPos[1] = currentPos[1] - 1
                
                # player -1 이동처리
                elif currentPlayer == 1:
                    if event.key == 1073741904: # left
                        if currentPos[0] > 0:
                            currentPos[0] = currentPos[0] - 1
                    elif event.key == 1073741906: # up
                        if currentPos[1] < 7:
                            currentPos[1] = currentPos[1] + 1
                    elif event.key == 1073741903: # right
                        if currentPos[0] < 7:
                            currentPos[0] = currentPos[0] + 1
                    elif event.key == 1073741905: # down
                        if currentPos[1] > 0:
                            currentPos[1] = currentPos[1] - 1
                
                
                # 칸 선택시 처리
                if event.key == 13: # Enter
                    # 아직 어느 piece도 선택되지 않은 경우
                    if managedBoard.selected == None:
                        # 현재 칸에 piece가 없거나 상대 piece인 경우
                        if managedBoard.retPiece(currentPos[0], currentPos[1]) == None or managedBoard.retPiece(currentPos[0], currentPos[1]).group * currentPlayer == -1:
                            print("can't select")
                        # 현재 칸에 자신의 piece가 있는 경우
                        elif managedBoard.retPiece(currentPos[0], currentPos[1]).group * currentPlayer == 1:
                            managedBoard.selectPiece(currentPos[0], currentPos[1])
                    
                    # 어떤 piece가 선택되어 있는 경우
                    else:
                        # 현재 칸이 이동, 혹은 적 piece를 잡을 수 있는 칸인 경우
                        if managedBoard.checkMovable(currentPos[0], currentPos[1]) or managedBoard.checkCatchable(currentPos[0], currentPos[1]):
                            isGameOver = managedBoard.movePieces(currentPos[0], currentPos[1])
                            currentPlayer = currentPlayer * -1
                        # select 해제
                        managedBoard.selectPiece(None, None)
        # 화면 클리어
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        
        # 화면 구성
        glPushMatrix()
        gluLookAt(-2,2,0, 0,0, 0, 0,1,0)
        
        # 현재 움직일수 있는 칸, 잡을 수 있는 칸, 선택되어 있는 칸 정보 업데이트
        managedBoard.updateColorBoard(currentPos)
        # 현재 움직일수 있는 칸, 잡을 수 있는 칸, 선택되어 있는 칸 출력
        markedBoard.draw(managedBoard.colorBoard)
        # 현재 piece 위치에 draw 함수 수행
        managedBoard.drawPieces(2)
        
        glPopMatrix()
        
        # 디스플레이
        pygame.display.flip()
        pygame.time.wait(10)
        
    pygame.quit()
    quit()

if __name__ == "__main__":
    main()