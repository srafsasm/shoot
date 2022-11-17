class chessBoard:
    def __init__(self):
        self.board = [[1,2,3,4,5,3,2,1],
                      [6,6,6,6,6,6,6,6],
                      [0,0,0,0,0,0,0,0],
                      [0,0,0,0,0,0,0,0],
                      [0,0,0,0,0,0,0,0],
                      [0,0,0,0,0,0,0,0],
                      [-6,-6,-6,-6,-6,-6,-6,-6],
                      [-1,-2,-3,-4,-5,-3,-2,-1]]
        
        self.colorBoard = [[0]*8 for i in range(8)]
        
    def updateColorBoard(self, movable, catchable):
        if movable == None and catchable == None:
            self.colorBoard = [[0]*8 for i in range(8)]
            return
        
        for i in movable:
            self.colorBoard[7-i[1]][i[0]] = 1
        for i in catchable:
            self.colorBoard[7-i[1]][i[0]] = 2
        
        
    def printBoard(self):
        for i in range(8):
            print(self.board[i])
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
        
    def move(self, x, y):
        if [x,y] in self.movable:
            self.position = [x, y]
            return 1
        elif [x,y] in self.catchable:
            self.position = [x, y]
            return 2
        else:
            return 0
    
    def checkMovable(self, x, y, board):
        if x >= 0 and x <= 7 and y >= 0 and y <= 7:
            y = 7 - y
            if board[y][x] * self.group > 0:
                print("can't move: ", board[y][x])
                return -1 # can't move (same group)
            elif board[y][x] * self.group < 0:
                print("catchable: ", board[y][x])
                return 1 # there is other group's pieces
            else:
                print("can move, ", x, " ", 7-y, " ", board[y][x])
                return 0 # can move
        else:
            print("can't move")
            return -1 # can't move

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
                        
    def getMovable(self):
        return self.movable
    
    def getCatchable(self):
        return self.catchable
    
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
        
    def getMovable(self):
        return self.movable
    
    def getCatchable(self):
        return self.catchable

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
        
    def getMovable(self):
        return self.movable
    
    def getCatchable(self):
        return self.catchable

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
        
    def getMovable(self):
        return self.movable
    
    def getCatchable(self):
        return self.catchable

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
        
    def getMovable(self):
        return self.movable
    
    def getCatchable(self):
        return self.catchable

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
        tempList = [[-1,1], [1,1], [0,1]]
        if not self.moved:
            tempList.append([0,2])
        for i in tempList:
            currentX = self.position[0] + i[0]
            currentY = self.position[1] + i[1]
            temp = super().checkMovable(currentX, currentY,  board)
            if temp == 0 and tempNum > 2:
                self.movable.append([currentX, currentY])
            elif temp == 1 and tempNum <= 2:
                self.catchable.append([currentX, currentY])
            tempNum = tempNum + 1
        
    def getMovable(self):
        return self.movable
    
    def getCatchable(self):
        return self.catchable
                        
class chess:
    def __init__(self):
        self.chessBoard = chessBoard()
        self.whiteKing = pawns(4, 2, 3, -1)
    
    def test(self):
        self.chessBoard.printBoard()
        self.chessBoard.printColorBoard()
        self.whiteKing.getMovablePlace(self.chessBoard.board)
        print(self.whiteKing.getMovable())
        print(self.whiteKing.getCatchable())
        self.chessBoard.updateColorBoard(self.whiteKing.getMovable(), self.whiteKing.getCatchable())
        self.chessBoard.printColorBoard()
        self.chessBoard.updateColorBoard(None, None)
    
if __name__ == "__main__":
    chess = chess()
    chess.test()
