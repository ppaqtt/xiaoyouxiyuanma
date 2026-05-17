#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
羽毛球游戏 - Badminton Game
真实的羽毛球物理模拟，支持AI对战模式
"""

import pygame
import os
import math
import random
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

# 游戏常量设置
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60

# 颜色定义
WHITE = (255, 255, 255)
GREEN = (34, 139, 34)
BLUE = (0, 100, 200)
RED = (200, 30, 30)
BLACK = (0, 0, 0)
YELLOW = (255, 200, 0)
GRAY = (128, 128, 128)
ORANGE = (255, 140, 0)
LIGHT_GREEN = (144, 238, 144)
COURT_BLUE = (0, 80, 180)

# 羽毛球参数
SHUTTLECOCK_RADIUS = 8
SHUTTLECOCK_SPEED_INITIAL = 15
SHUTTLECOCK_MAX_SPEED = 30
GRAVITY = 0.25
AIR_RESISTANCE = 0.992
DRAG_FACTOR = 0.998
FLOAT_FACTOR = 0.15

# 球拍参数
RACKET_SIZE = 100
RACKET_SPEED = 12
AI_RACKET_SPEED = 9

# 球场参数
COURT_WIDTH = 800
COURT_HEIGHT = 600
COURT_LEFT = (SCREEN_WIDTH - COURT_WIDTH) // 2
COURT_TOP = 50

# 单打边线
SINGLE_WIDTH = 600
SINGLE_HEIGHT = 500
SINGLE_LEFT = COURT_LEFT + (COURT_WIDTH - SINGLE_WIDTH) // 2
SINGLE_TOP = COURT_TOP + (COURT_HEIGHT - SINGLE_HEIGHT) // 2

# 球网
NET_X = SCREEN_WIDTH // 2
NET_HEIGHT = 160
NET_WIDTH = 5
NET_MESH_COLOR = (200, 200, 200)


class Shuttlecock:
    """羽毛球类 - 真实的空气动力学模拟"""
    def __init__(self):
        self.reset()

    def reset(self):
        """重置羽毛球"""
        self.x = SCREEN_WIDTH // 2
        self.y = 100
        self.z = 100  # 高度
        self.vx = 0
        self.vy = 0
        self.vz = 0
        self.speed = 0
        self.rotation = 0  # 羽毛球的旋转
        self.trail = []
        self.is_in_play = False
        self.is_falling = False

    def serve(self, server_is_player=True):
        """发球"""
        self.is_in_play = True
        self.is_falling = False

        if server_is_player:
            self.x = SCREEN_WIDTH // 2
            self.y = SINGLE_TOP + 100
            self.z = 150
        else:
            self.x = SCREEN_WIDTH // 2
            self.y = SINGLE_TOP + SINGLE_HEIGHT - 100
            self.z = 150

        # 发球弧线
        direction = -1 if server_is_player else 1
        angle = random.uniform(-math.pi/8, math.pi/8)
        self.vx = math.sin(angle) * SHUTTLECOCK_SPEED_INITIAL * 0.5
        self.vy = math.cos(angle) * SHUTTLECOCK_SPEED_INITIAL * direction
        self.vz = random.uniform(3, 6)

    def update(self):
        """更新羽毛球物理"""
        if not self.is_in_play:
            return

        # 添加轨迹
        self.trail.append((self.x, self.y, self.z))
        if len(self.trail) > 25:
            self.trail.pop(0)

        # 羽毛球特殊物理：当速度减小时，下降变慢（飘浮效果）
        speed = math.sqrt(self.vx**2 + self.vy**2)

        # 重力效果（随速度减小而减弱）
        gravity_effect = GRAVITY * (1 + FLOAT_FACTOR / (speed + 1))
        self.vz -= gravity_effect

        # 空气阻力
        self.vx *= DRAG_FACTOR
        self.vy *= DRAG_FACTOR
        self.vz *= AIR_RESISTANCE

        # 更新位置
        self.x += self.vx
        self.y += self.vy
        self.z += self.vz

        # 旋转效果
        self.rotation += (self.vx + self.vy) * 0.02

        # 边界检测
        # 高度为0时落地
        if self.z <= 0:
            self.z = 0
            return "ground"

        # 边界出界检测
        if self.y < SINGLE_TOP - 50 or self.y > SINGLE_TOP + SINGLE_HEIGHT + 50:
            return "out_y"
        if self.x < SINGLE_LEFT - 30 or self.x > SINGLE_LEFT + SINGLE_WIDTH + 30:
            return "out_x"

        # 碰到球网
        if abs(self.x - NET_X) < NET_WIDTH // 2 + 10:
            if self.z < NET_HEIGHT:
                self.vx = -self.vx * 0.5
                self.x = NET_X + (NET_WIDTH // 2 + 15) if self.vx > 0 else NET_X - (NET_WIDTH // 2 + 15)

        return None

    def draw(self, screen):
        """绘制羽毛球（考虑高度和旋转）"""
        if not self.is_in_play:
            return

        # 绘制轨迹
        for i, (tx, ty, tz) in enumerate(self.trail):
            alpha = int(255 * (i / len(self.trail)) * 0.3)
            size = max(2, int(SHUTTLECOCK_RADIUS * (i / len(self.trail))))
            screen_y = ty - int(tz * 0.6)
            color = (255, 220, 180)
            pygame.draw.circle(screen, color, (int(tx), int(screen_y)), size)

        # 计算屏幕位置
        screen_y = self.y - int(self.z * 0.6)

        # 绘制阴影
        shadow_alpha = max(50, 180 - int(self.z * 3))
        shadow_size = int(SHUTTLECOCK_RADIUS * (1 - self.z / 300))
        if shadow_size > 0:
            pygame.draw.ellipse(screen, (0, 0, 0),
                              (int(self.x - shadow_size), int(self.y - shadow_size // 2),
                               int(shadow_size * 2), int(shadow_size)), 0)

        # 绘制羽毛球主体（锥形简化表示）
        if screen_y > 0:
            # 羽毛球头部（软木部分）
            pygame.draw.circle(screen, WHITE, (int(self.x), int(screen_y)), SHUTTLECOCK_RADIUS)
            pygame.draw.circle(screen, (220, 220, 220), (int(self.x), int(screen_y)), SHUTTLECOCK_RADIUS, 1)

            # 羽毛部分（旋转的椭圆）
            angle_rad = math.radians(self.rotation * 50)
            for i in range(4):
                feather_angle = angle_rad + i * math.pi / 2
                ex = self.x + math.cos(feather_angle) * SHUTTLECOCK_RADIUS * 1.5
                ey = screen_y + math.sin(feather_angle) * SHUTTLECOCK_RADIUS * 0.8
                pygame.draw.line(screen, WHITE, (int(self.x), int(screen_y)),
                               (int(ex), int(ey)), 2)

    def get_ground_pos(self):
        """预测落点"""
        if self.vz <= 0:
            return self.x, self.y

        # 计算落地时间
        t = self.z / max(self.vz, 0.1)
        gx = self.x + self.vx * t
        gy = self.y + self.vy * t

        return gx, gy


class Racket:
    """羽毛球拍类"""
    def __init__(self, x, y, is_ai=False):
        self.x = x
        self.y = y
        self.z = 50  # 球拍高度
        self.target_z = 50
        self.is_ai = is_ai
        self.last_x = x
        self.last_y = y
        self.angle = 0  # 球拍倾斜角度
        self.swing_power = 0
        self.is_swinging = False
        self.swing_timer = 0

    def update(self, shuttlecock=None):
        """更新球拍"""
        self.last_x = self.x
        self.last_y = self.y

        if self.is_ai:
            # AI控制 - 更好的预判
            if shuttlecock and shuttlecock.is_in_play:
                # 预测羽毛球的落点
                gx, gy = shuttlecock.get_ground_pos()

                # AI只在己方半场追击
                if self.y > NET_X:
                    # 移动球拍
                    dx = gx - self.x
                    dy = gy - self.y

                    if abs(dx) > 20:
                        self.x += min(abs(dx), AI_RACKET_SPEED) * (1 if dx > 0 else -1)
                    if abs(dy) > 20:
                        self.y += min(abs(dy), AI_RACKET_SPEED * 0.7) * (1 if dy > 0 else -1)

                    # 调整高度
                    if shuttlecock.z > 80:
                        self.target_z = shuttlecock.z * 0.6
                    else:
                        self.target_z = 40

                    # AI挥拍时机
                    distance = math.sqrt(dx**2 + dy**2)
                    if distance < RACKET_SIZE * 0.8 and not self.is_swinging:
                        if random.random() < 0.15:
                            self.swing()
                else:
                    # 球在对方半场，返回防守位置
                    self.x += (SCREEN_WIDTH // 2 - self.x) * 0.02
                    self.y += (SINGLE_TOP + SINGLE_HEIGHT - 100 - self.y) * 0.02
        else:
            # 玩家控制
            keys = pygame.key.get_pressed()

            # 移动
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.x -= RACKET_SPEED
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.x += RACKET_SPEED
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.y -= RACKET_SPEED
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.y += RACKET_SPEED

            # 高度调整
            if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                self.target_z = 120
            else:
                self.target_z = 50

            # 挥拍
            if keys[pygame.K_SPACE]:
                if not self.is_swinging:
                    self.swing()

        # 平滑高度变化
        self.z += (self.target_z - self.z) * 0.1

        # 挥拍动画
        if self.is_swinging:
            self.swing_timer += 1
            self.swing_power = math.sin(self.swing_timer * 0.15) * 15
            if self.swing_timer > 25:
                self.is_swinging = False
                self.swing_timer = 0
                self.swing_power = 0

        # 角度变化
        if self.is_swinging:
            self.angle = self.swing_power * 0.1

        # 边界限制
        self.x = max(SINGLE_LEFT + RACKET_SIZE // 3,
                     min(SINGLE_LEFT + SINGLE_WIDTH - RACKET_SIZE // 3, self.x))
        self.y = max(SINGLE_TOP + RACKET_SIZE // 3,
                     min(SINGLE_TOP + SINGLE_HEIGHT - RACKET_SIZE // 3, self.y))
        self.z = max(20, min(180, self.z))

    def swing(self):
        """挥拍"""
        self.is_swinging = True
        self.swing_timer = 0

    def check_hit(self, shuttlecock):
        """检测是否击中羽毛球"""
        if not self.is_swinging:
            return False

        if not shuttlecock.is_in_play:
            return False

        # 计算距离（考虑高度）
        dx = shuttlecock.x - self.x
        dy = shuttlecock.y - self.y
        dz = shuttlecock.z - self.z
        distance = math.sqrt(dx**2 + dy**2 + dz**2)

        hit_range = RACKET_SIZE // 2 + SHUTTLECOCK_RADIUS

        if distance < hit_range:
            # 计算击球方向
            angle = math.atan2(dy, dx)
            power = min(shuttlecock.speed * 1.05 + 5, SHUTTLECOCK_MAX_SPEED)

            # 根据球拍移动增强击球
            move_bonus = math.sqrt((self.x - self.last_x)**2 + (self.y - self.last_y)**2) * 0.3

            # 击球速度
            hit_speed = power + move_bonus + random.uniform(2, 5)

            # 反弹方向（总是飞向对方）
            direction = 1 if self.is_ai else -1

            # 设置新的速度
            shuttlecock.vx = math.cos(angle + random.uniform(-0.3, 0.3)) * hit_speed * 0.4
            shuttlecock.vy = direction * math.cos(angle + random.uniform(-0.5, 0.5)) * hit_speed
            shuttlecock.vz = abs(shuttlecock.vz) * 0.3 + random.uniform(4, 8)

            shuttlecock.x = self.x + direction * 10
            shuttlecock.y = self.y
            shuttlecock.z = self.z + 10

            return True

        return False

    def draw(self, screen):
        """绘制球拍"""
        color = BLUE if not self.is_ai else RED
        screen_y = self.y - int(self.z * 0.6)

        # 球拍框（椭圆形）
        racket_rect = pygame.Rect(
            int(self.x - RACKET_SIZE // 2),
            int(screen_y - RACKET_SIZE // 2),
            RACKET_SIZE,
            RACKET_SIZE
        )

        # 绘制握柄
        handle_start = (self.x, screen_y + RACKET_SIZE // 2 - 10)
        handle_end = (self.x + 25, screen_y + RACKET_SIZE // 2 + 20)
        pygame.draw.line(screen, (139, 90, 43), handle_start, handle_end, 8)

        # 球拍框
        pygame.draw.ellipse(screen, color, racket_rect)
        pygame.draw.ellipse(screen, WHITE, racket_rect, 2)

        # 球拍网格
        for i in range(-3, 4):
            offset_x = i * (RACKET_SIZE // 8)
            pygame.draw.line(screen, WHITE,
                           (self.x + offset_x, screen_y - RACKET_SIZE // 2 + 5),
                           (self.x + offset_x, screen_y + RACKET_SIZE // 2 - 5), 1)
        for i in range(-3, 4):
            offset_y = i * (RACKET_SIZE // 8)
            pygame.draw.line(screen, WHITE,
                           (self.x - RACKET_SIZE // 2 + 5, screen_y + offset_y),
                           (self.x + RACKET_SIZE // 2 - 5, screen_y + offset_y), 1)


class BadmintonGame:
    """羽毛球游戏主类"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("羽毛球 - Badminton")
        self.clock = pygame.time.Clock()
        self.font = get_chinese_font(36)
        self.large_font = get_chinese_font(72)
        self.small_font = get_chinese_font(24)

        self.state = "menu"  # menu, serving, playing, point, game_over
        self.player_score = 0
        self.ai_score = 0
        self.win_score = 21
        self.serving_player = "player"
        self.rally_count = 0  # 回合数

        self.shuttlecock = Shuttlecock()
        self.player_racket = Racket(SCREEN_WIDTH // 2, SINGLE_TOP + SINGLE_HEIGHT - 100, is_ai=False)
        self.ai_racket = Racket(SCREEN_WIDTH // 2, SINGLE_TOP + 100, is_ai=True)

        self.hit_effects = []
        self.message_timer = 0
        self.message = ""
        self.sound_enabled = True

    def reset_rally(self):
        """重置回合"""
        self.shuttlecock.reset()
        self.shuttlecock.is_in_play = False
        self.rally_count = 0

    def reset_game(self):
        """重置游戏"""
        self.player_score = 0
        self.ai_score = 0
        self.serving_player = "player"
        self.reset_rally()

    def add_point(self, player):
        """得分"""
        if player == "player":
            self.player_score += 1
        else:
            self.ai_score += 1

        self.message = f"{'玩家' if player == 'player' else 'AI'}得分!"
        self.message_timer = 90
        self.rally_count = 0

        # 轮流发球
        self.serving_player = "ai" if player == "player" else "player"

        # 检查是否有人获胜
        if self.player_score >= self.win_score or self.ai_score >= self.win_score:
            self.state = "game_over"
        else:
            self.reset_rally()
            self.state = "serving"

    def draw_court(self):
        """绘制羽毛球场"""
        # 场地背景
        self.screen.fill(GREEN)

        # 球场边线外区域
        pygame.draw.rect(self.screen, COURT_BLUE,
                        (COURT_LEFT, COURT_TOP, COURT_WIDTH, COURT_HEIGHT))

        # 边线
        pygame.draw.rect(self.screen, WHITE,
                        (COURT_LEFT, COURT_TOP, COURT_WIDTH, COURT_HEIGHT), 3)

        # 单打边线
        pygame.draw.rect(self.screen, WHITE,
                        (SINGLE_LEFT, SINGLE_TOP, SINGLE_WIDTH, SINGLE_HEIGHT), 2)

        # 中线
        pygame.draw.line(self.screen, WHITE,
                        (NET_X, SINGLE_TOP),
                        (NET_X, SINGLE_TOP + SINGLE_HEIGHT), 2)

        # 发球线（前场线）
        service_line_y = SINGLE_TOP + SINGLE_HEIGHT // 2
        pygame.draw.line(self.screen, WHITE,
                        (SINGLE_LEFT, service_line_y),
                        (SINGLE_LEFT + SINGLE_WIDTH, service_line_y), 2)

        # 左右发球线
        mid_x = (SINGLE_LEFT + SINGLE_LEFT + SINGLE_WIDTH) // 2
        pygame.draw.line(self.screen, WHITE,
                        (mid_x, SINGLE_TOP),
                        (mid_x, service_line_y), 2)
        pygame.draw.line(self.screen, WHITE,
                        (mid_x, service_line_y),
                        (mid_x, SINGLE_TOP + SINGLE_HEIGHT), 2)

        # 球网
        # 网柱
        pygame.draw.rect(self.screen, WHITE,
                        (NET_X - 5, SCREEN_HEIGHT // 2 - NET_HEIGHT, 10, NET_HEIGHT))

        # 网面
        for i in range(-30, 31):
            x = NET_X + i * 2
            y_top = SCREEN_HEIGHT // 2 - NET_HEIGHT + 5
            pygame.draw.line(self.screen, NET_MESH_COLOR,
                           (x, y_top), (x, SCREEN_HEIGHT // 2), 1)

        # 网顶白边
        pygame.draw.line(self.screen, WHITE,
                        (NET_X - 60, SCREEN_HEIGHT // 2 - NET_HEIGHT),
                        (NET_X + 60, SCREEN_HEIGHT // 2 - NET_HEIGHT), 3)

    def draw_score(self):
        """绘制比分"""
        # 玩家分数（底部）
        player_color = BLUE
        player_text = self.font.render(f"玩家: {self.player_score}", True, player_color)
        self.screen.blit(player_text, (50, SCREEN_HEIGHT - 50))

        # AI分数（顶部）
        ai_text = self.font.render(f"AI: {self.ai_score}", True, RED)
        self.screen.blit(ai_text, (50, 15))

        # 中间显示回合
        rally_text = self.small_font.render(f"回合: {self.rally_count}", True, WHITE)
        self.screen.blit(rally_text, (SCREEN_WIDTH - 120, 15))

        # 发球指示
        serve_text = self.small_font.render(
            f"{'玩家' if self.serving_player == 'player' else 'AI'}发球", True, YELLOW)
        self.screen.blit(serve_text, (SCREEN_WIDTH // 2 - serve_text.get_width() // 2, 5))

        # 消息显示
        if self.message_timer > 0:
            msg = self.large_font.render(self.message, True, YELLOW)
            self.screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            self.message_timer -= 1

    def draw_menu(self):
        """绘制菜单"""
        self.screen.fill(BLACK)

        # 标题
        title = self.large_font.render("羽毛球", True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 80))

        subtitle = self.font.render("Badminton Game", True, GREEN)
        self.screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 150))

        # 菜单选项
        menu_items = [
            "按 1 - 开始游戏",
            "按 Q - 退出"
        ]

        for i, item in enumerate(menu_items):
            text = self.font.render(item, True, WHITE)
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 280 + i * 50))

        # 操作说明
        controls = [
            "操作说明:",
            "左右/AD - 移动球拍",
            "上下/WASD - 移动位置",
            "空格键 - 挥拍击球",
            "Shift - 高球拍（扣杀准备）",
            "",
            "提示: 羽毛球会飘浮，",
            "需要预判落点!"
        ]

        for i, ctrl in enumerate(controls):
            color = GRAY if i > 0 else WHITE
            text = self.small_font.render(ctrl, True, color)
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 420 + i * 28))

    def draw_serving_instruction(self):
        """绘制发球指示"""
        if self.state == "serving":
            if self.serving_player == "player" and not self.shuttlecock.is_in_play:
                text = self.font.render("按空格键发球", True, YELLOW)
                self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2))

    def add_hit_effect(self, x, y):
        """添加击球特效"""
        self.hit_effects.append({'x': x, 'y': y, 'radius': 5, 'alpha': 200})

    def draw_hit_effect(self):
        """绘制击球特效"""
        for effect in self.hit_effects[:]:
            pygame.draw.circle(self.screen, ORANGE,
                             (int(effect['x']), int(effect['y'])),
                             effect['radius'])
            effect['radius'] += 8
            effect['alpha'] -= 40
            if effect['alpha'] <= 0:
                self.hit_effects.remove(effect)

    def handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if self.state == "menu":
                    if event.key == pygame.K_1:
                        self.reset_game()
                        self.state = "serving"
                    elif event.key == pygame.K_q:
                        return False

                elif self.state == "serving":
                    if event.key == pygame.K_SPACE and self.serving_player == "player":
                        self.shuttlecock.serve(server_is_player=True)
                        self.state = "playing"

                elif self.state == "game_over":
                    if event.key == pygame.K_SPACE:
                        self.state = "menu"

        return True

    def update(self):
        """更新游戏"""
        if self.state not in ["serving", "playing"]:
            return

        # 更新球拍
        self.player_racket.update(self.shuttlecock)
        self.ai_racket.update(self.shuttlecock)

        # AI发球
        if self.state == "serving" and self.serving_player == "ai":
            if random.random() < 0.015:
                self.shuttlecock.serve(server_is_player=False)
                self.state = "playing"

        # 更新羽毛球
        if self.state == "playing":
            result = self.shuttlecock.update()

            # 检测击球
            if self.player_racket.check_hit(self.shuttlecock):
                self.add_hit_effect(self.shuttlecock.x, self.shuttlecock.y)
                self.rally_count += 1

            if self.ai_racket.check_hit(self.shuttlecock):
                self.add_hit_effect(self.shuttlecock.x, self.shuttlecock.y)
                self.rally_count += 1

            # 判定结果
            if result == "ground":
                # 球落地
                if self.shuttlecock.y > NET_X:
                    # 球在玩家半场落地，玩家失分
                    self.add_point("ai")
                else:
                    # 球在AI半场落地，AI失分
                    self.add_point("player")

            elif result == "out_y":
                self.add_point("ai" if self.shuttlecock.y < NET_X else "player")

            elif result == "out_x":
                self.add_point("ai")

            # 超时判定（球速过慢）
            speed = math.sqrt(self.shuttlecock.vx**2 + self.shuttlecock.vy**2)
            if speed < 0.5 and self.shuttlecock.z < 5:
                if self.shuttlecock.y > NET_X:
                    self.add_point("ai")
                else:
                    self.add_point("player")

    def draw(self):
        """绘制"""
        if self.state == "menu":
            self.draw_menu()
        else:
            self.draw_court()
            self.shuttlecock.draw(self.screen)
            self.player_racket.draw(self.screen)
            self.ai_racket.draw(self.screen)
            self.draw_score()
            self.draw_hit_effect()
            self.draw_serving_instruction()

            if self.state == "game_over":
                self.draw_game_over()

        pygame.display.flip()

    def draw_game_over(self):
        """绘制游戏结束"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        if self.player_score > self.ai_score:
            result = "恭喜获胜!"
            color = GREEN
        else:
            result = "AI获胜!"
            color = RED

        result_text = self.large_font.render(result, True, color)
        self.screen.blit(result_text, (SCREEN_WIDTH // 2 - result_text.get_width() // 2, 200))

        score_text = self.font.render(f"最终比分: {self.player_score} - {self.ai_score}", True, WHITE)
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 300))

        restart = self.font.render("按 SPACE 返回菜单", True, WHITE)
        self.screen.blit(restart, (SCREEN_WIDTH // 2 - restart.get_width() // 2, 400))

    def run(self):
        """运行游戏"""
        running = True

        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = BadmintonGame()
    game.run()
