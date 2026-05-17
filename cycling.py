#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自行车竞赛游戏 - Cycling Race Game
包含多种赛道和速度控制系统
作者: Sports Game Developer
"""

import pygame
import os
import random
import math
import sys

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
DARK_GREEN = (34, 139, 34)
SKY_BLUE = (135, 206, 235)
BROWN = (139, 69, 19)
GREEN = (0, 180, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
YELLOW = (255, 255, 0)

# 设置显示窗口
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("自行车竞赛 - Cycling Championship")
clock = pygame.time.Clock()

# 字体设置
font_large = get_chinese_font(72)
font_medium = get_chinese_font(48)
font_small = get_chinese_font(36)
font_tiny = get_chinese_font(24)


class Cyclist:
    """自行车选手类"""

    def __init__(self, x, y, color, name, is_player=False):
        self.x = x
        self.y = y
        self.color = color
        self.name = name
        self.is_player = is_player
        self.speed = 0
        self.max_speed = 8
        self.stamina = 100  # 体力
        self.distance = 0  # 已行驶距离
        self.finished = False
        self.finish_time = 0
        self.pedal_count = 0

    def update(self, dt, is_pedaling, slope=0):
        """更新选手位置"""
        if not self.finished:
            # 踏频控制速度
            if is_pedaling or self.is_player:
                if self.stamina > 0:
                    # 消耗体力
                    self.stamina = max(0, self.stamina - 0.1)
                    # 根据体力调整速度
                    stamina_factor = 0.5 + (self.stamina / 100) * 0.5

                    if self.is_player:
                        # 玩家速度控制
                        if is_pedaling:
                            self.speed = min(self.speed + 0.5, self.max_speed * stamina_factor)
                            self.pedal_count += 1
                        else:
                            self.speed = max(self.speed - 0.2, 2)
                    else:
                        # AI速度
                        self.speed = self.max_speed * stamina_factor * (0.6 + random.random() * 0.3)
                else:
                    self.speed = max(self.speed - 0.1, 1)
            else:
                self.speed = max(self.speed - 0.1, 0)

            # 坡度影响
            if slope > 0:  # 上坡
                self.speed *= (1 - slope * 0.3)
            elif slope < 0:  # 下坡
                self.speed *= (1 - slope * 0.2)

            self.speed = max(0, self.speed)

            # 更新距离
            self.distance += self.speed * dt * 10

            # 检查是否到达终点
            if self.distance >= 10000:  # 10公里
                self.finished = True
                self.finish_time = pygame.time.get_ticks()


class CyclingGame:
    """自行车比赛主游戏类"""

    def __init__(self):
        self.state = "menu"  # menu, select_track, racing, result
        self.current_track = None
        self.tracks = {
            "flat": {
                "name": "平坦公路",
                "length": 10000,
                "difficulty": "简单",
                "description": "适合初学者的平坦赛道",
                "slope_range": (-0.1, 0.1)
            },
            "mountain": {
                "name": "山地赛道",
                "length": 10000,
                "difficulty": "困难",
                "description": "充满上坡和下坡的挑战",
                "slope_range": (-0.5, 0.5)
            },
            "canyon": {
                "name": "峡谷赛道",
                "length": 10000,
                "difficulty": "中等",
                "description": "需要掌握节奏的峡谷地形",
                "slope_range": (-0.3, 0.3)
            }
        }
        self.cyclists = []
        self.player = None
        self.game_start_time = 0
        self.current_slope = 0
        self.terrain_offset = 0
        self.weather = "sunny"  # sunny, rainy, windy
        self.rankings = []

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

    def draw_background(self, slope):
        """绘制赛道背景"""
        # 天空
        if self.weather == "sunny":
            sky_color = SKY_BLUE
        elif self.weather == "rainy":
            sky_color = (100, 100, 120)
        else:
            sky_color = (180, 200, 220)

        pygame.draw.rect(screen, sky_color, (0, 0, SCREEN_WIDTH, 300))

        # 太阳或云
        if self.weather == "sunny":
            pygame.draw.circle(screen, YELLOW, (100, 80), 40)
        else:
            for i in range(3):
                pygame.draw.ellipse(screen, WHITE, (200 + i * 100, 50 + i * 10, 80, 40))

        # 远山
        for i in range(5):
            height = 100 + math.sin(i * 0.5) * 50
            points = [
                (i * 300 - 100, 300),
                (i * 300 + 150, 300 - height),
                (i * 300 + 400, 300)
            ]
            pygame.draw.polygon(screen, (100, 150, 100), points)

        # 地面 - 根据坡度变化
        ground_y = 300
        terrain_points = [(0, 300)]

        for x in range(0, SCREEN_WIDTH + 50, 50):
            y_offset = math.sin((x + self.terrain_offset) * 0.01) * 20
            y_offset += slope * (x - SCREEN_WIDTH // 2) * 0.5
            terrain_points.append((x, ground_y + y_offset + 400))

        terrain_points.append((SCREEN_WIDTH, 700))
        terrain_points.append((0, 700))

        pygame.draw.polygon(screen, DARK_GREEN, terrain_points)

        # 道路
        road_points = []
        for x in range(0, SCREEN_WIDTH + 50, 50):
            y_offset = math.sin((x + self.terrain_offset) * 0.01) * 20
            y_offset += slope * (x - SCREEN_WIDTH // 2) * 0.5
            road_points.append((x, ground_y + y_offset + 380))

        # 绘制道路
        for i in range(len(road_points) - 1):
            color = GRAY if i % 2 == 0 else (100, 100, 100)
            pygame.draw.line(screen, color, road_points[i], road_points[i + 1], 80)

        # 道路中线
        for i in range(0, len(road_points) - 1, 2):
            if i + 1 < len(road_points):
                pygame.draw.line(screen, YELLOW, road_points[i], road_points[i + 1], 3)

        return road_points

    def draw_menu(self):
        """绘制主菜单"""
        # 绘制背景
        screen.fill(SKY_BLUE)

        # 绘制群山
        for i in range(8):
            height = 150 + random.randint(0, 100)
            points = [(i * 200 - 100, 400), (i * 200 + 100, 400 - height), (i * 200 + 300, 400)]
            pygame.draw.polygon(screen, DARK_GREEN, points)

        # 绘制道路
        pygame.draw.rect(screen, GRAY, (0, 400, SCREEN_WIDTH, 100))
        pygame.draw.line(screen, YELLOW, (0, 450), (SCREEN_WIDTH, 450), 3)

        # 绘制自行车装饰
        self.draw_bike(200, 420, RED)
        self.draw_bike(400, 420, BLUE)

        # 绘制标题
        self.draw_text("自行车锦标赛", SCREEN_WIDTH // 2, 80, "large", BLACK)

        # 绘制说明
        self.draw_text("选择赛道开始比赛!", SCREEN_WIDTH // 2, 130, "medium", BLACK)

        # 绘制难度提示
        self.draw_text("提示: 上坡耗体力，下坡省体力", SCREEN_WIDTH // 2, 550, "small", BLACK)
        self.draw_text("按住空格键踩踏板加速!", SCREEN_WIDTH // 2, 590, "small", BLACK)

        # 绘制开始按钮
        self.start_button = self.draw_button("选择赛道", SCREEN_WIDTH // 2 - 100,
                                            SCREEN_HEIGHT - 80, 200, 60, GREEN)

    def draw_bike(self, x, y, color):
        """绘制自行车"""
        # 车轮
        pygame.draw.circle(screen, BLACK, (x - 20, y), 15, 2)
        pygame.draw.circle(screen, BLACK, (x + 20, y), 15, 2)

        # 车架
        pygame.draw.line(screen, color, (x - 20, y), (x, y - 20), 3)
        pygame.draw.line(screen, color, (x + 20, y), (x, y - 20), 3)
        pygame.draw.line(screen, color, (x, y - 20), (x - 10, y - 30), 3)

        # 车把
        pygame.draw.line(screen, BLACK, (x - 5, y - 30), (x + 5, y - 30), 2)

        # 车座
        pygame.draw.ellipse(screen, BLACK, (x - 15, y - 35, 10, 5))

    def draw_track_select(self):
        """绘制赛道选择界面"""
        screen.fill(SKY_BLUE)

        # 绘制标题
        self.draw_text("选择赛道", SCREEN_WIDTH // 2, 50, "large", BLACK)

        # 绘制各个赛道选项
        y_start = 130
        track_list = list(self.tracks.items())
        colors = [GREEN, ORANGE, BROWN]
        difficulties = ["简单", "困难", "中等"]

        self.track_buttons = []
        for i, (key, track) in enumerate(track_list):
            y = y_start + i * 170

            # 绘制赛道卡片
            card_rect = pygame.Rect(100, y, SCREEN_WIDTH - 200, 150)
            pygame.draw.rect(screen, colors[i], card_rect)
            pygame.draw.rect(screen, WHITE, card_rect, 3)

            # 绘制赛道名称
            self.draw_text(track["name"], 200, y + 40, "medium", WHITE)

            # 绘制难度
            diff_color = GREEN if track["difficulty"] == "简单" else ORANGE if track["difficulty"] == "中等" else RED
            self.draw_text(f"难度: {track['difficulty']}", 200, y + 80, "small", WHITE)

            # 绘制描述
            self.draw_text(track["description"], 500, y + 40, "small", WHITE)

            # 绘制距离
            self.draw_text(f"距离: {track['length'] / 1000:.0f}公里", 500, y + 80, "small", WHITE)

            # 绘制坡度范围
            slope_min, slope_max = track["slope_range"]
            self.draw_text(f"坡度: {slope_min:.1f} ~ {slope_max:.1f}", 800, y + 60, "small", WHITE)

            self.track_buttons.append(card_rect)

        # 返回按钮
        self.back_button = self.draw_button("返回", 50, SCREEN_HEIGHT - 80, 100, 50, GRAY)

    def draw_race(self):
        """绘制比赛界面"""
        # 绘制赛道背景
        road_points = self.draw_background(self.current_slope)

        # 绘制选手
        y_base = 480
        for cyclist in self.cyclists:
            self.draw_cyclist(cyclist, y_base)

        # 绘制赛道信息
        self.draw_track_info()

        # 绘制体力条
        self.draw_stamina_bar()

        # 绘制天气效果
        if self.weather == "rainy":
            self.draw_rain()
        elif self.weather == "windy":
            self.draw_wind()

        # 绘制排名
        self.draw_rankings()

        # 绘制提示
        self.draw_text("按住空格键踩踏板! 上坡按W减速省体力，下坡按S加速", SCREEN_WIDTH // 2,
                      SCREEN_HEIGHT - 20, "small", WHITE)

    def draw_cyclist(self, cyclist, y_base):
        """绘制骑手"""
        x = int(cyclist.x % SCREEN_WIDTH)
        y = int(y_base + math.sin((x + self.terrain_offset) * 0.01) * 10)
        y += self.current_slope * (x - SCREEN_WIDTH // 2) * 0.3

        # 绘制自行车
        self.draw_bike(x, y, cyclist.color)

        # 绘制骑手
        pygame.draw.circle(screen, cyclist.color, (x, y - 35), 12)  # 头
        pygame.draw.ellipse(screen, cyclist.color, (x - 8, y - 50, 16, 20))  # 身体

        # 绘制腿部动画
        leg_angle = (cyclist.pedal_count % 20) / 20 * 360
        leg_x = x + int(math.cos(math.radians(leg_angle)) * 10)
        leg_y = y - 15 + int(math.sin(math.radians(leg_angle)) * 5)
        pygame.draw.line(screen, cyclist.color, (x - 5, y - 30), (leg_x, leg_y), 4)

        # 绘制名字
        name_color = WHITE if cyclist.is_player else cyclist.color
        self.draw_text(cyclist.name, x, y - 70, "tiny", name_color)

        # 绘制完成标记
        if cyclist.finished:
            pygame.draw.circle(screen, GOLD, (x, y - 50), 20)
            self.draw_text(f"{cyclist.finish_time/1000:.0f}s", x, y - 50, "tiny", BLACK)

    def draw_track_info(self):
        """绘制赛道信息面板"""
        # 绘制信息面板
        pygame.draw.rect(screen, (0, 0, 0, 180), (20, 20, 250, 120))
        pygame.draw.rect(screen, WHITE, (20, 20, 250, 120), 2)

        # 赛道名称
        track_name = self.tracks[self.current_track]["name"]
        self.draw_text(f"赛道: {track_name}", 145, 45, "small", WHITE)

        # 当前坡度
        slope_text = "平坦" if abs(self.current_slope) < 0.1 else "上坡" if self.current_slope > 0 else "下坡"
        slope_color = GREEN if abs(self.current_slope) < 0.1 else RED if self.current_slope > 0 else BLUE
        self.draw_text(f"坡度: {slope_text}", 145, 75, "small", slope_color)

        # 已行进距离
        if self.player:
            dist_km = self.player.distance / 1000
            self.draw_text(f"距离: {dist_km:.1f}/10.0 公里", 145, 105, "small", WHITE)

    def draw_stamina_bar(self):
        """绘制体力条"""
        if not self.player:
            return

        # 体力条背景
        pygame.draw.rect(screen, WHITE, (20, 160, 200, 30), 2)
        pygame.draw.rect(screen, (0, 0, 0, 180), (20, 160, 200, 30))

        # 体力条填充
        stamina_width = self.player.stamina / 100 * 196
        if self.player.stamina > 50:
            stamina_color = GREEN
        elif self.player.stamina > 25:
            stamina_color = ORANGE
        else:
            stamina_color = RED

        pygame.draw.rect(screen, stamina_color, (22, 162, stamina_width, 26))

        # 体力文字
        self.draw_text(f"体力: {int(self.player.stamina)}%", 120, 175, "tiny", WHITE)

    def draw_rain(self):
        """绘制雨滴效果"""
        for _ in range(50):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            pygame.draw.line(screen, (150, 150, 200), (x, y), (x - 5, y + 10), 1)

    def draw_wind(self):
        """绘制风效果"""
        for i in range(10):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(200, 500)
            pygame.draw.line(screen, WHITE, (x, y), (x + 30, y), 2)

    def draw_rankings(self):
        """绘制实时排名"""
        # 激活的选手
        active_cyclists = [c for c in self.cyclists if not c.finished]
        active_cyclists.sort(key=lambda c: c.distance, reverse=True)

        # 绘制排名面板
        pygame.draw.rect(screen, (0, 0, 0, 180), (SCREEN_WIDTH - 180, 20, 160, 100))
        pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH - 180, 20, 160, 100), 2)

        self.draw_text("排名", SCREEN_WIDTH - 100, 40, "small", WHITE)

        for i, cyclist in enumerate(active_cyclists[:4]):
            color = GOLD if i == 0 else WHITE
            self.draw_text(f"{i + 1}. {cyclist.name}", SCREEN_WIDTH - 170, 60 + i * 18,
                          "tiny", color)

    def draw_result(self):
        """绘制比赛结果"""
        screen.fill(SKY_BLUE)

        # 绘制背景装饰
        for i in range(8):
            height = 100 + random.randint(0, 80)
            points = [(i * 200 - 100, SCREEN_HEIGHT), (i * 200 + 100, SCREEN_HEIGHT - height),
                     (i * 200 + 300, SCREEN_HEIGHT)]
            pygame.draw.polygon(screen, DARK_GREEN, points)

        # 绘制终点线装饰
        pygame.draw.rect(screen, WHITE, (550, 150, 100, 400))
        for y in range(150, 550, 20):
            for x in range(550, 650, 20):
                if ((x + y) // 20) % 2 == 0:
                    pygame.draw.rect(screen, BLACK, (x, y, 20, 20))

        # 绘制标题
        self.draw_text("比赛结果", SCREEN_WIDTH // 2, 50, "large", BLACK)

        # 排序选手
        sorted_cyclists = sorted(self.cyclists, key=lambda c: c.finish_time)

        # 绘制排行榜
        y = 180
        medals = [GOLD, (192, 192, 192), (205, 127, 50)]

        for i, cyclist in enumerate(sorted_cyclists):
            # 绘制排名背景
            color = medals[i] if i < 3 else GRAY
            pygame.draw.rect(screen, color, (200, y, SCREEN_WIDTH - 400, 70))
            pygame.draw.rect(screen, BLACK, (200, y, SCREEN_WIDTH - 400, 70), 2)

            # 绘制排名
            rank_emoji = ["1st", "2nd", "3rd", f"{i + 1}th"][min(i, 3)]
            self.draw_text(rank_emoji, 280, y + 35, "medium", BLACK)

            # 绘制名字
            name_color = RED if cyclist.is_player else WHITE
            self.draw_text(cyclist.name, 450, y + 35, "medium", name_color)

            # 绘制时间
            time_text = f"{cyclist.finish_time / 1000:.2f}秒"
            self.draw_text(time_text, 700, y + 35, "medium", BLACK)

            # 绘制距离
            dist_km = cyclist.distance / 1000
            self.draw_text(f"{dist_km:.1f}km", 850, y + 35, "small", BLACK)

            # 玩家标记
            if cyclist.is_player:
                pygame.draw.rect(screen, RED, (920, y + 20, 60, 30))
                self.draw_text("YOU", 950, y + 35, "tiny", WHITE)

            y += 85

        # 绘制玩家成绩总结
        player = [c for c in self.cyclists if c.is_player][0]
        player_rank = sorted_cyclists.index(player) + 1

        if player_rank == 1:
            msg = "恭喜你获得冠军!"
            color = GOLD
        elif player_rank == 2:
            msg = "获得第二名，表现出色!"
            color = (192, 192, 192)
        elif player_rank == 3:
            msg = "获得第三名，继续加油!"
            color = (205, 127, 50)
        else:
            msg = f"第{player_rank}名，继续努力!"
            color = BLACK

        self.draw_text(msg, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100, "medium", color)

        # 返回按钮
        self.back_button = self.draw_button("返回主菜单", SCREEN_WIDTH // 2 - 100,
                                           SCREEN_HEIGHT - 50, 200, 50, GREEN)

    def start_race(self, track):
        """开始比赛"""
        self.current_track = track
        self.state = "racing"
        self.cyclists = []

        # 随机选择天气
        weathers = ["sunny", "sunny", "sunny", "rainy", "windy"]
        self.weather = random.choice(weathers)

        # 创建选手
        colors = [RED, BLUE, GREEN, ORANGE, PURPLE]
        names = ["你", "电脑1", "电脑2", "电脑3", "电脑4"]

        # 添加玩家
        self.player = Cyclist(0, 0, RED, names[0], is_player=True)
        self.player.max_speed = 8
        self.cyclists.append(self.player)

        # 添加AI选手
        for i in range(1, 5):
            ai = Cyclist(0, 0, colors[i], names[i], is_player=False)
            ai.max_speed = 6 + random.random() * 3
            ai.stamina = 80 + random.random() * 20
            self.cyclists.append(ai)

        self.game_start_time = 0
        self.current_slope = 0
        self.terrain_offset = 0

    def handle_event(self, event):
        """处理事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            if self.state == "menu":
                if self.start_button.collidepoint(mouse_pos):
                    self.state = "select_track"

            elif self.state == "select_track":
                for i, button in enumerate(self.track_buttons):
                    if button.collidepoint(mouse_pos):
                        track_key = list(self.tracks.keys())[i]
                        self.start_race(track_key)

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
                    if self.game_start_time == 0:
                        self.game_start_time = pygame.time.get_ticks()

    def update(self):
        """更新游戏状态"""
        dt = 1.0 / FPS
        keys = pygame.key.get_pressed()

        if self.state == "racing":
            # 检查是否所有选手都完成
            all_finished = all(c.finished for c in self.cyclists)

            if all_finished:
                self.state = "result"
                return

            # 开始计时
            if self.game_start_time == 0 and keys[pygame.K_SPACE]:
                self.game_start_time = pygame.time.get_ticks()

            # 更新地形偏移
            if self.player:
                self.terrain_offset += self.player.speed * 2

            # 更新坡度
            slope_range = self.tracks[self.current_track]["slope_range"]
            self.current_slope = math.sin(pygame.time.get_ticks() * 0.0005) * (slope_range[1] - slope_range[0]) / 2

            # 更新选手
            for cyclist in self.cyclists:
                is_pedaling = keys[pygame.K_SPACE] and cyclist.is_player
                cyclist.update(dt, is_pedaling, self.current_slope)

                # 天气影响
                if self.weather == "rainy":
                    cyclist.speed *= 0.9
                elif self.weather == "windy":
                    cyclist.speed *= 1.1

    def draw(self):
        """绘制游戏"""
        if self.state == "menu":
            self.draw_menu()
        elif self.state == "select_track":
            self.draw_track_select()
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
    game = CyclingGame()
    game.run()
