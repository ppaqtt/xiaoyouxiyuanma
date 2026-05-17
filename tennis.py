#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网球游戏 - Tennis Game
真实的网球物理模拟，支持AI对战模式
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
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
FPS = 60

# 颜色定义
WHITE = (255, 255, 255)
GREEN = (50, 150, 50)
CLAY = (200, 120, 80)
GRAY = (200, 200, 200)
BLUE = (30, 30, 180)
RED = (180, 30, 30)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
LIGHT_GREEN = (144, 238, 144)
LINE_COLOR = WHITE

# 网球参数
BALL_RADIUS = 6
BALL_SPEED_INITIAL = 12
BALL_MAX_SPEED = 25
GRAVITY = 0.4
AIR_RESISTANCE = 0.995
BOUNCE_FACTOR = 0.7

# 球拍参数
RACKET_LENGTH = 120
RACKET_WIDTH = 30
RACKET_SPEED = 12
AI_RACKET_SPEED = 8

# 球场参数（标准网球场的俯视图简化版）
COURT_WIDTH = 1000
COURT_HEIGHT = 500
COURT_LEFT = (SCREEN_WIDTH - COURT_WIDTH) // 2
COURT_TOP = 100

# 网球场地尺寸（单打）
SINGLE_WIDTH = 840
SINGLE_HEIGHT = 400
SINGLE_LEFT = COURT_LEFT + (COURT_WIDTH - SINGLE_WIDTH) // 2
SINGLE_TOP = COURT_TOP + (COURT_HEIGHT - SINGLE_HEIGHT) // 2

# 发球线位置
BASELINE_PLAYER = SINGLE_TOP + SINGLE_HEIGHT - 50
BASELINE_AI = SINGLE_TOP + 50
NET_HEIGHT = 100
NET_Y = SCREEN_HEIGHT // 2


class TennisBall:
    """网球类 - 实现三维物理模拟"""
    def __init__(self):
        self.reset()

    def reset(self, serving_side="player"):
        """重置球"""
        if serving_side == "player":
            self.x = SCREEN_WIDTH // 2
            self.y = BASELINE_PLAYER - 50
        else:
            self.x = SCREEN_WIDTH // 2
            self.y = BASELINE_AI + 50

        self.z = 0  # 高度
        self.vx = 0
        self.vy = 0
        self.vz = 0  # 垂直速度
        self.speed = BALL_SPEED_INITIAL
        self.rotation = [0, 0, 0]  # 球的旋转
        self.trail = []
        self.is_in_play = False

    def serve(self, player_serving=True):
        """发球"""
        self.is_in_play = True
        # 随机发球角度
        direction = 1 if player_serving else -1
        angle = random.uniform(-math.pi/6, math.pi/6)
        self.vx = math.sin(angle) * self.speed * 0.3
        self.vy = math.cos(angle) * self.speed * direction
        self.vz = random.uniform(3, 5)  # 初始上升速度
        self.z = 0

    def update(self):
        """更新球的物理"""
        if not self.is_in_play:
            return

        # 添加轨迹点
        self.trail.append((self.x, self.y, self.z))
        if len(self.trail) > 20:
            self.trail.pop(0)

        # 应用重力
        self.vz -= GRAVITY

        # 应用空气阻力
        self.vx *= AIR_RESISTANCE
        self.vy *= AIR_RESISTANCE

        # 更新位置
        self.x += self.vx
        self.y += self.vy
        self.z += self.vz

        # 地面反弹
        if self.z <= 0:
            self.z = 0
            self.vz = -self.vz * BOUNCE_FACTOR

            # 地面摩擦
            self.vx *= 0.8
            self.vy *= 0.8

            # 停止条件
            if abs(self.vz) < 0.5:
                self.vz = 0

        # 网球越位检测
        if self.y < SINGLE_TOP - 50 or self.y > SINGLE_TOP + SINGLE_HEIGHT + 50:
            return -1 if self.y > NET_Y else 1  # 出界方向
        if self.x < SINGLE_LEFT - 50 or self.x > SINGLE_LEFT + SINGLE_WIDTH + 50:
            return 0  # 边线出界

        # 网球碰到网
        if SINGLE_LEFT < self.x < SINGLE_LEFT + SINGLE_WIDTH:
            if abs(self.y - NET_Y) < 10 and self.z < NET_HEIGHT:
                self.vy = -self.vy * 0.5
                self.vz = abs(self.vz) * 0.5
                self.y = NET_Y - 10 if self.vy < 0 else NET_Y + 10

        return None  # 正常

    def draw(self, screen):
        """绘制球（考虑高度）"""
        if not self.is_in_play:
            return

        # 绘制轨迹
        for i, (tx, ty, tz) in enumerate(self.trail):
            alpha = int(255 * (i / len(self.trail)) * 0.4)
            size = max(2, int(BALL_RADIUS * (i / len(self.trail))))
            screen_y = ty - int(tz * 0.8)  # 高度影响屏幕位置
            color = (255, 200, 0)
            pygame.draw.circle(screen, color, (int(tx), int(screen_y)), size)

        # 计算球的屏幕位置
        screen_y = self.y - int(self.z * 0.8)

        # 绘制阴影
        shadow_y = self.y
        shadow_alpha = max(50, 200 - int(self.z * 5))
        shadow_size = int(BALL_RADIUS * (1 - self.z / 200))
        if shadow_size > 0:
            pygame.draw.circle(screen, (0, 0, 0), (int(self.x), int(shadow_y)), shadow_size)

        # 绘制球
        if screen_y > 0 and screen_y < SCREEN_HEIGHT:
            pygame.draw.circle(screen, YELLOW, (int(self.x), int(screen_y)), BALL_RADIUS)
            pygame.draw.circle(screen, WHITE, (int(self.x), int(screen_y)), BALL_RADIUS, 1)

    def get_ground_y(self):
        """获取球落地时的Y坐标"""
        if self.vz <= 0:
            return self.y
        # 预测落地位置
        time = self.z / self.vz if self.vz > 0 else 0
        return self.y + self.vy * time


class Racket:
    """球拍类"""
    def __init__(self, x, y, is_ai=False):
        self.x = x
        self.y = y
        self.z = 0  # 球拍高度
        self.target_z = 0
        self.is_ai = is_ai
        self.last_x = x
        self.last_y = y
        self.swing_angle = 0
        self.is_swinging = False
        self.swing_direction = 0

    def update(self, ball=None):
        """更新球拍"""
        self.last_x = self.x
        self.last_y = self.y

        if self.is_ai:
            # AI控制
            if ball and ball.is_in_play:
                # 预测球的位置
                predict_time = abs(ball.y - self.y) / (abs(ball.vy) + 1) if ball.vy != 0 else 1
                predict_x = ball.x + ball.vx * predict_time * 0.5
                predict_y = ball.y

                # 移动球拍
                if predict_x > self.x + 30:
                    self.x += AI_RACKET_SPEED
                elif predict_x < self.x - 30:
                    self.x -= AI_RACKET_SPEED

                # 调整高度
                if ball.z > 50:
                    self.target_z = ball.z * 0.5
                else:
                    self.target_z = 20

                self.z += (self.target_z - self.z) * 0.1

                # AI发球/击球
                if not self.is_swinging and ball.y > NET_Y and ball.y < BASELINE_PLAYER:
                    if abs(ball.x - self.x) < RACKET_LENGTH // 2:
                        self.swing()
        else:
            # 玩家控制
            keys = pygame.key.get_pressed()

            # 左右移动
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.x -= RACKET_SPEED
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.x += RACKET_SPEED

            # 上下移动（模拟前后移动）
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.y -= RACKET_SPEED * 0.5
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.y += RACKET_SPEED * 0.5

            # 高度控制
            if keys[pygame.K_SPACE]:
                self.target_z = 80
            else:
                self.target_z = 20

            self.z += (self.target_z - self.z) * 0.15

            # 挥拍
            if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                if not self.is_swinging:
                    self.swing()

        # 边界限制
        self.x = max(SINGLE_LEFT + RACKET_LENGTH // 2,
                     min(SINGLE_LEFT + SINGLE_WIDTH - RACKET_LENGTH // 2, self.x))
        self.y = max(SINGLE_TOP + RACKET_LENGTH // 2,
                     min(SINGLE_TOP + SINGLE_HEIGHT - RACKET_LENGTH // 2, self.y))
        self.z = max(0, min(150, self.z))

        # 更新挥拍动画
        if self.is_swinging:
            self.swing_angle += self.swing_direction * 0.3
            if abs(self.swing_angle) > math.pi / 3:
                self.swing_direction = 0
                self.swing_angle = 0
                self.is_swinging = False

    def swing(self):
        """挥拍"""
        self.is_swinging = True
        self.swing_direction = 1 if self.is_ai else -1

    def check_hit(self, ball):
        """检测是否击中球"""
        if not self.is_swinging:
            return False

        if not ball.is_in_play:
            return False

        # 计算距离（考虑高度）
        dx = ball.x - self.x
        dy = ball.y - self.y
        dz = ball.z - self.z
        distance = math.sqrt(dx**2 + dy**2 + dz**2)

        # 击中范围
        hit_range = RACKET_LENGTH // 2 + BALL_RADIUS

        if distance < hit_range:
            # 计算反弹
            angle = math.atan2(dy, dx)
            power = min(ball.speed * 1.1 + 3, BALL_MAX_SPEED)

            ball.vx = math.cos(angle) * power * 0.5 + (self.x - self.last_x) * 0.2
            ball.vy = -abs(math.sin(angle) * power) if not self.is_ai else abs(math.sin(angle) * power)
            ball.vz = abs(self.vz) * 0.5 + random.uniform(2, 5)
            ball.z = self.z + 10

            # 球的旋转
            ball.rotation[0] += (self.y - self.last_y) * 0.1

            return True

        return False

    def draw(self, screen):
        """绘制球拍"""
        color = BLUE if not self.is_ai else RED
        screen_y = self.y - int(self.z * 0.8)

        # 球拍矩形（简化表示）
        pygame.draw.ellipse(screen, color,
                           (int(self.x - RACKET_WIDTH // 2),
                            int(screen_y - RACKET_LENGTH // 2),
                            RACKET_WIDTH,
                            RACKET_LENGTH))

        # 握柄
        grip_end_y = screen_y + RACKET_LENGTH // 2 + 20
        pygame.draw.line(screen, (139, 90, 43),
                        (self.x, screen_y + RACKET_LENGTH // 2),
                        (self.x, grip_end_y), 8)

        pygame.draw.ellipse(screen, color,
                           (int(self.x - RACKET_WIDTH // 2),
                            int(screen_y - RACKET_LENGTH // 2),
                            RACKET_WIDTH,
                            RACKET_LENGTH), 2)


class TennisGame:
    """网球游戏主类"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("网球 - Tennis")
        self.clock = pygame.time.Clock()
        self.font = get_chinese_font(36)
        self.large_font = get_chinese_font(72)
        self.small_font = get_chinese_font(24)

        self.state = "menu"  # menu, serving, playing, point, game_over
        self.player_score = 0  # 玩家局数
        self.ai_score = 0
        self.player_points = 0  # 玩家本局分数
        self.ai_points = 0
        self.serving_player = "player"

        # 网球计分：0, 15, 30, 40, Ad
        self.score_names = {0: "0", 1: "15", 2: "30", 3: "40"}

        self.ball = TennisBall()
        self.player_racket = Racket(SCREEN_WIDTH // 2, BASELINE_PLAYER, is_ai=False)
        self.ai_racket = Racket(SCREEN_WIDTH // 2, BASELINE_AI, is_ai=True)

        self.hit_effects = []
        self.message_timer = 0
        self.message = ""

    def reset_point(self):
        """重置分数"""
        self.ball.reset()
        self.ball.is_in_play = False
        self.player_points = 0
        self.ai_points = 0
        self.state = "serving"

    def reset_game(self):
        """重置游戏"""
        self.player_score = 0
        self.ai_score = 0
        self.serving_player = "player"
        self.reset_point()

    def add_point(self, player):
        """得分"""
        if player == "player":
            self.player_points += 1
        else:
            self.ai_points += 1
        self.message = f"{'玩家' if player == 'player' else 'AI'}得分!"
        self.message_timer = 60

        # 检查本局是否结束
        p, a = self.player_points, self.ai_points

        # 常规情况
        if p >= 4 and p - a >= 2:
            self.player_score += 1
            self.serving_player = "ai" if self.serving_player == "player" else "player"
            if self.player_score >= 6:
                self.state = "game_over"
            else:
                self.reset_point()
        elif a >= 4 and a - p >= 2:
            self.ai_score += 1
            self.serving_player = "ai" if self.serving_player == "player" else "player"
            if self.ai_score >= 6:
                self.state = "game_over"
            else:
                self.reset_point()
        # 占先情况
        elif p >= 3 and a >= 3:
            if p - a >= 2:
                self.player_score += 1
                self.serving_player = "ai" if self.serving_player == "player" else "player"
                self.reset_point()
            elif a - p >= 2:
                self.ai_score += 1
                self.serving_player = "ai" if self.serving_player == "player" else "player"
                self.reset_point()

    def get_score_display(self):
        """获取分数显示"""
        p = self.score_names.get(self.player_points, "Ad" if self.player_points > 3 else "40")
        a = self.score_names.get(self.ai_points, "Ad" if self.ai_points > 3 else "40")

        # 占先显示
        if self.player_points >= 3 and self.ai_points >= 3:
            if self.player_points == self.ai_points:
                return "40 - 40"
            elif self.player_points > self.ai_points:
                return "Ad - 40"
            else:
                return "40 - Ad"

        return f"{p} - {a}"

    def draw_court(self):
        """绘制网球场"""
        # 场地背景
        self.screen.fill(GREEN)

        # 边线外区域
        pygame.draw.rect(self.screen, CLAY,
                        (COURT_LEFT, COURT_TOP, COURT_WIDTH, COURT_HEIGHT))

        # 双打边线
        pygame.draw.rect(self.screen, LINE_COLOR,
                        (COURT_LEFT, COURT_TOP, COURT_WIDTH, COURT_HEIGHT), 3)

        # 单打边线
        pygame.draw.rect(self.screen, LINE_COLOR,
                        (SINGLE_LEFT, SINGLE_TOP, SINGLE_WIDTH, SINGLE_HEIGHT), 2)

        # 发球区
        service_center_y = (SINGLE_TOP + SINGLE_TOP + SINGLE_HEIGHT) // 2

        # 中线
        pygame.draw.line(self.screen, LINE_COLOR,
                        (SCREEN_WIDTH // 2, SINGLE_TOP),
                        (SCREEN_WIDTH // 2, SINGLE_TOP + SINGLE_HEIGHT), 2)

        # 发球线
        pygame.draw.line(self.screen, LINE_COLOR,
                        (SINGLE_LEFT, BASELINE_PLAYER),
                        (SINGLE_LEFT + SINGLE_WIDTH, BASELINE_PLAYER), 2)

        pygame.draw.line(self.screen, LINE_COLOR,
                        (SINGLE_LEFT, BASELINE_AI),
                        (SINGLE_LEFT + SINGLE_WIDTH, BASELINE_AI), 2)

        # 服务区
        pygame.draw.line(self.screen, LINE_COLOR,
                        (SINGLE_LEFT, service_center_y),
                        (SINGLE_LEFT + SINGLE_WIDTH, service_center_y), 2)

        # 网
        net_x = SCREEN_WIDTH // 2
        for i in range(-10, 11):
            x = net_x + i * 10
            pygame.draw.line(self.screen, WHITE, (x, NET_Y - NET_HEIGHT), (x, NET_Y), 1)
        pygame.draw.line(self.screen, WHITE,
                         (net_x - 100, NET_Y - NET_HEIGHT),
                         (net_x + 100, NET_Y - NET_HEIGHT), 3)
        pygame.draw.line(self.screen, WHITE,
                         (net_x - 100, NET_Y),
                         (net_x + 100, NET_Y), 3)

    def draw_score(self):
        """绘制比分"""
        # 玩家比分（底部）
        player_text = self.font.render(f"玩家: {self.player_score}", True, BLUE)
        self.screen.blit(player_text, (100, SCREEN_HEIGHT - 60))

        player_pts = self.font.render(f"本局: {self.get_score_display()}", True, WHITE)
        self.screen.blit(player_pts, (100, SCREEN_HEIGHT - 30))

        # AI比分（顶部）
        ai_text = self.font.render(f"AI: {self.ai_score}", True, RED)
        self.screen.blit(ai_text, (SCREEN_WIDTH - 200, 30))

        ai_pts = self.font.render(f"本局: {self.get_score_display()}", True, WHITE)
        self.screen.blit(ai_pts, (SCREEN_WIDTH - 200, 60))

        # 发球指示
        serve_text = self.small_font.render(
            f"{'玩家' if self.serving_player == 'player' else 'AI'}发球", True, YELLOW)
        self.screen.blit(serve_text, (SCREEN_WIDTH // 2 - serve_text.get_width() // 2, 5))

        # 消息显示
        if self.message_timer > 0:
            msg = self.font.render(self.message, True, YELLOW)
            self.screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, SCREEN_HEIGHT // 2))
            self.message_timer -= 1

    def draw_menu(self):
        """绘制菜单"""
        self.screen.fill(BLACK)

        title = self.large_font.render("网球", True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))

        subtitle = self.font.render("Tennis Game", True, GREEN)
        self.screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 170))

        menu_items = [
            "按 1 - 开始游戏",
            "按 Q - 退出"
        ]

        for i, item in enumerate(menu_items):
            text = self.font.render(item, True, WHITE)
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 300 + i * 50))

        controls = [
            "操作说明:",
            "左右/AD - 移动球拍",
            "上下/WASD - 前后移动",
            "空格键 - 抬高球拍（截击）",
            "Shift - 挥拍击球"
        ]

        for i, ctrl in enumerate(controls):
            text = self.small_font.render(ctrl, True, GRAY)
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 450 + i * 30))

    def draw_serving_instruction(self):
        """绘制发球指示"""
        if self.state == "serving":
            if (self.serving_player == "player" and not self.ball.is_in_play):
                text = self.font.render("按空格键发球", True, YELLOW)
                self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2))

    def handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if self.state == "menu":
                    if event.key == pygame.K_1:
                        self.reset_game()
                    elif event.key == pygame.K_q:
                        return False

                elif self.state == "serving":
                    if event.key == pygame.K_SPACE and self.serving_player == "player":
                        self.ball.serve(player_serving=True)
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
        self.player_racket.update(self.ball)
        self.ai_racket.update(self.ball)

        # AI发球
        if self.state == "serving" and self.serving_player == "ai":
            if random.random() < 0.02:  # 随机发球时机
                self.ball.serve(player_serving=False)
                self.state = "playing"

        # 更新球
        if self.state == "playing":
            result = self.ball.update()

            # 检测击球
            if self.player_racket.check_hit(self.ball):
                self.add_hit_effect(self.ball.x, self.ball.y)

            if self.ai_racket.check_hit(self.ball):
                self.add_hit_effect(self.ball.x, self.ball.y)

            # 出界判定
            if result is not None:
                if self.ball.y < NET_Y:
                    self.add_point("ai")
                else:
                    self.add_point("player")

            # 球落地停止
            if self.ball.z <= 0 and abs(self.ball.vz) < 0.1:
                if self.ball.y < NET_Y:
                    self.add_point("ai")
                else:
                    self.add_point("player")

    def add_hit_effect(self, x, y):
        """添加击球特效"""
        self.hit_effects.append({'x': x, 'y': y, 'radius': 5, 'alpha': 200})

    def draw_hit_effect(self):
        """绘制击球特效"""
        for effect in self.hit_effects[:]:
            pygame.draw.circle(self.screen, WHITE,
                             (int(effect['x']), int(effect['y'])),
                             effect['radius'])
            effect['radius'] += 5
            effect['alpha'] -= 30
            if effect['alpha'] <= 0:
                self.hit_effects.remove(effect)

    def draw(self):
        """绘制"""
        if self.state == "menu":
            self.draw_menu()
        else:
            self.draw_court()
            self.ball.draw(self.screen)
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
        self.screen.blit(result_text, (SCREEN_WIDTH // 2 - result_text.get_width() // 2, 250))

        score_text = self.font.render(f"最终比分: {self.player_score} - {self.ai_score}", True, WHITE)
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 350))

        restart = self.font.render("按 SPACE 返回菜单", True, WHITE)
        self.screen.blit(restart, (SCREEN_WIDTH // 2 - restart.get_width() // 2, 450))

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
    game = TennisGame()
    game.run()
