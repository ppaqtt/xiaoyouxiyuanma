#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
田径运动会游戏 - Athletics Game
包含跑步、跳远、投掷等田径项目
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
GREEN = (0, 200, 0)
BLUE = (0, 100, 200)
GOLD = (255, 215, 0)
GRAY = (128, 128, 128)
LIGHT_BLUE = (173, 216, 230)
DARK_GREEN = (0, 100, 0)
ORANGE = (255, 165, 0)

# 设置显示窗口
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("田径运动会 - Athletics Olympics")
clock = pygame.time.Clock()

# 字体设置
font_large = get_chinese_font(72)
font_medium = get_chinese_font(48)
font_small = get_chinese_font(36)
font_tiny = get_chinese_font(24)


class AthleticsGame:
    """田径运动会主游戏类"""

    def __init__(self):
        self.state = "menu"  # menu, running, result
        self.current_event = None
        self.events = ["sprint_100m", "long_jump", "javelin"]
        self.event_index = 0
        self.results = []
        self.player_score = 0
        self.cpu_scores = [0, 0, 0]
        self.game_time = 0
        self.best_scores = {"sprint_100m": float('inf'), "long_jump": 0, "javelin": 0}

        # 跑步游戏变量
        self.player_x = 100
        self.player_y = SCREEN_HEIGHT // 2
        self.player_speed = 0
        self.cpu_positions = [(100, SCREEN_HEIGHT // 3), (100, SCREEN_HEIGHT * 2 // 3)]
        self.cpu_speeds = [0, 0]
        self.race_distance = 0
        self.race_finished = False
        self.race_start_time = 0
        self.player_race_time = 0

        # 跳远游戏变量
        self.jump_power = 0
        self.jump_angle = 45
        self.is_jumping = False
        self.jump_result = 0
        self.jump_start_x = 150
        self.jump_x = 150
        self.jump_y = 400
        self.jump_vel_x = 0
        self.jump_vel_y = 0
        self.in_air = False

        # 投掷游戏变量
        self.throw_power = 0
        self.throw_angle = 45
        self.is_throwing = False
        self.throw_result = 0
        self.throwing = False
        self.throw_x = 100
        self.throw_y = 400
        self.throw_vel_x = 0
        self.throw_vel_y = 0
        self.throw_in_air = False

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
        self.draw_text(text, x + width // 2, y + height // 2, "medium", WHITE)
        return button_rect

    def draw_menu(self):
        """绘制主菜单"""
        # 绘制背景
        screen.fill(LIGHT_BLUE)

        # 绘制跑道装饰
        pygame.draw.rect(screen, GRAY, (0, SCREEN_HEIGHT - 150, SCREEN_WIDTH, 150))
        for i in range(10):
            pygame.draw.rect(screen, WHITE, (i * 130, SCREEN_HEIGHT - 140, 120, 130), 3)

        # 绘制标题
        self.draw_text("田径运动会", SCREEN_WIDTH // 2, 100, "large", BLUE)

        # 绘制项目说明
        self.draw_text("包含三个经典田径项目", SCREEN_WIDTH // 2, 180, "medium", BLACK)

        # 绘制项目列表
        events_text = ["1. 100米短跑 - 按空格键冲刺", "2. 跳远 - 蓄力跳跃", "3. 标枪 - 蓄力投掷"]
        for i, text in enumerate(events_text):
            self.draw_text(text, SCREEN_WIDTH // 2, 280 + i * 50, "small", BLACK)

        # 绘制开始按钮
        self.start_button = self.draw_button("开始比赛", SCREEN_WIDTH // 2 - 100, 500, 200, 60, GREEN)

    def draw_sprint_100m(self):
        """绘制100米短跑"""
        # 绘制跑道
        screen.fill(GREEN)

        # 绘制跑道线
        pygame.draw.rect(screen, WHITE, (0, 150, SCREEN_WIDTH, 400), 3)
        for i in range(4):
            pygame.draw.line(screen, WHITE, (0, 150 + i * 100), (SCREEN_WIDTH, 150 + i * 100), 2)

        # 绘制起跑线
        pygame.draw.line(screen, WHITE, (80, 150), (80, 550), 4)

        # 绘制终点线
        pygame.draw.rect(screen, BLACK, (SCREEN_WIDTH - 50, 150, 10, 400))
        pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH - 45, 150, 5, 400))

        # 绘制距离标记
        for i in range(11):
            x = 80 + (SCREEN_WIDTH - 130) * i / 10
            self.draw_text(f"{i*10}m", x, 140, "tiny", BLACK)

        # 绘制选手
        colors = [RED, BLUE, ORANGE]
        names = ["你", "电脑1", "电脑2"]

        # 玩家
        pygame.draw.circle(screen, RED, (int(self.player_x), 250), 20)
        self.draw_text("你", self.player_x, 230, "tiny", BLACK)

        # 电脑选手
        for i, pos in enumerate(self.cpu_positions):
            pygame.draw.circle(screen, colors[i + 1], (int(pos[0]), int(pos[1])), 20)
            self.draw_text(names[i + 1], pos[0], pos[1] - 20, "tiny", BLACK)

        # 绘制计时器
        if self.race_start_time > 0:
            elapsed = (pygame.time.get_ticks() - self.race_start_time) / 1000
            self.draw_text(f"时间: {elapsed:.2f}秒", SCREEN_WIDTH // 2, 50, "medium", BLACK)

        # 绘制提示
        self.draw_text("按住空格键加速冲刺!", SCREEN_WIDTH // 2, 600, "small", BLACK)

        # 绘制位置指示
        progress = self.player_x / (SCREEN_WIDTH - 50)
        self.draw_text(f"进度: {int(progress * 100)}%", 100, 580, "tiny", BLACK)

    def draw_long_jump(self):
        """绘制跳远"""
        # 绘制沙坑和跑道
        screen.fill(GREEN)

        # 绘制沙坑
        pygame.draw.rect(screen, (210, 180, 140), (SCREEN_WIDTH - 300, 350, 280, 100))
        self.draw_text("沙坑", SCREEN_WIDTH - 160, 400, "small", BLACK)

        # 绘制起跳线
        pygame.draw.line(screen, WHITE, (150, 350), (150, 450), 4)

        # 绘制刻度
        for i in range(20):
            x = 150 + i * 30
            if i % 2 == 0:
                pygame.draw.line(screen, WHITE, (x, 440), (x, 460), 2)
                self.draw_text(f"{i}m", x, 475, "tiny", WHITE)
            else:
                pygame.draw.line(screen, WHITE, (x, 445), (x, 455), 1)

        # 绘制助跑区
        pygame.draw.rect(screen, GRAY, (50, 300, 100, 150))
        self.draw_text("助跑区", 100, 380, "tiny", WHITE)

        # 绘制选手
        if not self.in_air:
            pygame.draw.circle(screen, RED, (int(self.jump_x), int(self.jump_y)), 20)
            self.draw_text("你", self.jump_x, self.jump_y - 30, "tiny", BLACK)
        else:
            pygame.draw.circle(screen, RED, (int(self.jump_x), int(self.jump_y)), 20)
            # 绘制跳跃轨迹
            pygame.draw.arc(screen, BLUE, (int(self.jump_x - 50), int(self.jump_y - 100), 100, 100),
                           math.radians(0), math.radians(180), 2)

        # 绘制力量条
        pygame.draw.rect(screen, WHITE, (50, 100, 300, 30), 2)
        fill_width = min(self.jump_power / 100 * 300, 300)
        color = GREEN if self.jump_power < 50 else ORANGE if self.jump_power < 80 else RED
        pygame.draw.rect(screen, color, (52, 102, fill_width, 26))
        self.draw_text(f"力量: {int(self.jump_power)}%", 200, 115, "tiny", BLACK)

        # 绘制角度指示
        self.draw_text(f"角度: {self.jump_angle}°", 200, 160, "tiny", BLACK)

        # 绘制跳跃结果
        if self.jump_result > 0:
            self.draw_text(f"跳跃距离: {self.jump_result:.2f}米", SCREEN_WIDTH // 2, 50, "medium", BLUE)

        # 绘制提示
        if not self.in_air:
            self.draw_text("按空格键蓄力，松开跳跃!", SCREEN_WIDTH // 2, 550, "small", BLACK)
        else:
            self.draw_text("跳跃中...", SCREEN_WIDTH // 2, 550, "small", BLACK)

    def draw_javelin(self):
        """绘制标枪投掷"""
        # 绘制场地
        screen.fill(GREEN)

        # 绘制投掷区
        pygame.draw.rect(screen, GRAY, (50, 300, 150, 200))
        self.draw_text("投掷区", 125, 400, "small", WHITE)

        # 绘制落地区
        pygame.draw.rect(screen, LIGHT_BLUE, (200, 350, 900, 150))

        # 绘制距离刻度
        for i in range(31):
            x = 200 + i * 30
            if i % 5 == 0:
                pygame.draw.line(screen, WHITE, (x, 350), (x, 370), 2)
                self.draw_text(f"{i*10}m", x, 385, "tiny", WHITE)
            else:
                pygame.draw.line(screen, WHITE, (x, 355), (x, 365), 1)

        # 绘制标枪
        if self.throw_in_air:
            # 计算标枪旋转角度
            angle = math.degrees(math.atan2(-self.throw_vel_y, self.throw_vel_x))
            pygame.draw.line(screen, ORANGE, (int(self.throw_x), int(self.throw_y)),
                           (int(self.throw_x + 40 * math.cos(math.radians(angle))),
                            int(self.throw_y - 40 * math.sin(math.radians(angle)))), 4)
            # 标枪尖
            tip_x = self.throw_x + 40 * math.cos(math.radians(angle))
            tip_y = self.throw_y - 40 * math.sin(math.radians(angle))
            pygame.draw.circle(screen, GRAY, (int(tip_x), int(tip_y)), 5)
        elif not self.throwing:
            # 静止标枪
            angle = 90 - self.throw_angle
            pygame.draw.line(screen, ORANGE, (int(self.throw_x), int(self.throw_y)),
                           (int(self.throw_x + 40 * math.sin(math.radians(self.throw_angle))),
                            int(self.throw_y - 40 * math.cos(math.radians(self.throw_angle)))), 4)

        # 绘制选手
        pygame.draw.circle(screen, RED, (int(self.throw_x), int(self.throw_y + 30)), 20)
        self.draw_text("你", self.throw_x, self.throw_y, "tiny", BLACK)

        # 绘制力量条
        pygame.draw.rect(screen, WHITE, (50, 100, 300, 30), 2)
        fill_width = min(self.throw_power / 100 * 300, 300)
        color = GREEN if self.throw_power < 50 else ORANGE if self.throw_power < 80 else RED
        pygame.draw.rect(screen, color, (52, 102, fill_width, 26))
        self.draw_text(f"力量: {int(self.throw_power)}%", 200, 115, "tiny", BLACK)

        # 绘制角度指示
        self.draw_text(f"角度: {self.throw_angle}°", 200, 160, "tiny", BLACK)

        # 绘制投掷结果
        if self.throw_result > 0:
            self.draw_text(f"投掷距离: {self.throw_result:.1f}米", SCREEN_WIDTH // 2, 50, "medium", BLUE)

        # 绘制提示
        if not self.throwing and not self.throw_in_air:
            self.draw_text("按空格键蓄力，松开投掷!", SCREEN_WIDTH // 2, 550, "small", BLACK)
        elif self.throwing:
            self.draw_text("投掷中...", SCREEN_WIDTH // 2, 550, "small", BLACK)

    def draw_result(self):
        """绘制结果界面"""
        screen.fill(LIGHT_BLUE)

        # 绘制标题
        self.draw_text("比赛结果", SCREEN_WIDTH // 2, 80, "large", BLUE)

        # 显示各项目成绩
        y_offset = 150
        for i, event in enumerate(["100米短跑", "跳远", "标枪投掷"]):
            self.draw_text(event, 200, y_offset + i * 120, "medium", BLACK)

            # 玩家成绩
            player_score = self.results[i] if i < len(self.results) else 0
            self.draw_text(f"你: {player_score:.2f}", 450, y_offset + i * 120, "medium", RED)

            # 电脑成绩
            cpu_score = self.cpu_scores[i] if i < len(self.cpu_scores) else 0
            self.draw_text(f"电脑平均: {cpu_score:.2f}", 700, y_offset + i * 120, "medium", GRAY)

        # 绘制总分
        self.draw_text(f"总分", 200, y_offset + 400, "medium", BLACK)
        self.draw_text(f"你: {self.player_score:.2f}", 450, y_offset + 400, "medium", RED)

        # 返回按钮
        self.back_button = self.draw_button("返回主菜单", SCREEN_WIDTH // 2 - 100, 620, 200, 50, BLUE)

    def update_sprint(self, dt, keys):
        """更新100米短跑"""
        if not self.race_finished:
            # 玩家速度控制
            if keys[pygame.K_SPACE]:
                self.player_speed = min(self.player_speed + 0.5, 12)
            else:
                self.player_speed = max(self.player_speed - 0.1, 2)

            # 更新玩家位置
            self.player_x += self.player_speed

            # 记录开始时间
            if self.race_start_time == 0:
                self.race_start_time = pygame.time.get_ticks()

            # 电脑AI
            for i in range(2):
                self.cpu_speeds[i] = 5 + random.random() * 4
                self.cpu_positions = list(self.cpu_positions)
                self.cpu_positions[i] = (self.cpu_positions[i][0] + self.cpu_speeds[i],
                                          self.cpu_positions[i][1])
                self.cpu_positions = tuple(self.cpu_positions)

            # 检查是否到达终点
            if self.player_x >= SCREEN_WIDTH - 50:
                self.player_race_time = (pygame.time.get_ticks() - self.race_start_time) / 1000
                self.results.append(self.player_race_time)
                self.player_score += self.player_race_time
                self.race_finished = True

    def update_long_jump(self, dt, keys):
        """更新跳远"""
        if not self.in_air:
            # 蓄力阶段
            if keys[pygame.K_SPACE]:
                self.jump_power = min(self.jump_power + 1, 100)
                self.is_jumping = True
        else:
            # 跳跃中
            self.jump_x += self.jump_vel_x * dt
            self.jump_y += self.jump_vel_y * dt
            self.jump_vel_y += 0.5  # 重力

            # 落地检测
            if self.jump_y >= 400:
                self.jump_y = 400
                self.in_air = False
                self.jump_result = (self.jump_x - self.jump_start_x) / 100
                if self.jump_result > 0:
                    self.results.append(self.jump_result)
                    self.player_score -= self.jump_result  # 跳远是距离越大越好，所以减

    def update_javelin(self, dt, keys):
        """更新标枪投掷"""
        if not self.throw_in_air:
            if not self.throwing:
                # 蓄力阶段
                if keys[pygame.K_SPACE]:
                    self.throw_power = min(self.throw_power + 1, 100)
                    self.is_throwing = True
            else:
                # 投掷中
                self.throw_x += self.throw_vel_x * dt
                self.throw_y += self.throw_vel_y * dt
                self.throw_vel_y += 0.3  # 重力

                # 落地检测
                if self.throw_y >= 400:
                    self.throw_result = (self.throw_x - self.throw_x) / 10
                    self.throw_result = max(0, (self.throw_x - 100) / 20)
                    if self.throw_result > 0:
                        self.results.append(self.throw_result)
                        self.player_score -= self.throw_result
                    self.throw_in_air = False
                    self.throwing = False

                # 出界检测
                if self.throw_x > SCREEN_WIDTH - 50:
                    self.throw_result = (self.throw_x - 100) / 20
                    if self.throw_result > 0:
                        self.results.append(self.throw_result)
                        self.player_score -= self.throw_result
                    self.throw_in_air = False
                    self.throwing = False

    def handle_event(self, event):
        """处理事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            if self.state == "menu":
                if self.start_button.collidepoint(mouse_pos):
                    self.state = "running"
                    self.current_event = self.events[self.event_index]
                    self.reset_event()

            elif self.state == "result":
                if self.back_button.collidepoint(mouse_pos):
                    self.state = "menu"
                    self.reset_game()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if self.current_event == "sprint_100m" and not self.race_finished:
                    pass  # 冲刺在update中处理

            elif event.key == pygame.K_RETURN:
                if self.race_finished or (self.current_event in ["long_jump", "javelin"] and
                                          not getattr(self, 'in_air', False) and
                                          not getattr(self, 'throw_in_air', False) and
                                          not getattr(self, 'throwing', False)):
                    self.next_event()

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                if self.current_event == "long_jump" and self.is_jumping and not self.in_air:
                    # 执行跳跃
                    self.in_air = True
                    self.jump_x = self.jump_start_x
                    self.jump_y = 400
                    power = self.jump_power / 100 * 15
                    self.jump_vel_x = power * math.cos(math.radians(self.jump_angle))
                    self.jump_vel_y = -power * math.sin(math.radians(self.jump_angle))
                    self.is_jumping = False
                    self.jump_power = 0

                elif self.current_event == "javelin" and self.is_throwing and not self.throwing:
                    # 执行投掷
                    self.throwing = True
                    self.throw_in_air = True
                    self.throw_x = 125
                    self.throw_y = 400
                    power = self.throw_power / 100 * 30
                    self.throw_vel_x = power * math.sin(math.radians(self.throw_angle))
                    self.throw_vel_y = -power * math.cos(math.radians(self.throw_angle))
                    self.is_throwing = False
                    self.throw_power = 0

    def next_event(self):
        """下一个项目"""
        self.event_index += 1

        if self.event_index >= len(self.events):
            # 比赛结束，计算电脑分数
            for i in range(3):
                if i == 0:  # 100米短跑
                    self.cpu_scores[i] = 12 + random.random() * 3
                else:  # 跳远和标枪
                    self.cpu_scores[i] = 5 + random.random() * 5

            self.state = "result"
        else:
            self.current_event = self.events[self.event_index]
            self.reset_event()

    def reset_event(self):
        """重置当前项目"""
        if self.current_event == "sprint_100m":
            self.player_x = 100
            self.player_speed = 0
            self.cpu_positions = [(100, SCREEN_HEIGHT // 3), (100, SCREEN_HEIGHT * 2 // 3)]
            self.cpu_speeds = [0, 0]
            self.race_finished = False
            self.race_start_time = 0
            self.player_race_time = 0

        elif self.current_event == "long_jump":
            self.jump_power = 0
            self.is_jumping = False
            self.jump_result = 0
            self.jump_x = self.jump_start_x
            self.jump_y = 400
            self.in_air = False

        elif self.current_event == "javelin":
            self.throw_power = 0
            self.is_throwing = False
            self.throw_result = 0
            self.throw_x = 125
            self.throw_y = 400
            self.throwing = False
            self.throw_in_air = False

    def reset_game(self):
        """重置游戏"""
        self.state = "menu"
        self.event_index = 0
        self.results = []
        self.player_score = 0
        self.cpu_scores = [0, 0, 0]
        self.current_event = None

    def update(self):
        """更新游戏状态"""
        dt = 1.0 / FPS
        keys = pygame.key.get_pressed()

        if self.state == "running":
            if self.current_event == "sprint_100m":
                self.update_sprint(dt, keys)
            elif self.current_event == "long_jump":
                self.update_long_jump(dt, keys)
            elif self.current_event == "javelin":
                self.update_javelin(dt, keys)

    def draw(self):
        """绘制游戏"""
        if self.state == "menu":
            self.draw_menu()
        elif self.state == "running":
            # 绘制当前项目
            if self.current_event == "sprint_100m":
                self.draw_sprint_100m()
            elif self.current_event == "long_jump":
                self.draw_long_jump()
            elif self.current_event == "javelin":
                self.draw_javelin()

            # 绘制当前项目指示
            event_names = {"sprint_100m": "100米短跑", "long_jump": "跳远", "javelin": "标枪投掷"}
            self.draw_text(f"当前项目: {event_names.get(self.current_event, '')}",
                          SCREEN_WIDTH // 2, 20, "small", BLACK)

            # 绘制进度
            self.draw_text(f"项目 {self.event_index + 1}/3", SCREEN_WIDTH - 100, 20, "tiny", BLACK)

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
    game = AthleticsGame()
    game.run()
