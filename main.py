import random
from turtle import *
import time

TILE_HEIGHT = 9
TILE_WIDTH = 5
BLOCK = [
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

GAME_MAP_HEIGHT = TILE_HEIGHT*3
GAME_MAP_WIDTH = TILE_WIDTH*3

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

# LEFT, UP, RIGHT, DOWN
DX = [-1, 0, 1, 0]
DY = [0, -1, 0, 1]
MAP_GAP = 16
TILE_GAP = 48

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

class GameMap:
    def __init__(self, table: TileTable):
        tracer(0, delay=None)
        speed(0)
        hideturtle()
        self.table = table
        for idx in range(self.table.height):
            self.table[idx] = self.table[idx][-1:0:-1]+self.table[idx]
        self.table.print()

    def position(self, y, x):
        """
        給定 table 的 (y, x) 座標，回傳該格左上角的畫布座標 (screen_y, screen_x)
        """
        return ((y-self.table.height*3/2)*MAP_GAP+SCREEN_HEIGHT/2, (x-self.table.width*3/2)*MAP_GAP+SCREEN_WIDTH/2)
    
    def draw_line(self, y1, x1, y2, x2):
        """
        給定 table 的 (y1, x1) 跟 (y2, x2)，畫出連線
        """
        y1, x1 = self.position(y1, x1)
        y2, x2 = self.position(y2, x2)
        teleport(x1, y1)
        goto(x2, y2)

    # 給定網格的 (y, x)，畫出該格的邊界
    def draw_border(self, y, x, dir):
        """
        給定網格的 (y, x) 和方向 dir，畫出該格的邊界
        0: LEFT
        1: UP
        2: RIGHT
        3: DOWN
        """
        match dir:
            case 0: # LEFT
                self.draw_line(y, x, y+1, x)
            case 1: # UP
                self.draw_line(y, x, y, x+1)
            case 2: # RIGHT
                self.draw_line(y, x+1, y+1, x+1)
            case 3: # DOWN
                self.draw_line(y+1, x, y+1, x+1)

    # 給定 TILE 的座標左上角 (y1, x1) 跟右下角 (y2, x2)，在裡面畫出矩形
    def draw_inner_wall(self, y1, x1, y2, x2):
        """
        給定 table 的座標左上角 (y1, x1) 跟右下角 (y2, x2)，在裡面畫出矩形
        """

        if ((y1, x2)==(y2, x2)):
            y1 = y1*3+0.7
            x1 = x1*3+0.7
            y2 = y2*3+2.3
            x2 = x2*3+2.3
        else:
            dy1 = [0.7, 1.5, 0.7, 1.5]
            dx1 = [1.5, 0.7, 1.5, 0.7]
            dy2 = [2.3, 1.5, 2.3, 1.5]
            dx2 = [1.5, 2.3, 1.5, 2.3]
            for i in range(4):
                if ((y1, x1)==(y2+DY[i], x2+DX[i])):
                    y1 = y1*3+dy1[(i+2)%4]
                    x1 = x1*3+dx1[(i+2)%4]
                    y2 = y2*3+dy2[(i+2)%4]
                    x2 = x2*3+dx2[(i+2)%4]
                    break
    
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

    def draw_table(self):
        """
        畫灰色網格
        """
        pencolor("#CCCCCC")
        pensize(1)
        for i in range(self.table.height*3):
            for j in range(self.table.width*3):
                for k in range(4):
                    self.draw_border(i, j, k)
        update()

    def draw_axis(self):
        """
        畫座標軸
        """
        pensize(3)
        pencolor("#FF0000")
        teleport(-1000, 0)
        goto(1000, 0)
        pencolor("#00FF00")
        teleport(0, -1000)
        goto(0, 1000)
        update()

    def draw_inner_border(self):
        """
        畫內部邊界
        """
        pencolor("#0000FF")
        fillcolor("#0000FF")
        for i in range(0, self.table.height):
            for j in range(0, self.table.width):
                fillcolor("#0000FF")
                self.draw_inner_wall(i, j, i, j)
                for k in range(4):
                    if self.table.is_inside(i+DY[k], j+DX[k]) and self.table[i][j]==self.table[i+DY[k]][j+DX[k]]:
                        self.draw_inner_wall(i, j, i+DY[k], j+DX[k])
        update()

    def draw_outside_border(self):
        """
        畫邊框
        """
        pensize(5)
        fillcolor("#0000FF")
        for i in range(-1, self.table.height):
            self.draw_inner_wall(i, -1, i+1, -1)
            self.draw_inner_wall(i, self.table.width, i+1, self.table.width)
        for i in range(-1, self.table.width):
            self.draw_inner_wall(-1, i, -1, i+1)
            self.draw_inner_wall(self.table.width, i, self.table.width, i+1)
        update()

if __name__ == "__main__":
    while True:
        screen = Screen()
        screen.setup(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
        # (左下角x, 左下角y, 右上角x, 右上角y)
        screen.setworldcoordinates(0, SCREEN_HEIGHT, SCREEN_WIDTH, 0)

        tileTable = TileTable()
        tileTable.generate_map()
        gameMap = GameMap(tileTable)
        gameMap.draw_axis()
        gameMap.draw_table()
        gameMap.draw_outside_border()
        gameMap.draw_inner_border()
        break
        time.sleep(1)
        reset()

input()