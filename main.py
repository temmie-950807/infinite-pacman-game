import random
from turtle import *
import copy
from enum import Enum
from dataclasses import dataclass

TILE_BUFFER = 4
TILE_HEIGHT = 12
TILE_WIDTH = 4
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

SPEED = 2 # 越高越快，必須是 3*MAP_CELL_GAP 的因數

@dataclass
class Point:
    y: int
    x: int
    def __add__(self, other): return Point(self.y + other.y, self.x + other.x)
    def __sub__(self, other): return Point(self.y - other.y, self.x - other.x)
    def __mul__(self, scalar): return Point(self.y * scalar, self.x * scalar)
    def distance_sq(self, other): return (self.y - other.y)**2 + (self.x - other.x)**2

class Direction(Enum):
    LEFT, UP, RIGHT, DOWN, STOP = Point(0, -1), Point(-1, 0), Point(0, 1), Point(1, 0), Point(0, 0)

    @property
    def opposite(self):
        return Point(-self.value.y, -self.value.x)

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
        return 0<=nowY<self.height and 0<=nowX<self.width
    
    def is_inside_tmp(self, nowY, nowX):
        return 0<=nowY<self.height_tmp and 0<=nowX<self.width_tmp

    def generate_map(self, nowY, nowX, id):
        if nowY<2:
            return True

        if self.table_tmp[nowY][nowX]!=0:
            if self.generate_map(nowY-(nowX==0), (nowX-1)%self.width_tmp, id):
                return True
        else:
            random.shuffle(BLOCK)
            for b in BLOCK:
                check_points = [(nowY+dy, nowX+dx) for dy, dx in b]

                if all(self.is_inside_tmp(y, x) and self.table_tmp[y][x]==0 for y, x in check_points):
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

    def is_valid(self, pos: Point):
        """
        回傳布林值代表 (nowY, nowX) 是否在範圍內並且不是牆壁。
        """
        return 0<=pos.y and pos.y<self.height and 0<=pos.x and pos.x<self.width and self.gameTable[pos.y][pos.x]!=1
    def fill(self, tileY1, tileX1, tileY2, tileX2):
        tileY1, tileY2 = sorted((tileY1, tileY2))
        tileX1, tileX2 = sorted((tileX1, tileX2))
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
class Food:
    def __init__(self, gameMap: GameMap):
        self.gameMap = gameMap
        self.haveFood = [[not cell for cell in row] for row in gameMap.gameTable]

    def update_refresh(self):
        haveFoodTmp = [[True for _ in range(self.gameMap.width)] for __ in range(self.gameMap.height)]

        new_rows = [[True] * self.gameMap.width for _ in range(3)]
        self.haveFood = new_rows + self.haveFood[:-3]
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
        self.direction = Direction.STOP
        self.gameMap = gameMap
        self.screen = screen
        self.speed = speed
        self.counter = 0

    def move(self, in_canva: callable):
        self.counter += 1
        if (self.counter==self.speed):
            self.counter = 0
            nextPos = self.pos + self.direction.value
            if self.gameMap.is_valid(nextPos) and in_canva(nextPos):
                self.pos = nextPos

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
        self.animation_counter = 0 # 0 1 2 3 4 5

    def move(self, food: Food, in_canva: callable):
        self.counter += 1
        self.animation_counter += 1
        self.animation_counter %= 6
        if (self.counter==self.speed):
            self.counter = 0
            nextPos = self.pos + self.direction.value
            if self.gameMap.is_valid(nextPos) and in_canva(nextPos):
                self.pos = nextPos

        if food.haveFood[self.pos.y][self.pos.x]:
            self.score += 1
            food.haveFood[self.pos.y][self.pos.x] = False

    def go_left(self):  self.set_dir(Direction.LEFT)
    def go_up(self):    self.set_dir(Direction.UP)
    def go_right(self): self.set_dir(Direction.RIGHT)
    def go_down(self):  self.set_dir(Direction.DOWN)
class Ghost(Unit):
    def __init__(self, pos, color, gameMap, screen, speed):
        self.targetPos = Point(-1, -1)
        super().__init__(pos, color, gameMap, screen, speed)

    def think(self, pacman: Pacman):
        """
        設定鬼要前進的下一個方向
        """
        targetPos = self.get_target_position(pacman)
        self.targetPos = targetPos

        bestDirection = Direction.STOP
        minDistance = float("inf")
        oppositeDirection = self.direction.opposite

        for dir in [Direction.LEFT, Direction.UP, Direction.RIGHT, Direction.DOWN]:
            if dir.value==oppositeDirection:
                continue

            nextPos = self.pos + dir.value
            if self.gameMap.is_valid(nextPos):
                dis = self.targetPos.distance_sq(nextPos)
                if dis<minDistance:
                    minDistance = dis
                    bestDirection = dir

        self.set_dir(bestDirection)
    
    def get_target_position(self, pacman):
        raise NotImplementedError()
class Blinky(Ghost):
    def __init__(self, pos, color, gameMap, screen, speed):
        self.originalSpeed = speed
        super().__init__(pos, color, gameMap, screen, speed)
    def get_target_position(self, pacman: Pacman):
        """
        Blinky 的攻擊模式：不停地找到與 PacMan 的最短路徑，並朝著最短路徑
        """
        return pacman.pos

    def update_the_speed(self, pacman: Pacman):
        """
        每當分數多出 50，速度就會增加 1
        """
        self.speed = max(1, self.originalSpeed - pacman.score//50)
class Pinky(Ghost):
    def get_target_position(self, pacman: Pacman):
        """
        Pinky 的攻擊模式：不停地找到與 PacMan 面前四格的最短路徑，並朝著最短路徑移動
        """
        targetDir = pacman.direction
        targetPos = pacman.pos + Direction(targetDir).value*4
        return targetPos
class Inky(Ghost):
    def __init__(self, pos: int, color: str, gameMap: GameMap, screen, speed: int, blinky: Blinky):
        self.blinky = blinky
        super().__init__(pos, color, gameMap, screen, speed)

    def get_target_position(self, pacman: Pacman):
        """
        Inky 的攻擊模式：走向點 A（Blinky 的位置）與點 B（Pac-Man 的面前 2 兩格）的兩倍向量
        """
        a = self.blinky.pos
        b = pacman.pos
        pacManDirection = pacman.direction
        b = b+Direction(pacManDirection).value*2
        targetPos = self.blinky.pos+(b-a)*2
        return targetPos
class Clyde(Ghost):
    def get_target_position(self, pacman: Pacman):
        """
        Clyde 的攻擊模式：如果在 Pac-Man 8 格之外，則跟 Blinky 一樣攻擊，否則會退回左下角
        """
        dist = self.pos.distance_sq(pacman.pos)**0.5
        if dist>8:
            targetPos = pacman.pos
        else:
            targetPos = Point(self.gameMap.height/2+10, 2)  # 左下角
        return targetPos
class Canva:
    def __init__(self, gameTable: GameMap, ghosts: list[Ghost], food: Food):
        reset()
        tracer(0, delay=None)
        speed(0)
        hideturtle()
        bgcolor("#000000")

        self.gameTable = gameTable
        self.ghosts = ghosts
        self.food = food
        self.scrollOffset = 0

    def draw(self, scrollOffset: int):
        self.scrollOffset = scrollOffset
        clear()

        # 繪製食物
        for i in range(self.gameTable.height):
            for j in range(self.gameTable.width):
                if self.food.haveFood[i][j]:
                    pos = self._position(Point(i, j))
                    teleport(pos.x, pos.y)
                    dot(5, "white")

        # 繪製牆壁
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

        # 繪製鬼與鬼的目標格
        for ghost in self.ghosts:
            pos = self._position(ghost.pos)
            teleport(pos.x, pos.y)
            dot(20, ghost.color)
            pencolor(ghost.color)
            self._draw_target(ghost.targetPos)

        # 繪製 Pac-Man
        self._draw_pacman(game.pacman)

        # 繪製文字
        pencolor("white")
        teleport(10, SCREEN_HEIGHT-10)
        write(f"Score: {game.pacman.score}", font=("Arial", 16, "normal"))
        teleport(10, SCREEN_HEIGHT-30)
        write(f"Speed: {game.ghosts[0].speed}", font=("Arial", 16, "normal"))

        update()

    def in_canva(self, mapPos: Point) -> bool:
        """
        回傳布林值代表 mapPos 座標是否在畫布範圍內
        """
        screenPos = self._position(mapPos)
        return 0<=screenPos.y and screenPos.y<=SCREEN_HEIGHT and 0<=screenPos.x and screenPos.x<=SCREEN_WIDTH

    def _position(self, mapPos: Point) -> Point:
        """
        給定 table 的 mapPos 座標，回傳該格左上角的畫布座標 screenPos
        """
        screenPos = Point(
            (mapPos.y - (self.gameTable.height-1)/2) * MAP_CELL_GAP + SCREEN_HEIGHT/2, # 為什麼要 -1，不清楚
            (mapPos.x - (self.gameTable.width-1)/2) * MAP_CELL_GAP + SCREEN_WIDTH/2
        )
        screenPos.y += self.scrollOffset
        return screenPos
    
    def _draw_rectangle(self, mapY1, mapX1, mapY2, mapX2):
        """
        給定 table 的對角線座標 (mapY1, mapX1) 跟 (mapY2, mapX2)，在裡面畫出矩形
        """
        mapY1, mapY2 = sorted((mapY1, mapY2))
        mapX1, mapX2 = sorted((mapX1, mapX2))
        if not self.in_canva(Point(mapY1+2, mapX1+2)) and not self.in_canva(Point(mapY2-2, mapX2-2)):
            return
        pencolor("#0000FF")
        pensize(10)
        screen1 = self._position(Point(mapY1, mapX1))
        screen2 = self._position(Point(mapY2, mapX2))
        teleport(screen1.x, screen1.y)
        begin_fill()
        goto(screen1.x, screen2.y)
        goto(screen2.x, screen2.y)
        goto(screen2.x, screen1.y)
        goto(screen1.x, screen1.y)
        end_fill()

    def _draw_target(self, mapPos: Point):
        """
        給定 table 的座標 mapPos，在裡面畫出目標點
        """
        setheading(0)
        screenPos = self._position(mapPos)
        pensize(2)
        for x in [1, 5, 10]:
            teleport(screenPos.x, screenPos.y-x)
            circle(x)
        teleport(screenPos.x, screenPos.y)
        goto(screenPos.x, screenPos.y+15)
        goto(screenPos.x, screenPos.y-15)
        teleport(screenPos.x, screenPos.y)
        goto(screenPos.x+15, screenPos.y)
        goto(screenPos.x-15, screenPos.y)

    def _draw_pacman(self, pacman: Pacman):
        screenPos = self._position(pacman.pos)
        teleport(screenPos.x, screenPos.y)

        if pacman.direction==Direction.LEFT:
            setheading(180)
        elif pacman.direction==Direction.UP:
            setheading(270)
        elif pacman.direction==Direction.RIGHT:
            setheading(0)
        elif pacman.direction==Direction.DOWN:
            setheading(90)
        else:
            setheading(0)

        print(heading())

        deg = min(pacman.animation_counter, 6-pacman.animation_counter)*15
        print(pacman.animation_counter, deg)
        fillcolor(pacman.color)
        penup()
        begin_fill()
        left(deg)
        forward(10)
        left(90)
        circle(10, 360 - deg*2)
        left(90)
        forward(10)
        end_fill()
        pendown()

        # 0 -> 0
        # 1 -> 15
        # 2 -> 30
        # 3 -> 45
        # 4 -> 30
        # 5 -> 15
        
class Game:
    def __init__(self, gameMap: GameMap, pacman: Pacman, ghosts: list[Ghost], food: Food, canva: Canva):
        self.gameMap = gameMap
        self.pacman = pacman
        self.ghosts = ghosts
        self.food = food
        self.canva = canva
        self.scrollOffset = 0

    def in_canva(self, mapPos: Point) -> bool:
        return self.canva.in_canva(mapPos)

    def update(self):
        self.pacman.move(self.food, self.in_canva)
        for ghost in self.ghosts:
            ghost.think(self.pacman)
            ghost.move(self.in_canva)
        ghosts[0].update_the_speed(self.pacman)

        self.scrollOffset += SPEED
        if self.scrollOffset == 3*MAP_CELL_GAP:
            self.scrollOffset = 0
            self.pacman.update_refresh()
            for ghost in self.ghosts:
                ghost.update_refresh()
            self.gameMap.update_refresh()
            self.food.update_refresh()

        canva.draw(self.scrollOffset)

if __name__ == "__main__":
    screen = Screen()
    screen.setup(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
    screen.setworldcoordinates(0, SCREEN_HEIGHT, SCREEN_WIDTH, 0) # (左下角x, 左下角y, 右上角x, 右上角y)

    tileTable = TileTable()
    gameMap = GameMap(tileTable)
    food = Food(gameMap)

    pacman = Pacman(Point(-1, -1), "yellow", gameMap, screen, 4)
    blinky = Blinky(Point(-1, -1), "red", gameMap, screen, 8)
    inky = Inky(Point(-1, -1), "cyan", gameMap, screen, 8, blinky)
    pinky = Pinky(Point(-1, -1), "pink", gameMap, screen, 8)
    clyde = Clyde(Point(-1, -1), "orange", gameMap, screen, 8)
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

    ghosts = [blinky, inky, pinky, clyde]
    canva = Canva(gameMap, ghosts, food)
    game = Game(gameMap, pacman, ghosts, food, canva)
    while True:
        game.update()

input()