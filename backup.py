import random
import turtle
from enum import Enum

MAP_HEIGHT = 27
MAP_WIDTH = 15

TILE_HEIGHT = MAP_HEIGHT//3
TILE_WIDTH = MAP_WIDTH//3

tileTable = [[0] * TILE_WIDTH for _ in range(TILE_HEIGHT)]

block = [
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

def inside(nowX, nowY):
    return 0<=nowX and nowX<TILE_HEIGHT and 0<=nowY and nowY<TILE_WIDTH

found = False
def dfs(nowX, nowY, id):
    global found

    if nowX==TILE_HEIGHT and nowY==0:
        found = True
        return

    if tileTable[nowX][nowY]!=0:
        dfs(nowX+(nowY==TILE_WIDTH-1), (nowY+1)%TILE_WIDTH, id)

    else:
        random.shuffle(block)
        for b in block:
            ok = True
            for (offsetX, offsetY) in b:
                if (not inside(nowX+offsetX, nowY+offsetY)) or tileTable[nowX+offsetX][nowY+offsetY]!=0:
                    ok = False
                    break

            if (ok):
                for (offsetX, offsetY) in b:
                    tileTable[nowX+offsetX][nowY+offsetY] = id
                dfs(nowX+(nowY==TILE_WIDTH-1), (nowY+1)%TILE_WIDTH, id+1)
                if found:
                    return
                for (offsetX, offsetY) in b:
                    tileTable[nowX+offsetX][nowY+offsetY] = 0

def mirror_table():
    global tileTable, TILE_WIDTH, MAP_WIDTH
    for i in range(TILE_HEIGHT):
        tileTable[i] = list(reversed(tileTable[i]))[:-1] + tileTable[i]

    TILE_WIDTH = TILE_WIDTH*2-1
    MAP_WIDTH = MAP_WIDTH*2-3

# ============================= draw =============================
DX = [0, 0, -1, 1]
DY = [-1, 1, 0, 0]
turtle.tracer(0, delay=None)
turtle.speed(0) # 畫筆的移動速度，範圍是0-10，數字越大越快。
turtle.hideturtle()
GAP = 16

def draw_line(x1, y1, x2, y2):
    x1 -= 250
    y1 += 250
    x2 -= 250
    y2 += 250
    turtle.teleport(x1, y1)
    turtle.goto(x2, y2)

class Direction(Enum):
    LEFT = 0
    RIGHT = 1
    UP = 2
    DOWN = 3

def position(x, y):
    return (x*3*GAP, -y*3*GAP)

def draw_border(y, x, dir: Direction):
    x, y = position(x, y)
    match dir:
        case 0:
            draw_line(x, y, x, y-3*GAP)
        case 1:
            draw_line(x+3*GAP, y, x+3*GAP, y-3*GAP)
        case 2:
            draw_line(x, y, x+3*GAP, y)
        case 3:
            draw_line(x, y-3*GAP, x+3*GAP, y-3*GAP)

def draw_inner_wall(y, x, width = 2):
    x, y = position(x, y)
    x -= 250
    y += 250
    turtle.begin_fill()
    turtle.teleport(x+GAP//2, y-GAP//2)
    turtle.goto(x+width*GAP+GAP//2, y-GAP//2)
    turtle.goto(x+width*GAP+GAP//2, y-width*GAP-GAP//2)
    turtle.goto(x+GAP//2, y-width*GAP-GAP//2)
    turtle.goto(x+GAP//2, y-GAP//2)
    turtle.end_fill()

def draw():
    # 畫底色灰色
    turtle.pencolor("#EEEEEE")
    turtle.pensize(1)
    for i in range(MAP_WIDTH+1):
        draw_line(i*GAP, 0, i*GAP, -MAP_HEIGHT*GAP)
    turtle.teleport(0, 0)
    for i in range(MAP_HEIGHT+1):
        draw_line(0, -i*GAP, MAP_WIDTH*GAP, -i*GAP)

    # 畫主要網格
    # turtle.pencolor("#000000")
    # turtle.pensize(3)
    # for i in range(TILE_HEIGHT):
    #     for j in range(TILE_WIDTH):
    #         for k in range(4):
    #             if (not inside(i+DX[k], j+DY[k])) or tileTable[i][j]!=tileTable[i+DX[k]][j+DY[k]]:
    #                 draw_border(i, j, k)

    # 畫上裡面的牆
    turtle.fillcolor("#0000AA")
    turtle.penup()
    for i in range(TILE_HEIGHT):
        for j in range(TILE_WIDTH):
            draw_inner_wall(i, j)
            for k in range(4):
                if inside(i+DX[k], j+DY[k]) and tileTable[i][j]==tileTable[i+DX[k]][j+DY[k]]:
                    draw_inner_wall(i+0.5*DX[k], j+0.5*DY[k])
    turtle.pendown()
# ============================= draw =============================

if __name__ == "__main__":
    dfs(0, 0, 1)
    mirror_table()
    for x in tileTable:
        print(*x)
    draw()

turtle.update()
input()