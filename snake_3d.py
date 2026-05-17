#!/usr/bin/env python3
"""
3D贪吃蛇游戏 - 伪3D透视效果
WASD控制方向，吃食物增长得分
"""

import pygame
import os
import sys
import random
import math

# 初始化pygame
pygame.init()



# 尝试使用中文字体
def get_chinese_font(size):
    """获取支持中文的字体"""
    font_names = [
        "C:/Windows/Fonts/simsun.ttc",  # 宋体
        "C:/Windows/Fonts/msyh.ttc",    # 微软雅黑
        "C:/Windows/Fonts/simhei.ttf",  # 黑体
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",  # Linux
        "/System/Library/Fonts/PingFang.ttc",  # macOS
    ]
    for font_name in font_names:
        if os.path.exists(font_name):
            try:
                return pygame.font.Font(font_name, size)
            except:
                continue
    return get_chinese_font(size)

# 屏幕设置
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("3D贪吃蛇 - WASD控制方向")

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 100, 0)
RED = (220, 50, 50)
YELLOW = (255, 220, 0)
BLUE = (50, 100, 220)
GRAY = (80, 80, 80)
DARK_GRAY = (40, 40, 40)
LIGHT_BLUE = (100, 180, 255)

# 3D网格参数
GRID_SIZE = 15  # 网格大小 15x15
CELL = 30  # 单元格基础大小
PERSPECTIVE = 0.6  # 透视缩放系数（越远越小）

# 3D视角参数 - 俯视带透视
CAMERA_HEIGHT = 500  # 摄像机高度
FOCAL_LENGTH = 400   # 焦距

# 字体
font_large = pygame.font.SysFont("simhei", 48, bold=True)
font_medium = pygame.font.SysFont("simhei", 28)
font_small = pygame.font.SysFont("simhei", 20)


class Snake3D:
    """3D贪吃蛇游戏主类"""

    def __init__(self):
        self.state = "menu"  # menu, playing, gameover
        self.reset_game()

    def reset_game(self):
        """重置游戏状态"""
        # 蛇的初始位置（网格坐标）
        mid = GRID_SIZE // 2
        self.snake = [(mid, mid), (mid - 1, mid), (mid - 2, mid)]
        self.direction = (1, 0)  # 初始向右
        self.next_direction = (1, 0)
        self.score = 0
        self.food = self.spawn_food()
        self.speed = 150  # 毫秒/步
        self.last_move = pygame.time.get_ticks()
        self.eat_animation = 0  # 吃食物动画计时

    def spawn_food(self):
        """在空位置生成食物"""
        while True:
            pos = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))
            if pos not in self.snake:
                return pos

    def project_3d(self, gx, gy):
        """将网格坐标投影到屏幕坐标（伪3D透视）"""
        # 将网格中心作为原点
        cx = gx - GRID_SIZE / 2 + 0.5
        cy = gy - GRID_SIZE / 2 + 0.5

        # 透视投影 - 远处的格子更小
        # 使用简单的透视公式：screen_size = base_size * focal / (focal + depth)
        depth = cy * 8  # 深度（y方向越大越远）
        scale = FOCAL_LENGTH / (FOCAL_LENGTH + depth)

        # 屏幕坐标
        sx = WIDTH / 2 + cx * CELL * scale * 1.2
        sy = HEIGHT / 2 + 80 + cy * CELL * scale * 0.8  # 偏移使网格居中

        return sx, sy, scale

    def draw_3d_block(self, surface, gx, gy, color, height=1.0, is_head=False):
        """绘制3D方块"""
        sx, sy, scale = self.project_3d(gx, gy)
        size = CELL * scale * 0.45

        if size < 1:
            return

        # 方块高度
        h = size * height * 0.6

        # 顶面颜色（亮）
        top_color = tuple(min(255, c + 60) for c in color)
        # 右面颜色（中）
        right_color = tuple(max(0, c - 30) for c in color)
        # 前面颜色（暗）
        front_color = tuple(max(0, c - 60) for c in color)

        # 绘制前面（暗面）
        front_points = [
            (sx - size, sy),
            (sx + size, sy),
            (sx + size, sy + h),
            (sx - size, sy + h)
        ]
        pygame.draw.polygon(surface, front_color, front_points)
        pygame.draw.polygon(surface, BLACK, front_points, 1)

        # 绘制右面
        right_points = [
            (sx + size, sy),
            (sx + size * 1.3, sy - h * 0.5),
            (sx + size * 1.3, sy + h * 0.5),
            (sx + size, sy + h)
        ]
        pygame.draw.polygon(surface, right_color, right_points)
        pygame.draw.polygon(surface, BLACK, right_points, 1)

        # 绘制顶面（亮面）
        top_points = [
            (sx - size, sy),
            (sx + size, sy),
            (sx + size * 1.3, sy - h * 0.5),
            (sx - size * 0.7, sy - h * 0.5)
        ]
        pygame.draw.polygon(surface, top_color, top_points)
        pygame.draw.polygon(surface, BLACK, top_points, 1)

        # 蛇头绘制眼睛
        if is_head and size > 5:
            eye_size = max(2, size * 0.2)
            # 根据方向确定眼睛位置
            dx, dy = self.direction
            ex1 = sx + dx * size * 0.3 - dy * size * 0.3
            ey1 = sy + dy * size * 0.1 + dx * size * 0.1
            ex2 = sx + dx * size * 0.3 + dy * size * 0.3
            ey2 = sy + dy * size * 0.1 - dx * size * 0.1
            pygame.draw.circle(surface, WHITE, (int(ex1), int(ey1)), int(eye_size))
            pygame.draw.circle(surface, WHITE, (int(ex2), int(ey2)), int(eye_size))
            pygame.draw.circle(surface, BLACK, (int(ex1 + dx * 1), int(ey1)), int(eye_size * 0.5))
            pygame.draw.circle(surface, BLACK, (int(ex2 + dx * 1), int(ey2)), int(eye_size * 0.5))

    def draw_food(self, surface):
        """绘制食物（3D球体效果）"""
        fx, fy = self.food
        sx, sy, scale = self.project_3d(fx, fy)
        size = CELL * scale * 0.4

        if size < 1:
            return

        # 动画效果 - 食物上下浮动
        bob = math.sin(pygame.time.get_ticks() * 0.005) * size * 0.3

        # 绘制阴影
        shadow_points = [
            (sx - size, sy + size * 0.5),
            (sx + size, sy + size * 0.5),
            (sx + size * 1.2, sy + size * 0.3),
            (sx - size * 0.8, sy + size * 0.3)
        ]
        pygame.draw.polygon(surface, (30, 30, 30), shadow_points)

        # 绘制球体（用多层圆形模拟）
        for i in range(int(size), 0, -1):
            ratio = i / size
            r = int(220 * ratio + 35)
            g = int(50 * ratio)
            b = int(50 * ratio)
            pygame.draw.circle(surface, (r, g, b), (int(sx), int(sy - size * 0.5 + bob)), i)

        # 高光
        highlight_size = max(1, int(size * 0.3))
        pygame.draw.circle(surface, (255, 200, 200),
                           (int(sx - size * 0.2), int(sy - size * 0.7 + bob)), highlight_size)

    def draw_grid(self, surface):
        """绘制3D网格地面"""
        # 绘制网格线
        for i in range(GRID_SIZE + 1):
            # 横线
            points = []
            for j in range(GRID_SIZE + 1):
                sx, sy, _ = self.project_3d(j - 0.5, i - 0.5)
                points.append((sx, sy))
            if len(points) > 1:
                color = (40, 60, 40) if i % 2 == 0 else (30, 50, 30)
                pygame.draw.lines(surface, color, False, points, 1)

            # 纵线
            points = []
            for j in range(GRID_SIZE + 1):
                sx, sy, _ = self.project_3d(i - 0.5, j - 0.5)
                points.append((sx, sy))
            if len(points) > 1:
                color = (40, 60, 40) if i % 2 == 0 else (30, 50, 30)
                pygame.draw.lines(surface, color, False, points, 1)

        # 绘制网格方块（棋盘格）
        for gx in range(GRID_SIZE):
            for gy in range(GRID_SIZE):
                sx1, sy1, s1 = self.project_3d(gx, gy)
                sx2, sy2, s2 = self.project_3d(gx + 1, gy + 1)
                size = CELL * s1 * 0.45
                if (gx + gy) % 2 == 0:
                    color = (25, 45, 25)
                else:
                    color = (35, 55, 35)
                rect_points = [
                    (sx1 - size, sy1),
                    (sx2 + size * (s2 / s1 if s1 > 0 else 1), sy2),
                    (sx2 + size * (s2 / s1 if s1 > 0 else 1) * 1.3, sy2 - size * (s2 / s1 if s1 > 0 else 1) * 0.5),
                    (sx1 - size * 0.7, sy1 - size * 0.5)
                ]
                pygame.draw.polygon(surface, color, rect_points)

    def update(self):
        """更新游戏逻辑"""
        if self.state != "playing":
            return

        now = pygame.time.get_ticks()
        if now - self.last_move < self.speed:
            return
        self.last_move = now

        # 更新方向
        self.direction = self.next_direction

        # 计算新头部位置
        head = self.snake[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])

        # 检查碰撞 - 墙壁
        if (new_head[0] < 0 or new_head[0] >= GRID_SIZE or
                new_head[1] < 0 or new_head[1] >= GRID_SIZE):
            self.state = "gameover"
            return

        # 检查碰撞 - 自身
        if new_head in self.snake:
            self.state = "gameover"
            return

        # 移动蛇
        self.snake.insert(0, new_head)

        # 检查是否吃到食物
        if new_head == self.food:
            self.score += 10
            self.food = self.spawn_food()
            self.eat_animation = 10
            # 加速
            self.speed = max(60, self.speed - 2)
        else:
            self.snake.pop()

        if self.eat_animation > 0:
            self.eat_animation -= 1

    def handle_input(self, event):
        """处理输入"""
        if event.type == pygame.KEYDOWN:
            if self.state == "menu":
                if event.key == pygame.K_RETURN:
                    self.state = "playing"
                    self.reset_game()
            elif self.state == "playing":
                if event.key == pygame.K_w and self.direction != (0, 1):
                    self.next_direction = (0, -1)
                elif event.key == pygame.K_s and self.direction != (0, -1):
                    self.next_direction = (0, 1)
                elif event.key == pygame.K_a and self.direction != (1, 0):
                    self.next_direction = (-1, 0)
                elif event.key == pygame.K_d and self.direction != (-1, 0):
                    self.next_direction = (1, 0)
            elif self.state == "gameover":
                if event.key == pygame.K_RETURN:
                    self.state = "playing"
                    self.reset_game()
                elif event.key == pygame.K_ESCAPE:
                    self.state = "menu"

    def draw(self, surface):
        """绘制游戏画面"""
        surface.fill((15, 15, 25))

        if self.state == "menu":
            self.draw_menu(surface)
        elif self.state == "playing":
            self.draw_game(surface)
        elif self.state == "gameover":
            self.draw_game(surface)
            self.draw_gameover(surface)

    def draw_menu(self, surface):
        """绘制菜单"""
        # 标题
        title = font_large.render("3D 贪吃蛇", True, LIGHT_BLUE)
        surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 120))

        # 装饰线
        pygame.draw.line(surface, LIGHT_BLUE, (200, 180), (600, 180), 2)

        # 操作说明
        instructions = [
            "WASD - 控制蛇的移动方向",
            "吃食物增长得分，碰到墙壁或自身游戏结束",
            "速度会随着得分逐渐加快",
            "",
            "按 Enter 开始游戏"
        ]
        for i, text in enumerate(instructions):
            color = YELLOW if "Enter" in text else WHITE
            t = font_small.render(text, True, color)
            surface.blit(t, (WIDTH // 2 - t.get_width() // 2, 220 + i * 35))

        # 装饰性3D方块
        t = pygame.time.get_ticks() * 0.001
        for i in range(5):
            angle = t + i * 1.2
            x = WIDTH // 2 + math.cos(angle) * 150
            y = 450 + math.sin(angle) * 30
            size = 15 + math.sin(angle * 2) * 5
            color = [GREEN, BLUE, RED, YELLOW, LIGHT_BLUE][i]
            # 简单3D方块
            pygame.draw.rect(surface, color, (x - size, y - size, size * 2, size * 2))
            pygame.draw.rect(surface, tuple(min(255, c + 40) for c in color),
                             (x - size, y - size - 5, size * 2, size * 2))
            pygame.draw.rect(surface, tuple(max(0, c - 40) for c in color),
                             (x, y - size, size, size * 2))

    def draw_game(self, surface):
        """绘制游戏画面"""
        # 绘制网格
        self.draw_grid(surface)

        # 绘制边界高亮
        for i in range(GRID_SIZE):
            for j in [0, GRID_SIZE - 1]:
                sx, sy, scale = self.project_3d(i, j)
                size = CELL * scale * 0.45
                if size > 1:
                    pygame.draw.circle(surface, (80, 0, 0), (int(sx), int(sy)), max(1, int(size * 0.15)))
            for j in [0, GRID_SIZE - 1]:
                sx, sy, scale = self.project_3d(j, i)
                size = CELL * scale * 0.45
                if size > 1:
                    pygame.draw.circle(surface, (80, 0, 0), (int(sx), int(sy)), max(1, int(size * 0.15)))

        # 绘制食物
        self.draw_food(surface)

        # 绘制蛇（从尾到头，确保头在最上面）
        for i in range(len(self.snake) - 1, -1, -1):
            gx, gy = self.snake[i]
            # 颜色渐变：头部亮，尾部暗
            ratio = 1 - i / max(len(self.snake), 1)
            r = int(50 + 150 * ratio)
            g = int(180 + 75 * ratio)
            b = int(50 + 50 * ratio)
            color = (r, g, b)
            height = 0.8 + 0.4 * ratio  # 头部更高
            is_head = (i == 0)
            self.draw_3d_block(surface, gx, gy, color, height, is_head)

        # 绘制UI
        self.draw_ui(surface)

    def draw_ui(self, surface):
        """绘制用户界面"""
        # 半透明背景
        ui_bg = pygame.Surface((200, 80), pygame.SRCALPHA)
        ui_bg.fill((0, 0, 0, 150))
        surface.blit(ui_bg, (10, 10))

        # 分数
        score_text = font_medium.render(f"得分: {self.score}", True, YELLOW)
        surface.blit(score_text, (20, 15))

        # 蛇长度
        length_text = font_small.render(f"长度: {len(self.snake)}", True, WHITE)
        surface.blit(length_text, (20, 50))

        # 速度指示
        speed_ratio = (150 - self.speed) / 90
        speed_text = font_small.render(f"速度: {'█' * int(speed_ratio * 10)}{'░' * (10 - int(speed_ratio * 10))}", True, LIGHT_BLUE)
        surface.blit(speed_text, (WIDTH - 250, 15))

    def draw_gameover(self, surface):
        """绘制游戏结束画面"""
        # 半透明遮罩
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))

        # 游戏结束文字
        go_text = font_large.render("游戏结束!", True, RED)
        surface.blit(go_text, (WIDTH // 2 - go_text.get_width() // 2, 200))

        # 最终得分
        score_text = font_medium.render(f"最终得分: {self.score}", True, YELLOW)
        surface.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 280))

        # 提示
        hint1 = font_small.render("按 Enter 重新开始", True, WHITE)
        hint2 = font_small.render("按 ESC 返回菜单", True, WHITE)
        surface.blit(hint1, (WIDTH // 2 - hint1.get_width() // 2, 350))
        surface.blit(hint2, (WIDTH // 2 - hint2.get_width() // 2, 385))


def main():
    """主函数"""
    clock = pygame.time.Clock()
    game = Snake3D()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            game.handle_input(event)

        game.update()
        game.draw(screen)
        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
