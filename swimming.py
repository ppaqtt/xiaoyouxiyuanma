#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
游泳比赛游戏 - Swimming Competition Game
包含多种泳姿和比赛模式
作者: Sports Game Developer
"""

import pygame
import random
import math
import sys

# 初始化pygame
pygame.init()

# 游戏设置
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
FPS = 60

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 100, 200)
GOLD = (255, 215, 0)
GRAY = (128, 128, 128)
LIGHT_BLUE = (173, 216, 230)
DARK_BLUE = (0, 50, 150)
POOL_BLUE = (0, 150, 200)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
GREEN = (0, 180, 0)
PURPLE = (128, 0, 128)
YELLOW = (255, 255, 0)

# 设置显示窗口
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("游泳比赛 - Swimming Championship")
clock = pygame.time.Clock()

# 字体设置
font_large = pygame.font.Font(None, 72)
font_medium = pygame.font.Font(None, 48)
font_small = pygame.font.Font(None, 36)
font_tiny = pygame.font.Font(None, 24)


class Swimmer:
    """游泳选手类"""

    def __init__(self, x, y, color, name, is_player=False):
        self.x = x
        self.y = y
        self.color = color
        self.name = name
        self.is_player = is_player
        self.speed = 0
        self.max_speed = 5
        self.lane = 0
        self.finished = False
        self.finish_time = 0
        self.stroke_count = 0
        self.current_stroke = 0

    def update(self, dt, is_stroking, stroke_speed=1.0):
        """更新选手位置"""
        if not self.finished:
            if is_stroking or self.is_player:
                # 划水动作
                self.current_stroke += stroke_speed * dt * 10

                # 根据划水频率更新速度
                if self.is_player:
                    if is_stroking:
                        self.speed = min(self.speed + 0.3, self.max_speed)
                    else:
                        self.speed = max(self.speed - 0.1, 1)
                else:
                    # AI速度控制
                    self.speed = self.max_speed * (0.7 + random.random() * 0.4)

            self.x += self.speed

            # 检查是否到达终点
            if self.x >= SCREEN_WIDTH - 150:
                self.finished = True
                self.finish_time = pygame.time.get_ticks()


class SwimmingGame:
    """游泳比赛主游戏类"""

    def __init__(self):
        self.state = "menu"  # menu, select_mode, racing, result
        self.current_mode = None
        self.modes = {
            "freestyle": {"name": "自由泳", "laps": 4, "speed": 1.0, "description": "速度最快的泳姿"},
            "breaststroke": {"name": "蛙泳", "laps": 4, "speed": 0.7, "description": "节奏稳定的泳姿"},
            "butterfly": {"name": "蝶泳", "laps": 4, "speed": 0.9, "description": "最具观赏性的泳姿"},
            "backstroke": {"name": "仰泳", "laps": 4, "speed": 0.8, "description": "背朝水面的泳姿"}
        }
        self.swimmers = []
        self.player = None
        self.game_start_time = 0
        self.player_time = 0
        self.rankings = []
        self.race_distance = 0

    def draw_text(self, text, x, y, size="medium", color=BLACK):
        """绘制文本"""
        if size == "large":
            font = font_large
        elif size == "medium":
            font = font_small
        elif size == "small":
            font = font_tiny
        else:
            font = font_small

        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(x, y))
        screen.blit(text_surface, text_rect)

    def draw_button(self, text, x, y, width, height, color, hover_color=None):
        """绘制按钮"""
        mouse_pos = pygame.mouse.get_pos()
        button_rect = pygame.Rect(x, y, width, height)

        if button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, hover_color or color, button_rect)
        else:
            pygame.draw.rect(screen, color, button_rect)

        pygame.draw.rect(screen, BLACK, button_rect, 2)
        self.draw_text(text, x + width // 2, y + height // 2, "small", WHITE)
        return button_rect

    def draw_menu(self):
        """绘制主菜单"""
        # 绘制泳池背景
        screen.fill(DARK_BLUE)

        # 绘制泳池底部
        for i in range(5):
            color = POOL_BLUE if i % 2 == 0 else DARK_BLUE
            pygame.draw.rect(screen, color, (0, 150 + i * 120, SCREEN_WIDTH, 120))

        # 绘制泳池边线
        pygame.draw.rect(screen, WHITE, (0, 150, SCREEN_WIDTH, 5))
        pygame.draw.rect(screen, WHITE, (0, SCREEN_HEIGHT - 150, SCREEN_WIDTH, 5))

        # 绘制泳道线
        for i in range(1, 5):
            pygame.draw.line(screen, WHITE, (0, 150 + i * 100), (SCREEN_WIDTH, 150 + i * 100), 2)

        # 绘制标题
        self.draw_text("游泳锦标赛", SCREEN_WIDTH // 2, 60, "large", WHITE)

        # 绘制说明
        self.draw_text("选择泳姿开始比赛!", SCREEN_WIDTH // 2, 110, "medium", CYAN)

        # 绘制开始按钮
        self.start_button = self.draw_button("选择泳姿", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 100,
                                            200, 60, GREEN)

    def draw_mode_select(self):
        """绘制泳姿选择界面"""
        screen.fill(DARK_BLUE)

        # 绘制标题
        self.draw_text("选择泳姿", SCREEN_WIDTH // 2, 50, "large", WHITE)

        # 绘制各个泳姿选项
        y_start = 150
        mode_list = list(self.modes.items())
        colors = [GREEN, ORANGE, PURPLE, CYAN]

        self.mode_buttons = []
        for i, (key, mode) in enumerate(mode_list):
            y = y_start + i * 130

            # 绘制模式卡片
            card_rect = pygame.Rect(100, y, SCREEN_WIDTH - 200, 110)
            pygame.draw.rect(screen, colors[i], card_rect)
            pygame.draw.rect(screen, WHITE, card_rect, 3)

            # 绘制模式名称
            self.draw_text(mode["name"], 200, y + 35, "medium", WHITE)
            self.draw_text(f"圈数: {mode['laps']}", 200, y + 70, "small", WHITE)
            self.draw_text(mode["description"], 400, y + 50, "small", WHITE)

            # 绘制速度条
            speed_width = mode["speed"] * 200
            pygame.draw.rect(screen, WHITE, (600, y + 30, 200, 30), 2)
            pygame.draw.rect(screen, YELLOW, (600, y + 30, int(speed_width), 30))
            self.draw_text(f"速度: {mode['speed']:.1f}x", 700, y + 75, "tiny", WHITE)

            self.mode_buttons.append(card_rect)

        # 返回按钮
        self.back_button = self.draw_button("返回", 50, SCREEN_HEIGHT - 80, 100, 50, GRAY)

    def draw_race(self):
        """绘制比赛界面"""
        # 绘制泳池
        screen.fill(POOL_BLUE)

        # 绘制泳池底部纹理
        for i in range(20):
            for j in range(7):
                if (i + j) % 2 == 0:
                    pygame.draw.rect(screen, (0, 180, 220), (i * 60, 100 + j * 80, 60, 80))

        # 绘制泳道
        for i in range(6):
            pygame.draw.line(screen, WHITE, (0, 100 + i * 100), (SCREEN_WIDTH, 100 + i * 100), 2)

        # 绘制起点
        pygame.draw.rect(screen, RED, (50, 100, 10, 500))
        for i in range(5):
            pygame.draw.rect(screen, WHITE, (50, 100 + i * 100, 10, 50))

        # 绘制终点
        pygame.draw.rect(screen, BLACK, (SCREEN_WIDTH - 60, 100, 10, 500))
        for i in range(5):
            pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH - 55, 100 + i * 100, 5, 50))

        # 绘制圈数标记
        laps = self.modes[self.current_mode]["laps"]
        for i in range(laps + 1):
            x = 50 + (SCREEN_WIDTH - 110) * i / laps
            pygame.draw.line(screen, YELLOW, (x, 100), (x, 600), 2)
            self.draw_text(f"第{i}圈", x, 85, "tiny", WHITE)

        # 绘制泳姿指示
        mode_name = self.modes[self.current_mode]["name"]
        self.draw_text(f"泳姿: {mode_name}", 100, 30, "medium", WHITE)

        # 绘制计时器
        if self.game_start_time > 0:
            elapsed = (pygame.time.get_ticks() - self.game_start_time) / 1000
            self.draw_text(f"时间: {elapsed:.2f}秒", SCREEN_WIDTH // 2, 30, "medium", WHITE)

        # 绘制选手
        for swimmer in self.swimmers:
            self.draw_swimmer(swimmer)

        # 绘制排名
        self.draw_rankings()

        # 绘制提示
        self.draw_text("按住空格键划水!", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30, "small", WHITE)

    def draw_swimmer(self, swimmer):
        """绘制单个游泳选手"""
        x = int(swimmer.x)
        y = int(swimmer.y)

        # 绘制游泳者身体
        pygame.draw.ellipse(screen, swimmer.color, (x - 15, y - 10, 30, 20))

        # 绘制头部
        pygame.draw.circle(screen, swimmer.color, (x + 15, y), 10)

        # 绘制手臂划水效果
        stroke_offset = int(math.sin(swimmer.current_stroke) * 10)
        pygame.draw.line(screen, swimmer.color, (x, y), (x - 20, y + stroke_offset), 3)
        pygame.draw.line(screen, swimmer.color, (x, y), (x - 20, y - stroke_offset), 3)

        # 绘制腿部打水效果
        leg_offset = int(math.sin(swimmer.current_stroke * 2) * 5)
        pygame.draw.line(screen, swimmer.color, (x - 15, y), (x - 25, y + leg_offset), 3)

        # 绘制名字
        self.draw_text(swimmer.name, x, y - 25, "tiny", WHITE)

        # 绘制完成标记
        if swimmer.finished:
            pygame.draw.circle(screen, GOLD, (x, y), 15)
            self.draw_text(f"{swimmer.finish_time/1000:.1f}s", x, y, "tiny", BLACK)

    def draw_rankings(self):
        """绘制实时排名"""
        # 获取未完成选手的排名
        active_swimmers = [s for s in self.swimmers if not s.finished]
        active_swimmers.sort(key=lambda s: s.x, reverse=True)

        # 绘制排名面板
        pygame.draw.rect(screen, (0, 0, 0, 128), (SCREEN_WIDTH - 180, 620, 170, 70))
        pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH - 180, 620, 170, 70), 2)

        self.draw_text("排名", SCREEN_WIDTH - 95, 635, "small", WHITE)

        for i, swimmer in enumerate(active_swimmers[:3]):
            color = GOLD if i == 0 else WHITE if i == 1 else ORANGE
            self.draw_text(f"{i + 1}. {swimmer.name}", SCREEN_WIDTH - 170, 660 + i * 15,
                          "tiny", color)

    def draw_result(self):
        """绘制比赛结果"""
        screen.fill(DARK_BLUE)

        # 绘制标题
        self.draw_text("比赛结果", SCREEN_WIDTH // 2, 50, "large", GOLD)

        # 排序选手
        sorted_swimmers = sorted(self.swimmers, key=lambda s: s.finish_time)

        # 绘制排行榜
        y = 150
        medals = [GOLD, (192, 192, 192), (205, 127, 50)]  # 金银铜

        for i, swimmer in enumerate(sorted_swimmers):
            # 绘制排名背景
            color = medals[i] if i < 3 else GRAY
            pygame.draw.rect(screen, color, (100, y, SCREEN_WIDTH - 200, 80))
            pygame.draw.rect(screen, WHITE, (100, y, SCREEN_WIDTH - 200, 80), 2)

            # 绘制排名
            rank_text = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"{i + 1}"
            self.draw_text(rank_text, 150, y + 40, "medium", BLACK)

            # 绘制名字
            name_color = RED if swimmer.is_player else WHITE
            self.draw_text(swimmer.name, 300, y + 40, "medium", name_color)

            # 绘制时间
            time_text = f"{swimmer.finish_time / 1000:.2f}秒"
            self.draw_text(time_text, 600, y + 40, "medium", BLACK)

            # 绘制泳姿
            if swimmer.is_player:
                self.draw_text("★ 你 ★", 850, y + 40, "medium", RED)

            y += 90

        # 绘制玩家成绩特别提示
        player = [s for s in self.swimmers if s.is_player][0]
        player_rank = sorted_swimmers.index(player) + 1

        if player_rank == 1:
            msg = "恭喜你获得冠军!"
            color = GOLD
        elif player_rank == 2:
            msg = "不错，获得第二名!"
            color = (192, 192, 192)
        elif player_rank == 3:
            msg = "获得第三名，继续加油!"
            color = (205, 127, 50)
        else:
            msg = f"第{player_rank}名，继续努力!"
            color = WHITE

        self.draw_text(msg, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 120, "medium", color)

        # 返回按钮
        self.back_button = self.draw_button("返回主菜单", SCREEN_WIDTH // 2 - 100,
                                           SCREEN_HEIGHT - 70, 200, 50, GREEN)

    def start_race(self, mode):
        """开始比赛"""
        self.current_mode = mode
        self.state = "racing"
        self.swimmers = []

        # 创建选手
        lanes = [150, 250, 350, 450, 550]
        colors = [RED, BLUE, GREEN, ORANGE, PURPLE]
        names = ["你", "电脑1", "电脑2", "电脑3", "电脑4"]

        # 添加玩家
        self.player = Swimmer(60, lanes[0], RED, names[0], is_player=True)
        self.player.max_speed = 5 * self.modes[mode]["speed"]
        self.swimmers.append(self.player)

        # 添加AI选手
        for i in range(1, 5):
            ai = Swimmer(60, lanes[i], colors[i], names[i], is_player=False)
            ai.max_speed = (4 + random.random() * 2) * self.modes[mode]["speed"]
            ai.lane = i
            self.swimmers.append(ai)

        self.game_start_time = 0
        self.rankings = []

    def handle_event(self, event):
        """处理事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            if self.state == "menu":
                if self.start_button.collidepoint(mouse_pos):
                    self.state = "select_mode"

            elif self.state == "select_mode":
                for i, button in enumerate(self.mode_buttons):
                    if button.collidepoint(mouse_pos):
                        mode_key = list(self.modes.keys())[i]
                        self.start_race(mode_key)

                if self.back_button.collidepoint(mouse_pos):
                    self.state = "menu"

            elif self.state == "result":
                if self.back_button.collidepoint(mouse_pos):
                    self.state = "menu"

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.state == "racing":
                    self.state = "menu"
            elif event.key == pygame.K_SPACE:
                if self.state == "racing":
                    # 开始计时
                    if self.game_start_time == 0:
                        self.game_start_time = pygame.time.get_ticks()

    def update(self):
        """更新游戏状态"""
        dt = 1.0 / FPS
        keys = pygame.key.get_pressed()

        if self.state == "racing":
            # 检查是否所有选手都完成
            all_finished = all(s.finished for s in self.swimmers)

            if all_finished:
                self.state = "result"
                return

            # 更新选手
            for swimmer in self.swimmers:
                is_stroking = keys[pygame.K_SPACE] and swimmer.is_player
                stroke_speed = self.modes[self.current_mode]["speed"]
                swimmer.update(dt, is_stroking, stroke_speed)

    def draw(self):
        """绘制游戏"""
        if self.state == "menu":
            self.draw_menu()
        elif self.state == "select_mode":
            self.draw_mode_select()
        elif self.state == "racing":
            self.draw_race()
        elif self.state == "result":
            self.draw_result()

    def run(self):
        """游戏主循环"""
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                self.handle_event(event)

            self.update()
            self.draw()

            pygame.display.flip()
            clock.tick(FPS)

        pygame.quit()
        sys.exit()


# 主程序入口
if __name__ == "__main__":
    game = SwimmingGame()
    game.run()
