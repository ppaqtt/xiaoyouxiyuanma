"""
弹球物理游戏 - 经典弹球机
操作说明：
- Z键：控制左flipper
- /键：控制右flipper
- 空格键：发射弹球
- ESC键：退出游戏
- 球碰到bumper得分
- 3条命，球掉出底部失去一条命
"""

import pygame
import math
import random
import sys

# 初始化pygame
pygame.init()

# 窗口设置
WIDTH, HEIGHT = 500, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("弹球物理 - Pinball Physics")

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
DARK_GRAY = (60, 60, 60)
RED = (255, 60, 60)
GREEN = (60, 255, 100)
BLUE = (60, 120, 255)
YELLOW = (255, 220, 60)
ORANGE = (255, 160, 60)
PURPLE = (180, 80, 255)
CYAN = (60, 220, 255)
BG_COLOR = (15, 15, 35)
TABLE_COLOR = (25, 40, 80)

# 物理常量
GRAVITY = 600          # 重力加速度（像素/秒^2）
BALL_RADIUS = 8        # 球半径
BALL_MASS = 1.0
RESTITUTION = 0.6      # 弹性系数
FRICTION = 0.999       # 摩擦系数

# 字体
try:
    font_small = pygame.font.SysFont("simhei", 16)
    font_medium = pygame.font.SysFont("simhei", 24)
    font_large = pygame.font.SysFont("simhei", 36)
except:
    font_small = pygame.font.Font(None, 16)
    font_medium = pygame.font.Font(None, 24)
    font_large = pygame.font.Font(None, 36)


class Ball:
    """弹球"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.radius = BALL_RADIUS
        self.active = True
        self.trail = []  # 轨迹效果

    def update(self, dt):
        """更新球的位置"""
        if not self.active:
            return

        # 记录轨迹
        self.trail.append((self.x, self.y))
        if len(self.trail) > 15:
            self.trail.pop(0)

        # 应用重力
        self.vy += GRAVITY * dt

        # 应用摩擦力
        self.vx *= FRICTION
        self.vy *= FRICTION

        # 限制最大速度
        speed = math.sqrt(self.vx ** 2 + self.vy ** 2)
        max_speed = 1200
        if speed > max_speed:
            self.vx = self.vx / speed * max_speed
            self.vy = self.vy / speed * max_speed

        # 更新位置
        self.x += self.vx * dt
        self.y += self.vy * dt

    def draw(self, surface):
        """绘制球"""
        if not self.active:
            return

        # 绘制轨迹
        for i, (tx, ty) in enumerate(self.trail):
            alpha = i / len(self.trail) if self.trail else 0
            radius = max(1, int(self.radius * alpha * 0.6))
            color = (int(100 * alpha), int(150 * alpha), int(255 * alpha))
            pygame.draw.circle(surface, color, (int(tx), int(ty)), radius)

        # 绘制球体
        pygame.draw.circle(surface, (200, 200, 220), (int(self.x), int(self.y)), self.radius)
        # 高光
        pygame.draw.circle(surface, WHITE,
            (int(self.x - self.radius * 0.3), int(self.y - self.radius * 0.3)),
            max(1, self.radius // 3))


class Flipper:
    """弹射器（flipper）"""
    def __init__(self, x, y, side):
        self.x = x  # 铰接点
        self.y = y
        self.side = side  # "left" 或 "right"
        self.length = 70
        self.width = 12
        self.angle = 0  # 当前角度
        self.target_angle = 0
        self.rest_angle = 30 if side == "left" else -30  # 静止角度（度）
        self.active_angle = -30 if side == "left" else 30  # 激活角度（度）
        self.angle = self.rest_angle
        self.angular_speed = 0
        self.activated = False

    def update(self, dt):
        """更新flipper状态"""
        if self.activated:
            self.target_angle = self.active_angle
        else:
            self.target_angle = self.rest_angle

        # 平滑旋转
        diff = self.target_angle - self.angle
        self.angular_speed = diff * 15  # 旋转速度
        self.angle += self.angular_speed * dt

    def get_end_point(self):
        """获取flipper末端坐标"""
        rad = math.radians(self.angle)
        if self.side == "left":
            ex = self.x + math.cos(rad) * self.length
        else:
            ex = self.x - math.cos(rad) * self.length
        ey = self.y + math.sin(rad) * self.length
        return ex, ey

    def draw(self, surface):
        """绘制flipper"""
        ex, ey = self.get_end_point()

        # 绘制flipper主体（梯形）
        rad = math.radians(self.angle)
        perp_x = -math.sin(rad) * self.width / 2
        perp_y = math.cos(rad) * self.width / 2

        # 铰接端（较窄）
        hw1 = self.width * 0.3
        # 末端（较宽）
        hw2 = self.width * 0.7

        if self.side == "left":
            p1 = (self.x - perp_x * 0.6, self.y - perp_y * 0.6)
            p2 = (self.x + perp_x * 0.6, self.y + perp_y * 0.6)
            p3 = (ex + perp_x, ey + perp_y)
            p4 = (ex - perp_x, ey - perp_y)
        else:
            p1 = (self.x + perp_x * 0.6, self.y + perp_y * 0.6)
            p2 = (self.x - perp_x * 0.6, self.y - perp_y * 0.6)
            p3 = (ex - perp_x, ey - perp_y)
            p4 = (ex + perp_x, ey + perp_y)

        color = ORANGE if self.activated else YELLOW
        pygame.draw.polygon(surface, color, [p1, p2, p3, p4])
        pygame.draw.polygon(surface, WHITE, [p1, p2, p3, p4], 2)

        # 铰接点
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), 6)
        pygame.draw.circle(surface, DARK_GRAY, (int(self.x), int(self.y)), 4)

    def collide_ball(self, ball):
        """检测flipper与球的碰撞"""
        ex, ey = self.get_end_point()

        # 计算球到线段的最近点
        dx = ex - self.x
        dy = ey - self.y
        length_sq = dx * dx + dy * dy
        if length_sq == 0:
            return False

        t = max(0, min(1, ((ball.x - self.x) * dx + (ball.y - self.y) * dy) / length_sq))
        closest_x = self.x + t * dx
        closest_y = self.y + t * dy

        dist_x = ball.x - closest_x
        dist_y = ball.y - closest_y
        dist = math.sqrt(dist_x * dist_x + dist_y * dist_y)

        min_dist = ball.radius + self.width / 2

        if dist < min_dist and dist > 0:
            # 法线方向
            nx = dist_x / dist
            ny = dist_y / dist

            # 分离球
            overlap = min_dist - dist
            ball.x += nx * overlap
            ball.y += ny * overlap

            # 反射速度
            dot = ball.vx * nx + ball.vy * ny
            ball.vx -= 2 * dot * nx * RESTITUTION
            ball.vy -= 2 * dot * ny * RESTITUTION

            # 如果flipper正在激活，给球额外的力
            if self.activated and abs(self.angular_speed) > 10:
                # 计算flipper末端的线速度
                end_speed = abs(self.angular_speed) * self.length * 0.01
                ball.vy -= end_speed * 8
                ball.vx += (1 if self.side == "left" else -1) * end_speed * 3

            return True
        return False


class Bumper:
    """弹球bumper（碰撞得分物体）"""
    def __init__(self, x, y, radius=25, points=100, color=RED):
        self.x = x
        self.y = y
        self.radius = radius
        self.points = points
        self.color = color
        self.hit_timer = 0  # 碰撞动画计时器
        self.base_radius = radius

    def update(self, dt):
        """更新bumper状态"""
        if self.hit_timer > 0:
            self.hit_timer -= dt
            # 碰撞时放大效果
            scale = 1.0 + 0.3 * (self.hit_timer / 0.3)
            self.radius = int(self.base_radius * scale)
        else:
            self.radius = self.base_radius

    def draw(self, surface):
        """绘制bumper"""
        # 外圈光晕
        if self.hit_timer > 0:
            glow_radius = self.radius + 10
            glow_color = tuple(min(255, c + 100) for c in self.color)
            pygame.draw.circle(surface, glow_color, (int(self.x), int(self.y)), glow_radius)

        # 主体
        color = WHITE if self.hit_timer > 0 else self.color
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.radius)
        # 内圈
        inner_color = tuple(min(255, c + 80) for c in self.color)
        pygame.draw.circle(surface, inner_color, (int(self.x), int(self.y)), self.radius - 5)
        # 分数文字
        text = font_small.render(str(self.points), True, WHITE)
        surface.blit(text, (self.x - text.get_width() // 2, self.y - text.get_height() // 2))

    def collide_ball(self, ball):
        """检测bumper与球的碰撞"""
        dx = ball.x - self.x
        dy = ball.y - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        min_dist = ball.radius + self.radius

        if dist < min_dist and dist > 0:
            # 法线方向
            nx = dx / dist
            ny = dy / dist

            # 分离
            overlap = min_dist - dist
            ball.x += nx * overlap
            ball.y += ny * overlap

            # 反弹（bumper给球一个固定的弹射力）
            bounce_speed = 350
            ball.vx = nx * bounce_speed
            ball.vy = ny * bounce_speed

            self.hit_timer = 0.3
            return True
        return False


class Wall:
    """墙壁（线段碰撞体）"""
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def draw(self, surface):
        """绘制墙壁"""
        pygame.draw.line(surface, (80, 120, 200), (int(self.x1), int(self.y1)),
                        (int(self.x2), int(self.y2)), 4)

    def collide_ball(self, ball):
        """检测墙壁与球的碰撞"""
        dx = self.x2 - self.x1
        dy = self.y2 - self.y1
        length_sq = dx * dx + dy * dy
        if length_sq == 0:
            return False

        t = max(0, min(1, ((ball.x - self.x1) * dx + (ball.y - self.y1) * dy) / length_sq))
        closest_x = self.x1 + t * dx
        closest_y = self.y1 + t * dy

        dist_x = ball.x - closest_x
        dist_y = ball.y - closest_y
        dist = math.sqrt(dist_x * dist_x + dist_y * dist_y)

        if dist < ball.radius + 2 and dist > 0:
            nx = dist_x / dist
            ny = dist_y / dist

            # 分离
            overlap = ball.radius + 2 - dist
            ball.x += nx * overlap
            ball.y += ny * overlap

            # 反射
            dot = ball.vx * nx + ball.vy * ny
            ball.vx -= 2 * dot * nx * RESTITUTION
            ball.vy -= 2 * dot * ny * RESTITUTION
            return True
        return False


class Particle:
    """粒子效果"""
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(50, 200)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = random.uniform(0.2, 0.6)
        self.max_life = self.life
        self.size = random.randint(2, 4)

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 300 * dt
        self.life -= dt

    def draw(self, surface):
        if self.life > 0:
            alpha = self.life / self.max_life
            size = max(1, int(self.size * alpha))
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), size)


class PinballGame:
    """弹球游戏主类"""
    def __init__(self):
        self.reset_game()

    def reset_game(self):
        """重置游戏"""
        self.lives = 3
        self.score = 0
        self.high_score = getattr(self, 'high_score', 0)
        self.ball = None
        self.state = "ready"  # ready, playing, launching, gameover
        self.particles = []
        self.combo = 0
        self.combo_timer = 0

        # 创建flippers
        self.left_flipper = Flipper(150, 720, "left")
        self.right_flipper = Flipper(350, 720, "right")

        # 创建bumper
        self.bumpers = [
            Bumper(250, 250, 30, 100, RED),
            Bumper(150, 350, 25, 75, BLUE),
            Bumper(350, 350, 25, 75, GREEN),
            Bumper(250, 450, 20, 50, PURPLE),
            Bumper(180, 200, 20, 50, ORANGE),
            Bumper(320, 200, 20, 50, CYAN),
        ]

        # 创建墙壁（弹球机边界）
        self.walls = [
            # 左墙
            Wall(30, 100, 30, 650),
            # 右墙
            Wall(470, 100, 470, 650),
            # 顶部弧形（用线段近似）
            Wall(30, 100, 100, 60),
            Wall(100, 60, 200, 45),
            Wall(200, 45, 300, 45),
            Wall(300, 45, 400, 60),
            Wall(400, 60, 470, 100),
            # 左下引导墙
            Wall(30, 650, 100, 730),
            # 右下引导墙
            Wall(470, 650, 400, 730),
            # 上方小挡板
            Wall(100, 150, 130, 200),
            Wall(400, 150, 370, 200),
        ]

        # 发射位置
        self.launch_x = 460
        self.launch_y = 700
        self.launch_power = 0
        self.charging = False

    def launch_ball(self):
        """发射弹球"""
        self.ball = Ball(self.launch_x, self.launch_y)
        self.ball.vx = random.uniform(-30, -10)
        self.ball.vy = -self.launch_power
        self.state = "playing"

    def spawn_particles(self, x, y, color, count=10):
        """生成粒子效果"""
        for _ in range(count):
            self.particles.append(Particle(x, y, color))

    def update(self, dt):
        """更新游戏状态"""
        # 更新flippers
        self.left_flipper.update(dt)
        self.right_flipper.update(dt)

        # 更新bumper动画
        for bumper in self.bumpers:
            bumper.update(dt)

        # 更新粒子
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.life > 0]

        # 连击计时
        if self.combo_timer > 0:
            self.combo_timer -= dt
            if self.combo_timer <= 0:
                self.combo = 0

        if self.state == "launching":
            # 蓄力中
            if self.charging:
                self.launch_power = min(800, self.launch_power + 600 * dt)

        elif self.state == "playing" and self.ball and self.ball.active:
            # 更新球
            self.ball.update(dt)

            # 碰撞检测 - 墙壁
            for wall in self.walls:
                wall.collide_ball(self.ball)

            # 碰撞检测 - bumper
            for bumper in self.bumpers:
                if bumper.collide_ball(self.ball):
                    self.combo += 1
                    self.combo_timer = 2.0
                    points = bumper.points * max(1, self.combo)
                    self.score += points
                    self.spawn_particles(bumper.x, bumper.y, bumper.color, 8)

            # 碰撞检测 - flippers
            self.left_flipper.collide_ball(self.ball)
            self.right_flipper.collide_ball(self.ball)

            # 检查球是否掉出底部
            if self.ball.y > HEIGHT + 20:
                self.ball.active = False
                self.lives -= 1
                self.combo = 0
                if self.lives <= 0:
                    self.state = "gameover"
                    self.high_score = max(self.high_score, self.score)
                else:
                    self.state = "ready"

    def draw(self):
        """绘制游戏画面"""
        screen.fill(BG_COLOR)

        # 绘制桌面背景
        table_rect = pygame.Rect(25, 40, 450, 710)
        pygame.draw.rect(screen, TABLE_COLOR, table_rect, border_radius=10)
        pygame.draw.rect(screen, (60, 100, 180), table_rect, 3, border_radius=10)

        # 绘制装饰线
        for y in range(100, 700, 100):
            pygame.draw.line(screen, (30, 50, 90), (35, y), (465, y), 1)

        # 绘制墙壁
        for wall in self.walls:
            wall.draw(screen)

        # 绘制bumper
        for bumper in self.bumpers:
            bumper.draw(screen)

        # 绘制flippers
        self.left_flipper.draw(screen)
        self.right_flipper.draw(screen)

        # 绘制球
        if self.ball:
            self.ball.draw(screen)

        # 绘制粒子
        for p in self.particles:
            p.draw(screen)

        # 绘制发射区域
        if self.state == "ready":
            # 提示文字
            hint = font_medium.render("按住空格蓄力", True, YELLOW)
            screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, 600))
            hint2 = font_small.render("松开发射", True, GRAY)
            screen.blit(hint2, (WIDTH // 2 - hint2.get_width() // 2, 630))

            # 球预览
            pygame.draw.circle(screen, (200, 200, 220), (self.launch_x, self.launch_y), BALL_RADIUS)

        elif self.state == "launching":
            # 蓄力条
            bar_height = int(self.launch_power / 800 * 100)
            bar_rect = pygame.Rect(self.launch_x + 15, self.launch_y - bar_height, 10, bar_height)
            color = GREEN if self.launch_power < 400 else (YELLOW if self.launch_power < 600 else RED)
            pygame.draw.rect(screen, color, bar_rect)
            pygame.draw.rect(screen, WHITE, (self.launch_x + 14, self.launch_y - 100, 12, 102), 1)

            # 球预览
            pygame.draw.circle(screen, (200, 200, 220), (self.launch_x, self.launch_y), BALL_RADIUS)

        # 绘制HUD
        self.draw_hud()

        # 游戏结束画面
        if self.state == "gameover":
            self.draw_gameover()

        pygame.display.flip()

    def draw_hud(self):
        """绘制游戏信息"""
        # 分数
        score_text = font_medium.render(f"分数: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 5))

        # 最高分
        high_text = font_small.render(f"最高: {self.high_score}", True, GRAY)
        screen.blit(high_text, (10, 30))

        # 生命值
        lives_label = font_small.render("生命:", True, WHITE)
        screen.blit(lives_label, (WIDTH - 130, 5))
        for i in range(self.lives):
            pygame.draw.circle(screen, RED, (WIDTH - 70 + i * 25, 15), 8)
            pygame.draw.circle(screen, (255, 150, 150), (WIDTH - 72 + i * 25, 12), 3)

        # 连击
        if self.combo > 1:
            combo_text = font_medium.render(f"连击 x{self.combo}!", True, ORANGE)
            screen.blit(combo_text, (WIDTH // 2 - combo_text.get_width() // 2, 5))

        # 操作提示
        help_text = font_small.render("Z:左flipper  /:右flipper  空格:发射", True, DARK_GRAY)
        screen.blit(help_text, (WIDTH // 2 - help_text.get_width() // 2, HEIGHT - 20))

    def draw_gameover(self):
        """绘制游戏结束画面"""
        # 半透明遮罩
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(180)
        screen.blit(overlay, (0, 0))

        # 游戏结束文字
        title = font_large.render("游戏结束", True, RED)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 250))

        # 分数
        score_text = font_medium.render(f"最终分数: {self.score}", True, WHITE)
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 320))

        # 最高分
        high_text = font_medium.render(f"最高分: {self.high_score}", True, YELLOW)
        screen.blit(high_text, (WIDTH // 2 - high_text.get_width() // 2, 360))

        # 重新开始提示
        restart = font_medium.render("按 ENTER 重新开始", True, GREEN)
        screen.blit(restart, (WIDTH // 2 - restart.get_width() // 2, 430))


def main():
    clock = pygame.time.Clock()
    game = PinballGame()

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        dt = min(dt, 0.02)  # 限制最大时间步长

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_RETURN:
                    if game.state == "gameover":
                        game.reset_game()

                elif event.key == pygame.K_SPACE:
                    if game.state == "ready":
                        game.state = "launching"
                        game.charging = True
                        game.launch_power = 0

                elif event.key == pygame.K_z:
                    game.left_flipper.activated = True

                elif event.key == pygame.K_SLASH:
                    game.right_flipper.activated = True

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    if game.state == "launching":
                        game.charging = False
                        game.launch_ball()

                elif event.key == pygame.K_z:
                    game.left_flipper.activated = False

                elif event.key == pygame.K_SLASH:
                    game.right_flipper.activated = False

        game.update(dt)
        game.draw()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
