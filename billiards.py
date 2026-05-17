#!/usr/bin/env python3
"""
桌球游戏 - 简化版8球台球
鼠标拖拽瞄准和控制力度，白色母球撞击彩色球进袋
"""

import pygame
import os
import sys
import math
import random

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
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("桌球游戏 - 鼠标拖拽瞄准击球")

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (200, 30, 30)
YELLOW = (230, 200, 0)
BLUE = (30, 60, 200)
GREEN = (0, 130, 60)
DARK_GREEN = (0, 80, 40)
BROWN = (100, 60, 20)
ORANGE = (230, 130, 0)
PURPLE = (100, 30, 150)
MAROON = (120, 20, 20)
GRAY = (150, 150, 150)
DARK_GRAY = (60, 60, 60)

# 球桌参数
TABLE_LEFT = 80
TABLE_TOP = 80
TABLE_WIDTH = 840
TABLE_HEIGHT = 440
TABLE_RIGHT = TABLE_LEFT + TABLE_WIDTH
TABLE_BOTTOM = TABLE_TOP + TABLE_HEIGHT

# 球的参数
BALL_RADIUS = 12
FRICTION = 0.985  # 摩擦力
MIN_SPEED = 0.1   # 最小速度阈值

# 袋口参数
POCKET_RADIUS = 22
POCKETS = [
    (TABLE_LEFT + 5, TABLE_TOP + 5),          # 左上
    (TABLE_LEFT + TABLE_WIDTH // 2, TABLE_TOP - 3),  # 中上
    (TABLE_RIGHT - 5, TABLE_TOP + 5),         # 右上
    (TABLE_LEFT + 5, TABLE_BOTTOM - 5),       # 左下
    (TABLE_LEFT + TABLE_WIDTH // 2, TABLE_BOTTOM + 3),  # 中下
    (TABLE_RIGHT - 5, TABLE_BOTTOM - 5),      # 右下
]

# 球的颜色（简化8球：1个白球 + 7个纯色 + 7个条纹 + 1个8号球）
BALL_COLORS = {
    0: WHITE,       # 母球
    1: YELLOW,      # 1号
    2: BLUE,        # 2号
    3: RED,         # 3号
    4: PURPLE,      # 4号
    5: ORANGE,      # 5号
    6: (0, 130, 0), # 6号 绿
    7: MAROON,      # 7号
    8: BLACK,       # 8号
    9: YELLOW,      # 9号 条纹
    10: BLUE,       # 10号 条纹
    11: RED,        # 11号 条纹
    12: PURPLE,     # 12号 条纹
    13: ORANGE,     # 13号 条纹
    14: (0, 130, 0),# 14号 条纹
    15: MAROON,     # 15号 条纹
}

# 字体
font_large = pygame.font.SysFont("simhei", 42, bold=True)
font_medium = pygame.font.SysFont("simhei", 24)
font_small = pygame.font.SysFont("simhei", 18)


class Ball:
    """台球类"""

    def __init__(self, x, y, number):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.number = number
        self.color = BALL_COLORS[number]
        self.striped = number >= 9  # 9-15号为条纹球
        self.pocketed = False
        self.radius = BALL_RADIUS

    def update(self):
        """更新球的位置"""
        if self.pocketed:
            return

        self.x += self.vx
        self.y += self.vy

        # 摩擦力
        self.vx *= FRICTION
        self.vy *= FRICTION

        # 速度过小则停止
        if abs(self.vx) < MIN_SPEED and abs(self.vy) < MIN_SPEED:
            self.vx = 0
            self.vy = 0

        # 碰撞边界
        if self.x - self.radius < TABLE_LEFT:
            self.x = TABLE_LEFT + self.radius
            self.vx = -self.vx * 0.8
        if self.x + self.radius > TABLE_RIGHT:
            self.x = TABLE_RIGHT - self.radius
            self.vx = -self.vx * 0.8
        if self.y - self.radius < TABLE_TOP:
            self.y = TABLE_TOP + self.radius
            self.vy = -self.vy * 0.8
        if self.y + self.radius > TABLE_BOTTOM:
            self.y = TABLE_BOTTOM - self.radius
            self.vy = -self.vy * 0.8

    def is_moving(self):
        """检查球是否在运动"""
        return abs(self.vx) > MIN_SPEED or abs(self.vy) > MIN_SPEED

    def draw(self, surface):
        """绘制球"""
        if self.pocketed:
            return

        x, y = int(self.x), int(self.y)
        r = self.radius

        # 阴影
        pygame.draw.circle(surface, (30, 60, 30), (x + 2, y + 2), r)

        if self.number == 0:
            # 母球 - 纯白
            pygame.draw.circle(surface, WHITE, (x, y), r)
        elif self.striped:
            # 条纹球 - 白底 + 彩色条纹
            pygame.draw.circle(surface, WHITE, (x, y), r)
            # 绘制条纹（中间彩色带）
            stripe_rect = pygame.Rect(x - r, y - r // 2, r * 2, r)
            pygame.draw.rect(surface, self.color, stripe_rect)
            # 用圆形裁剪
            # 重新画圆形边框
            pygame.draw.circle(surface, self.color, (x, y), r)
            # 画白色上下部分
            for angle in range(0, 360):
                rad = math.radians(angle)
                px = x + math.cos(rad) * r
                py = y + math.sin(rad) * r
                if py < y - r * 0.4 or py > y + r * 0.4:
                    pygame.draw.circle(surface, WHITE, (int(px), int(py)), 1)
        else:
            # 纯色球
            pygame.draw.circle(surface, self.color, (x, y), r)

        # 球号
        if self.number > 0:
            # 白色圆圈背景
            pygame.draw.circle(surface, WHITE, (x, y), r // 2 + 1)
            num_text = font_small.render(str(self.number), True, BLACK)
            surface.blit(num_text, (x - num_text.get_width() // 2, y - num_text.get_height() // 2))

        # 高光
        pygame.draw.circle(surface, (255, 255, 255, 180), (x - r // 3, y - r // 3), r // 4)

        # 边框
        pygame.draw.circle(surface, DARK_GRAY, (x, y), r, 1)


class BilliardsGame:
    """桌球游戏主类"""

    def __init__(self):
        self.state = "menu"  # menu, playing, aiming, moving, gameover
        self.balls = []
        self.cue_ball = None
        self.dragging = False
        self.drag_start = (0, 0)
        self.drag_end = (0, 0)
        self.power = 0
        self.max_power = 25
        self.message = ""
        self.message_timer = 0
        self.pocketed_balls = []
        self.shot_count = 0
        self.reset_game()

    def reset_game(self):
        """重置游戏"""
        self.balls = []
        self.pocketed_balls = []
        self.shot_count = 0
        self.message = ""
        self.message_timer = 0

        # 放置母球
        cue_x = TABLE_LEFT + TABLE_WIDTH * 0.25
        cue_y = TABLE_TOP + TABLE_HEIGHT * 0.5
        self.cue_ball = Ball(cue_x, cue_y, 0)
        self.balls.append(self.cue_ball)

        # 放置其他球（三角形排列）
        start_x = TABLE_LEFT + TABLE_WIDTH * 0.7
        start_y = TABLE_TOP + TABLE_HEIGHT * 0.5
        ball_numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        random.shuffle(ball_numbers)
        # 确保8号球在中间位置（第5个，即第3行中间）
        idx8 = ball_numbers.index(8)
        ball_numbers[idx8], ball_numbers[4] = ball_numbers[4], ball_numbers[idx8]

        spacing = BALL_RADIUS * 2.1
        idx = 0
        for row in range(5):
            for col in range(row + 1):
                if idx >= len(ball_numbers):
                    break
                bx = start_x + row * spacing * math.cos(math.radians(30))
                by = start_y + (col - row / 2) * spacing
                ball = Ball(bx, by, ball_numbers[idx])
                self.balls.append(ball)
                idx += 1

        self.state = "playing"

    def all_stopped(self):
        """检查所有球是否停止"""
        return all(not b.is_moving() for b in self.balls if not b.pocketed)

    def check_pockets(self):
        """检查是否有球进袋"""
        for ball in self.balls:
            if ball.pocketed:
                continue
            for pocket in POCKETS:
                dist = math.sqrt((ball.x - pocket[0]) ** 2 + (ball.y - pocket[1]) ** 2)
                if dist < POCKET_RADIUS:
                    ball.pocketed = True
                    ball.vx = 0
                    ball.vy = 0
                    if ball.number == 0:
                        # 母球进袋 - 犯规
                        self.message = "犯规！母球进袋"
                        self.message_timer = 120
                        # 重置母球位置
                        ball.pocketed = False
                        ball.x = TABLE_LEFT + TABLE_WIDTH * 0.25
                        ball.y = TABLE_TOP + TABLE_HEIGHT * 0.5
                        ball.vx = 0
                        ball.vy = 0
                        # 确保不与其他球重叠
                        for other in self.balls:
                            if other != ball and not other.pocketed:
                                dist = math.sqrt((ball.x - other.x) ** 2 + (ball.y - other.y) ** 2)
                                if dist < BALL_RADIUS * 2.5:
                                    ball.y += BALL_RADIUS * 3
                    else:
                        self.pocketed_balls.append(ball.number)
                        if ball.number == 8:
                            # 8号球进袋 - 检查是否赢了
                            remaining = [b for b in self.balls if not b.pocketed and b.number not in (0, 8)]
                            if len(remaining) == 0:
                                self.message = "恭喜！你赢了！"
                                self.state = "gameover"
                            else:
                                self.message = "8号球进袋！游戏结束"
                                self.state = "gameover"
                        else:
                            self.message = f"{ball.number}号球进袋！"
                            self.message_timer = 60
                    break

    def check_ball_collisions(self):
        """检查球与球之间的碰撞"""
        active_balls = [b for b in self.balls if not b.pocketed]
        for i in range(len(active_balls)):
            for j in range(i + 1, len(active_balls)):
                b1 = active_balls[i]
                b2 = active_balls[j]
                dx = b2.x - b1.x
                dy = b2.y - b1.y
                dist = math.sqrt(dx * dx + dy * dy)
                min_dist = b1.radius + b2.radius

                if dist < min_dist and dist > 0:
                    # 碰撞法线
                    nx = dx / dist
                    ny = dy / dist

                    # 分离球
                    overlap = min_dist - dist
                    b1.x -= nx * overlap / 2
                    b1.y -= ny * overlap / 2
                    b2.x += nx * overlap / 2
                    b2.y += ny * overlap / 2

                    # 弹性碰撞
                    dvx = b1.vx - b2.vx
                    dvy = b1.vy - b2.vy
                    dot = dvx * nx + dvy * ny

                    if dot > 0:
                        b1.vx -= dot * nx * 0.95
                        b1.vy -= dot * ny * 0.95
                        b2.vx += dot * nx * 0.95
                        b2.vy += dot * ny * 0.95

    def shoot(self, power, angle):
        """击球"""
        if self.cue_ball.pocketed:
            return
        self.cue_ball.vx = math.cos(angle) * power
        self.cue_ball.vy = math.sin(angle) * power
        self.shot_count += 1
        self.state = "moving"

    def handle_input(self, event):
        """处理输入"""
        if event.type == pygame.KEYDOWN:
            if self.state == "menu":
                if event.key == pygame.K_RETURN:
                    self.reset_game()
            elif self.state == "gameover":
                if event.key == pygame.K_RETURN:
                    self.reset_game()
                elif event.key == pygame.K_ESCAPE:
                    self.state = "menu"
            elif self.state == "playing":
                if event.key == pygame.K_r:
                    self.reset_game()

        if self.state == "playing":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # 检查是否点击在母球附近
                mx, my = event.pos
                dist = math.sqrt((mx - self.cue_ball.x) ** 2 + (my - self.cue_ball.y) ** 2)
                if dist < BALL_RADIUS * 3:
                    self.dragging = True
                    self.drag_start = (mx, my)
                    self.drag_end = (mx, my)

            elif event.type == pygame.MOUSEMOTION and self.dragging:
                self.drag_end = event.pos
                # 计算力度
                dx = self.drag_start[0] - self.drag_end[0]
                dy = self.drag_start[1] - self.drag_end[1]
                self.power = min(math.sqrt(dx * dx + dy * dy) / 15, self.max_power)

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.dragging:
                self.dragging = False
                if self.power > 0.5:
                    dx = self.drag_start[0] - self.drag_end[0]
                    dy = self.drag_start[1] - self.drag_end[1]
                    angle = math.atan2(dy, dx)
                    self.shoot(self.power, angle)
                self.power = 0

    def update(self):
        """更新游戏逻辑"""
        if self.message_timer > 0:
            self.message_timer -= 1

        if self.state == "moving":
            for ball in self.balls:
                ball.update()
            self.check_ball_collisions()
            self.check_pockets()

            if self.all_stopped():
                self.state = "playing"

    def draw(self, surface):
        """绘制游戏画面"""
        surface.fill((40, 30, 20))

        if self.state == "menu":
            self.draw_menu(surface)
        else:
            self.draw_game(surface)
            if self.state == "gameover":
                self.draw_gameover(surface)

    def draw_menu(self, surface):
        """绘制菜单"""
        title = font_large.render("桌球游戏", True, WHITE)
        surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

        pygame.draw.line(surface, YELLOW, (300, 155), (700, 155), 2)

        instructions = [
            "在母球附近按住鼠标左键拖拽瞄准",
            "拖拽距离越远，击球力度越大",
            "松开鼠标发射母球",
            "将所有彩色球击入袋口即可获胜",
            "注意：母球进袋会犯规并重置位置",
            "按 R 键重新开始",
            "",
            "按 Enter 开始游戏"
        ]
        for i, text in enumerate(instructions):
            color = YELLOW if "Enter" in text else WHITE
            t = font_small.render(text, True, color)
            surface.blit(t, (WIDTH // 2 - t.get_width() // 2, 190 + i * 32))

    def draw_game(self, surface):
        """绘制游戏画面"""
        # 球桌边框
        border = 20
        pygame.draw.rect(surface, BROWN,
                         (TABLE_LEFT - border, TABLE_TOP - border,
                          TABLE_WIDTH + border * 2, TABLE_HEIGHT + border * 2),
                         border_radius=10)
        # 内边框装饰
        pygame.draw.rect(surface, (120, 70, 30),
                         (TABLE_LEFT - border + 3, TABLE_TOP - border + 3,
                          TABLE_WIDTH + border * 2 - 6, TABLE_HEIGHT + border * 2 - 6),
                         border_radius=8)

        # 球桌表面
        pygame.draw.rect(surface, GREEN, (TABLE_LEFT, TABLE_TOP, TABLE_WIDTH, TABLE_HEIGHT))

        # 球桌布纹理（细微线条）
        for i in range(TABLE_LEFT, TABLE_RIGHT, 20):
            pygame.draw.line(surface, DARK_GREEN, (i, TABLE_TOP), (i, TABLE_BOTTOM), 1)

        # 开球线
        line_x = int(TABLE_LEFT + TABLE_WIDTH * 0.25)
        pygame.draw.line(surface, (0, 100, 50), (line_x, TABLE_TOP), (line_x, TABLE_BOTTOM), 1)

        # 袋口
        for pocket in POCKETS:
            pygame.draw.circle(surface, (20, 20, 20), (int(pocket[0]), int(pocket[1])), POCKET_RADIUS)
            pygame.draw.circle(surface, (10, 10, 10), (int(pocket[0]), int(pocket[1])), POCKET_RADIUS - 3)

        # 瞄准线
        if self.dragging and self.power > 0.5:
            dx = self.drag_start[0] - self.drag_end[0]
            dy = self.drag_start[1] - self.drag_end[1]
            angle = math.atan2(dy, dx)

            # 瞄准虚线
            for i in range(0, 300, 8):
                px = self.cue_ball.x + math.cos(angle) * i
                py = self.cue_ball.y + math.sin(angle) * i
                if TABLE_LEFT < px < TABLE_RIGHT and TABLE_TOP < py < TABLE_BOTTOM:
                    alpha = max(50, 255 - i)
                    pygame.draw.circle(surface, (255, 255, 255), (int(px), int(py)), 1)

            # 球杆
            cue_length = 150
            cue_start_x = self.cue_ball.x - math.cos(angle) * (BALL_RADIUS + 5 + self.power * 3)
            cue_start_y = self.cue_ball.y - math.sin(angle) * (BALL_RADIUS + 5 + self.power * 3)
            cue_end_x = cue_start_x - math.cos(angle) * cue_length
            cue_end_y = cue_start_y - math.sin(angle) * cue_length
            pygame.draw.line(surface, (180, 140, 80),
                             (int(cue_start_x), int(cue_start_y)),
                             (int(cue_end_x), int(cue_end_y)), 4)
            pygame.draw.line(surface, (220, 200, 150),
                             (int(cue_start_x), int(cue_start_y)),
                             (int(cue_start_x - math.cos(angle) * 20),
                              int(cue_start_y - math.sin(angle) * 20)), 5)

        # 绘制球
        for ball in self.balls:
            ball.draw(surface)

        # 力度条
        if self.dragging:
            self.draw_power_bar(surface)

        # 已进袋的球
        self.draw_pocketed(surface)

        # 消息
        if self.message_timer > 0 and self.message:
            msg_text = font_medium.render(self.message, True, YELLOW)
            msg_bg = pygame.Surface((msg_text.get_width() + 20, msg_text.get_height() + 10), pygame.SRCALPHA)
            msg_bg.fill((0, 0, 0, 180))
            surface.blit(msg_bg, (WIDTH // 2 - msg_text.get_width() // 2 - 10, TABLE_BOTTOM + 25))
            surface.blit(msg_text, (WIDTH // 2 - msg_text.get_width() // 2, TABLE_BOTTOM + 30))

        # 操作提示
        hint = font_small.render("在母球上拖拽鼠标瞄准击球 | R 重新开始", True, (180, 180, 180))
        surface.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 25))

        # 击球次数
        shot_text = font_small.render(f"击球次数: {self.shot_count}", True, WHITE)
        surface.blit(shot_text, (TABLE_RIGHT - 120, TABLE_TOP - 35))

    def draw_power_bar(self, surface):
        """绘制力度条"""
        bar_x = TABLE_RIGHT + 30
        bar_y = TABLE_TOP
        bar_width = 20
        bar_height = TABLE_HEIGHT

        # 背景
        pygame.draw.rect(surface, DARK_GRAY, (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)

        # 力度填充
        ratio = self.power / self.max_power
        fill_height = int(bar_height * ratio)

        # 颜色渐变（绿->黄->红）
        if ratio < 0.5:
            color = (int(255 * ratio * 2), 255, 0)
        else:
            color = (255, int(255 * (1 - ratio) * 2), 0)

        pygame.draw.rect(surface, color,
                         (bar_x + 2, bar_y + bar_height - fill_height,
                          bar_width - 4, fill_height))

        # 力度文字
        power_text = font_small.render(f"{int(ratio * 100)}%", True, WHITE)
        surface.blit(power_text, (bar_x - 5, bar_y + bar_height + 5))

    def draw_pocketed(self, surface):
        """绘制已进袋的球"""
        if not self.pocketed_balls:
            return

        label = font_small.render("已进袋:", True, WHITE)
        surface.blit(label, (TABLE_LEFT, TABLE_TOP - 35))

        for i, num in enumerate(self.pocketed_balls):
            x = TABLE_LEFT + 70 + i * 28
            y = TABLE_TOP - 25
            color = BALL_COLORS[num]
            pygame.draw.circle(surface, color, (x, y), 10)
            if num >= 9:
                pygame.draw.circle(surface, WHITE, (x, y), 10, 3)
            pygame.draw.circle(surface, WHITE, (x, y), 5)
            num_t = font_small.render(str(num), True, BLACK)
            surface.blit(num_t, (x - num_t.get_width() // 2, y - num_t.get_height() // 2))

    def draw_gameover(self, surface):
        """绘制游戏结束"""
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))

        go_text = font_large.render("游戏结束", True, WHITE)
        surface.blit(go_text, (WIDTH // 2 - go_text.get_width() // 2, 200))

        result = font_medium.render(self.message, True, YELLOW)
        surface.blit(result, (WIDTH // 2 - result.get_width() // 2, 270))

        shots = font_small.render(f"总击球次数: {self.shot_count}", True, WHITE)
        surface.blit(shots, (WIDTH // 2 - shots.get_width() // 2, 320))

        hint = font_small.render("按 Enter 重新开始 | ESC 返回菜单", True, GRAY)
        surface.blit(hint, (WIDTH // 2 - hint.get_width() // 2, 370))


def main():
    """主函数"""
    clock = pygame.time.Clock()
    game = BilliardsGame()

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
