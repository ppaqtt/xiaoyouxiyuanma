"""
沙狐球游戏 (Shuffleboard)
桌上沙狐球模拟游戏：
- 用鼠标控制力度和方向推球
- 球在桌面上滑动减速
- 目标是将球推到得分区域（同心圆靶）
- 离中心越近分数越高
- 玩家和AI各4个球，轮流推球

操作说明：
- 移动鼠标瞄准方向
- 按住左键蓄力，松开推球
- R 重新开始
"""

import pygame
import math
import random
import sys

# 初始化
pygame.init()

# 常量
SCREEN_W, SCREEN_H = 600, 900
FPS = 60

# 颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 40, 40)
BLUE = (40, 80, 200)
YELLOW = (255, 215, 0)
GOLD = (255, 200, 50)
GREEN = (50, 180, 50)
DARK_GREEN = (20, 80, 20)
BROWN = (139, 90, 43)
DARK_BROWN = (100, 60, 30)
LIGHT_BROWN = (180, 130, 70)
GRAY = (150, 150, 150)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (80, 80, 80)
CREAM = (245, 235, 210)
TABLE_COLOR = (60, 130, 60)
FELT_COLOR = (50, 120, 50)

# 桌面区域
TABLE_LEFT = 50
TABLE_RIGHT = 550
TABLE_TOP = 50
TABLE_BOTTOM = 850
TABLE_W = TABLE_RIGHT - TABLE_LEFT
TABLE_H = TABLE_BOTTOM - TABLE_TOP
TABLE_CX = (TABLE_LEFT + TABLE_RIGHT) // 2
TABLE_CY = (TABLE_TOP + TABLE_BOTTOM) // 2

# 靶心位置（桌面上方）
TARGET_CY = 200
# 球的起始位置
START_Y = 750

# 球的属性
BALL_RADIUS = 15
FRICTION = 0.985  # 摩擦系数
MIN_SPEED = 0.1  # 最小速度阈值

# 得分区域半径
ZONE_10_R = 20   # 10分
ZONE_5_R = 50    # 5分
ZONE_3_R = 90    # 3分
ZONE_1_R = 130   # 1分

# 每方球数
BALLS_PER_SIDE = 4


class Ball:
    """沙狐球"""
    def __init__(self, x, y, team):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.team = team  # 0=玩家(红色), 1=AI(蓝色)
        self.radius = BALL_RADIUS
        self.active = False  # 是否已推出
        self.scored = False
        self.score = 0

    def update(self):
        """更新球的位置"""
        if not self.active:
            return
        self.x += self.vx
        self.y += self.vy
        # 摩擦力
        self.vx *= FRICTION
        self.vy *= FRICTION
        # 停止条件
        speed = math.sqrt(self.vx ** 2 + self.vy ** 2)
        if speed < MIN_SPEED:
            self.vx = 0
            self.vy = 0
        # 桌面边界碰撞
        if self.x - self.radius < TABLE_LEFT:
            self.x = TABLE_LEFT + self.radius
            self.vx = -self.vx * 0.5
        if self.x + self.radius > TABLE_RIGHT:
            self.x = TABLE_RIGHT - self.radius
            self.vx = -self.vx * 0.5
        if self.y - self.radius < TABLE_TOP:
            self.y = TABLE_TOP + self.radius
            self.vy = -self.vy * 0.3
        if self.y + self.radius > TABLE_BOTTOM:
            self.y = TABLE_BOTTOM - self.radius
            self.vy = -self.vy * 0.5

    def is_moving(self):
        return abs(self.vx) > MIN_SPEED or abs(self.vy) > MIN_SPEED

    def get_score(self):
        """计算得分"""
        dist = math.sqrt((self.x - TABLE_CX) ** 2 + (self.y - TARGET_CY) ** 2)
        if dist <= ZONE_10_R:
            return 10
        elif dist <= ZONE_5_R:
            return 5
        elif dist <= ZONE_3_R:
            return 3
        elif dist <= ZONE_1_R:
            return 1
        return 0


def check_ball_collision(b1, b2):
    """检查并处理两球碰撞"""
    dx = b2.x - b1.x
    dy = b2.y - b1.y
    dist = math.sqrt(dx * dx + dy * dy)
    min_dist = b1.radius + b2.radius
    if dist < min_dist and dist > 0:
        # 分离
        overlap = min_dist - dist
        nx, ny = dx / dist, dy / dist
        b1.x -= nx * overlap / 2
        b1.y -= ny * overlap / 2
        b2.x += nx * overlap / 2
        b2.y += ny * overlap / 2
        # 弹性碰撞
        dvx = b1.vx - b2.vx
        dvy = b1.vy - b2.vy
        dot = dvx * nx + dvy * ny
        if dot > 0:
            b1.vx -= dot * nx * 0.8
            b1.vy -= dot * ny * 0.8
            b2.vx += dot * nx * 0.8
            b2.vy += dot * ny * 0.8


class ShuffleboardGame:
    """沙狐球游戏主类"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("沙狐球 - Shuffleboard")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("simhei", 20)
        self.big_font = pygame.font.SysFont("simhei", 36)
        self.small_font = pygame.font.SysFont("simhei", 14)

        self.new_game()

    def new_game(self):
        """开始新游戏"""
        self.balls = []
        self.player_balls_left = BALLS_PER_SIDE
        self.ai_balls_left = BALLS_PER_SIDE
        self.turn = "player"  # player, ai
        self.state = "aiming"  # aiming, charging, rolling, ai_turn, game_over
        self.power = 0
        self.max_power = 18
        self.charging = False
        self.charge_dir = 1
        self.aim_angle = -math.pi / 2  # 向上
        self.player_score = 0
        self.ai_score = 0
        self.message = "你的回合 - 瞄准并推球"
        self.message_color = WHITE
        self.current_ball = None
        self.ai_timer = 0
        self.round_num = 1

    def all_stopped(self):
        """检查所有球是否停止"""
        for b in self.balls:
            if b.active and b.is_moving():
                return False
        return True

    def create_ball(self, team):
        """创建新球"""
        x = TABLE_CX + random.randint(-20, 20)
        y = START_Y
        ball = Ball(x, y, team)
        ball.active = False
        return ball

    def launch_ball(self, power, angle):
        """发射球"""
        if self.current_ball:
            self.current_ball.vx = math.cos(angle) * power
            self.current_ball.vy = math.sin(angle) * power
            self.current_ball.active = True
            self.balls.append(self.current_ball)
            self.state = "rolling"

    def calculate_scores(self):
        """计算得分"""
        self.player_score = 0
        self.ai_score = 0
        for b in self.balls:
            b.score = b.get_score()
            if b.team == 0:
                self.player_score += b.score
            else:
                self.ai_score += b.score

    def ai_take_turn(self):
        """AI推球"""
        ball = self.create_ball(1)
        self.current_ball = ball
        self.ai_balls_left -= 1

        # AI瞄准策略：瞄准靶心附近，加一些随机偏移
        target_x = TABLE_CX + random.randint(-40, 40)
        target_y = TARGET_CY + random.randint(-30, 30)

        dx = target_x - ball.x
        dy = target_y - ball.y
        dist = math.sqrt(dx * dx + dy * dy)
        angle = math.atan2(dy, dx)

        # 力度：根据距离估算，加随机
        power = min(dist / 30 + random.uniform(-2, 2), self.max_power)
        power = max(power, 5)

        self.launch_ball(power, angle)
        self.state = "rolling"

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_r:
                    self.new_game()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and self.state == "aiming" and self.turn == "player":
                    self.charging = True
                    self.power = 0
                    self.state = "charging"
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self.state == "charging":
                    self.charging = False
                    # 发射
                    ball = self.create_ball(0)
                    self.current_ball = ball
                    self.player_balls_left -= 1
                    self.launch_ball(self.power, self.aim_angle)
        return True

    def update(self):
        """更新游戏逻辑"""
        # 更新瞄准角度
        if self.state in ("aiming", "charging"):
            mx, my = pygame.mouse.get_pos()
            # 从球的起始位置计算角度
            dx = mx - TABLE_CX
            dy = my - START_Y
            self.aim_angle = math.atan2(dy, dx)
            # 限制角度范围（只能向上推）
            if self.aim_angle > -0.1:
                self.aim_angle = -0.1
            if self.aim_angle < -math.pi + 0.1:
                self.aim_angle = -math.pi + 0.1

        # 蓄力
        if self.state == "charging" and self.charging:
            self.power += 0.3 * self.charge_dir
            if self.power >= self.max_power:
                self.power = self.max_power
                self.charge_dir = -1
            elif self.power <= 0:
                self.power = 0
                self.charge_dir = 1

        # 更新球
        for b in self.balls:
            b.update()

        # 球与球碰撞
        for i in range(len(self.balls)):
            for j in range(i + 1, len(self.balls)):
                if self.balls[i].active and self.balls[j].active:
                    check_ball_collision(self.balls[i], self.balls[j])

        # 球停止后
        if self.state == "rolling" and self.all_stopped():
            self.calculate_scores()
            self._next_turn()

        # AI回合
        if self.state == "ai_turn":
            self.ai_timer += 1
            if self.ai_timer >= 60:
                self.ai_timer = 0
                self.ai_take_turn()

    def _next_turn(self):
        """切换回合"""
        if self.player_balls_left <= 0 and self.ai_balls_left <= 0:
            self.state = "game_over"
            self.calculate_scores()
            if self.player_score > self.ai_score:
                self.message = f"你赢了! {self.player_score} : {self.ai_score}"
                self.message_color = GREEN
            elif self.ai_score > self.player_score:
                self.message = f"AI赢了! {self.player_score} : {self.ai_score}"
                self.message_color = RED
            else:
                self.message = f"平局! {self.player_score} : {self.ai_score}"
                self.message_color = YELLOW
            return

        if self.turn == "player":
            self.turn = "ai"
            if self.ai_balls_left > 0:
                self.state = "ai_turn"
                self.ai_timer = 0
                self.message = "AI正在思考..."
                self.message_color = LIGHT_GRAY
            else:
                # AI没球了，跳过
                self.turn = "player"
                self.state = "aiming"
                self.message = "你的回合"
                self.message_color = WHITE
        else:
            self.turn = "player"
            if self.player_balls_left > 0:
                self.state = "aiming"
                self.message = "你的回合 - 瞄准并推球"
                self.message_color = WHITE
            else:
                # 玩家没球了
                self.turn = "ai"
                if self.ai_balls_left > 0:
                    self.state = "ai_turn"
                    self.ai_timer = 0
                    self.message = "AI正在思考..."
                    self.message_color = LIGHT_GRAY
                else:
                    self.state = "game_over"

    def draw(self):
        """绘制游戏画面"""
        self.screen.fill(DARK_BROWN)

        # 桌面
        table_rect = pygame.Rect(TABLE_LEFT, TABLE_TOP, TABLE_W, TABLE_H)
        pygame.draw.rect(self.screen, TABLE_COLOR, table_rect, border_radius=10)
        pygame.draw.rect(self.screen, DARK_BROWN, table_rect, 4, border_radius=10)

        # 桌面纹理线条
        for i in range(TABLE_LEFT + 20, TABLE_RIGHT, 30):
            pygame.draw.line(self.screen, (55, 125, 55),
                             (i, TABLE_TOP + 5), (i, TABLE_BOTTOM - 5), 1)

        # 得分区域
        self._draw_target()

        # 发球线
        pygame.draw.line(self.screen, WHITE,
                         (TABLE_LEFT + 10, START_Y + 30),
                         (TABLE_RIGHT - 10, START_Y + 30), 2)
        line_txt = self.small_font.render("发球线", True, WHITE)
        self.screen.blit(line_txt, (TABLE_CX - line_txt.get_width() // 2, START_Y + 33))

        # 绘制球
        for b in self.balls:
            self._draw_ball(b)

        # 瞄准线
        if self.state in ("aiming", "charging") and self.turn == "player":
            self._draw_aim_line()

        # 力度条
        if self.state == "charging":
            self._draw_power_bar()

        # 信息面板
        self._draw_info()

        # 游戏结束
        if self.state == "game_over":
            self._draw_game_over()

        pygame.display.flip()

    def _draw_target(self):
        """绘制得分靶"""
        # 同心圆
        zones = [
            (ZONE_1_R, (180, 200, 180), "1分"),
            (ZONE_3_R, (160, 190, 160), "3分"),
            (ZONE_5_R, (140, 180, 140), "5分"),
            (ZONE_10_R, (120, 170, 120), "10分"),
        ]
        for radius, color, label in zones:
            pygame.draw.circle(self.screen, color, (TABLE_CX, TARGET_CY), radius)
            pygame.draw.circle(self.screen, DARK_GREEN, (TABLE_CX, TARGET_CY), radius, 2)

        # 靶心
        pygame.draw.circle(self.screen, RED, (TABLE_CX, TARGET_CY), 8)
        pygame.draw.circle(self.screen, YELLOW, (TABLE_CX, TARGET_CY), 4)

        # 分数标签
        for radius, color, label in [(ZONE_1_R, None, "1"), (ZONE_3_R, None, "3"),
                                      (ZONE_5_R, None, "5"), (ZONE_10_R, None, "10")]:
            txt = self.small_font.render(label, True, DARK_GREEN)
            self.screen.blit(txt, (TABLE_CX + radius - 15, TARGET_CY - 8))

    def _draw_ball(self, ball):
        """绘制球"""
        color = RED if ball.team == 0 else BLUE
        dark = (150, 20, 20) if ball.team == 0 else (20, 50, 150)
        light = (240, 100, 100) if ball.team == 0 else (100, 130, 240)

        # 阴影
        pygame.draw.circle(self.screen, (30, 80, 30),
                           (int(ball.x) + 3, int(ball.y) + 3), ball.radius)
        # 球体
        pygame.draw.circle(self.screen, color, (int(ball.x), int(ball.y)), ball.radius)
        # 高光
        pygame.draw.circle(self.screen, light,
                           (int(ball.x) - 4, int(ball.y) - 4), ball.radius // 3)
        # 边框
        pygame.draw.circle(self.screen, dark, (int(ball.x), int(ball.y)), ball.radius, 2)

        # 得分标记
        if not ball.is_moving() and ball.active:
            score = ball.get_score()
            if score > 0:
                txt = self.small_font.render(str(score), True, YELLOW)
                self.screen.blit(txt, (int(ball.x) - txt.get_width() // 2,
                                       int(ball.y) - ball.radius - 15))

    def _draw_aim_line(self):
        """绘制瞄准线"""
        start_x = TABLE_CX
        start_y = START_Y
        length = 150
        end_x = start_x + math.cos(self.aim_angle) * length
        end_y = start_y + math.sin(self.aim_angle) * length

        # 虚线效果
        segments = 15
        for i in range(segments):
            if i % 2 == 0:
                t1 = i / segments
                t2 = (i + 1) / segments
                x1 = start_x + (end_x - start_x) * t1
                y1 = start_y + (end_y - start_y) * t1
                x2 = start_x + (end_x - start_x) * t2
                y2 = start_y + (end_y - start_y) * t2
                pygame.draw.line(self.screen, YELLOW, (int(x1), int(y1)),
                                 (int(x2), int(y2)), 2)

        # 箭头
        arrow_size = 8
        angle = self.aim_angle
        ax = end_x
        ay = end_y
        p1 = (ax + math.cos(angle) * arrow_size,
              ay + math.sin(angle) * arrow_size)
        p2 = (ax + math.cos(angle + 2.5) * arrow_size,
              ay + math.sin(angle + 2.5) * arrow_size)
        p3 = (ax + math.cos(angle - 2.5) * arrow_size,
              ay + math.sin(angle - 2.5) * arrow_size)
        pygame.draw.polygon(self.screen, YELLOW,
                            [(int(p1[0]), int(p1[1])),
                             (int(p2[0]), int(p2[1])),
                             (int(p3[0]), int(p3[1]))])

        # 球预览
        pygame.draw.circle(self.screen, (200, 80, 80, 128),
                           (start_x, start_y), BALL_RADIUS, 2)

    def _draw_power_bar(self):
        """绘制力度条"""
        bar_x = TABLE_RIGHT + 15
        bar_y = TABLE_TOP + 100
        bar_w = 25
        bar_h = 400

        # 背景
        pygame.draw.rect(self.screen, DARK_GRAY, (bar_x, bar_y, bar_w, bar_h),
                         border_radius=5)
        # 填充
        ratio = self.power / self.max_power
        fill_h = int(bar_h * ratio)
        # 渐变颜色
        if ratio < 0.3:
            bar_color = GREEN
        elif ratio < 0.7:
            bar_color = YELLOW
        else:
            bar_color = RED
        pygame.draw.rect(self.screen, bar_color,
                         (bar_x, bar_y + bar_h - fill_h, bar_w, fill_h),
                         border_radius=5)
        # 边框
        pygame.draw.rect(self.screen, WHITE, (bar_x, bar_y, bar_w, bar_h), 2,
                         border_radius=5)
        # 标签
        txt = self.small_font.render("力度", True, WHITE)
        self.screen.blit(txt, (bar_x + bar_w // 2 - txt.get_width() // 2,
                               bar_y - 20))
        pct = self.small_font.render(f"{int(ratio * 100)}%", True, WHITE)
        self.screen.blit(pct, (bar_x + bar_w // 2 - pct.get_width() // 2,
                               bar_y + bar_h + 5))

    def _draw_info(self):
        """绘制信息面板"""
        # 玩家信息
        p_label = self.font.render(f"你 (红): {self.player_score}分", True, RED)
        self.screen.blit(p_label, (TABLE_LEFT, TABLE_BOTTOM + 10))
        p_balls = self.small_font.render(f"剩余球: {self.player_balls_left}", True,
                                         LIGHT_GRAY)
        self.screen.blit(p_balls, (TABLE_LEFT, TABLE_BOTTOM + 35))

        # AI信息
        a_label = self.font.render(f"AI (蓝): {self.ai_score}分", True, BLUE)
        self.screen.blit(a_label, (TABLE_RIGHT - a_label.get_width(), TABLE_BOTTOM + 10))
        a_balls = self.small_font.render(f"剩余球: {self.ai_balls_left}", True,
                                         LIGHT_GRAY)
        self.screen.blit(a_balls, (TABLE_RIGHT - a_balls.get_width(),
                                   TABLE_BOTTOM + 35))

        # 消息
        msg = self.font.render(self.message, True, self.message_color)
        self.screen.blit(msg, (TABLE_CX - msg.get_width() // 2, TABLE_BOTTOM + 10))

        # 操作提示
        help_txt = self.small_font.render("鼠标瞄准 | 按住左键蓄力 | 松开推球 | R:重开",
                                          True, GRAY)
        self.screen.blit(help_txt, (TABLE_CX - help_txt.get_width() // 2,
                                    SCREEN_H - 20))

    def _draw_game_over(self):
        """绘制游戏结束"""
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))

        if self.player_score > self.ai_score:
            text = "你赢了!"
            color = GREEN
        elif self.ai_score > self.player_score:
            text = "AI赢了!"
            color = RED
        else:
            text = "平局!"
            color = YELLOW

        txt = self.big_font.render(text, True, color)
        self.screen.blit(txt, (SCREEN_W // 2 - txt.get_width() // 2,
                               SCREEN_H // 2 - 40))
        score = self.font.render(f"{self.player_score} : {self.ai_score}", True, WHITE)
        self.screen.blit(score, (SCREEN_W // 2 - score.get_width() // 2,
                                 SCREEN_H // 2 + 10))
        sub = self.font.render("按 R 重新开始", True, LIGHT_GRAY)
        self.screen.blit(sub, (SCREEN_W // 2 - sub.get_width() // 2,
                               SCREEN_H // 2 + 50))

    def run(self):
        """游戏主循环"""
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = ShuffleboardGame()
    game.run()
