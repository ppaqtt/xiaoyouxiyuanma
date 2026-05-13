import pygame
import sys
import random

# 初始化pygame
pygame.init()

# 游戏常量
WIDTH, HEIGHT = 800, 700
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("逻辑解谜 - 电路连接")
FONT = pygame.font.Font(None, 32)
TITLE_FONT = pygame.font.Font(None, 48)

# 颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_GRAY = (30, 30, 30)
GRAY = (100, 100, 100)
LIGHT_GRAY = (180, 180, 180)
BLUE = (50, 100, 200)
LIGHT_BLUE = (100, 150, 255)
GREEN = (50, 200, 50)
LIGHT_GREEN = (100, 255, 100)
RED = (200, 50, 50)
YELLOW = (255, 220, 100)
ORANGE = (255, 150, 50)

# 组件类型
EMPTY = 0
SOURCE = 1
TARGET = 2
STRAIGHT = 3
CORNER = 4
CROSS = 5
T_SHAPE = 6

# 方向
UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3

# 组件连接定义
COMPONENT_CONNECTIONS = {
    STRAIGHT: {0: [0, 2], 1: [1, 3]},
    CORNER: {0: [0, 1], 1: [1, 2], 2: [2, 3], 3: [3, 0]},
    CROSS: {0: [0, 1, 2, 3], 1: [0, 1, 2, 3], 2: [0, 1, 2, 3], 3: [0, 1, 2, 3]},
    T_SHAPE: {0: [0, 1, 3], 1: [0, 1, 2], 2: [1, 2, 3], 3: [0, 2, 3]}
}

class CircuitComponent:
    def __init__(self, comp_type, rotation=0):
        self.type = comp_type
        self.rotation = rotation % 4
        self.powered = False
        self.source = False
        self.target = False

    def get_connections(self):
        if self.type == SOURCE or self.type == TARGET:
            return [0, 1, 2, 3]
        if self.type not in COMPONENT_CONNECTIONS:
            return []
        rot_map = COMPONENT_CONNECTIONS[self.type]
        return rot_map.get(self.rotation, [])

    def rotate(self):
        self.rotation = (self.rotation + 1) % 4

    def draw(self, surface, x, y, size):
        padding = 5
        inner_size = size - padding * 2
        cx, cy = x + size//2, y + size//2

        # 背景
        pygame.draw.rect(surface, DARK_GRAY, (x + padding, y + padding, inner_size, inner_size), 0, 5)

        if self.type == EMPTY:
            return

        # 电源/目标颜色
        if self.source:
            color = GREEN if self.powered else LIGHT_GREEN
        elif self.target:
            color = YELLOW if self.powered else ORANGE
        else:
            color = LIGHT_BLUE if self.powered else BLUE

        # 绘制组件
        if self.type == SOURCE or self.type == TARGET:
            pygame.draw.circle(surface, color, (cx, cy), inner_size//3)
            if self.type == SOURCE:
                pygame.draw.polygon(surface, WHITE, [
                    (cx, cy - 15), (cx + 10, cy + 10), (cx - 10, cy + 10)
                ])
            else:
                pygame.draw.circle(surface, WHITE, (cx, cy), 8)

        elif self.type == STRAIGHT:
            if self.rotation in [0, 2]:
                pygame.draw.rect(surface, color, (cx - 10, y + padding, 20, inner_size))
            else:
                pygame.draw.rect(surface, color, (x + padding, cy - 10, inner_size, 20))

        elif self.type == CORNER:
            corners = {
                0: [(x + padding, y + padding), (cx, y + padding), (cx, cy), (x + padding, cy)],
                1: [(cx, y + padding), (x + size - padding, y + padding), (x + size - padding, cy), (cx, cy)],
                2: [(cx, cy), (x + size - padding, cy), (x + size - padding, y + size - padding), (cx, y + size - padding)],
                3: [(x + padding, cy), (cx, cy), (cx, y + size - padding), (x + padding, y + size - padding)]
            }
            pygame.draw.polygon(surface, color, corners[self.rotation])
            # 画直线部分
            if self.rotation in [0, 3]:
                pygame.draw.rect(surface, color, (x + padding, cy - 10, 20, cy - y - padding))
            if self.rotation in [0, 1]:
                pygame.draw.rect(surface, color, (cx - 10, y + padding, 20, cx - y - padding))
            if self.rotation in [1, 2]:
                pygame.draw.rect(surface, color, (cx - 10, cy - 10, cx - x - padding + 10, 20))
            if self.rotation in [2, 3]:
                pygame.draw.rect(surface, color, (x + padding, cy - 10, cx - x - padding + 10, 20))

        elif self.type == CROSS:
            pygame.draw.rect(surface, color, (cx - 10, y + padding, 20, inner_size))
            pygame.draw.rect(surface, color, (x + padding, cy - 10, inner_size, 20))
            pygame.draw.circle(surface, color, (cx, cy), 15)

        elif self.type == T_SHAPE:
            pygame.draw.rect(surface, color, (x + padding, cy - 10, inner_size, 20))
            if self.rotation == 0:
                pygame.draw.rect(surface, color, (cx - 10, y + padding, 20, cy - y - padding + 10))
            elif self.rotation == 1:
                pygame.draw.rect(surface, color, (cx - 10, cy - 10, cx - x - padding + 10, 20))
            elif self.rotation == 2:
                pygame.draw.rect(surface, color, (cx - 10, cy - 10, 20, cy - y - padding + 10))
            elif self.rotation == 3:
                pygame.draw.rect(surface, color, (x + padding, cy - 10, cx - x - padding + 10, 20))

class CircuitPuzzle:
    def __init__(self, level):
        self.level = level
        self.grid_size = 5
        self.cell_size = 100
        self.grid = []
        self.sources = []
        self.targets = []
        self.solved = False
        self.generate_level()

    def generate_level(self):
        self.grid = [[CircuitComponent(EMPTY) for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        
        # 根据等级设定布局
        if self.level == 1:
            # 简单直线连接
            self.grid[2][0] = CircuitComponent(SOURCE)
            self.grid[2][0].source = True
            self.sources.append((2, 0))
            self.grid[2][1] = CircuitComponent(STRAIGHT, 1)
            self.grid[2][2] = CircuitComponent(STRAIGHT, 1)
            self.grid[2][3] = CircuitComponent(STRAIGHT, 1)
            self.grid[2][4] = CircuitComponent(TARGET)
            self.grid[2][4].target = True
            self.targets.append((2, 4))
        elif self.level == 2:
            # 一个转角
            self.grid[0][0] = CircuitComponent(SOURCE)
            self.grid[0][0].source = True
            self.sources.append((0, 0))
            self.grid[0][1] = CircuitComponent(STRAIGHT, 1)
            self.grid[0][2] = CircuitComponent(CORNER, 0)
            self.grid[1][2] = CircuitComponent(STRAIGHT, 0)
            self.grid[2][2] = CircuitComponent(TARGET)
            self.grid[2][2].target = True
            self.targets.append((2, 2))
        elif self.level == 3:
            # T型连接
            self.grid[2][0] = CircuitComponent(SOURCE)
            self.grid[2][0].source = True
            self.sources.append((2, 0))
            self.grid[2][1] = CircuitComponent(STRAIGHT, 1)
            self.grid[2][2] = CircuitComponent(T_SHAPE, 0)
            self.grid[1][2] = CircuitComponent(STRAIGHT, 0)
            self.grid[0][2] = CircuitComponent(TARGET)
            self.grid[0][2].target = True
            self.targets.append((0, 2))
            self.grid[2][3] = CircuitComponent(STRAIGHT, 1)
            self.grid[2][4] = CircuitComponent(TARGET)
            self.grid[2][4].target = True
            self.targets.append((2, 4))
        elif self.level == 4:
            # 交叉
            self.grid[0][2] = CircuitComponent(SOURCE)
            self.grid[0][2].source = True
            self.sources.append((0, 2))
            self.grid[1][2] = CircuitComponent(STRAIGHT, 0)
            self.grid[2][2] = CircuitComponent(CROSS, 0)
            self.grid[3][2] = CircuitComponent(STRAIGHT, 0)
            self.grid[4][2] = CircuitComponent(TARGET)
            self.grid[4][2].target = True
            self.targets.append((4, 2))
            self.grid[2][0] = CircuitComponent(SOURCE)
            self.grid[2][0].source = True
            self.sources.append((2, 0))
            self.grid[2][1] = CircuitComponent(STRAIGHT, 1)
            self.grid[2][3] = CircuitComponent(STRAIGHT, 1)
            self.grid[2][4] = CircuitComponent(TARGET)
            self.grid[2][4].target = True
            self.targets.append((2, 4))
        elif self.level == 5:
            # 复杂迷宫
            self.grid[0][0] = CircuitComponent(SOURCE)
            self.grid[0][0].source = True
            self.sources.append((0, 0))
            self.grid[0][1] = CircuitComponent(STRAIGHT, 1)
            self.grid[0][2] = CircuitComponent(CORNER, 1)
            self.grid[1][2] = CircuitComponent(STRAIGHT, 0)
            self.grid[2][2] = CircuitComponent(CORNER, 2)
            self.grid[2][1] = CircuitComponent(STRAIGHT, 1)
            self.grid[2][0] = CircuitComponent(CORNER, 3)
            self.grid[3][0] = CircuitComponent(STRAIGHT, 0)
            self.grid[4][0] = CircuitComponent(CORNER, 0)
            self.grid[4][1] = CircuitComponent(STRAIGHT, 1)
            self.grid[4][2] = CircuitComponent(STRAIGHT, 1)
            self.grid[4][3] = CircuitComponent(CORNER, 1)
            self.grid[3][3] = CircuitComponent(STRAIGHT, 0)
            self.grid[2][3] = CircuitComponent(CORNER, 2)
            self.grid[2][4] = CircuitComponent(TARGET)
            self.grid[2][4].target = True
            self.targets.append((2, 4))
        
        # 打乱组件旋转
        self.shuffle_puzzle()
        self.check_circuit()

    def shuffle_puzzle(self):
        for row in self.grid:
            for cell in row:
                if cell.type != SOURCE and cell.type != TARGET and cell.type != EMPTY:
                    for _ in range(random.randint(0, 3)):
                        cell.rotate()

    def check_circuit(self):
        # 重置通电状态
        for row in self.grid:
            for cell in row:
                cell.powered = False

        # BFS从电源开始传播
        from collections import deque
        queue = deque()

        for (r, c) in self.sources:
            self.grid[r][c].powered = True
            queue.append((r, c))

        directions = [(-1, 0, UP, DOWN), (0, 1, RIGHT, LEFT), (1, 0, DOWN, UP), (0, -1, LEFT, RIGHT)]

        while queue:
            r, c = queue.popleft()
            current = self.grid[r][c]
            conn = current.get_connections()

            for dr, dc, dir_out, dir_in in directions:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.grid_size and 0 <= nc < self.grid_size:
                    neighbor = self.grid[nr][nc]
                    if dir_out in conn and not neighbor.powered:
                        neighbor_conn = neighbor.get_connections()
                        if dir_in in neighbor_conn:
                            neighbor.powered = True
                            queue.append((nr, nc))

        # 检查是否所有目标都通电
        self.solved = all(self.grid[r][c].powered for (r, c) in self.targets)

    def draw(self, surface, offset_x, offset_y):
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                x = offset_x + c * self.cell_size
                y = offset_y + r * self.cell_size
                self.grid[r][c].draw(surface, x, y, self.cell_size)
                pygame.draw.rect(surface, GRAY, (x, y, self.cell_size, self.cell_size), 2)

        # 完成提示
        if self.solved:
            text = TITLE_FONT.render("恭喜通关！点击继续", True, GREEN)
            surface.blit(text, (WIDTH//2 - text.get_width()//2, 650))

class Game:
    def __init__(self):
        self.current_level = 1
        self.max_level = 5
        self.puzzle = CircuitPuzzle(self.current_level)
        self.offset_x = (WIDTH - self.puzzle.grid_size * self.puzzle.cell_size) // 2
        self.offset_y = 100

    def next_level(self):
        if self.current_level < self.max_level:
            self.current_level += 1
            self.puzzle = CircuitPuzzle(self.current_level)

    def handle_click(self, pos):
        if self.puzzle.solved:
            self.next_level()
            return

        x, y = pos
        c = (x - self.offset_x) // self.puzzle.cell_size
        r = (y - self.offset_y) // self.puzzle.cell_size

        if 0 <= r < self.puzzle.grid_size and 0 <= c < self.puzzle.grid_size:
            cell = self.puzzle.grid[r][c]
            if cell.type != SOURCE and cell.type != TARGET and cell.type != EMPTY:
                cell.rotate()
                self.puzzle.check_circuit()

    def draw(self):
        SCREEN.fill(BLACK)

        # 标题
        title = TITLE_FONT.render(f"电路连接 - 第 {self.current_level} 关", True, WHITE)
        SCREEN.blit(title, (WIDTH//2 - title.get_width()//2, 30))

        # 说明
        hint = FONT.render("点击组件旋转，连接电源到目标！", True, LIGHT_GRAY)
        SCREEN.blit(hint, (WIDTH//2 - hint.get_width()//2, 70))

        # 绘制谜题
        self.puzzle.draw(SCREEN, self.offset_x, self.offset_y)

        # 图例
        legend_y = 620
        pygame.draw.circle(SCREEN, LIGHT_GREEN, (50, legend_y), 15)
        SCREEN.blit(FONT.render("电源", True, WHITE), (80, legend_y - 12))

        pygame.draw.circle(SCREEN, ORANGE, (180, legend_y), 15)
        SCREEN.blit(FONT.render("目标", True, WHITE), (210, legend_y - 12))

        SCREEN.blit(FONT.render("R: 重置关卡", True, WHITE), (350, legend_y - 12))

        pygame.display.flip()

    def run(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.puzzle = CircuitPuzzle(self.current_level)
                    elif event.key == pygame.K_ESCAPE:
                        running = False

            self.draw()
            clock.tick(30)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
