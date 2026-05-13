"""
钓鱼达人升级版
功能：
- 多种鱼类（不同大小、稀有度、分值）
- 力量条机制（需要在合适时机点击）
- 商店系统（用金币购买更好的鱼竿）
- 图鉴收集系统

操作说明：
- 点击"抛竿"开始钓鱼
- 力量条来回移动时点击"收杆"（绿色区域最佳）
- 钓到鱼后获得金币
- 在商店购买更好的鱼竿
- 查看图鉴收集进度

操作：
- 空格/点击: 抛竿/收杆
- 1-4: 切换场景标签
- ESC: 返回
"""

import pygame
import random
import math
import sys

# 初始化
pygame.init()

# 常量
SCREEN_W, SCREEN_H = 900, 650
FPS = 60

# 颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 50, 50)
GREEN = (50, 180, 50)
BLUE = (50, 100, 220)
YELLOW = (255, 215, 0)
GOLD = (255, 200, 50)
CYAN = (0, 200, 200)
ORANGE = (255, 165, 0)
PURPLE = (150, 50, 200)
GRAY = (150, 150, 150)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (80, 80, 80)
DARK_BG = (20, 30, 50)
WATER_BLUE = (30, 80, 140)
WATER_LIGHT = (50, 120, 180)
SKY_BLUE = (100, 180, 240)
SAND = (220, 200, 150)
PANEL_BG = (30, 40, 60)
BUTTON_BG = (50, 60, 90)
BUTTON_HOVER = (70, 80, 120)

# 稀有度颜色
RARITY_COLORS = {
    "普通": (180, 180, 180),
    "优良": (50, 200, 50),
    "稀有": (50, 100, 255),
    "史诗": (180, 50, 255),
    "传说": (255, 165, 0),
}

# 鱼类数据
FISH_DATA = [
    {"name": "小鲫鱼", "rarity": "普通", "min_size": 10, "max_size": 20,
     "score": 10, "price": 5, "color": (200, 180, 100), "difficulty": 0.3},
    {"name": "草鱼", "rarity": "普通", "min_size": 15, "max_size": 35,
     "score": 15, "price": 8, "color": (100, 160, 80), "difficulty": 0.35},
    {"name": "鲤鱼", "rarity": "普通", "min_size": 20, "max_size": 40,
     "score": 20, "price": 12, "color": (220, 150, 50), "difficulty": 0.4},
    {"name": "鲈鱼", "rarity": "优良", "min_size": 25, "max_size": 50,
     "score": 35, "price": 20, "color": (80, 140, 80), "difficulty": 0.5},
    {"name": "鳜鱼", "rarity": "优良", "min_size": 20, "max_size": 45,
     "score": 40, "price": 25, "color": (160, 120, 60), "difficulty": 0.55},
    {"name": "金龙鱼", "rarity": "稀有", "min_size": 30, "max_size": 60,
     "score": 80, "price": 50, "color": (255, 200, 50), "difficulty": 0.65},
    {"name": "中华鲟", "rarity": "稀有", "min_size": 50, "max_size": 100,
     "score": 100, "price": 70, "color": (100, 100, 120), "difficulty": 0.7},
    {"name": "剑鱼", "rarity": "史诗", "min_size": 60, "max_size": 120,
     "score": 200, "price": 150, "color": (50, 80, 180), "difficulty": 0.8},
    {"name": "蓝鳍金枪鱼", "rarity": "史诗", "min_size": 70, "max_size": 150,
     "score": 250, "price": 200, "color": (30, 60, 160), "difficulty": 0.85},
    {"name": "龙王鲸", "rarity": "传说", "min_size": 100, "max_size": 200,
     "score": 500, "price": 400, "color": (200, 50, 50), "difficulty": 0.95},
]

# 鱼竿数据
ROD_DATA = [
    {"name": "竹制鱼竿", "power": 1.0, "price": 0,
     "desc": "基础鱼竿，绿色区域较小", "green_size": 0.15},
    {"name": "碳素鱼竿", "power": 1.2, "price": 100,
     "desc": "绿色区域增大，更容易钓到鱼", "green_size": 0.2},
    {"name": "钛合金鱼竿", "power": 1.5, "price": 300,
     "desc": "强力鱼竿，可钓更大的鱼", "green_size": 0.25},
    {"name": "传说鱼竿", "power": 2.0, "price": 800,
     "desc": "传说级鱼竿，绿色区域最大", "green_size": 0.3},
]

# 游戏状态
STATE_IDLE = 0       # 等待抛竿
STATE_CASTING = 1    # 抛竿动画
STATE_WAITING = 2    # 等待鱼上钩
STATE_BITE = 3       # 鱼咬钩了
STATE_MINIGAME = 4   # 力量条小游戏
STATE_CAUGHT = 5     # 钓到了
STATE_FAILED = 6     # 跑了
STATE_SHOP = 7       # 商店
STATE_ALBUM = 8      # 图鉴


class Particle:
    """粒子效果"""
    def __init__(self, x, y, color, vx=0, vy=0, life=30):
        self.x = x
        self.y = y
        self.color = color
        self.vx = vx + random.uniform(-2, 2)
        self.vy = vy + random.uniform(-3, -1)
        self.life = life
        self.max_life = life
        self.size = random.randint(2, 5)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1  # 重力
        self.life -= 1

    def draw(self, screen):
        alpha = self.life / self.max_life
        r = max(1, int(self.size * alpha))
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), r)


class FishingGame:
    """钓鱼达人升级版主类"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("钓鱼达人升级版")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("simhei", 18)
        self.big_font = pygame.font.SysFont("simhei", 32)
        self.small_font = pygame.font.SysFont("simhei", 14)
        self.title_font = pygame.font.SysFont("simhei", 24)

        # 游戏数据
        self.gold = 50
        self.total_score = 0
        self.current_rod = 0  # 当前鱼竿索引
        self.owned_rods = [True, False, False, False]
        self.fish_album = {}  # 图鉴: {鱼名: {"count": 数量, "max_size": 最大尺寸}}
        self.fish_caught_count = 0

        # 游戏状态
        self.state = STATE_IDLE
        self.timer = 0
        self.cast_anim = 0
        self.wait_timer = 0
        self.bite_timer = 0

        # 力量条
        self.power_pos = 0  # 0-1
        self.power_dir = 1
        self.power_speed = 0.02
        self.current_fish = None
        self.current_fish_size = 0

        # 粒子
        self.particles = []

        # 水面动画
        self.water_offset = 0

        # 浮漂位置
        self.bobber_x = 450
        self.bobber_y = 300
        self.bobber_base_y = 300

        # 消息
        self.message = "点击抛竿开始钓鱼!"
        self.message_color = WHITE
        self.message_timer = 0

        # 商店滚动
        self.shop_scroll = 0

        # 图鉴滚动
        self.album_scroll = 0

        # 按钮
        self.cast_btn = pygame.Rect(350, 550, 200, 50)
        self.reel_btn = pygame.Rect(350, 550, 200, 50)
        self.shop_btn = pygame.Rect(10, 10, 80, 35)
        self.album_btn = pygame.Rect(100, 10, 80, 35)
        self.back_btn = pygame.Rect(10, 10, 80, 35)

        # 钓到的鱼展示
        self.caught_display_timer = 0

    def set_message(self, text, color=WHITE, duration=120):
        self.message = text
        self.message_color = color
        self.message_timer = duration

    def get_rod(self):
        return ROD_DATA[self.current_rod]

    def select_fish(self):
        """根据鱼竿和概率选择一条鱼"""
        rod = self.get_rod()
        # 根据鱼竿等级调整概率
        available = []
        for fish in FISH_DATA:
            # 难度越高的鱼，出现概率越低
            weight = max(0.1, 1.0 - fish["difficulty"] + (rod["power"] - 1.0) * 0.3)
            # 稀有度加成
            rarity_mult = {"普通": 1.0, "优良": 0.6, "稀有": 0.3,
                           "史诗": 0.1, "传说": 0.03}
            weight *= rarity_mult.get(fish["rarity"], 1.0)
            available.append((fish, weight))
        # 加权随机选择
        total = sum(w for _, w in available)
        r = random.uniform(0, total)
        cumulative = 0
        for fish, weight in available:
            cumulative += weight
            if r <= cumulative:
                return fish
        return available[0][0]

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state in (STATE_SHOP, STATE_ALBUM):
                        self.state = STATE_IDLE
                    else:
                        return False
                elif event.key == pygame.K_SPACE:
                    self._handle_action()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self._handle_click(event.pos)
        return True

    def _handle_click(self, pos):
        mx, my = pos
        if self.state in (STATE_SHOP, STATE_ALBUM):
            # 返回按钮
            if self.back_btn.collidepoint(mx, my):
                self.state = STATE_IDLE
                return
            # 商店购买
            if self.state == STATE_SHOP:
                self._handle_shop_click(mx, my)
            return

        # 商店和图鉴按钮
        if self.shop_btn.collidepoint(mx, my):
            self.state = STATE_SHOP
            return
        if self.album_btn.collidepoint(mx, my):
            self.state = STATE_ALBUM
            return

        # 抛竿/收杆按钮
        if self.state == STATE_IDLE:
            if self.cast_btn.collidepoint(mx, my):
                self._start_casting()
        elif self.state == STATE_BITE:
            if self.cast_btn.collidepoint(mx, my):
                self._start_minigame()
        elif self.state == STATE_MINIGAME:
            if self.reel_btn.collidepoint(mx, my):
                self._reel_in()
        elif self.state in (STATE_CAUGHT, STATE_FAILED):
            self.state = STATE_IDLE

    def _handle_action(self):
        if self.state == STATE_IDLE:
            self._start_casting()
        elif self.state == STATE_BITE:
            self._start_minigame()
        elif self.state == STATE_MINIGAME:
            self._reel_in()
        elif self.state in (STATE_CAUGHT, STATE_FAILED):
            self.state = STATE_IDLE

    def _start_casting(self):
        self.state = STATE_CASTING
        self.cast_anim = 0
        self.set_message("抛竿中...", CYAN)

    def _start_minigame(self):
        self.state = STATE_MINIGAME
        self.current_fish = self.select_fish()
        rod = self.get_rod()
        self.power_speed = 0.015 + self.current_fish["difficulty"] * 0.02
        # 鱼竿越好速度越慢
        self.power_speed /= rod["power"] * 0.8
        self.power_pos = 0
        self.power_dir = 1
        self.set_message("在绿色区域点击收杆!", YELLOW)

    def _reel_in(self):
        """收杆判定"""
        rod = self.get_rod()
        green_size = rod["green_size"]
        # 绿色区域在中间
        green_center = 0.5
        green_left = green_center - green_size / 2
        green_right = green_center + green_size / 2

        if green_left <= self.power_pos <= green_right:
            # 成功!
            self.state = STATE_CAUGHT
            fish = self.current_fish
            size = random.randint(fish["min_size"], fish["max_size"])
            self.current_fish_size = size
            score = int(fish["score"] * (size / fish["min_size"]))
            gold = int(fish["price"] * (size / fish["min_size"]))
            self.gold += gold
            self.total_score += score
            self.fish_caught_count += 1

            # 更新图鉴
            if fish["name"] not in self.fish_album:
                self.fish_album[fish["name"]] = {"count": 0, "max_size": 0}
            self.fish_album[fish["name"]]["count"] += 1
            if size > self.fish_album[fish["name"]]["max_size"]:
                self.fish_album[fish["name"]]["max_size"] = size

            rarity_color = RARITY_COLORS.get(fish["rarity"], WHITE)
            self.set_message(
                f"钓到了 [{fish['rarity']}] {fish['name']}! "
                f"{size}cm +{gold}金币 +{score}分", rarity_color, 180)

            # 粒子效果
            for _ in range(30):
                self.particles.append(
                    Particle(self.bobber_x, self.bobber_y, GOLD,
                             random.uniform(-5, 5), random.uniform(-8, -2), 40))
            self.caught_display_timer = 180
        else:
            # 失败
            self.state = STATE_FAILED
            self.set_message("鱼跑了! 力度不对...", RED, 90)

    def _handle_shop_click(self, mx, my):
        """处理商店点击"""
        for i, rod in enumerate(ROD_DATA):
            btn_y = 100 + i * 120 - self.shop_scroll
            btn_rect = pygame.Rect(50, btn_y, 800, 100)
            if btn_rect.collidepoint(mx, my):
                if self.owned_rods[i]:
                    self.current_rod = i
                    self.set_message(f"装备了 {rod['name']}", GREEN)
                elif self.gold >= rod["price"]:
                    self.gold -= rod["price"]
                    self.owned_rods[i] = True
                    self.current_rod = i
                    self.set_message(f"购买了 {rod['name']}!", GOLD)
                else:
                    self.set_message(f"金币不足! 需要 {rod['price']} 金币", RED)

    def update(self):
        """更新游戏逻辑"""
        self.water_offset += 0.5
        if self.message_timer > 0:
            self.message_timer -= 1

        # 粒子更新
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.life > 0]

        if self.state == STATE_CASTING:
            self.cast_anim += 1
            if self.cast_anim >= 30:
                self.state = STATE_WAITING
                self.wait_timer = random.randint(60, 180)
                self.set_message("等待鱼上钩...", LIGHT_GRAY)

        elif self.state == STATE_WAITING:
            self.wait_timer -= 1
            # 浮漂动画
            self.bobber_y = self.bobber_base_y + math.sin(self.water_offset * 0.05) * 3
            if self.wait_timer <= 0:
                self.state = STATE_BITE
                self.bite_timer = 90  # 1.5秒内要点击
                self.set_message("鱼咬钩了! 快点击收杆!", RED)

        elif self.state == STATE_BITE:
            self.bite_timer -= 1
            # 浮漂剧烈抖动
            self.bobber_y = self.bobber_base_y + random.randint(-8, 8)
            if self.bite_timer <= 0:
                self.state = STATE_FAILED
                self.set_message("太慢了! 鱼跑了...", RED)

        elif self.state == STATE_MINIGAME:
            self.power_pos += self.power_speed * self.power_dir
            if self.power_pos >= 1:
                self.power_pos = 1
                self.power_dir = -1
            elif self.power_pos <= 0:
                self.power_pos = 0
                self.power_dir = 1

        elif self.state == STATE_CAUGHT:
            self.caught_display_timer -= 1
            if self.caught_display_timer <= 0:
                self.state = STATE_IDLE
                self.set_message("点击抛竿继续钓鱼!", WHITE)

    def draw(self):
        """绘制游戏画面"""
        if self.state in (STATE_SHOP, STATE_ALBUM):
            self._draw_shop() if self.state == STATE_SHOP else self._draw_album()
            pygame.display.flip()
            return

        # 天空
        self.screen.fill(SKY_BLUE)

        # 太阳
        pygame.draw.circle(self.screen, YELLOW, (750, 80), 40)
        pygame.draw.circle(self.screen, (255, 240, 150), (750, 80), 35)

        # 云朵
        self._draw_cloud(150, 60, 1.0)
        self._draw_cloud(400, 40, 0.7)
        self._draw_cloud(600, 90, 0.8)

        # 远山
        points = [(0, 250), (100, 180), (200, 220), (350, 160),
                  (500, 200), (650, 170), (800, 210), (900, 250)]
        pygame.draw.polygon(self.screen, (60, 120, 60), points)

        # 水面
        water_rect = pygame.Rect(0, 250, SCREEN_W, 300)
        pygame.draw.rect(self.screen, WATER_BLUE, water_rect)
        # 水波纹
        for i in range(0, SCREEN_W, 30):
            y = 250 + math.sin((i + self.water_offset) * 0.03) * 5
            pygame.draw.circle(self.screen, WATER_LIGHT, (i, int(y)), 3)

        # 水下深色渐变
        for y in range(250, 550, 2):
            alpha = (y - 250) / 300
            color = (int(30 * (1 - alpha) + 10 * alpha),
                     int(80 * (1 - alpha) + 40 * alpha),
                     int(140 * (1 - alpha) + 80 * alpha))
            pygame.draw.line(self.screen, color, (0, y), (SCREEN_W, y))

        # 河岸
        pygame.draw.rect(self.screen, SAND, (0, 520, SCREEN_W, 130))
        pygame.draw.rect(self.screen, (200, 180, 130), (0, 520, SCREEN_W, 5))

        # 草地
        for i in range(0, SCREEN_W, 15):
            h = random.randint(10, 25)
            pygame.draw.line(self.screen, (40, 120, 40),
                             (i, 520), (i + random.randint(-3, 3), 520 - h), 2)

        # 钓鱼人（简单图形）
        self._draw_fisherman()

        # 钓线和浮漂
        if self.state in (STATE_WAITING, STATE_BITE, STATE_MINIGAME):
            self._draw_fishing_line()

        # 粒子
        for p in self.particles:
            p.draw(self.screen)

        # 力量条
        if self.state == STATE_MINIGAME:
            self._draw_power_bar()

        # 钓到的鱼展示
        if self.state == STATE_CAUGHT and self.current_fish:
            self._draw_caught_fish()

        # UI面板
        self._draw_ui()

        # 按钮
        self._draw_buttons()

        # 消息
        if self.message_timer > 0:
            msg = self.font.render(self.message, True, self.message_color)
            # 消息背景
            bg_rect = pygame.Rect(SCREEN_W // 2 - msg.get_width() // 2 - 10,
                                  480, msg.get_width() + 20, 30)
            s = pygame.Surface((bg_rect.w, bg_rect.h), pygame.SRCALPHA)
            s.fill((0, 0, 0, 150))
            self.screen.blit(s, bg_rect)
            self.screen.blit(msg, (SCREEN_W // 2 - msg.get_width() // 2, 485))

        pygame.display.flip()

    def _draw_cloud(self, x, y, scale):
        """绘制云朵"""
        s = scale
        pygame.draw.ellipse(self.screen, WHITE,
                            (x, y, int(80 * s), int(30 * s)))
        pygame.draw.ellipse(self.screen, WHITE,
                            (x + int(20 * s), y - int(15 * s), int(50 * s), int(30 * s)))
        pygame.draw.ellipse(self.screen, WHITE,
                            (x + int(40 * s), y, int(60 * s), int(25 * s)))

    def _draw_fisherman(self):
        """绘制钓鱼人"""
        fx, fy = 200, 490
        # 身体
        pygame.draw.rect(self.screen, (50, 50, 150), (fx - 10, fy - 30, 20, 30))
        # 头
        pygame.draw.circle(self.screen, (240, 200, 160), (fx, fy - 40), 12)
        # 帽子
        pygame.draw.rect(self.screen, (100, 80, 40), (fx - 15, fy - 55, 30, 8))
        pygame.draw.rect(self.screen, (100, 80, 40), (fx - 8, fy - 62, 16, 10))
        # 手臂（持竿）
        pygame.draw.line(self.screen, (240, 200, 160),
                         (fx + 10, fy - 20), (fx + 40, fy - 50), 3)
        # 鱼竿
        rod_tip_x, rod_tip_y = fx + 250, fy - 120
        pygame.draw.line(self.screen, (139, 90, 43),
                         (fx + 35, fy - 45), (rod_tip_x, rod_tip_y), 3)
        pygame.draw.line(self.screen, (160, 110, 60),
                         (fx + 35, fy - 45), (rod_tip_x, rod_tip_y), 1)

    def _draw_fishing_line(self):
        """绘制钓线和浮漂"""
        rod_tip_x, rod_tip_y = 450, 370
        # 钓线
        pygame.draw.line(self.screen, LIGHT_GRAY,
                         (rod_tip_x, rod_tip_y),
                         (self.bobber_x, int(self.bobber_y)), 1)
        # 浮漂
        bob_color = RED if self.state == STATE_BITE else WHITE
        pygame.draw.circle(self.screen, bob_color,
                           (int(self.bobber_x), int(self.bobber_y)), 6)
        pygame.draw.circle(self.screen, RED,
                           (int(self.bobber_x), int(self.bobber_y) + 4), 4)
        # 水波纹
        if self.state == STATE_BITE:
            r = 10 + abs(math.sin(self.water_offset * 0.2)) * 8
            pygame.draw.circle(self.screen, WHITE,
                               (int(self.bobber_x), int(self.bobber_y)),
                               int(r), 1)

    def _draw_power_bar(self):
        """绘制力量条"""
        bar_x = 350
        bar_y = 300
        bar_w = 200
        bar_h = 30

        # 背景
        pygame.draw.rect(self.screen, DARK_GRAY, (bar_x - 2, bar_y - 2,
                                                    bar_w + 4, bar_h + 4),
                         border_radius=5)

        # 红色区域（两端）
        rod = self.get_rod()
        green_size = rod["green_size"]
        green_left = 0.5 - green_size / 2
        green_right = 0.5 + green_size / 2

        # 绘制条
        for i in range(bar_w):
            ratio = i / bar_w
            if green_left <= ratio <= green_right:
                color = GREEN
            else:
                # 越远越红
                dist = min(abs(ratio - green_left), abs(ratio - green_right))
                r_val = min(255, int(100 + dist * 400))
                color = (r_val, 50, 50)
            pygame.draw.line(self.screen, color,
                             (bar_x + i, bar_y), (bar_x + i, bar_y + bar_h))

        # 指示器
        indicator_x = bar_x + int(self.power_pos * bar_w)
        pygame.draw.rect(self.screen, WHITE,
                         (indicator_x - 3, bar_y - 5, 6, bar_h + 10))
        pygame.draw.rect(self.screen, YELLOW,
                         (indicator_x - 2, bar_y - 4, 4, bar_h + 8))

        # 标签
        txt = self.font.render("在绿色区域点击!", True, WHITE)
        self.screen.blit(txt, (bar_x + bar_w // 2 - txt.get_width() // 2,
                               bar_y - 30))

    def _draw_caught_fish(self):
        """绘制钓到的鱼"""
        if not self.current_fish:
            return
        fish = self.current_fish
        size = self.current_fish_size
        cx, cy = SCREEN_W // 2, 200

        # 鱼的展示框
        box = pygame.Rect(cx - 150, cy - 80, 300, 160)
        s = pygame.Surface((300, 160), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        self.screen.blit(s, box)
        pygame.draw.rect(self.screen, GOLD, box, 2, border_radius=10)

        # 鱼名
        rarity_color = RARITY_COLORS.get(fish["rarity"], WHITE)
        name_txt = self.title_font.render(fish["name"], True, rarity_color)
        self.screen.blit(name_txt, (cx - name_txt.get_width() // 2, cy - 70))

        # 稀有度
        rarity_txt = self.small_font.render(f"[{fish['rarity']}]", True, rarity_color)
        self.screen.blit(rarity_txt, (cx - rarity_txt.get_width() // 2, cy - 42))

        # 画鱼
        fish_scale = min(1.0, size / 100) * 0.8 + 0.3
        self._draw_fish_sprite(cx, cy + 15, fish["color"], fish_scale)

        # 尺寸和分数
        info = self.font.render(f"{size}cm | +{int(fish['price'] * size / fish['min_size'])}金币",
                                True, GOLD)
        self.screen.blit(info, (cx - info.get_width() // 2, cy + 55))

    def _draw_fish_sprite(self, cx, cy, color, scale=1.0):
        """绘制鱼的精灵"""
        w = int(60 * scale)
        h = int(25 * scale)
        # 鱼身
        body_rect = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
        pygame.draw.ellipse(self.screen, color, body_rect)
        # 鱼尾
        tail_points = [
            (cx - w // 2, cy),
            (cx - w // 2 - int(15 * scale), cy - int(12 * scale)),
            (cx - w // 2 - int(15 * scale), cy + int(12 * scale)),
        ]
        pygame.draw.polygon(self.screen, color, tail_points)
        # 眼睛
        eye_x = cx + w // 4
        eye_y = cy - h // 6
        pygame.draw.circle(self.screen, WHITE, (eye_x, eye_y), max(2, int(4 * scale)))
        pygame.draw.circle(self.screen, BLACK, (eye_x + 1, eye_y), max(1, int(2 * scale)))
        # 鱼鳍
        fin_points = [
            (cx, cy - h // 2),
            (cx - int(5 * scale), cy - h // 2 - int(10 * scale)),
            (cx + int(5 * scale), cy - h // 2),
        ]
        pygame.draw.polygon(self.screen, tuple(max(0, c - 30) for c in color), fin_points)

    def _draw_ui(self):
        """绘制UI信息"""
        # 顶部信息栏
        bar = pygame.Surface((SCREEN_W, 50), pygame.SRCALPHA)
        bar.fill((0, 0, 0, 150))
        self.screen.blit(bar, (0, 0))

        # 金币
        gold_txt = self.font.render(f"金币: {self.gold}", True, GOLD)
        self.screen.blit(gold_txt, (SCREEN_W - 150, 15))

        # 分数
        score_txt = self.font.render(f"总分: {self.total_score}", True, WHITE)
        self.screen.blit(score_txt, (SCREEN_W - 300, 15))

        # 鱼竿
        rod = self.get_rod()
        rod_txt = self.small_font.render(f"鱼竿: {rod['name']}", True, CYAN)
        self.screen.blit(rod_txt, (SCREEN_W - 450, 17))

        # 钓鱼数
        count_txt = self.small_font.render(f"已钓: {self.fish_caught_count}条", True, WHITE)
        self.screen.blit(count_txt, (200, 17))

    def _draw_buttons(self):
        """绘制按钮"""
        mx, my = pygame.mouse.get_pos()

        if self.state == STATE_IDLE:
            # 抛竿按钮
            color = BUTTON_HOVER if self.cast_btn.collidepoint(mx, my) else BUTTON_BG
            pygame.draw.rect(self.screen, color, self.cast_btn, border_radius=10)
            pygame.draw.rect(self.screen, CYAN, self.cast_btn, 2, border_radius=10)
            txt = self.font.render("抛竿", True, WHITE)
            self.screen.blit(txt, (self.cast_btn.centerx - txt.get_width() // 2,
                                   self.cast_btn.centery - txt.get_height() // 2))
        elif self.state == STATE_BITE:
            # 收杆按钮（闪烁）
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.01))
            color = (int(200 + 55 * pulse), int(50 * pulse), int(50 * pulse))
            pygame.draw.rect(self.screen, color, self.cast_btn, border_radius=10)
            pygame.draw.rect(self.screen, WHITE, self.cast_btn, 2, border_radius=10)
            txt = self.font.render("快收杆!", True, WHITE)
            self.screen.blit(txt, (self.cast_btn.centerx - txt.get_width() // 2,
                                   self.cast_btn.centery - txt.get_height() // 2))
        elif self.state == STATE_MINIGAME:
            # 收杆按钮
            color = BUTTON_HOVER if self.reel_btn.collidepoint(mx, my) else BUTTON_BG
            pygame.draw.rect(self.screen, color, self.reel_btn, border_radius=10)
            pygame.draw.rect(self.screen, GREEN, self.reel_btn, 2, border_radius=10)
            txt = self.font.render("收杆!", True, WHITE)
            self.screen.blit(txt, (self.reel_btn.centerx - txt.get_width() // 2,
                                   self.reel_btn.centery - txt.get_height() // 2))

        # 商店按钮
        shop_color = BUTTON_HOVER if self.shop_btn.collidepoint(mx, my) else BUTTON_BG
        pygame.draw.rect(self.screen, shop_color, self.shop_btn, border_radius=5)
        pygame.draw.rect(self.screen, GOLD, self.shop_btn, 1, border_radius=5)
        shop_txt = self.small_font.render("商店", True, GOLD)
        self.screen.blit(shop_txt, (self.shop_btn.centerx - shop_txt.get_width() // 2,
                                    self.shop_btn.centery - shop_txt.get_height() // 2))

        # 图鉴按钮
        album_color = BUTTON_HOVER if self.album_btn.collidepoint(mx, my) else BUTTON_BG
        pygame.draw.rect(self.screen, album_color, self.album_btn, border_radius=5)
        pygame.draw.rect(self.screen, CYAN, self.album_btn, 1, border_radius=5)
        album_txt = self.small_font.render("图鉴", True, CYAN)
        self.screen.blit(album_txt, (self.album_btn.centerx - album_txt.get_width() // 2,
                                     self.album_btn.centery - album_txt.get_height() // 2))

        # 底部提示
        help_txt = self.small_font.render(
            "空格/点击: 抛竿/收杆 | 商店: 购买鱼竿 | 图鉴: 查看收集",
            True, GRAY)
        self.screen.blit(help_txt, (SCREEN_W // 2 - help_txt.get_width() // 2,
                                    SCREEN_H - 25))

    def _draw_shop(self):
        """绘制商店界面"""
        self.screen.fill(DARK_BG)

        # 标题
        title = self.big_font.render("鱼竿商店", True, GOLD)
        self.screen.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 15))

        # 金币
        gold_txt = self.font.render(f"金币: {self.gold}", True, GOLD)
        self.screen.blit(gold_txt, (SCREEN_W - 150, 20))

        # 返回按钮
        mx, my = pygame.mouse.get_pos()
        back_color = BUTTON_HOVER if self.back_btn.collidepoint(mx, my) else BUTTON_BG
        pygame.draw.rect(self.screen, back_color, self.back_btn, border_radius=5)
        pygame.draw.rect(self.screen, WHITE, self.back_btn, 1, border_radius=5)
        back_txt = self.small_font.render("返回", True, WHITE)
        self.screen.blit(back_txt, (self.back_btn.centerx - back_txt.get_width() // 2,
                                    self.back_btn.centery - back_txt.get_height() // 2))

        # 鱼竿列表
        for i, rod in enumerate(ROD_DATA):
            y = 80 + i * 130
            card = pygame.Rect(50, y, 800, 110)

            # 卡片背景
            bg_color = (40, 50, 70) if not self.owned_rods[i] else (30, 60, 40)
            if self.current_rod == i:
                bg_color = (40, 70, 50)
            pygame.draw.rect(self.screen, bg_color, card, border_radius=10)
            border_color = GOLD if self.current_rod == i else GRAY
            pygame.draw.rect(self.screen, border_color, card, 2, border_radius=10)

            # 鱼竿名称
            name_color = GOLD if self.current_rod == i else WHITE
            name_txt = self.title_font.render(rod["name"], True, name_color)
            self.screen.blit(name_txt, (70, y + 10))

            # 描述
            desc_txt = self.small_font.render(rod["desc"], True, LIGHT_GRAY)
            self.screen.blit(desc_txt, (70, y + 45))

            # 属性
            power_txt = self.small_font.render(f"力量: {rod['power']}x", True, CYAN)
            self.screen.blit(power_txt, (70, y + 70))

            green_txt = self.small_font.render(
                f"绿色区域: {int(rod['green_size'] * 100)}%", True, GREEN)
            self.screen.blit(green_txt, (200, y + 70))

            # 按钮
            btn_rect = pygame.Rect(680, y + 30, 150, 45)
            if self.owned_rods[i]:
                if self.current_rod == i:
                    btn_color = (30, 80, 30)
                    btn_text = "使用中"
                    btn_text_color = GREEN
                else:
                    btn_color = BUTTON_BG
                    btn_text = "装备"
                    btn_text_color = WHITE
            else:
                btn_color = (80, 40, 40) if self.gold < rod["price"] else (40, 60, 100)
                btn_text = f"购买 {rod['price']}g"
                btn_text_color = RED if self.gold < rod["price"] else GOLD

            if btn_rect.collidepoint(mx, my):
                btn_color = tuple(min(255, c + 20) for c in btn_color)
            pygame.draw.rect(self.screen, btn_color, btn_rect, border_radius=8)
            pygame.draw.rect(self.screen, btn_text_color, btn_rect, 2, border_radius=8)
            bt = self.font.render(btn_text, True, btn_text_color)
            self.screen.blit(bt, (btn_rect.centerx - bt.get_width() // 2,
                                  btn_rect.centery - bt.get_height() // 2))

    def _draw_album(self):
        """绘制图鉴界面"""
        self.screen.fill(DARK_BG)

        # 标题
        title = self.big_font.render("鱼类图鉴", True, GOLD)
        self.screen.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 15))

        # 收集进度
        collected = len(self.fish_album)
        total = len(FISH_DATA)
        progress = self.font.render(f"收集进度: {collected}/{total}", True, WHITE)
        self.screen.blit(progress, (SCREEN_W // 2 - progress.get_width() // 2, 55))

        # 进度条
        bar_w = 400
        bar_x = SCREEN_W // 2 - bar_w // 2
        pygame.draw.rect(self.screen, DARK_GRAY, (bar_x, 82, bar_w, 12), border_radius=6)
        if total > 0:
            fill_w = int(bar_w * collected / total)
            pygame.draw.rect(self.screen, GOLD, (bar_x, 82, fill_w, 12), border_radius=6)

        # 返回按钮
        mx, my = pygame.mouse.get_pos()
        back_color = BUTTON_HOVER if self.back_btn.collidepoint(mx, my) else BUTTON_BG
        pygame.draw.rect(self.screen, back_color, self.back_btn, border_radius=5)
        pygame.draw.rect(self.screen, WHITE, self.back_btn, 1, border_radius=5)
        back_txt = self.small_font.render("返回", True, WHITE)
        self.screen.blit(back_txt, (self.back_btn.centerx - back_txt.get_width() // 2,
                                    self.back_btn.centery - back_txt.get_height() // 2))

        # 鱼类列表
        for i, fish in enumerate(FISH_DATA):
            col = i % 2
            row = i // 2
            x = 30 + col * 440
            y = 110 + row * 105 - self.album_scroll

            if y < 100 or y > SCREEN_H - 20:
                continue

            card = pygame.Rect(x, y, 420, 95)
            discovered = fish["name"] in self.fish_album

            bg = (40, 50, 70) if discovered else (30, 30, 40)
            pygame.draw.rect(self.screen, bg, card, border_radius=8)

            rarity_color = RARITY_COLORS.get(fish["rarity"], GRAY)
            border = rarity_color if discovered else DARK_GRAY
            pygame.draw.rect(self.screen, border, card, 2, border_radius=8)

            if discovered:
                # 鱼名
                name_txt = self.font.render(fish["name"], True, rarity_color)
                self.screen.blit(name_txt, (x + 15, y + 8))

                # 稀有度
                r_txt = self.small_font.render(f"[{fish['rarity']}]", True, rarity_color)
                self.screen.blit(r_txt, (x + 15 + name_txt.get_width() + 10, y + 10))

                # 画鱼
                self._draw_fish_sprite(x + 60, y + 55, fish["color"], 0.6)

                # 信息
                info = self.fish_album[fish["name"]]
                detail = self.small_font.render(
                    f"数量: {info['count']} | 最大: {info['max_size']}cm | "
                    f"分值: {fish['score']}", True, LIGHT_GRAY)
                self.screen.blit(detail, (x + 120, y + 45))

                size_range = self.small_font.render(
                    f"尺寸范围: {fish['min_size']}-{fish['max_size']}cm", True, GRAY)
                self.screen.blit(size_range, (x + 120, y + 68))
            else:
                # 未发现
                unk = self.font.render("???", True, DARK_GRAY)
                self.screen.blit(unk, (x + 15, y + 8))
                unk2 = self.small_font.render("未发现", True, DARK_GRAY)
                self.screen.blit(unk2, (x + 15, y + 35))
                # 稀有度提示
                hint = self.small_font.render(f"稀有度: {fish['rarity']}", True,
                                              tuple(c // 2 for c in rarity_color))
                self.screen.blit(hint, (x + 15, y + 58))

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
    game = FishingGame()
    game.run()
