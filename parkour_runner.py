#!/usr/bin/env python3
"""
跑酷游戏 - 自动向前跑，空格跳跃躲避障碍物
障碍物随机生成，速度逐渐加快
"""

import pygame
import os
import sys
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
WIDTH, HEIGHT = 800, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("跑酷游戏 - 空格跳跃")

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
SKY_BLUE = (135, 200, 235)
GROUND_COLOR = (100, 180, 80)
GROUND_DARK = (80, 150, 60)
RED = (220, 60, 60)
ORANGE = (240, 150, 30)
YELLOW = (255, 220, 50)
BLUE = (60, 120, 220)
DARK_GRAY = (60, 60, 60)
GRAY = (150, 150, 150)
BROWN = (139, 90, 43)
DARK_BROWN = (100, 60, 30)
PURPLE = (150, 50, 200)
CYAN = (0, 200, 200)

# 地面参数
GROUND_Y = 380  # 地面Y坐标

# 字体
font_large = pygame.font.SysFont("simhei", 48, bold=True)
font_medium = pygame.font.SysFont("simhei", 28)
font_small = pygame.font.SysFont("simhei", 20)


class Particle:
    """粒子效果类"""

    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-5, -1)
        self.life = random.randint(15, 30)
        self.max_life = self.life
        self.color = color
        self.size = random.randint(2, 5)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.2  # 重力
        self.life -= 1

    def draw(self, surface):
        alpha = self.life / self.max_life
        size = max(1, int(self.size * alpha))
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), size)


class Obstacle:
    """障碍物类"""

    def __init__(self, x, obs_type="box"):
        self.x = x
        self.type = obs_type  # box, spike, tall_box, double_box
        self.passed = False

        if self.type == "box":
            self.width = 30
            self.height = 30
            self.y = GROUND_Y - self.height
            self.color = RED
        elif self.type == "spike":
            self.width = 25
            self.height = 35
            self.y = GROUND_Y - self.height
            self.color = ORANGE
        elif self.type == "tall_box":
            self.width = 25
            self.height = 55
            self.y = GROUND_Y - self.height
            self.color = PURPLE
        elif self.type == "double_box":
            self.width = 50
            self.height = 30
            self.y = GROUND_Y - self.height
            self.color = BLUE

    def get_rect(self):
        """获取碰撞矩形"""
        if self.type == "spike":
            # 三角形碰撞用缩小矩形近似
            return pygame.Rect(self.x + 5, self.y + 10, self.width - 10, self.height - 10)
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, surface):
        """绘制障碍物"""
        if self.type == "box":
            # 箱子
            pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))
            pygame.draw.rect(surface, (180, 40, 40), (self.x, self.y, self.width, self.height), 2)
            # X标记
            pygame.draw.line(surface, YELLOW, (self.x + 5, self.y + 5),
                             (self.x + self.width - 5, self.y + self.height - 5), 2)
            pygame.draw.line(surface, YELLOW, (self.x + self.width - 5, self.y + 5),
                             (self.x + 5, self.y + self.height - 5), 2)

        elif self.type == "spike":
            # 尖刺（三角形）
            points = [
                (self.x + self.width // 2, self.y),
                (self.x, self.y + self.height),
                (self.x + self.width, self.y + self.height)
            ]
            pygame.draw.polygon(surface, self.color, points)
            pygame.draw.polygon(surface, (200, 120, 20), points, 2)
            # 内部线条
            pygame.draw.line(surface, YELLOW,
                             (self.x + self.width // 2, self.y + 8),
                             (self.x + self.width // 2, self.y + self.height - 5), 2)

        elif self.type == "tall_box":
            # 高箱子
            pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))
            pygame.draw.rect(surface, (120, 30, 170), (self.x, self.y, self.width, self.height), 2)
            # 警告条纹
            for i in range(0, self.height, 10):
                pygame.draw.line(surface, YELLOW, (self.x, self.y + i),
                                 (self.x + self.width, self.y + i + 5), 1)

        elif self.type == "double_box":
            # 双箱子
            pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))
            pygame.draw.rect(surface, (40, 90, 180), (self.x, self.y, self.width, self.height), 2)
            mid = self.x + self.width // 2
            pygame.draw.line(surface, WHITE, (mid, self.y), (mid, self.y + self.height), 2)


class Player:
    """玩家角色类"""

    def __init__(self):
        self.x = 100
        self.y = GROUND_Y
        self.width = 30
        self.height = 40
        self.vy = 0
        self.on_ground = True
        self.jump_power = -13
        self.gravity = 0.6
        self.run_frame = 0
        self.run_timer = 0
        self.alive = True

    def jump(self):
        """跳跃"""
        if self.on_ground:
            self.vy = self.jump_power
            self.on_ground = False

    def update(self):
        """更新玩家状态"""
        # 重力
        self.vy += self.gravity
        self.y += self.vy

        # 地面碰撞
        if self.y >= GROUND_Y:
            self.y = GROUND_Y
            self.vy = 0
            self.on_ground = True

        # 跑步动画
        self.run_timer += 1
        if self.run_timer >= 6:
            self.run_timer = 0
            self.run_frame = (self.run_frame + 1) % 4

    def get_rect(self):
        """获取碰撞矩形"""
        return pygame.Rect(self.x - self.width // 2 + 5, self.y - self.height + 5,
                           self.width - 10, self.height - 5)

    def draw(self, surface):
        """绘制玩家角色"""
        x = int(self.x)
        y = int(self.y)
        frame = self.run_frame

        # 身体
        body_color = (50, 150, 250)
        pygame.draw.rect(surface, body_color,
                         (x - 10, y - 35, 20, 20), border_radius=3)

        # 头部
        head_color = (255, 200, 150)
        pygame.draw.circle(surface, head_color, (x, y - 42), 10)

        # 眼睛
        pygame.draw.circle(surface, WHITE, (x + 3, y - 44), 3)
        pygame.draw.circle(surface, BLACK, (x + 4, y - 44), 1)

        # 嘴巴
        if not self.on_ground:
            pygame.draw.circle(surface, BLACK, (x + 3, y - 39), 2)
        else:
            pygame.draw.line(surface, BLACK, (x + 1, y - 39), (x + 6, y - 39), 1)

        # 腿部动画
        leg_offset = [(-5, 0), (5, 0), (-3, -5), (3, -5)]
        if not self.on_ground:
            # 跳跃姿势
            pygame.draw.line(surface, DARK_GRAY, (x - 5, y - 15), (x - 10, y - 5), 3)
            pygame.draw.line(surface, DARK_GRAY, (x + 5, y - 15), (x + 10, y - 5), 3)
        else:
            lo = leg_offset[frame]
            pygame.draw.line(surface, DARK_GRAY, (x - 5, y - 15),
                             (x - 5 + lo[0], y + lo[1]), 3)
            pygame.draw.line(surface, DARK_GRAY, (x + 5, y - 15),
                             (x + 5 - lo[0], y + lo[1]), 3)

        # 手臂
        arm_swing = math.sin(frame * math.pi / 2) * 8
        pygame.draw.line(surface, body_color, (x - 10, y - 30),
                         (x - 15, y - 20 + arm_swing), 3)
        pygame.draw.line(surface, body_color, (x + 10, y - 30),
                         (x + 15, y - 20 - arm_swing), 3)


class Cloud:
    """云朵类"""

    def __init__(self, x=None):
        self.x = x if x else random.randint(WIDTH, WIDTH + 200)
        self.y = random.randint(30, 150)
        self.speed = random.uniform(0.3, 0.8)
        self.size = random.uniform(0.6, 1.2)

    def update(self, game_speed):
        self.x -= self.speed * game_speed / 5
        if self.x < -100:
            self.x = WIDTH + random.randint(50, 200)
            self.y = random.randint(30, 150)

    def draw(self, surface):
        s = self.size
        x, y = int(self.x), int(self.y)
        pygame.draw.ellipse(surface, WHITE, (x, y, int(60 * s), int(30 * s)))
        pygame.draw.ellipse(surface, WHITE, (x + int(15 * s), y - int(15 * s), int(40 * s), int(30 * s)))
        pygame.draw.ellipse(surface, WHITE, (x + int(30 * s), y, int(50 * s), int(25 * s)))


class BackgroundBuilding:
    """背景建筑类"""

    def __init__(self, x=None):
        self.x = x if x else random.randint(WIDTH, WIDTH + 300)
        self.width = random.randint(40, 80)
        self.height = random.randint(60, 180)
        self.y = GROUND_Y - self.height
        self.color = random.choice([
            (80, 80, 100), (90, 85, 95), (75, 80, 90), (85, 90, 100)
        ])
        self.windows = []
        # 生成窗户
        for wy in range(self.y + 10, GROUND_Y - 15, 20):
            for wx in range(self.x + 8, self.x + self.width - 12, 15):
                if random.random() > 0.3:
                    self.windows.append((wx, wy, random.choice([
                        (255, 255, 150), (200, 200, 100), (150, 150, 80)
                    ])))

    def update(self, game_speed):
        self.x -= game_speed * 0.3
        # 更新窗户位置
        new_windows = []
        for wx, wy, wc in self.windows:
            new_wx = wx - game_speed * 0.3
            new_windows.append((new_wx, wy, wc))
        self.windows = new_windows

        if self.x + self.width < -10:
            self.__init__()

    def draw(self, surface):
        pygame.draw.rect(surface, self.color,
                         (int(self.x), self.y, self.width, self.height))
        for wx, wy, wc in self.windows:
            pygame.draw.rect(surface, wc, (int(wx), wy, 8, 10))


class ParkourGame:
    """跑酷游戏主类"""

    def __init__(self):
        self.state = "menu"  # menu, playing, gameover
        self.reset_game()

    def reset_game(self):
        """重置游戏"""
        self.player = Player()
        self.obstacles = []
        self.particles = []
        self.clouds = [Cloud(random.randint(0, WIDTH)) for _ in range(5)]
        self.buildings = [BackgroundBuilding(random.randint(0, WIDTH)) for _ in range(6)]
        self.score = 0
        self.distance = 0
        self.speed = 5  # 初始速度
        self.max_speed = 15
        self.spawn_timer = 0
        self.spawn_interval = 90  # 初始生成间隔
        self.ground_offset = 0
        self.high_score = getattr(self, 'high_score', 0)
        self.combo = 0  # 连续躲避计数
        self.best_combo = 0

    def spawn_obstacle(self):
        """生成障碍物"""
        obs_type = random.choices(
            ["box", "spike", "tall_box", "double_box"],
            weights=[40, 25, 20, 15]
        )[0]
        obs = Obstacle(WIDTH + 50, obs_type)
        self.obstacles.append(obs)

    def create_particles(self, x, y, color, count=10):
        """创建粒子效果"""
        for _ in range(count):
            self.particles.append(Particle(x, y, color))

    def update(self):
        """更新游戏逻辑"""
        if self.state != "playing":
            return

        # 更新距离和分数
        self.distance += self.speed
        self.score = int(self.distance / 10)

        # 逐渐加速
        self.speed = min(self.max_speed, 5 + self.distance / 1000)

        # 更新生成间隔（速度越快间隔越短）
        self.spawn_interval = max(35, 90 - int(self.distance / 200))

        # 生成障碍物
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            self.spawn_obstacle()

        # 更新玩家
        self.player.update()

        # 跑步粒子
        if self.player.on_ground and random.random() > 0.7:
            self.create_particles(
                self.player.x - 10, GROUND_Y,
                (150, 130, 100), 1
            )

        # 更新障碍物
        for obs in self.obstacles[:]:
            obs.x -= self.speed

            # 检查是否通过障碍物
            if not obs.passed and obs.x + obs.width < self.player.x:
                obs.passed = True
                self.combo += 1
                self.best_combo = max(self.best_combo, self.combo)
                # 得分奖励
                self.score += self.combo * 2

            # 碰撞检测
            if self.player.get_rect().colliderect(obs.get_rect()):
                self.player.alive = False
                self.state = "gameover"
                self.high_score = max(self.high_score, self.score)
                # 碰撞粒子
                self.create_particles(self.player.x, self.player.y - 20, RED, 20)
                self.create_particles(self.player.x, self.player.y - 20, YELLOW, 15)

            # 移除屏幕外的障碍物
            if obs.x + obs.width < -50:
                self.obstacles.remove(obs)

        # 更新粒子
        for p in self.particles[:]:
            p.update()
            if p.life <= 0:
                self.particles.remove(p)

        # 更新云朵
        for cloud in self.clouds:
            cloud.update(self.speed)

        # 更新背景建筑
        for building in self.buildings:
            building.update(self.speed)

        # 地面滚动
        self.ground_offset = (self.ground_offset + self.speed) % 40

    def handle_input(self, event):
        """处理输入"""
        if event.type == pygame.KEYDOWN:
            if self.state == "menu":
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    self.state = "playing"
                    self.reset_game()
            elif self.state == "playing":
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    self.player.jump()
            elif self.state == "gameover":
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    self.state = "playing"
                    self.reset_game()
                elif event.key == pygame.K_ESCAPE:
                    self.state = "menu"

    def draw(self, surface):
        """绘制游戏画面"""
        if self.state == "menu":
            self.draw_menu(surface)
        elif self.state == "playing":
            self.draw_game(surface)
        elif self.state == "gameover":
            self.draw_game(surface)
            self.draw_gameover(surface)

    def draw_menu(self, surface):
        """绘制菜单"""
        # 天空渐变背景
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            r = int(135 * (1 - ratio) + 50 * ratio)
            g = int(200 * (1 - ratio) + 30 * ratio)
            b = int(235 * (1 - ratio) + 80 * ratio)
            pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))

        # 地面
        pygame.draw.rect(surface, GROUND_COLOR, (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))
        pygame.draw.line(surface, GROUND_DARK, (0, GROUND_Y), (WIDTH, GROUND_Y), 3)

        # 标题
        title = font_large.render("跑酷大冒险", True, WHITE)
        shadow = font_large.render("跑酷大冒险", True, (0, 0, 80))
        surface.blit(shadow, (WIDTH // 2 - title.get_width() // 2 + 3, 83))
        surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))

        # 装饰线
        pygame.draw.line(surface, YELLOW, (250, 140), (550, 140), 2)

        # 操作说明
        instructions = [
            "空格键 / 上箭头 - 跳跃",
            "躲避障碍物，跑得越远分数越高",
            "速度会逐渐加快，挑战你的反应极限！",
            "连续躲避障碍物可获得连击加分",
            "",
            "按 空格键 开始游戏"
        ]
        for i, text in enumerate(instructions):
            color = YELLOW if "空格键 开始" in text else WHITE
            t = font_small.render(text, True, color)
            surface.blit(t, (WIDTH // 2 - t.get_width() // 2, 170 + i * 32))

        # 最高分
        if self.high_score > 0:
            hs = font_medium.render(f"最高分: {self.high_score}", True, YELLOW)
            surface.blit(hs, (WIDTH // 2 - hs.get_width() // 2, 400))

    def draw_game(self, surface):
        """绘制游戏画面"""
        # 天空渐变
        for y in range(GROUND_Y):
            ratio = y / GROUND_Y
            r = int(135 * (1 - ratio) + 100 * ratio)
            g = int(200 * (1 - ratio) + 160 * ratio)
            b = int(235 * (1 - ratio) + 200 * ratio)
            pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))

        # 背景建筑
        for building in self.buildings:
            building.draw(surface)

        # 云朵
        for cloud in self.clouds:
            cloud.draw(surface)

        # 远山
        mountain_points = [(0, GROUND_Y)]
        for mx in range(0, WIDTH + 50, 50):
            my = GROUND_Y - 40 - math.sin(mx * 0.01 + self.distance * 0.0001) * 30
            mountain_points.append((mx, my))
        mountain_points.append((WIDTH, GROUND_Y))
        pygame.draw.polygon(surface, (120, 160, 120), mountain_points)

        # 地面
        pygame.draw.rect(surface, GROUND_COLOR, (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))

        # 地面纹理（滚动效果）
        for x in range(-40, WIDTH + 40, 40):
            gx = x - int(self.ground_offset)
            pygame.draw.line(surface, GROUND_DARK, (gx, GROUND_Y + 5), (gx + 20, GROUND_Y + 5), 1)
            pygame.draw.line(surface, (90, 160, 65), (gx + 10, GROUND_Y + 15), (gx + 30, GROUND_Y + 15), 1)

        # 地面线
        pygame.draw.line(surface, GROUND_DARK, (0, GROUND_Y), (WIDTH, GROUND_Y), 3)

        # 绘制障碍物
        for obs in self.obstacles:
            obs.draw(surface)

        # 绘制粒子
        for p in self.particles:
            p.draw(surface)

        # 绘制玩家
        if self.player.alive:
            self.player.draw(surface)

        # 绘制UI
        self.draw_ui(surface)

    def draw_ui(self, surface):
        """绘制用户界面"""
        # 半透明UI背景
        ui_bg = pygame.Surface((220, 90), pygame.SRCALPHA)
        ui_bg.fill((0, 0, 0, 120))
        surface.blit(ui_bg, (10, 10))

        # 分数
        score_text = font_medium.render(f"分数: {self.score}", True, YELLOW)
        surface.blit(score_text, (20, 15))

        # 距离
        dist_text = font_small.render(f"距离: {int(self.distance)}m", True, WHITE)
        surface.blit(dist_text, (20, 48))

        # 速度
        speed_text = font_small.render(f"速度: {self.speed:.1f}", True, CYAN)
        surface.blit(speed_text, (20, 72))

        # 连击
        if self.combo > 1:
            combo_text = font_medium.render(f"连击 x{self.combo}", True, ORANGE)
            surface.blit(combo_text, (WIDTH - combo_text.get_width() - 20, 15))

        # 速度条
        speed_ratio = (self.speed - 5) / (self.max_speed - 5)
        bar_x = WIDTH - 170
        bar_y = 55
        bar_width = 150
        bar_height = 12
        pygame.draw.rect(surface, DARK_GRAY, (bar_x, bar_y, bar_width, bar_height))
        if speed_ratio < 0.5:
            bar_color = (int(255 * speed_ratio * 2), 255, 0)
        else:
            bar_color = (255, int(255 * (1 - speed_ratio) * 2), 0)
        pygame.draw.rect(surface, bar_color,
                         (bar_x, bar_y, int(bar_width * speed_ratio), bar_height))
        pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)
        speed_label = font_small.render("速度", True, WHITE)
        surface.blit(speed_label, (bar_x - 40, bar_y - 3))

    def draw_gameover(self, surface):
        """绘制游戏结束画面"""
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))

        go_text = font_large.render("游戏结束!", True, RED)
        surface.blit(go_text, (WIDTH // 2 - go_text.get_width() // 2, 130))

        # 分数面板
        panel = pygame.Surface((300, 200), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 180))
        surface.blit(panel, (WIDTH // 2 - 150, 190))

        score_text = font_medium.render(f"得分: {self.score}", True, YELLOW)
        surface.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 200))

        dist_text = font_small.render(f"距离: {int(self.distance)}m", True, WHITE)
        surface.blit(dist_text, (WIDTH // 2 - dist_text.get_width() // 2, 240))

        combo_text = font_small.render(f"最大连击: {self.best_combo}", True, ORANGE)
        surface.blit(combo_text, (WIDTH // 2 - combo_text.get_width() // 2, 270))

        if self.score >= self.high_score:
            new_record = font_medium.render("新纪录!", True, YELLOW)
            surface.blit(new_record, (WIDTH // 2 - new_record.get_width() // 2, 305))

        hint1 = font_small.render("按 空格键 重新开始", True, WHITE)
        hint2 = font_small.render("按 ESC 返回菜单", True, GRAY)
        surface.blit(hint1, (WIDTH // 2 - hint1.get_width() // 2, 420))
        surface.blit(hint2, (WIDTH // 2 - hint2.get_width() // 2, 450))


def main():
    """主函数"""
    clock = pygame.time.Clock()
    game = ParkourGame()

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
