import random
from turtle import *
import time

TILE_HEIGHT = 5
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

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

# LEFT, UP, RIGHT, DOWN
DX = [-1, 0, 1, 0]
DY = [0, -1, 0, 1]
MAP_CELL_GAP = 16

class TileTable:
    def __init__(self, height = TILE_HEIGHT, width = TILE_WIDTH):
        self.table = [[0] * width for _ in range(height)]
        self.generate_map()

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
        print("Tile Table:")
        for row in self.table:
            for cell in row:
                print(f"{cell:2}", end=" ")
            print()
        print("hegiht:", self.height, "width:", self.width)
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
        self.table = table
        for idx in range(self.table.height):
            self.table[idx] = self.table[idx][-1:0:-1]+self.table[idx]

        self.gameTable = [
            [0 for _ in range(self.table.width*3+5)] for __ in range(self.table.height*3+5)
        ]

        # 左右的外牆
        for i in range(self.height):
            self.gameTable[i][0] = 1
            self.gameTable[i][1] = 1
            self.gameTable[i][-1] = 1
            self.gameTable[i][-2] = 1

        # 上下的外牆
        for j in range(self.width):
            self.gameTable[0][j] = 1
            self.gameTable[1][j] = 1
            self.gameTable[-1][j] = 1
            self.gameTable[-2][j] = 1

        # 中間的地圖
        for i in range(self.table.height):
            for j in range(self.table.width):
                self.fill(i, j, i, j)
                for k in range(4):
                    if (self.table.is_inside(i+DY[k], j+DX[k]) and
                        self.table[i][j]==self.table[i+DY[k]][j+DX[k]]):
                        self.fill(i, j, i+DY[k], j+DX[k])

    @property
    def height(self):
        return len(self.gameTable)
    
    @property
    def width(self):
        return len(self.gameTable[0])
    
    def __getitem__(self, index):
        return self.gameTable[index]
    
    def __setitem__(self, index, value):
        self.gameTable[index] = value

    def fill(self, tileY1, tileX1, tileY2, tileX2):
        tileY1, tileX1, tileY2, tileX2 = min(tileY1, tileY2), min(tileX1, tileX2), max(tileY1, tileY2), max(tileX1, tileX2)
        tileY1 = tileY1*3+3
        tileX1 = tileX1*3+3
        tileY2 = tileY2*3+3+1
        tileX2 = tileX2*3+3+1
        for i in range(tileY1, tileY2+1):
            for j in range(tileX1, tileX2+1):
                self.gameTable[i][j] = 1
    
    def print(self):
        print("Game Map:")
        for row in self.gameTable:
            for cell in row:
                print(f"{cell:2}", end=" ")
            print()
        print("hegiht:", self.height, "width:", self.width)
        print()

class Canva:
    def __init__(self, gameTable: GameMap):
        tracer(0, delay=None)
        speed(0)
        hideturtle()
        self.gameTable = gameTable

        self._draw_axis()

        fillcolor("#0000FF")
        for i in range(self.gameTable.height-1):
            for j in range(self.gameTable.width-1):
                if self.gameTable[i][j] and self.gameTable[i+1][j] and self.gameTable[i][j+1] and self.gameTable[i+1][j+1]:
                    # 整個正方形
                    self._draw_rectangle(i, j, i+1, j+1)
                elif self.gameTable[i][j] and self.gameTable[i][j+1]:
                    # 向右的長方形
                    self._draw_rectangle(i, j, i, j+1)
                elif self.gameTable[i][j] and self.gameTable[i+1][j]:
                    # 向下的長方形
                    self._draw_rectangle(i, j, i+1, j)

        self._draw_table()
        update()

    def _position(self, mapY, mapX):
        """
        給定 table 的 (mapY, mapX) 座標，回傳該格左上角的畫布座標 (screen_y, screen_x)
        """
        screenY = (mapY - (self.gameTable.height-1)/2) * MAP_CELL_GAP + SCREEN_HEIGHT/2 # 為什麼要 -1，不清楚
        screenX = (mapX - (self.gameTable.width-1)/2) * MAP_CELL_GAP + SCREEN_WIDTH/2
        return (screenY, screenX)
    
    def _draw_line(self, mapY1, mapX1, mapY2, mapX2):
        """
        給定 table 的 (mapY1, mapX1) 跟 (mapY2, mapX2)，畫出連線
        """
        screenY1, screenX1 = self._position(mapY1, mapX1)
        screenY2, screenX2 = self._position(mapY2, mapX2)
        teleport(screenX1, screenY1)
        goto(screenX2, screenY2)

    def _draw_rectangle(self, mapY1, mapX1, mapY2, mapX2):
        """
        給定 table 的對角線座標 (mapY1, mapX1) 跟 (mapY2, mapX2)，在裡面畫出矩形
        """
        mapY1, mapX1, mapY2, mapX2 = min(mapY1, mapY2), min(mapX1, mapX2), max(mapY1, mapY2), max(mapX1, mapX2)
        mapY1 -= 0.4
        mapX1 -= 0.4
        mapY2 += 0.4
        mapX2 += 0.4
        screenY1, screenX1 = self._position(mapY1, mapX1)
        screenY2, screenX2 = self._position(mapY2, mapX2)
        penup()
        teleport(screenX1, screenY1)
        begin_fill()
        goto(screenX1, screenY2)
        goto(screenX2, screenY2)
        goto(screenX2, screenY1)
        goto(screenX1, screenY1)
        end_fill()
        pendown()

    def _draw_border(self, mapY, mapX, dir):
        """
        給定 table 的 (mapY, mapX) 和方向 dir，畫出該格的邊界
        0: RIGHT
        1: DOWN
        """
        if dir==0:
            self._draw_line(mapY, mapX, mapY, mapX+1)
        else:
            self._draw_line(mapY, mapX, mapY+1, mapX)

    def _draw_table(self):
        """
        畫灰色座標網格
        """
        pencolor("#CCCCCC")
        pensize(1)
        for i in range(0, self.gameTable.height):
            for j in range(0, self.gameTable.width):
                if i<self.gameTable.height-1 and j<self.gameTable.width-1:
                    self._draw_border(i, j, 0)  # RIGHT
                    self._draw_border(i, j, 1)  # DOWN
                elif i==self.gameTable.height-1 and j<self.gameTable.width-1:
                    self._draw_border(i, j, 0)  # RIGHT
                elif i<self.gameTable.height-1 and j==self.gameTable.width-1:
                    self._draw_border(i, j, 1)  # DOWN

    def _draw_axis(self):
        """
        畫座標軸
        """
        pensize(3)
        pencolor("#FF0000")
        teleport(-1000, SCREEN_HEIGHT/2)
        goto(1000, SCREEN_HEIGHT/2)
        pencolor("#00FF00")
        teleport(SCREEN_WIDTH/2, -1000)
        goto(SCREEN_WIDTH/2, 1000)

        pensize(1)

if __name__ == "__main__":
    screen = Screen()
    screen.setup(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
    screen.setworldcoordinates(0, SCREEN_HEIGHT, SCREEN_WIDTH, 0) # (左下角x, 左下角y, 右上角x, 右上角y)

    tileTable = TileTable()
    tileTable.print()

    gameMap = GameMap(tileTable)
    gameMap.print()

    canva = Canva(gameMap)

input()