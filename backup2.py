import random
from turtle import *
from enum import Enum

TILE_HEIGHT = 9
TILE_WIDTH = 5
MAP_HEIGHT = TILE_HEIGHT*3
MAP_WIDTH = TILE_WIDTH*3
BLOCK = [
    [(0, 0)],
    
    # 直線
    [(0, 0), (1, 0)],
    [(0, 0), (1, 0), (2, 0)],

    # 橫線
    [(0, 0), (0, 1)],
    [(0, 0), (0, 1), (0, 2)],

    # L 彎
    [(0, 0), (0, 1), (1, 0)],
    [(0, 0), (1, 1), (1, 0)],
    [(0, 0), (1, 1), (1, 0)],
    [(0, 0), (1, 0), (-1, 1)],


    [(0, 0), (1, 0), (2, 0), (1, 1)],
    [(0, 0), (1, 0), (2, 0), (0, 1)],
    [(0, 0), (1, 0), (2, 0), (2, 1)],
]

class TileTable:
    def __init__(self, height = TILE_HEIGHT, width = TILE_WIDTH):
        self.table = [[0] * width for _ in range(height)]

    @property
    def height(self):
        return len(self.table)
    
    @property
    def width(self):
        return len(self.table[0])
    
    def __getitem__(self, index):
        return self.table[index]
    
    def __setitem__(self, index, value):
        self.table[index] = value

    def is_inside(self, nowY, nowX):
        return 0<=nowY and nowY<self.height and 0<=nowX and nowX<self.width
    
    def print(self):
        for row in self.table:
            for cell in row:
                print(f"{cell:2}", end=" ")
            print()

    def generate_map(self, nowY = 0, nowX = 0, id = 1):
        if nowY==self.height and nowX==0:
            return True

        if self.table[nowY][nowX]!=0:
            if self.generate_map(nowY+(nowX==self.width-1), (nowX+1)%self.width, id):
                return True
        else:
            random.shuffle(BLOCK)
            for b in BLOCK:
                isValid = True
                for (offsetY, offsetX) in b:
                    if (not self.is_inside(nowY+offsetY, nowX+offsetX)) or self.table[nowY+offsetY][nowX+offsetX]!=0:
                        isValid = False
                        break

                if (isValid):
                    for (offsetY, offsetX) in b:
                        self.table[nowY+offsetY][nowX+offsetX] = id
                    if self.generate_map(nowY+(nowX==self.width-1), (nowX+1)%self.width, id+1):
                        return True
                    for (offsetY, offsetX) in b:
                        self.table[nowY+offsetY][nowX+offsetX] = 0

        return False

# LEFT, UP, RIGHT, DOWN
DX = [-1, 0, 1, 0]
DY = [0, -1, 0, 1]
MAP_GAP = 16
TILE_GAP = 48

class Canva:
    def __init__(self, table: TileTable):
        tracer(0, delay=None)
        speed(0)
        hideturtle()
        self.table = table
        for idx in range(self.table.height):
            self.table[idx] = self.table[idx][-1:0:-1]+self.table[idx]
        self.table.print()

    # 給定網格 (y, x)，回傳該格的左上角座標
    def position(self, y, x):
        return (-(y-self.table.height*3/2)*MAP_GAP, (x-self.table.width*3/2)*MAP_GAP)
    
    # 給定網格 (y1, x1) 的左上角和 (y2, x2) 的左上角，畫出連線
    def draw_line(self, y1, x1, y2, x2):
        y1, x1 = self.position(y1, x1)
        y2, x2 = self.position(y2, x2)
        teleport(x1, y1)
        goto(x2, y2)

    # 給定網格的 (y, x)，畫出該格的邊界
    def draw_border(self, y, x, dir):
        match dir:
            case 0: # LEFT
                self.draw_line(y, x, y+1, x)
            case 1: # UP
                self.draw_line(y, x, y, x+1)
            case 2: # RIGHT
                self.draw_line(y, x+1, y+1, x+1)
            case 3: # DOWN
                self.draw_line(y+1, x, y+1, x+1)

    # 給定網格的左上角 (y1, x1) 跟右下角 (y2, x2)，在裡面畫出矩形
    def draw_inner_wall(self, y1, x1, y2, x2):
        y1, x1 = self.position(y1, x1)
        y2, x2 = self.position(y2, x2)
        penup()
        teleport(x1, y1)
        begin_fill()
        goto(x1, y2)
        goto(x2, y2)
        goto(x2, y1)
        goto(x1, y1)
        end_fill()
        pendown()

    # 畫灰色網格
    def draw_table(self):
        pencolor("#CCCCCC")
        pensize(1)
        for i in range(self.table.height*3):
            for j in range(self.table.width*3):
                for k in range(4):
                    self.draw_border(i, j, k)
        update()

    # 畫座標軸
    def draw_axis(self):
        pensize(3)
        pencolor("#FF0000")
        teleport(-1000, 0)
        goto(1000, 0)
        pencolor("#00FF00")
        teleport(0, -1000)
        goto(0, 1000)
        update()

    def draw_inner_border(self):
        pencolor("#0000FF")
        fillcolor("#0000FF")
        for i in range(0, self.table.height):
            for j in range(0, self.table.width):
                fillcolor("#0000FF")
                self.draw_inner_wall(i*3+0.7, j*3+0.7, i*3+2.3, j*3+2.3)
                for k in range(4):
                    
                    if not self.table.is_inside(i+DY[k], j+DX[k]):
                        k1 = (k+1)%4
                        k2 = (k-1)%4
                        c1 = self.table.is_inside(i+DY[k1], j+DX[k1]) and self.table[i][j]!=self.table[i+DY[k1]][j+DX[k1]]
                        c2 = self.table.is_inside(i+DY[k2], j+DX[k2]) and self.table[i][j]!=self.table[i+DY[k2]][j+DX[k2]]
                        if c1 or c2:
                            match k:
                                case 0: # LEFT
                                    self.draw_inner_wall(i*3+0.7, j*3+1.5, (i+DY[k])*3+2.3, (j+DX[k])*3+1.5)
                                case 1: # UP
                                    self.draw_inner_wall(i*3+1.5, j*3+0.7, (i+DY[k])*3+1.5, (j+DX[k])*3+2.3)
                                case 2: # RIGHT
                                    self.draw_inner_wall(i*3+0.7, j*3+1.5, (i+DY[k])*3+2.3, (j+DX[k])*3+1.5)
                                case 3: # DOWN
                                    self.draw_inner_wall(i*3+1.5, j*3+0.7, (i+DY[k])*3+1.5, (j+DX[k])*3+2.3)
                    elif self.table[i][j]==self.table[i+DY[k]][j+DX[k]]:
                        match k:
                            case 0: # LEFT
                                self.draw_inner_wall(i*3+0.7, j*3+1.5, (i+DY[k])*3+2.3, (j+DX[k])*3+1.5)
                            case 1: # UP
                                self.draw_inner_wall(i*3+1.5, j*3+0.7, (i+DY[k])*3+1.5, (j+DX[k])*3+2.3)
                            case 2: # RIGHT
                                self.draw_inner_wall(i*3+0.7, j*3+1.5, (i+DY[k])*3+2.3, (j+DX[k])*3+1.5)
                            case 3: # DOWN
                                self.draw_inner_wall(i*3+1.5, j*3+0.7, (i+DY[k])*3+1.5, (j+DX[k])*3+2.3)
        update()

    # 畫邊框
    def draw_outside_border(self):
        pensize(5)
        pencolor("#0000FF")
        for i in range(-1, self.table.height*3+1):
            self.draw_border(i, -1, 0)
            self.draw_border(i, self.table.width*3+1, 0)
        for i in range(-1, self.table.width*3+1):
            self.draw_border(-1, i, 1)
            self.draw_border(self.table.height*3+1, i, 1)
        update()

if __name__ == "__main__":
    tileTable = TileTable()
    tileTable.generate_map()
    canva = Canva(tileTable)
    canva.draw_axis()
    canva.draw_table()
    canva.draw_outside_border()
    canva.draw_inner_border()

input()