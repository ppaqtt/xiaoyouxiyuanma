#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
乒乓球游戏 - Table Tennis Game
真实的乒乓球物理模拟，支持AI对战
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
SCREEN_HEIGHT = 600
FPS = 60

# 颜色定义
WHITE = (255, 255, 255)
GREEN = (34, 139, 34)
BLUE = (0, 105, 148)
RED = (220, 20, 60)
BLACK = (0, 0, 0)
ORANGE = (255, 140, 0)
GRAY = (128, 128, 128)
LIGHT_BLUE = (173, 216, 230)

# 乒乓球参数
BALL_RADIUS = 8
BALL_SPEED_INITIAL = 8
BALL_MAX_SPEED = 18
BALL_SPIN_FACTOR = 0.15

# 球拍参数
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 15
PADDLE_SPEED = 10
AI_PADDLE_SPEED = 7

# 球桌参数
TABLE_LENGTH = 800
TABLE_HEIGHT = 400
TABLE_TOP = 100
TABLE_LEFT = (SCREEN_WIDTH - TABLE_LENGTH) // 2

class Ball:
    """乒乓球类 - 实现真实的物理模拟"""
    def __init__(self):
        self.reset()
        self.trail = []  # 球轨迹

    def reset(self):
        """重置球到中心"""
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        # 随机初始角度（-45到45度或135到225度）
        angle = random.uniform(-math.pi/4, math.pi/4)
        if random.random() < 0.5:
            angle += math.pi
        self.vx = math.cos(angle) * BALL_SPEED_INITIAL
        self.vy = math.sin(angle) * BALL_SPEED_INITIAL
        self.speed = BALL_SPEED_INITIAL
        self.spin = 0  # 旋转（水平速度加成）
        self.trail = []

    def update(self):
        """更新球的位置和物理"""
        # 添加当前位置到轨迹
        self.trail.append((self.x, self.y))
        if len(self.trail) > 15:
            self.trail.pop(0)

        # 应用旋转效果
        self.vx += self.spin * 0.3
        self.spin *= 0.95  # 旋转衰减

        # 更新位置
        self.x += self.vx
        self.y += self.vy

        # 边界碰撞检测
        # 上下边界
        if self.y - BALL_RADIUS < TABLE_TOP:
            self.y = TABLE_TOP + BALL_RADIUS
            self.vy = -self.vy * 0.95
        if self.y + BALL_RADIUS > TABLE_TOP + TABLE_HEIGHT:
            self.y = TABLE_TOP + TABLE_HEIGHT - BALL_RADIUS
            self.vy = -self.vy * 0.95

        # 左右边界（出界判定）
        if self.x - BALL_RADIUS < TABLE_LEFT:
            return -1  # 左边界出界
        if self.x + BALL_RADIUS > TABLE_LEFT + TABLE_LENGTH:
            return 1   # 右边界出界

        return 0  # 正常

    def draw(self, screen):
        """绘制球和轨迹"""
        # 绘制轨迹
        for i, pos in enumerate(self.trail):
            alpha = int(255 * (i / len(self.trail)) * 0.3)
            size = int(BALL_RADIUS * (i / len(self.trail)))
            if size > 0:
                trail_color = (255, 165, 0)
                pygame.draw.circle(screen, trail_color, (int(pos[0]), int(pos[1])), size)

        # 绘制球
        pygame.draw.circle(screen, ORANGE, (int(self.x), int(self.y)), BALL_RADIUS)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), BALL_RADIUS, 2)

    def check_paddle_collision(self, paddle):
        """检测与球拍的碰撞"""
        # 球拍矩形
        paddle_rect = pygame.Rect(
            paddle.x - PADDLE_WIDTH // 2,
            paddle.y - PADDLE_HEIGHT // 2,
            PADDLE_WIDTH,
            PADDLE_HEIGHT
        )

        # 检测碰撞
        closest_x = max(paddle_rect.left, min(self.x, paddle_rect.right))
        closest_y = max(paddle_rect.top, min(self.y, paddle_rect.bottom))

        distance_x = self.x - closest_x
        distance_y = self.y - closest_y
        distance = math.sqrt(distance_x ** 2 + distance_y ** 2)

        if distance < BALL_RADIUS:
            # 计算碰撞角度
            hit_pos = (self.x - paddle.x) / (PADDLE_WIDTH / 2)  # -1 到 1

            # 根据击中位置调整反弹角度
            max_angle = math.pi / 3  # 最大反弹角度60度
            angle = hit_pos * max_angle

            # 增加速度
            self.speed = min(self.speed * 1.05, BALL_MAX_SPEED)

            # 根据球拍移动方向添加旋转
            if hasattr(paddle, 'last_x'):
                paddle_move = paddle.x - paddle.last_x
                self.spin += paddle_move * BALL_SPIN_FACTOR

            # 设置新速度
            if paddle.is_ai:
                # AI的球拍在下方，球向上飞
                self.vx = math.sin(angle) * self.speed
                self.vy = -math.cos(angle) * self.speed
            else:
                # 玩家球拍在上方，球向下飞
                self.vx = math.sin(angle) * self.speed
                self.vy = math.cos(angle) * self.speed

            return True
        return False


class Paddle:
    """球拍类"""
    def __init__(self, y, is_ai=False):
        self.x = SCREEN_WIDTH // 2
        self.y = y
        self.is_ai = is_ai
        self.last_x = self.x
        self.score = 0

    def update(self, ball=None):
        """更新球拍位置"""
        self.last_x = self.x

        if self.is_ai:
            # AI控制 - 根据球的移动预测
            if ball:
                # 预测球的位置
                predict_x = ball.x + ball.vx * 10

                # AI有一定的反应延迟和误差
                if ball.vy > 0:  # 球正在向下飞（面向AI）
                    if predict_x > self.x + 20:
                        self.x += AI_PADDLE_SPEED
                    elif predict_x < self.x - 20:
                        self.x -= AI_PADDLE_SPEED
                else:
                    # 球飞向对方，返回中心
                    if self.x > SCREEN_WIDTH // 2 + 50:
                        self.x -= AI_PADDLE_SPEED * 0.5
                    elif self.x < SCREEN_WIDTH // 2 - 50:
                        self.x += AI_PADDLE_SPEED * 0.5
        else:
            # 玩家控制
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.x -= PADDLE_SPEED
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.x += PADDLE_SPEED

        # 边界限制
        self.x = max(TABLE_LEFT + PADDLE_WIDTH // 2,
                     min(TABLE_LEFT + TABLE_LENGTH - PADDLE_WIDTH // 2, self.x))

    def draw(self, screen):
        """绘制球拍"""
        color = BLUE if not self.is_ai else RED
        pygame.draw.rect(screen, color,
                        (self.x - PADDLE_WIDTH // 2,
                         self.y - PADDLE_HEIGHT // 2,
                         PADDLE_WIDTH,
                         PADDLE_HEIGHT))
        # 球拍边缘高亮
        pygame.draw.rect(screen, WHITE,
                        (self.x - PADDLE_WIDTH // 2,
                         self.y - PADDLE_HEIGHT // 2,
                         PADDLE_WIDTH,
                         PADDLE_HEIGHT), 2)


class TableTennisGame:
    """乒乓球游戏主类"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("乒乓球 - Table Tennis")
        self.clock = pygame.time.Clock()
        self.font = get_chinese_font(36)
        self.large_font = get_chinese_font(72)

        self.state = "menu"  # menu, playing, paused, game_over
        self.player_score = 0
        self.ai_score = 0
        self.win_score = 11
        self.serving = True  # 轮流发球

        self.ball = Ball()
        self.player_paddle = Paddle(TABLE_TOP + 60, is_ai=False)
        self.ai_paddle = Paddle(TABLE_TOP + TABLE_HEIGHT - 60, is_ai=True)

        self.hit_effects = []  # 击球特效

    def reset_round(self):
        """重置回合"""
        self.ball.reset()
        # 发球方向
        if self.serving:
            self.ball.vy = abs(self.ball.vy)  # 向下发球
        else:
            self.ball.vy = -abs(self.ball.vy)  # 向上发球

    def reset_game(self):
        """重置游戏"""
        self.player_score = 0
        self.ai_score = 0
        self.serving = True
        self.ball.reset()
        self.ball.vy = -abs(self.ball.vy)

    def draw_table(self):
        """绘制球桌"""
        # 背景
        self.screen.fill(GREEN)

        # 球桌边框
        pygame.draw.rect(self.screen, WHITE,
                        (TABLE_LEFT - 10, TABLE_TOP - 10,
                         TABLE_LENGTH + 20, TABLE_HEIGHT + 20), 3)

        # 球桌表面
        pygame.draw.rect(self.screen, LIGHT_BLUE,
                        (TABLE_LEFT, TABLE_TOP, TABLE_LENGTH, TABLE_HEIGHT))

        # 中线
        pygame.draw.line(self.screen, WHITE,
                        (SCREEN_WIDTH // 2, TABLE_TOP),
                        (SCREEN_WIDTH // 2, TABLE_TOP + TABLE_HEIGHT), 2)

        # 中线圆
        pygame.draw.circle(self.screen, WHITE, (SCREEN_WIDTH // 2, TABLE_TOP + TABLE_HEIGHT // 2), 40, 2)

        # 边线
        pygame.draw.rect(self.screen, WHITE,
                        (TABLE_LEFT, TABLE_TOP, TABLE_LENGTH, TABLE_HEIGHT), 2)

    def draw_score(self):
        """绘制比分"""
        # 玩家分数（上方）
        player_text = self.font.render(f"玩家: {self.player_score}", True, BLUE)
        self.screen.blit(player_text, (SCREEN_WIDTH // 2 - 100, 30))

        # AI分数（下方）
        ai_text = self.font.render(f"AI: {self.ai_score}", True, RED)
        self.screen.blit(ai_text, (SCREEN_WIDTH // 2 + 20, 30))

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

    def add_hit_effect(self, x, y):
        """添加击球特效"""
        self.hit_effects.append({'x': x, 'y': y, 'radius': 5, 'alpha': 200})

    def draw_menu(self):
        """绘制菜单界面"""
        self.screen.fill(BLACK)

        # 标题
        title = self.large_font.render("乒乓球", True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))

        subtitle = self.font.render("Table Tennis", True, ORANGE)
        self.screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 170))

        # 菜单选项
        menu_items = [
            "按 1 - 开始游戏",
            "按 2 - AI难度: 中等",
            "按 Q - 退出"
        ]

        for i, item in enumerate(menu_items):
            text = self.font.render(item, True, WHITE)
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 300 + i * 50))

        # 操作说明
        controls = self.font.render("操作: 左右箭头或A/D键移动球拍", True, GRAY)
        self.screen.blit(controls, (SCREEN_WIDTH // 2 - controls.get_width() // 2, 500))

    def draw_game_over(self):
        """绘制游戏结束界面"""
        # 半透明遮罩
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        # 结果文本
        if self.player_score >= self.win_score:
            result = "恭喜获胜!"
            color = GREEN
        else:
            result = "AI获胜!"
            color = RED

        result_text = self.large_font.render(result, True, color)
        self.screen.blit(result_text, (SCREEN_WIDTH // 2 - result_text.get_width() // 2, 200))

        # 比分
        score_text = self.font.render(f"最终比分: {self.player_score} - {self.ai_score}", True, WHITE)
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 300))

        # 重新开始提示
        restart = self.font.render("按 SPACE 重新开始", True, WHITE)
        self.screen.blit(restart, (SCREEN_WIDTH // 2 - restart.get_width() // 2, 400))

    def handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if self.state == "menu":
                    if event.key == pygame.K_1:
                        self.state = "playing"
                        self.reset_game()
                    elif event.key == pygame.K_q:
                        return False

                elif self.state == "playing":
                    if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                        self.state = "paused"

                elif self.state == "paused":
                    if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                        self.state = "playing"
                    elif event.key == pygame.K_q:
                        self.state = "menu"

                elif self.state == "game_over":
                    if event.key == pygame.K_SPACE:
                        self.state = "menu"

        return True

    def update(self):
        """更新游戏状态"""
        if self.state != "playing":
            return

        # 更新球拍
        self.player_paddle.update()
        self.ai_paddle.update(self.ball)

        # 更新球
        result = self.ball.update()

        # 检测碰撞
        if self.ball.check_paddle_collision(self.player_paddle):
            self.add_hit_effect(self.ball.x, self.ball.y)
        if self.ball.check_paddle_collision(self.ai_paddle):
            self.add_hit_effect(self.ball.x, self.ball.y)

        # 得分判定
        if result != 0:
            if result == -1:  # 球从左边出界
                if self.ball.vy > 0:  # 飞向AI方向
                    self.player_score += 1
                    self.serving = False
                else:
                    self.ai_score += 1
                    self.serving = True
            elif result == 1:  # 球从右边出界
                if self.ball.vy < 0:  # 飞向玩家方向
                    self.ai_score += 1
                    self.serving = True
                else:
                    self.player_score += 1
                    self.serving = False

            # 检查是否有人获胜
            if self.player_score >= self.win_score or self.ai_score >= self.win_score:
                self.state = "game_over"
            else:
                self.reset_round()

    def draw(self):
        """绘制画面"""
        if self.state == "menu":
            self.draw_menu()
        else:
            self.draw_table()
            self.ball.draw(self.screen)
            self.player_paddle.draw(self.screen)
            self.ai_paddle.draw(self.screen)
            self.draw_score()
            self.draw_hit_effect()

            if self.state == "paused":
                pause_text = self.large_font.render("暂停", True, WHITE)
                self.screen.blit(pause_text,
                               (SCREEN_WIDTH // 2 - pause_text.get_width() // 2,
                                SCREEN_HEIGHT // 2 - 50))
                hint = self.font.render("按 P 继续", True, GRAY)
                self.screen.blit(hint,
                               (SCREEN_WIDTH // 2 - hint.get_width() // 2,
                                SCREEN_HEIGHT // 2 + 20))

            elif self.state == "game_over":
                self.draw_game_over()

        pygame.display.flip()

    def run(self):
        """运行游戏主循环"""
        running = True

        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = TableTennisGame()
    game.run()
