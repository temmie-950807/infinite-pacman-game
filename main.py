import random
from turtle import *
from queue import Queue
import copy
from enum import Enum

TILE_BUFFER = 4
TILE_HEIGHT = 12
TILE_WIDTH = 5
BLOCK = [
    # 直線
    [(0, 0), (-1, 0)],
    [(0, 0), (-1, 0), (-2, 0)],

    # 橫線
    [(0, 0), (0, -1)],
    [(0, 0), (0, -1), (0, -2)],

    # L 彎
    [(0, 0), (0, -1), (-1, 0)],
    [(0, 0), (-1, -1), (-1, 0)],
    [(0, 0), (-1, -1), (-1, 0)],
    [(0, 0), (-1, 0), (1, -1)],

    [(0, 0), (-1, 0), (-2, 0), (-1, -1)],
    [(0, 0), (-1, 0), (-2, 0), (0, -1)],
    [(0, 0), (-1, 0), (-2, 0), (-2, -1)],
]

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

# LEFT, UP, RIGHT, DOWN
DX = [-1, 0, 1, 0]
DY = [0, -1, 0, 1]
MAP_CELL_GAP = 16

SPEED = 1 # 越高越慢，必須是 3*MAP_CELL_GAP 的因數

class Point:
    """用來簡化座標計算的類別"""
    def __init__(self, y, x):
        self.y = y
        self.x = x

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar):
        return Point(self.x * scalar, self.y * scalar)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def distance_sq(self, other):
        """回傳距離的平方"""
        return (self.x - other.x)**2 + (self.y - other.y)**2

class Direction(Enum):
    LEFT = Point(-1, 0)
    UP = Point(0, -1)
    RIGHT = Point(1, 0)
    DOWN = Point(0, 1)
    STOP = Point(0, 0)

class TileTable:
    def __init__(self, height = TILE_HEIGHT + TILE_BUFFER, width = TILE_WIDTH):
        self.table_tmp = [[0] * width for _ in range(height)]
        self.table = [list() for _ in range(height)]
        self.generate_map(self.height_tmp-1, self.width_tmp-1, 1)
        self.build()

    @property
    def height(self):
        return len(self.table)
    
    @property
    def width(self):
        return len(self.table[0])
    
    @property
    def height_tmp(self):
        return len(self.table_tmp)
    
    @property
    def width_tmp(self):
        return len(self.table_tmp[0])
    
    def __getitem__(self, index):
        return self.table[index]
    
    def __setitem__(self, index, value):
        self.table[index] = value

    def is_inside(self, nowY, nowX):
        return 0<=nowY and nowY<self.height and 0<=nowX and nowX<self.width
    
    def is_inside_tmp(self, nowY, nowX):
        return 0<=nowY and nowY<self.height_tmp and 0<=nowX and nowX<self.width_tmp

    def generate_map(self, nowY, nowX, id):
        if nowY<2:
            return True

        if self.table_tmp[nowY][nowX]!=0:
            if self.generate_map(nowY-(nowX==0), (nowX-1)%self.width_tmp, id):
                return True
        else:
            random.shuffle(BLOCK)
            for b in BLOCK:
                isValid = True
                for (offsetY, offsetX) in b:
                    if (not self.is_inside_tmp(nowY+offsetY, nowX+offsetX)) or self.table_tmp[nowY+offsetY][nowX+offsetX]!=0:
                        isValid = False
                        break

                if isValid:
                    for (offsetY, offsetX) in b:
                        self.table_tmp[nowY+offsetY][nowX+offsetX] = id
                    if self.generate_map(nowY-(nowX==0), (nowX-1)%self.width_tmp, id%200+1):
                        return True
                    for (offsetY, offsetX) in b:
                        self.table_tmp[nowY+offsetY][nowX+offsetX] = 0

            self.table_tmp[nowY][nowX] = id
            if self.generate_map(nowY-(nowX==0), (nowX-1)%self.width_tmp, id%200+1):
                return True
            self.table_tmp[nowY][nowX] = 0

        return False
    
    def build(self):
        for i in range(self.height):
            self.table[i] = self.table_tmp[i][-1:0:-1]+self.table_tmp[i]

    def update_refresh(self):
        self.table_tmp.insert(0, [0]*self.width_tmp)
        del self.table_tmp[-1]
        self.generate_map(self.height_tmp-1, self.width_tmp-1, max(max(row) for row in self.table_tmp)+1)
        self.build()

    def print(self):
        print("Tile Table:")
        for row in self.table:
            for cell in row:
                print(f"{cell:2}", end=" ")
            print()
        print("hegiht:", self.height, "width:", self.width)
        print()

    def print_tmp(self):
        print("Tile Table Tmp:")
        for row in self.table_tmp:
            for cell in row:
                print(f"{cell:2}", end=" ")
            print()
        print("hegiht:", self.height_tmp, "width:", self.width_tmp)
        print()
class GameMap:
    def __init__(self, table: TileTable):
        self.table = table
        self.gameTable = [
            [0 for _ in range(self.table.width*3+5)] for __ in range(self.table.height*3+5)
        ]

        # 左右的外牆
        for i in range(self.height):
            self.gameTable[i][0] = 1
            self.gameTable[i][1] = 1
            self.gameTable[i][-1] = 1
            self.gameTable[i][-2] = 1

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

    def is_valid(self, nowY, nowX):
        """
        回傳布林值代表 (nowY, nowX) 是否在範圍內並且不是牆壁。
        """
        return 0<=nowY and nowY<self.height and 0<=nowX and nowX<self.width and self.gameTable[nowY][nowX]!=1

    def fill(self, tileY1, tileX1, tileY2, tileX2):
        tileY1, tileX1, tileY2, tileX2 = min(tileY1, tileY2), min(tileX1, tileX2), max(tileY1, tileY2), max(tileX1, tileX2)
        tileY1 = tileY1*3+3
        tileX1 = tileX1*3+3
        tileY2 = tileY2*3+3+1
        tileX2 = tileX2*3+3+1
        for i in range(tileY1, tileY2+1):
            for j in range(tileX1, tileX2+1):
                self.gameTable[i][j] = 1

    def update_refresh(self):
        tileTable.update_refresh()
        self.__init__(self.table)
    
    def print(self):
        print("Game Map:")
        for row in self.gameTable:
            for cell in row:
                print(f"{cell:2}", end=" ")
            print()
        print("hegiht:", self.height, "width:", self.width)
        print()
class Food:
    def __init__(self, gameMap: GameMap):
        self.gameMap = gameMap
        self.haveFood = copy.deepcopy(gameMap.gameTable)
        for i in range(gameMap.height):
            for j in range(gameMap.width):
                self.haveFood[i][j] = not self.haveFood[i][j]

    def update(self, units):
        pass

    def update_refresh(self):
        haveFoodTmp = [[True for _ in range(self.gameMap.width)] for __ in range(self.gameMap.height)]

        del self.haveFood[-1]
        del self.haveFood[-1]
        del self.haveFood[-1]
        for i in range(0, 3):
            self.haveFood.insert(i, gameMap.gameTable[i][:])
        for i in range(0, 3):
            for j in range(gameMap.width):
                self.haveFood[i][j] = [True for _ in range(gameMap.width)]

        for i in range(gameMap.height):
            for j in range(gameMap.width):
                if self.haveFood[i][j]==False:
                    haveFoodTmp[i][j] = False

        self.haveFood = copy.deepcopy(haveFoodTmp)
class Unit:
    def __init__(self, pos, color, gameMap: GameMap, screen, speed):
        self.pos = pos
        self.color = color
        self.direction = 1
        self.gameMap = gameMap
        self.screen = screen
        self.speed = speed
        self.counter = 0

    def update(self, units, food, offsetY):
        self.counter += 1

        if (self.counter==self.speed):
            self.counter = 0

            nextY = self.pos.y + DY[self.direction]
            nextX = self.pos.x + DX[self.direction]

            if self.gameMap.is_valid(nextY, nextX) and abs(self.pos.y-(gameMap.height/2-offsetY/16))<=14:
                self.pos = Point(nextY, nextX)

    def in_border(self, posY, offsetY):
        return abs(posY-(self.gameMap.height/2-offsetY/16))<=14

    def set_dir(self, dir_code):
        self.direction = dir_code

    def update_refresh(self):
        self.pos.y += 3
class Pacman(Unit):
    def __init__(self, pos, color, gameMap, screen, speed):
        super().__init__(pos, color, gameMap, screen, speed)
        self.screen.onkeypress(self.go_left, "a")
        self.screen.onkeypress(self.go_up, "w")
        self.screen.onkeypress(self.go_right, "d")
        self.screen.onkeypress(self.go_down, "s")
        self.screen.listen()
        self.score = 0

    def update(self, units, food: Food, offsetY = None):
        if food.haveFood[self.pos.y][self.pos.x]:
            self.score += 1
            food.haveFood[self.pos.y][self.pos.x] = False
        return super().update(units, food, offsetY)

    def go_left(self):  self.set_dir(0)
    def go_up(self):    self.set_dir(1)
    def go_right(self): self.set_dir(2)
    def go_down(self):  self.set_dir(3)
class Ghost(Unit):
    def __init__(self, pos, color, gameMap, screen, speed):
        self.targetY = -1
        self.targetX = -1
        super().__init__(pos, color, gameMap, screen, speed)

    def get_next_direction(self, targetY, targetX, units, offsetY):
        self.targetY = targetY
        self.targetX = targetX

        # qq = Queue()
        # qq.put((self.targetY, self.targetX))
        # dis = [[-1 for _ in range(self.gameMap.width)] for __ in range(self.gameMap.height)]
        # dis[self.targetY][self.targetX] = 0

        # while not qq.empty():
        #     nowY, nowX = qq.get()
        #     for i in range(4):
        #         nextY, nextX = nowY+DY[i], nowX+DX[i]
        #         if self.gameMap.is_valid(nextY, nextX) and self.in_border(nextY, offsetY) and dis[nextY][nextX]==-1:
        #             dis[nextY][nextX] = dis[nowY][nowX]+1
        #             qq.put((nextY, nextX))
        
        mi = -1
        argMi = -1
        for i in range(4):
            if (i+2)%4 == self.direction:
                continue
            nextY, nextX = self.pos.y+DY[i], self.pos.x+DX[i]
            if self.gameMap.is_valid(nextY, nextX) and self.in_border(nextY, offsetY):
                dis = ((nextY - self.targetY)**2 + (nextX - self.targetX)**2)**0.5
                if mi==-1:
                    mi = dis
                    argMi = i
                elif dis<mi:
                    mi = dis
                    argMi = i

        return argMi
        
class Blinky(Ghost):
    def update(self, units: dict[str, Unit], food: Food, offsetY: int):
        """
        Blinky 的攻擊模式：不停地找到與 PacMan 的最短路徑，並朝著最短路徑
        """
        nextDirection = self.get_next_direction(units["pacman"].pos.y, units["pacman"].pos.x, units, offsetY)
        self.set_dir(nextDirection)
        return super().update(units, food, offsetY)
class Pinky(Ghost):
    def update(self, units: dict[str, Unit], food: Food, offsetY: int):
        """
        Pinky 的攻擊模式：不停地找到與 PacMan 面前四格的最短路徑，並朝著最短路徑移動
        """
        targetDir = units["pacman"].direction
        targetY = units["pacman"].pos.y + DY[targetDir]*4
        targetX = units["pacman"].pos.x + DX[targetDir]*4
        # for i in range(1, 5):
        #     if self.gameMap.is_valid(targetY+DY[targetDir], targetX+DX[targetDir]) and self.in_border(targetY+DY[targetDir], offsetY):
        #         targetY += DY[targetDir]
        #         targetX += DX[targetDir]
        #     else:
        #         break
        nextDirection = self.get_next_direction(targetY, targetX, units, offsetY)
        self.set_dir(nextDirection)
        return super().update(units, food, offsetY)
class Inky(Ghost):
    def update(self, units: dict[str, Unit], food: Food, offsetY: int):
        """
        Inky 的攻擊模式：走向點 A（Blinky 的位置）與點 B（Pac-Man 的面前 2 兩格）的兩倍向量
        """
        aY, aX = units["blinky"].pos.y, units["blinky"].pos.x
        bY, bX = units["pacman"].pos.y, units["pacman"].pos.x
        pacManDirection = units["pacman"].direction
        bY += 2*DY[pacManDirection]
        bX += 2*DX[pacManDirection]

        targetY = units["blinky"].pos.y + 2*(bY-aY)
        targetX = units["blinky"].pos.x + 2*(bX-aX)
        nextDirection = self.get_next_direction(targetY, targetX, units, offsetY)
        self.set_dir(nextDirection)
        return super().update(units, food, offsetY)
class Clyde(Ghost):
    def update(self, units: dict[str, Unit], food: Food, offsetY: int):
        """
        Clyde 的攻擊模式：如果在 Pac-Man 8 格之外，則跟 Blinky 一樣攻擊，否則會退回左下角
        """
        dist = ((self.pos.y - units["pacman"].pos.y)**2+(self.pos.x - units["pacman"].pos.x)**2)**0.5
        if dist>8:
            targetY, targetX = units["pacman"].pos.y, units["pacman"].pos.x
        else:
            targetY, targetX = self.gameMap.height/2+10, 2  # 左下角
        nextDirection = self.get_next_direction(targetY, targetX, units, offsetY)
        self.set_dir(nextDirection)
        return super().update(units, food, offsetY)
class Canva:
    def __init__(self, gameTable: GameMap, units: list[Unit], food: Food):
        reset()
        tracer(0, delay=None)
        speed(0)
        hideturtle()

        bgcolor("#000000")

        self.gameTable = gameTable
        self.units = units
        self.food = food
        self.offsetY = 0

    def _draw(self):
        clear()
        hideturtle()
        # self._draw_axis()
        # self._draw_table()

        for i in range(self.gameTable.height):
            for j in range(self.gameTable.width):
                if self.food.haveFood[i][j]:
                    pos = self._position(i, j)
                    teleport(pos.x, pos.y)
                    dot(5, "white")

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

        for unit in units.values():
            pos = self._position(unit.pos.y, unit.pos.x)
            teleport(pos.x, pos.y)
            dot(20, unit.color)

            if issubclass(type(unit), Ghost):
                target = self._position(unit.targetY, unit.targetX)
                teleport(target.x, target.y)
                dot(10, unit.color)

        # if self.gameMap.is_valid(nextY, nextX) and abs(nextY-((gameMap.height-offset)/2))<=14:
        # print(f"half height: {gameMap.height/2}")
        # pencolor("#00FF00")
        # for i in range(gameMap.width):
        #     self._draw_border(gameMap.height/2-self.offsetY/16, i, 0)

        update()

    def _position(self, mapY, mapX):
        """
        給定 table 的 (mapY, mapX) 座標，回傳該格左上角的畫布座標 (screen_y, screen_x)
        """
        screenY = (mapY - (self.gameTable.height-1)/2) * MAP_CELL_GAP + SCREEN_HEIGHT/2 # 為什麼要 -1，不清楚
        screenX = (mapX - (self.gameTable.width-1)/2) * MAP_CELL_GAP + SCREEN_WIDTH/2
        screenY += self.offsetY
        return Point(screenY, screenX)
    
    def _draw_rectangle(self, mapY1, mapX1, mapY2, mapX2):
        """
        給定 table 的對角線座標 (mapY1, mapX1) 跟 (mapY2, mapX2)，在裡面畫出矩形
        """
        mapY1, mapX1, mapY2, mapX2 = min(mapY1, mapY2), min(mapX1, mapX2), max(mapY1, mapY2), max(mapX1, mapX2)
        pencolor("#0000FF")
        pensize(10)
        screen1 = self._position(mapY1, mapX1)
        screen2 = self._position(mapY2, mapX2)
        teleport(screen1.x, screen1.y)
        begin_fill()
        goto(screen1.x, screen2.y)
        goto(screen2.x, screen2.y)
        goto(screen2.x, screen1.y)
        goto(screen1.x, screen1.y)
        end_fill()

    def update(self):
        for unit in units.values():
            unit.update(self.units, self.food, self.offsetY)
        canva.offsetY += SPEED
        if canva.offsetY==3*MAP_CELL_GAP:
            canva.offsetY = 0
            for unit in units.values():
                unit.update_refresh()
            self.gameTable.update_refresh()
            self.food.update_refresh()
        self._draw()

class Game:
    def __init__(self, gameMap: GameMap, pacman: Pacman, ghosts: list[Ghost]):
        self.gameMap = gameMap
        self.pacman = pacman
        self.ghosts = ghosts
        self.scrollOffset = 0

    def update(self):
        self.pacman.update()
        for ghost in self.ghosts:
            ghost.update()

        self.scrollOffset += SPEED
        if self.scrollOffset == 3*MAP_CELL_GAP:
            self.scrollOffset = 0
            self.pacman.update_refresh()
            for ghost in self.ghosts:
                ghost.update_refresh()
            self.gameMap.update_refresh()

if __name__ == "__main__":
    screen = Screen()
    screen.setup(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
    screen.setworldcoordinates(0, SCREEN_HEIGHT, SCREEN_WIDTH, 0) # (左下角x, 左下角y, 右上角x, 右上角y)

    tileTable = TileTable()
    gameMap = GameMap(tileTable)
    food = Food(gameMap)

    pacman = Pacman(Point(-1, -1), "yellow", gameMap, screen, 1)
    blinky = Blinky(Point(-1, -1), "red", gameMap, screen, 2)
    inky = Inky(Point(-1, -1), "cyan", gameMap, screen, 2)
    pinky = Pinky(Point(-1, -1), "pink", gameMap, screen, 2)
    clyde = Clyde(Point(-1, -1), "orange", gameMap, screen, 2)
    for i in range(gameMap.height//2, -1, -1):
        for j in range(gameMap.width):
            if pacman.pos==Point(-1, -1) and gameMap[i][j]==0:
                pacman.pos = Point(i, j)

            elif blinky.pos==Point(-1, -1) and gameMap[i][j]==0:
                blinky.pos = Point(i, j)

            elif inky.pos==Point(-1, -1) and gameMap[i][j]==0:
                inky.pos = Point(i, j)

            elif pinky.pos==Point(-1, -1) and gameMap[i][j]==0:
                pinky.pos = Point(i, j)

            elif clyde.pos==Point(-1, -1) and gameMap[i][j]==0:
                clyde.pos = Point(i, j)

    units: dict[str, Unit] = {
        "pacman": pacman,
        "blinky": blinky,
        "inky": inky,
        "pinky": pinky,
        "clyde": clyde,
    }

    # game = Game(gameMap, pacman, [blinky, inky, pinky, clyde])

    canva = Canva(gameMap, units, food)
    while True:
        canva.update()

input()