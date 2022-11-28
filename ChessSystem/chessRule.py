from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from Chess.Board.board import *
from obj.chj.ogl import *
from obj.chj.ogl.objloader import CHJ_tiny_obj, OBJ
from obj.chj.ogl import light

PIECESIZE = 0.13

class chessBoard:
    def __init__(self):        
        self.board = [[rooks("BlackRook1",0,7,1),knights("BlackKnight1",1,7,1),bishops("BlackBishop1",2,7,1),queen("BlackQueen1",3,7,1),king("BlackKing1", 4,7,1),bishops("BlackBishop2",5,7,1),knights("BlackKnight2",6,7,1),rooks("BlackRook2",7,7,1)],
                      [pawns("BlackPawn1",0,6,1),pawns("BlackPawn2",1,6,1),pawns("BlackPawn3",2,6,1),pawns("BlackPawn4",3,6,1),pawns("BlackPawn5",4,6,1),pawns("BlackPawn6",5,6,1),pawns("BlackPawn7",6,6,1),pawns("BlackPawn8",7,6,1)],
                      [None,None,None,None,None,None,None,None],
                      [None,None,None,None,None,None,None,None],
                      [None,None,None,None,None,None,None,None],
                      [None,None,None,None,None,None,None,None],
                      [pawns("WhitePawn1",0,1,-1),pawns("WhitePawn2",1,1,-1),pawns("WhitePawn3",2,1,-1),pawns("WhitePawn4",3,1,-1),pawns("WhitePawn5",4,1,-1),pawns("WhitePawn6",5,1,-1),pawns("WhitePawn7",6,1,-1),pawns("WhitePawn8",7,1,-1)],
                      [rooks("WhiteRook1",0,0,-1),knights("WhiteKnight1",1,0,-1),bishops("WhiteBishop1",2,0,-1),queen("WhiteQueen1",3,0,-1),king("WhiteKing1", 4,0,-1),bishops("WhiteBishop2",5,0,-1),knights("WhiteKnight2",6,0,-1),rooks("WhiteRook2",7,0,-1)]]
        
        self.colorBoard = [[0]*8 for i in range(8)]
        self.currentMovable = []
        self.currentCatchable = []
        self.selected = None

        self.xstart = 0
        self.ystart = 0
        
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
            for piece in [block for rows in self.board for block in rows]: 
                if piece is None:
                    continue
                if piece.holding: 
                    piece.holding = False
        else:
            self.retPiece(x, y).getMovablePlace(self.board)
            self.currentMovable = self.retPiece(x, y).getMovable()
            self.currentCatchable = self.retPiece(x, y).getCatchable()
            self.selected = [x, y]
            self.xstart = self.movePiecesAmount(self.retPiece(x, y), y+1)
            self.ystart = self.movePiecesAmount(self.retPiece(x, y), x+1)
            self.retPiece(x,y).holding = True
            # print(self.currentMovable)
            # print(self.selected)
    
    def movePiecesAmount(self, piece, block_index):
        if block_index == 1: return piece.box1
        elif block_index == 2: return piece.box2
        elif block_index == 3: return piece.box3
        elif block_index == 4: return piece.box4
        elif block_index == 5: return piece.box5
        elif block_index == 6: return piece.box6
        elif block_index == 7: return piece.box7
        elif block_index == 8: return piece.box8
    
    def is_attacking(self, x2, y2):
        if self.selected != None:
            x1 = self.selected[0]
            y1 = self.selected[1]
            if [x2,y2] in self.retPiece(x1,y1).catchable:
                return (True, self.retPiece(x1, y1), self.retPiece(x2, y2), (x1, y1), (x2, y2))
            else:
                return (False, None, None, None, None)

    def remove_lost(self, x1, y1, x2, y2):
        # os.system("pause")
        result = False
        if self.retPiece(x2, y2).type[5:-1] == "King":
            result = True
        self.board[7-y2][x2] = self.board[7-y1][x1] # garbage 처리 필요할 듯 (아닐지도)
        self.board[7-y1][x1] = None
        self.board[7-y2][x2].move(x2, y2)
        self.retPiece(x2, y2).moving = True
        self.retPiece(x2, y2).moving_x_to = self.movePiecesAmount(self.retPiece(x2, y2), y2+1)
        self.retPiece(x2, y2).moving_z_to = self.movePiecesAmount(self.retPiece(x2, y2), x2+1)        
        return result

    def movePieces(self, x2, y2):
        result = False
        if self.selected != None:
            if self.retPiece(x2, y2) != None and self.retPiece(x2, y2).type[5:-1] == "King":
                result = True
            x1 = self.selected[0]
            y1 = self.selected[1]

            self.board[7-y2][x2] = self.board[7-y1][x1] # garbage 처리 필요할 듯 (아닐지도)
            self.board[7-y1][x1] = None
            self.board[7-y2][x2].move(x2, y2)
            
            self.retPiece(x2, y2).moving = True
            self.retPiece(x2, y2).moving_x_to = self.movePiecesAmount(self.retPiece(x2, y2), y2+1)
            self.retPiece(x2, y2).moving_z_to = self.movePiecesAmount(self.retPiece(x2, y2), x2+1)
        else:
            print("Not selected")
            
        return result
        
    # board 위의 말들을 그리는 함수. argument로 board의 side 길이를 받음
    def drawPieces(self, side):
        pass

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
        self.name = type
        self.position = [x, y]
        self.group = group
        self.movable = []
        self.catchable = []


        self.loaded = False

        self.height = 0.084
        self.holdheight = self.height+0.15

        self.place = [0, 0, 0]

        self.box1 = -0.595
        self.box2 = -0.425
        self.box3 = -0.250
        self.box4 = -0.085
        self.box8 = 0.595
        self.box7 = 0.425
        self.box6 = 0.250
        self.box5 = 0.085

        self.moving = False
        self.moving_x_to = 0
        self.moving_y_to = 0
        self.moving_z_to = 0
        self.movingCnt = 1
        self.movingSpeed = 40

        self.holding = False
        
        if self.name ==   'WhitePawn1':   self.place = [self.box2, self.height, self.box1]
        elif self.name == 'WhitePawn2':   self.place = [self.box2, self.height, self.box2]
        elif self.name == 'WhitePawn3':   self.place = [self.box2, self.height, self.box3]
        elif self.name == 'WhitePawn4':   self.place = [self.box2, self.height, self.box4]
        elif self.name == 'WhitePawn5':   self.place = [self.box2, self.height, self.box5]
        elif self.name == 'WhitePawn6':   self.place = [self.box2, self.height, self.box6]
        elif self.name == 'WhitePawn7':   self.place = [self.box2, self.height, self.box7]
        elif self.name == 'WhitePawn8':   self.place = [self.box2, self.height, self.box8]        
        elif self.name == 'WhiteRook1':   self.place = [self.box1, self.height, self.box1]
        elif self.name == 'WhiteRook2':   self.place = [self.box1, self.height, self.box8]
        elif self.name == 'WhiteKnight1': self.place = [self.box1, self.height, self.box2]
        elif self.name == 'WhiteKnight2': self.place = [self.box1, self.height, self.box7]
        elif self.name == 'WhiteBishop1': self.place = [self.box1, self.height, self.box3]
        elif self.name == 'WhiteBishop2': self.place = [self.box1, self.height, self.box6]
        elif self.name == 'WhiteQueen1':  self.place = [self.box1, self.height, self.box4]
        elif self.name == 'WhiteKing1':   self.place = [self.box1, self.height, self.box5]
        
        elif self.name == 'BlackPawn1':   self.place = [self.box7, self.height, self.box1]
        elif self.name == 'BlackPawn2':   self.place = [self.box7, self.height, self.box2]
        elif self.name == 'BlackPawn3':   self.place = [self.box7, self.height, self.box3]
        elif self.name == 'BlackPawn4':   self.place = [self.box7, self.height, self.box4]
        elif self.name == 'BlackPawn5':   self.place = [self.box7, self.height, self.box5]
        elif self.name == 'BlackPawn6':   self.place = [self.box7, self.height, self.box6]
        elif self.name == 'BlackPawn7':   self.place = [self.box7, self.height, self.box7]
        elif self.name == 'BlackPawn8':   self.place = [self.box7, self.height, self.box8]        
        elif self.name == 'BlackRook1':   self.place = [self.box8, self.height, self.box1]
        elif self.name == 'BlackRook2':   self.place = [self.box8, self.height, self.box8]
        elif self.name == 'BlackKnight1': self.place = [self.box8, self.height, self.box2]
        elif self.name == 'BlackKnight2': self.place = [self.box8, self.height, self.box7]
        elif self.name == 'BlackBishop1': self.place = [self.box8, self.height, self.box3]
        elif self.name == 'BlackBishop2': self.place = [self.box8, self.height, self.box6]
        elif self.name == 'BlackQueen1':  self.place = [self.box8, self.height, self.box4]
        elif self.name == 'BlackKing1':   self.place = [self.box8, self.height, self.box5]
        
        
    # 해당 chessPiece를 그리는 함수         <================ piece object 여기서 구현하시면 돼요
    def show(self):
        if not self.loaded:
            self.obj = OBJ('Chess/Pieces/', self.type[:-1] + '.obj', swapyz=True)
            self.obj.create_bbox()
            self.obj.create_gl_list()
            self.loaded = True
        
        glPushMatrix()
        glRotatef(90, 1, 0, 0)
        glTranslatef(self.place[0], self.place[1], self.place[2])
        glRotatef(-90, 1, 0, 0)
        if self.name[0:5] == 'Black':
            glRotatef(180, 0, 0, 1)

        glScale(PIECESIZE, PIECESIZE, PIECESIZE)
        glCallList(self.obj.gl_list)
        glPopMatrix()
    
    def holdPiece(self):
        glPushMatrix()
        glRotatef(90, 1, 0, 0)
        glTranslatef(self.place[0], self.place[1]+0.15, self.place[2])
        glRotatef(-90, 1, 0, 0)
        if self.name[0:5] == 'Black':
            glRotatef(180, 0, 0, 1)

        glScale(PIECESIZE, PIECESIZE, PIECESIZE)
        glCallList(self.obj.gl_list)
        glPopMatrix()
    
    def movePiece(self, x, y, z):

        glPushMatrix()
        glRotatef(90, 1, 0, 0)
        glTranslatef(self.place[0]+x*self.movingCnt, self.holdheight+y*self.movingCnt, self.place[2]+z*self.movingCnt)

        glRotatef(-90, 1, 0, 0)

        glScale(PIECESIZE, PIECESIZE, PIECESIZE)
        glCallList(self.obj.gl_list)
        glPopMatrix()

        if self.movingCnt >= self.movingSpeed:
            self.moving = False
            self.place[0] += self.movingSpeed * x
            self.place[1] = self.height
            self.place[2] += self.movingSpeed * z
            self.movingCnt = 1
        else:
            self.movingCnt += 1
        
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
        
    
if __name__ == "__main__":
    chess = chess()
    chess.test()
