from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

class chessBoard:
    def __init__(self):        
        self.board = [[rooks("rook",0,7,1),knights("knights",1,7,1),bishops("bishops",2,7,1),king("king", 3,7,1),queen("queen",4,7,1),bishops("bishops",5,7,1),knights("knights",6,7,1),rooks("rook",7,7,1)],
                      [pawns("pawn",0,6,1),pawns("pawn",1,6,1),pawns("pawn",2,6,1),pawns("pawn",3,6,1),pawns("pawn",4,6,1),pawns("pawn",5,6,1),pawns("pawn",6,6,1),pawns("pawn",7,6,1)],
                      [None,None,None,None,None,None,None,None],
                      [None,None,None,None,None,None,None,None],
                      [None,None,None,None,None,None,None,None],
                      [None,None,None,None,None,None,None,None],
                      [pawns("pawn",0,1,-1),pawns("pawn",1,1,-1),pawns("pawn",2,1,-1),pawns("pawn",3,1,-1),pawns("pawn",4,1,-1),pawns("pawn",5,1,-1),pawns("pawn",6,1,-1),pawns("pawn",7,1,-1)],
                      [rooks("rook",0,0,-1),knights("knights",1,0,-1),bishops("bishops",2,0,-1),king("king", 3,0,-1),queen("queen",4,0,-1),bishops("bishops",5,0,-1),knights("knights",6,0,-1),rooks("rook",7,0,-1)]]
        
        self.colorBoard = [[0]*8 for i in range(8)]
        self.currentMovable = []
        self.currentCatchable = []
        self.selected = None
        
    def updateColorBoard(self, pos):
        self.colorBoard = [[0]*8 for i in range(8)]
        
        for i in self.currentMovable:
            self.colorBoard[7-i[1]][i[0]] = 1
        for i in self.currentCatchable:
            self.colorBoard[7-i[1]][i[0]] = 2
        if pos != None:
            self.colorBoard[7-pos[1]][pos[0]] = 3
        if self.selected != None:
            self.colorBoard[7-self.selected[1]][self.selected[0]] = 4
            
    def selectPiece(self, x, y):
        if x == None and y == None:
            self.currentCatchable = []
            self.currentMovable = []
            self.selected = None
        else:
            self.retPiece(x, y).getMovablePlace(self.board)
            self.currentMovable = self.retPiece(x, y).getMovable()
            self.currentCatchable = self.retPiece(x, y).getCatchable()
            self.selected = [x, y]
            print(self.currentMovable)
            print(self.selected)
        
    def movePieces(self, x2, y2):
        result = False
        if self.selected != None:
            if self.retPiece(x2, y2) != None and self.retPiece(x2, y2).type == "king":
                result = True
            x1 = self.selected[0]
            y1 = self.selected[1]
            self.board[7-y2][x2] = self.board[7-y1][x1] # garbage 처리 필요할 듯 (아닐지도)
            self.board[7-y1][x1] = None
            self.board[7-y2][x2].move(x2, y2)
        else:
            print("Not selected")
            
        return result
        
    # board 위의 말들을 그리는 함수. argument로 board의 side 길이를 받음
    def drawPieces(self, side):
        recSide = side / 8
        for i in range(8):
            for j in range(8):
                if self.retPiece(j, i) != None:
                    self.retPiece(j, i).draw((0.5+j) * recSide, (0.5+i) * recSide, 0.05, recSide)
    
    # x축, y축 기준으로 좌표 입력했을때 piece 반환해주는 함수
    def retPiece(self, x, y):
        return self.board[7-y][x]
    
    def checkMovable(self, x, y):
        if [x, y] in self.currentMovable:
            return True
        else:
            return False
    
    def checkCatchable(self, x, y):
        if [x, y] in self.currentCatchable:
            return True
        else:
            return False
    
    def printBoard(self):
        for i in range(8):
            for j in range(8):
                if self.board[i][j] == None:
                    print("None", end= " ")
                else:
                    print(self.board[i][j].retType(), end=" ")
            print("\n")
        print("")
        
    def printColorBoard(self):
        for i in range(8):
            print(self.colorBoard[i])
        print("")
    
    
class chessPieces:
    def __init__(self, type, x, y, group):
        self.type = type
        self.position = [x, y]
        self.group = group
        self.movable = []
        self.catchable = []
        
    # 해당 chessPiece를 그리는 함수         <================ piece object 여기서 구현하시면 돼요
    def draw(self, z, x, size, recSide):
        # 팀 별로 piece 색상 변경
        if self.group == 1:
            glColor3f(0.5, 0.5, 0.5)
        else:
            glColor3f(1.0, 1.0, 1.0)
            
        glPushMatrix()
        # chess piece object 여기서 그려주시면 되요
        glTranslatef(-4 * recSide, 0, -4 * recSide)
        glBegin(GL_QUADS)
        glVertex3f(x+size, 0.02, z+size)
        glVertex3f(x+size, 0.02, z-size)
        glVertex3f(x-size, 0.02, z-size)
        glVertex3f(x-size, 0.02, z+size)
        glEnd()
        glPopMatrix()
        
        glColor3f(1.0, 1.0, 1.0)
        
    def move(self, x, y):
        if [x,y] in self.movable:
            self.position = [x, y]
            return 1
        elif [x,y] in self.catchable:
            self.position = [x, y]
            return 2
        else:
            return 0
    
    # getMovablePlace에서 사용, 우리는 직접 사용할 일 없어요
    def checkMovable(self, x, y, board):
        if x >= 0 and x <= 7 and y >= 0 and y <= 7: 
            y = 7 - y # x, y 값 리스트 기준으로 변환
            if board[y][x] == None:
                return 0 # can move
            elif board[y][x].retGroup() * self.group > 0:
                return -1 # can't move (same group)
            elif board[y][x].retGroup() * self.group < 0:
                return 1 # there is other group's pieces
            else:
                return 0 # can move
        else:
            return -1 # can't move
    
    # 각 piece class 마다 다른 이동방식 구현
    def getMovablePlace(self, board):
        pass
        
    def retGroup(self):
        return self.group
    
    def retType(self):
        return self.type
    
    def getMovable(self):
        return self.movable
    
    def getCatchable(self):
        return self.catchable

class bishops(chessPieces):
    def __init__(self, type, x, y, group):
        super().__init__(type, x, y, group)
        
    def getMovablePlace(self, board):
        self.movable = []
        self.catchable = []
        for i in [[1,1], [-1,1], [1,-1], [-1,-1]]:
            currentX = self.position[0]
            currentY = self.position[1]
            temp = 0
            while temp == 0:
                currentX = currentX + i[0]
                currentY = currentY + i[1]
                temp = super().checkMovable(currentX, currentY,  board)
                if temp == 0:
                    self.movable.append([currentX, currentY])
                elif temp == 1:
                    self.catchable.append([currentX, currentY])
    
class rooks(chessPieces):
    def __init__(self, type, x, y, group):
        super().__init__(type, x, y, group)
        
    def getMovablePlace(self, board):
        self.movable = []
        self.catchable = []
        for i in [[1,0], [-1,0], [0,1], [0,-1]]:
            currentX = self.position[0]
            currentY = self.position[1]
            temp = 0
            while temp == 0:
                currentX = currentX + i[0]
                currentY = currentY + i[1]
                temp = super().checkMovable(currentX, currentY,  board)
                if temp == 0:
                    self.movable.append([currentX, currentY])
                elif temp == 1:
                    self.catchable.append([currentX, currentY])

class queen(chessPieces):
    def __init__(self, type, x, y, group):
        super().__init__(type, x, y, group)
        
    def getMovablePlace(self, board):
        self.movable = []
        self.catchable = []
        for i in [[1,0], [-1,0], [0,1], [0,-1], [1,1], [-1,1], [1,-1], [-1,-1]]:
            currentX = self.position[0]
            currentY = self.position[1]
            temp = 0
            while temp == 0:
                currentX = currentX + i[0]
                currentY = currentY + i[1]
                temp = super().checkMovable(currentX, currentY,  board)
                if temp == 0:
                    self.movable.append([currentX, currentY])
                elif temp == 1:
                    self.catchable.append([currentX, currentY])

class king(chessPieces):
    def __init__(self, type, x, y, group):
        super().__init__(type, x, y, group)
        
    def getMovablePlace(self, board):
        self.movable = []
        self.catchable = []
        for i in [[1,0], [-1,0], [0,1], [0,-1], [1,1], [-1,1], [1,-1], [-1,-1]]:
            currentX = self.position[0] + i[0]
            currentY = self.position[1] + i[1]
            temp = super().checkMovable(currentX, currentY,  board)
            if temp == 0:
                self.movable.append([currentX, currentY])
            elif temp == 1:
                self.catchable.append([currentX, currentY])

class knights(chessPieces):
    def __init__(self, type, x, y, group):
        super().__init__(type, x, y, group)
        
    def getMovablePlace(self, board):
        self.movable = []
        self.catchable = []
        for i in [[-1,2], [1,2], [2,1], [2,-1], [1,-2], [-1,-2], [-2,-1], [-2,1]]:
            currentX = self.position[0] + i[0]
            currentY = self.position[1] + i[1]
            temp = super().checkMovable(currentX, currentY,  board)
            if temp == 0:
                self.movable.append([currentX, currentY])
            elif temp == 1:
                self.catchable.append([currentX, currentY])

class pawns(chessPieces):
    def __init__(self, type, x, y, group):
        super().__init__(type, x, y, group)
        self.moved = False
        
    def move(self, x, y):
        if [x,y] in self.movable:
            self.position = [x, y]
            self.moved = True
            return 1
        elif [x,y] in self.catchable:
            self.position = [x, y]
            self.moved = True
            return 2
        else:
            return 0
        
    def getMovablePlace(self, board):
        self.movable = []
        self.catchable = []
        tempNum = 1
        
        tempList = [[-1,1*-1*self.group], [1,1*-1*self.group], [0,1*-1*self.group]]
        if not self.moved:
            tempList.append([0,2*-1*self.group])
            
        for i in tempList:
            currentX = self.position[0] + i[0]
            currentY = self.position[1] + i[1]
            temp = super().checkMovable(currentX, currentY,  board)
            if temp == 0 and tempNum > 2:
                self.movable.append([currentX, currentY])
            elif temp == 1 and tempNum <= 2:
                self.catchable.append([currentX, currentY])
            tempNum = tempNum + 1
                        
# test용, 무시하세요
class chess:
    def __init__(self):
        self.chessBoard = chessBoard()
        self.whiteKing = queen(4, 2, 3, -1)
    
    def test(self):
        self.chessBoard.printBoard()
        #self.chessBoard.printColorBoard()
        self.whiteKing.getMovablePlace(self.chessBoard.board) # 움직일 수 있는 칸 탐색
        print(self.whiteKing.getMovable())
        print(self.whiteKing.getCatchable())
        self.chessBoard.updateColorBoard(self.whiteKing.getMovable(), self.whiteKing.getCatchable(), [0,0]) # color board 업데이트
        self.chessBoard.printColorBoard()
        self.chessBoard.updateColorBoard(None) # color board 초기화
        self.chessBoard.movePieces(2,3,2,5)
        self.chessBoard.printBoard()
        
    
if __name__ == "__main__":
    chess = chess()
    chess.test()
