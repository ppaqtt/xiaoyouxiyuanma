#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
放置塔防游戏 - Idle Tower Defense
挂机塔防放置游戏，支持自动建造和升级防御塔

游戏特色:
- 多种防御塔类型，各有特色
- 自动攻击入侵的敌人
- 波次系统，难度递增
- 丰富的升级选项
- 离线收益支持
"""

import pygame
import os
import sys
import math
import random
import time

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

# 游戏常量
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 650
FPS = 60

# 颜色定义
COLORS = {
    '背景': (25, 30, 40),
    '游戏区域': (30, 35, 50),
    '路径': (60, 55, 70),
    '主色调': (100, 180, 255),
    '强调色': (255, 180, 100),
    '文字': (240, 240, 245),
    '文字暗淡': (140, 145, 155),
    '成功色': (100, 255, 150),
    '警告色': (255, 150, 100),
    '危险色': (255, 80, 80),
    '按钮悬停': (55, 60, 75),
    '按钮正常': (45, 50, 65),
    '塔防区域': (35, 40, 55),
}

# 防御塔定义
TOWER_TYPES = [
    {
        "名称": "箭塔",
        "图标": "A",
        "颜色": (150, 180, 100),
        "基础伤害": 10,
        "基础范围": 100,
        "基础攻速": 1.0,
        "基础价格": 50,
        "描述": "基础防御塔，攻速稳定"
    },
    {
        "名称": "炮塔",
        "图标": "C",
        "颜色": (255, 150, 100),
        "基础伤害": 30,
        "基础范围": 80,
        "基础攻速": 0.5,
        "基础价格": 120,
        "描述": "高伤害，范围较小"
    },
    {
        "名称": "冰塔",
        "图标": "I",
        "颜色": (100, 200, 255),
        "基础伤害": 5,
        "基础范围": 90,
        "基础攻速": 0.8,
        "基础价格": 100,
        "描述": "减速敌人，伤害较低"
    },
    {
        "名称": "电塔",
        "图标": "E",
        "颜色": (200, 150, 255),
        "基础伤害": 15,
        "基础范围": 120,
        "基础攻速": 0.7,
        "基础价格": 200,
        "描述": "范围攻击，可攻击多个敌人"
    },
]

# 敌人类型
ENEMY_TYPES = [
    {"名称": "哥布林", "颜色": (100, 180, 100), "血量倍率": 1.0, "速度倍率": 1.0, "金币": 10},
    {"名称": "兽人", "颜色": (150, 100, 80), "血量倍率": 2.5, "速度倍率": 0.7, "金币": 25},
    {"名称": "巨魔", "颜色": (120, 120, 150), "血量倍率": 6, "速度倍率": 0.5, "金币": 50},
    {"名称": "巨龙", "颜色": (200, 100, 100), "血量倍率": 15, "速度倍率": 0.8, "金币": 150},
]

# 字体设置
try:
    FONT_NAME = "microsoftyahei"
    TITLE_FONT = pygame.font.SysFont(FONT_NAME, 28, bold=True)
    HEADER_FONT = pygame.font.SysFont(FONT_NAME, 20, bold=True)
    NORMAL_FONT = pygame.font.SysFont(FONT_NAME, 15)
    SMALL_FONT = pygame.font.SysFont(FONT_NAME, 13)
    COIN_FONT = pygame.font.SysFont(FONT_NAME, 22, bold=True)
except:
    FONT_NAME = pygame.font.get_default_font()
    TITLE_FONT = get_chinese_font(36)
    HEADER_FONT = get_chinese_font(26)
    NORMAL_FONT = get_chinese_font(20)
    SMALL_FONT = get_chinese_font(16)
    COIN_FONT = get_chinese_font(28)


class Enemy:
    """敌人类"""

    def __init__(self, enemy_type, path_points, wave):
        self.enemy_type = enemy_type
        self.path_points = path_points
        self.path_index = 0
        self.x, self.y = path_points[0]

        # 根据波次调整属性
        wave_scale = 1 + (wave - 1) * 0.15
        self.max_hp = int(50 * enemy_type["血量倍率"] * wave_scale)
        self.hp = self.max_hp
        self.speed = 60 * enemy_type["速度倍率"]
        self.gold = int(enemy_type["金币"] * (1 + wave * 0.1))

        self.slow_timer = 0
        self.slow_factor = 1.0
        self.dead = False
        self.reached_end = False

    def update(self, dt):
        """更新敌人位置"""
        # 减速效果
        if self.slow_timer > 0:
            self.slow_timer -= dt
            if self.slow_timer <= 0:
                self.slow_factor = 1.0

        # 移动
        if self.path_index < len(self.path_points) - 1:
            target_x, target_y = self.path_points[self.path_index + 1]
            dx = target_x - self.x
            dy = target_y - self.y
            dist = math.sqrt(dx * dx + dy * dy)

            if dist < 5:
                self.path_index += 1
            else:
                move_speed = self.speed * self.slow_factor * dt
                self.x += dx / dist * move_speed
                self.y += dy / dist * move_speed
        else:
            self.reached_end = True

    def take_damage(self, damage, slow=0, slow_duration=0):
        """受到伤害"""
        self.hp -= damage
        if slow > 0:
            self.slow_factor = 1.0 - slow
            self.slow_timer = slow_duration
        if self.hp <= 0:
            self.dead = True

    def draw(self, surface):
        """绘制敌人"""
        color = self.enemy_type["颜色"]
        if self.slow_timer > 0:
            # 减速时变蓝
            color = (100, 150, 255)

        # 敌人主体
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), 12)

        # 血条背景
        bar_width = 24
        bar_height = 4
        bar_x = self.x - bar_width // 2
        bar_y = self.y - 20

        pygame.draw.rect(surface, (60, 60, 70), (bar_x, bar_y, bar_width, bar_height))

        # 血条
        hp_ratio = self.hp / self.max_hp
        hp_color = COLORS['成功色'] if hp_ratio > 0.5 else COLORS['警告色'] if hp_ratio > 0.25 else COLORS['危险色']
        pygame.draw.rect(surface, hp_color, (bar_x, bar_y, int(bar_width * hp_ratio), bar_height))

        # 敌人名称
        name_surf = SMALL_FONT.render(self.enemy_type["名称"], True, COLORS['文字暗淡'])
        name_rect = name_surf.get_rect(center=(self.x, self.y + 25))
        surface.blit(name_surf, name_rect)


class Tower:
    """防御塔类"""

    def __init__(self, x, y, tower_type):
        self.x = x
        self.y = y
        self.tower_type = tower_type
        self.level = 1
        self.damage = tower_type["基础伤害"]
        self.range = tower_type["基础范围"]
        self.attack_speed = tower_type["基础攻速"]
        self.attack_timer = 0
        self.target = None
        self.anim_angle = 0

    def upgrade(self):
        """升级防御塔"""
        self.level += 1
        self.damage *= 1.4
        self.range *= 1.1
        self.attack_speed *= 1.1

    def get_upgrade_price(self):
        """获取升级价格"""
        return int(self.tower_type["基础价格"] * 0.8 * (1.5 ** self.level))

    def update(self, dt, enemies):
        """更新防御塔"""
        self.attack_timer += dt
        self.anim_angle += dt * 2

        # 找目标
        self.target = None
        min_dist = self.range

        for enemy in enemies:
            if enemy.dead or enemy.reached_end:
                continue
            dx = enemy.x - self.x
            dy = enemy.y - self.y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < min_dist:
                min_dist = dist
                self.target = enemy

        # 攻击
        if self.target and self.attack_timer >= 1.0 / self.attack_speed:
            self.attack_timer = 0
            return self.attack()

        return []

    def attack(self):
        """攻击并返回攻击信息"""
        attacks = []
        tower_name = self.tower_type["名称"]

        if tower_name == "电塔":
            # 电塔攻击多个敌人
            for enemy in [self.target]:
                if enemy:
                    attacks.append({
                        "enemy": enemy,
                        "damage": self.damage,
                        "slow": 0.3 if tower_name == "冰塔" else 0,
                        "slow_duration": 1.5
                    })
        else:
            # 其他塔攻击单个敌人
            slow = 0.5 if tower_name == "冰塔" else 0
            slow_duration = 2.0 if tower_name == "冰塔" else 0
            attacks.append({
                "enemy": self.target,
                "damage": self.damage,
                "slow": slow,
                "slow_duration": slow_duration
            })

        return attacks

    def draw(self, surface, show_range=False):
        """绘制防御塔"""
        color = self.tower_type["颜色"]

        # 范围指示
        if show_range:
            range_surface = pygame.Surface((self.range * 2, self.range * 2), pygame.SRCALPHA)
            pygame.draw.circle(range_surface, (*color, 30), (self.range, self.range), self.range)
            surface.blit(range_surface, (int(self.x - self.range), int(self.y - self.range)))

        # 塔座
        pygame.draw.circle(surface, (60, 60, 70), (int(self.x), int(self.y)), 18)
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), 15)

        # 塔顶图标
        icon = self.tower_type["图标"]
        icon_surf = SMALL_FONT.render(icon, True, (255, 255, 255))
        icon_rect = icon_surf.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(icon_surf, icon_rect)

        # 等级
        level_surf = SMALL_FONT.render(str(self.level), True, COLORS['强调色'])
        level_rect = level_surf.get_rect(center=(int(self.x), int(self.y) + 25))
        surface.blit(level_surf, level_rect)

        # 攻击动画
        if self.target and self.attack_timer < 0.1:
            pygame.draw.line(surface, (255, 255, 200),
                           (int(self.x), int(self.y)),
                           (int(self.target.x), int(self.target.y)), 2)


class Projectile:
    """子弹类"""

    def __init__(self, x, y, target, damage):
        self.x = x
        self.y = y
        self.target = target
        self.damage = damage
        self.speed = 300
        self.dead = False

    def update(self, dt):
        """更新子弹"""
        if self.target.dead or self.target.reached_end:
            self.dead = True
            return

        dx = self.target.x - self.x
        dy = self.target.y - self.y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist < 10:
            self.target.take_damage(self.damage)
            self.dead = True
        else:
            move = self.speed * dt
            self.x += dx / dist * move
            self.y += dy / dist * move

    def draw(self, surface):
        """绘制子弹"""
        pygame.draw.circle(surface, (255, 255, 200), (int(self.x), int(self.y)), 4)


class Upgrade:
    """升级项"""

    def __init__(self, name, desc, base_price, effect_value, effect_type, max_level=999):
        self.name = name
        self.desc = desc
        self.base_price = base_price
        self.effect_value = effect_value
        self.effect_type = effect_type
        self.max_level = max_level
        self.level = 0

    def get_price(self):
        return int(self.base_price * (1.2 ** self.level))

    def can_upgrade(self, gold):
        return self.level < self.max_level and gold >= self.get_price()

    def upgrade(self):
        if self.level < self.max_level:
            self.level += 1
            return True
        return False


class Game:
    """游戏主类"""

    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("放置塔防 - Idle Tower Defense")
        self.clock = pygame.time.Clock()

        # 游戏状态
        self.gold = 100
        self.lives = 20
        self.wave = 0
        self.running = True
        self.paused = False
        self.game_over = False

        # 路径点
        self.path_points = [
            (0, 150), (100, 150), (100, 350), (300, 350),
            (300, 150), (500, 150), (500, 450), (700, 450)
        ]

        # 防御塔和敌人
        self.towers = []
        self.enemies = []
        self.projectiles = []

        # 建造位置（可放置塔的位置）
        self.build_slots = [
            (50, 200), (150, 200), (50, 350), (150, 350),
            (200, 300), (200, 450), (400, 200), (400, 350),
            (400, 450), (450, 200), (600, 350), (600, 500),
            (650, 200), (750, 350), (750, 500),
        ]
        self.occupied_slots = set()

        # 波次控制
        self.wave_timer = 0
        self.wave_interval = 5  # 波次间隔
        self.spawn_timer = 0
        self.enemies_to_spawn = 0
        self.wave_in_progress = False

        # 升级
        self.upgrades = [
            Upgrade("金币收益", "击杀敌人获得金币+15%", 100, 0.15, "gold_bonus"),
            Upgrade("防御塔伤害", "所有塔伤害+20%", 200, 0.2, "tower_damage"),
            Upgrade("防御塔范围", "所有塔范围+15%", 150, 0.15, "tower_range"),
            Upgrade("防御塔攻速", "所有塔攻速+15%", 180, 0.15, "tower_speed"),
            Upgrade("初始金币", "游戏开始金币+100", 300, 100, "start_gold"),
            Upgrade("生命加成", "最大生命+5", 250, 5, "lives"),
        ]
        self.gold_multiplier = 1.0

        # 按钮
        self.tower_buttons = []
        self.upgrade_buttons = []
        self._init_buttons()

        # 离线收益
        self.last_update_time = time.time()
        self.offline_gold = 0
        self.offline_time = 0
        self.show_offline_popup = False

        # 粒子效果
        self.particles = []

        # 鼠标悬停
        self.mouse_pos = (0, 0)
        self.hovered_tower = None

    def _init_buttons(self):
        """初始化按钮"""
        # 塔按钮
        btn_width = 90
        btn_height = 70
        start_x = 600
        start_y = 80
        spacing = 80

        for i, tower in enumerate(TOWER_TYPES):
            rect = pygame.Rect(start_x + (i % 2) * 95, start_y + (i // 2) * 80, btn_width, btn_height)
            self.tower_buttons.append({
                "rect": rect,
                "tower": tower,
                "type_index": i
            })

        # 升级按钮
        btn_width = 165
        btn_height = 45
        start_x = 600
        start_y = 330
        spacing = 52

        for i, upgrade in enumerate(self.upgrades):
            rect = pygame.Rect(start_x, start_y + i * spacing, btn_width, btn_height)
            self.upgrade_buttons.append({
                "rect": rect,
                "upgrade": upgrade
            })

    def handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_w:
                    # 手动开始下一波
                    if not self.wave_in_progress:
                        self.start_next_wave()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.handle_click(event.pos)

            elif event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos
                self.update_hovered()

    def handle_click(self, pos):
        """处理点击"""
        # 离线弹窗
        if self.show_offline_popup:
            self.show_offline_popup = False
            return

        # 游戏结束
        if self.game_over:
            self.reset_game()
            return

        # 检查塔按钮
        for btn in self.tower_buttons:
            if btn["rect"].collidepoint(pos):
                self.selected_tower = btn["type_index"]
                return

        # 检查升级按钮
        for btn in self.upgrade_buttons:
            if btn["rect"].collidepoint(pos):
                self.try_upgrade(btn["upgrade"])
                return

        # 检查建造位置
        if hasattr(self, 'selected_tower'):
            for slot in self.build_slots:
                if slot in self.occupied_slots:
                    continue
                dx = pos[0] - slot[0]
                dy = pos[1] - slot[1]
                if dx * dx + dy * dy < 25 * 25:
                    price = TOWER_TYPES[self.selected_tower]["基础价格"]
                    if self.gold >= price:
                        self.gold -= price
                        tower = Tower(slot[0], slot[1], TOWER_TYPES[self.selected_tower])
                        self.towers.append(tower)
                        self.occupied_slots.add(slot)
                    return

    def update_hovered(self):
        """更新悬停状态"""
        self.hovered_tower = None
        for tower in self.towers:
            dx = self.mouse_pos[0] - tower.x
            dy = self.mouse_pos[1] - tower.y
            if dx * dx + dy * dy < 25 * 25:
                self.hovered_tower = tower
                break

    def try_upgrade(self, upgrade):
        """尝试升级"""
        if upgrade.can_upgrade(self.gold):
            price = upgrade.get_price()
            self.gold -= price
            upgrade.upgrade()

            # 应用升级效果
            if upgrade.effect_type == "gold_bonus":
                self.gold_multiplier += upgrade.effect_value
            elif upgrade.effect_type == "tower_damage":
                for tower in self.towers:
                    tower.damage *= (1 + upgrade.effect_value)
            elif upgrade.effect_type == "tower_range":
                for tower in self.towers:
                    tower.range *= (1 + upgrade.effect_value)
            elif upgrade.effect_type == "tower_speed":
                for tower in self.towers:
                    tower.attack_speed *= (1 + upgrade.effect_value)
            elif upgrade.effect_type == "start_gold":
                self.gold += int(upgrade.effect_value)
            elif upgrade.effect_type == "lives":
                self.lives += int(upgrade.effect_value)

    def start_next_wave(self):
        """开始下一波"""
        self.wave += 1
        self.wave_in_progress = True
        self.enemies_to_spawn = 3 + self.wave * 2
        self.spawn_timer = 0

    def update(self, dt):
        """更新游戏"""
        if self.paused or self.game_over:
            return

        # 自动波次
        if not self.wave_in_progress:
            self.wave_timer += dt
            if self.wave_timer >= self.wave_interval:
                self.wave_timer = 0
                self.start_next_wave()

        # 生成敌人
        if self.wave_in_progress and self.enemies_to_spawn > 0:
            self.spawn_timer += dt
            spawn_interval = max(0.3, 1.5 - self.wave * 0.05)
            if self.spawn_timer >= spawn_interval:
                self.spawn_timer = 0
                self.enemies_to_spawn -= 1
                self.spawn_enemy()

        # 更新防御塔
        for tower in self.towers:
            attacks = tower.update(dt, self.enemies)
            for attack in attacks:
                enemy = attack["enemy"]
                enemy.take_damage(attack["damage"], attack["slow"], attack["slow_duration"])

        # 更新敌人
        for enemy in self.enemies[:]:
            enemy.update(dt)
            if enemy.dead:
                gold = int(enemy.gold * self.gold_multiplier)
                self.gold += gold
                self._spawn_death_particles(enemy.x, enemy.y, enemy.enemy_type["颜色"])
                self.enemies.remove(enemy)
            elif enemy.reached_end:
                self.lives -= 1
                self.enemies.remove(enemy)
                if self.lives <= 0:
                    self.game_over = True

        # 检查波次完成
        if self.wave_in_progress and self.enemies_to_spawn == 0 and len(self.enemies) == 0:
            self.wave_in_progress = False

    def spawn_enemy(self):
        """生成敌人"""
        # 根据波次选择敌人类型
        enemy_type_index = min(self.wave // 3, len(ENEMY_TYPES) - 1)
        enemy_type = ENEMY_TYPES[enemy_type_index]
        enemy = Enemy(enemy_type, self.path_points, self.wave)
        self.enemies.append(enemy)

    def _spawn_death_particles(self, x, y, color):
        """生成死亡粒子"""
        for _ in range(5):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(30, 80)
            self.particles.append({
                "x": x,
                "y": y,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "life": 0.8,
                "color": color
            })

    def calculate_offline_earnings(self):
        """计算离线收益"""
        current_time = time.time()
        elapsed = current_time - self.last_update_time

        if elapsed > 10:
            self.offline_time = int(elapsed)
            # 估算离线收益
            base_rate = len(self.towers) * 2
            offline_gold = int(base_rate * elapsed * 0.2 * self.gold_multiplier)
            if offline_gold > 0:
                self.gold += offline_gold
                self.offline_gold = offline_gold
                self.show_offline_popup = True

        self.last_update_time = current_time

    def draw(self):
        """绘制游戏"""
        self.screen.fill(COLORS['背景'])

        # 绘制游戏区域
        self.draw_game_area()

        # 绘制侧边栏
        self.draw_sidebar()

        # 绘制粒子
        self.draw_particles()

        # 离线弹窗
        if self.show_offline_popup:
            self.draw_offline_popup()

        # 暂停提示
        if self.paused:
            self.draw_pause_overlay()

        # 游戏结束
        if self.game_over:
            self.draw_game_over()

        pygame.display.flip()

    def draw_game_area(self):
        """绘制游戏区域"""
        # 主面板
        panel_rect = pygame.Rect(30, 30, 540, 540)
        pygame.draw.rect(self.screen, COLORS['游戏区域'], panel_rect, border_radius=10)
        pygame.draw.rect(self.screen, COLORS['主色调'], panel_rect, 2, border_radius=10)

        # 绘制路径
        for i in range(len(self.path_points) - 1):
            p1 = self.path_points[i]
            p2 = self.path_points[i + 1]
            pygame.draw.line(self.screen, COLORS['路径'], p1, p2, 30)
            pygame.draw.line(self.screen, (80, 75, 90), p1, p2, 26)

        # 绘制建造位置
        for slot in self.build_slots:
            if slot not in self.occupied_slots:
                pygame.draw.circle(self.screen, (70, 75, 90), slot, 20)
                pygame.draw.circle(self.screen, (90, 95, 110), slot, 20, 2)

        # 绘制防御塔
        for tower in self.towers:
            show_range = tower == self.hovered_tower
            tower.draw(self.screen, show_range)

        # 绘制敌人
        for enemy in self.enemies:
            enemy.draw(self.screen)

        # 绘制波次信息
        wave_text = f"波次: {self.wave}"
        if self.wave_in_progress:
            wave_text += f" (进行中, 剩余: {self.enemies_to_spawn + len(self.enemies)})"
        else:
            wave_text += " (等待中...)"

        wave_surf = NORMAL_FONT.render(wave_text, True, COLORS['主色调'])
        wave_rect = wave_surf.get_rect(center=(300, 55))
        self.screen.blit(wave_surf, wave_rect)

        # 提示文字
        hint = "点击建造位置放置防御塔 | W键开始新波次"
        hint_surf = SMALL_FONT.render(hint, True, COLORS['文字暗淡'])
        hint_rect = hint_surf.get_rect(center=(300, 560))
        self.screen.blit(hint_surf, hint_rect)

    def draw_sidebar(self):
        """绘制侧边栏"""
        sidebar_rect = pygame.Rect(590, 30, 280, 540)
        pygame.draw.rect(self.screen, COLORS['塔防区域'], sidebar_rect, border_radius=10)
        pygame.draw.rect(self.screen, COLORS['强调色'], sidebar_rect, 2, border_radius=10)

        # 金币
        gold_text = f"{self.gold:,}"
        gold_surf = COIN_FONT.render(gold_text, True, (255, 215, 0))
        gold_rect = gold_surf.get_rect(center=(730, 55))
        self.screen.blit(gold_surf, gold_rect)

        # 生命
        lives_text = f"生命: {self.lives}"
        lives_color = COLORS['成功色'] if self.lives > 5 else COLORS['危险色']
        lives_surf = NORMAL_FONT.render(lives_text, True, lives_color)
        lives_rect = lives_surf.get_rect(center=(730, 80))
        self.screen.blit(lives_surf, lives_rect)

        # 建造标题
        build_title = HEADER_FONT.render("建造防御塔", True, COLORS['强调色'])
        build_rect = build_title.get_rect(center=(730, 105))
        self.screen.blit(build_title, build_rect)

        # 塔按钮
        for btn in self.tower_buttons:
            self.draw_tower_button(btn)

        # 升级标题
        upgrade_title = HEADER_FONT.render("升级选项", True, COLORS['强调色'])
        upgrade_rect = upgrade_title.get_rect(center=(730, 310))
        self.screen.blit(upgrade_title, upgrade_rect)

        # 升级按钮
        for btn in self.upgrade_buttons:
            self.draw_upgrade_button(btn)

    def draw_tower_button(self, btn):
        """绘制塔按钮"""
        tower = btn["tower"]
        rect = btn["rect"]
        can_afford = self.gold >= tower["基础价格"]

        btn_color = COLORS['按钮悬停'] if can_afford else COLORS['按钮正常']
        if rect.collidepoint(self.mouse_pos):
            btn_color = COLORS['按钮悬停']

        pygame.draw.rect(self.screen, btn_color, rect, border_radius=8)

        border_color = COLORS['成功色'] if can_afford else COLORS['文字暗淡']
        pygame.draw.rect(self.screen, border_color, rect, 2, border_radius=8)

        # 塔图标
        icon = tower["图标"]
        icon_surf = SMALL_FONT.render(icon, True, tower["颜色"])
        icon_rect = icon_surf.get_rect(center=(rect.centerx, rect.y + 20))
        self.screen.blit(icon_surf, icon_rect)

        # 塔名称
        name = tower["名称"]
        name_surf = SMALL_FONT.render(name, True, COLORS['文字'])
        name_rect = name_surf.get_rect(center=(rect.centerx, rect.y + 38))
        self.screen.blit(name_surf, name_rect)

        # 价格
        price = tower["基础价格"]
        price_text = f"{price}金"
        price_color = COLORS['成功色'] if can_afford else COLORS['警告色']
        price_surf = SMALL_FONT.render(price_text, True, price_color)
        price_rect = price_surf.get_rect(center=(rect.centerx, rect.y + 55))
        self.screen.blit(price_surf, price_rect)

    def draw_upgrade_button(self, btn):
        """绘制升级按钮"""
        upgrade = btn["upgrade"]
        rect = btn["rect"]
        can_afford = upgrade.can_upgrade(self.gold)

        btn_color = COLORS['按钮悬停'] if can_afford else COLORS['按钮正常']
        if rect.collidepoint(self.mouse_pos):
            btn_color = COLORS['按钮悬停']

        pygame.draw.rect(self.screen, btn_color, rect, border_radius=6)

        border_color = COLORS['成功色'] if can_afford else COLORS['文字暗淡']
        pygame.draw.rect(self.screen, border_color, rect, 1, border_radius=6)

        # 名称
        name = f"{upgrade.name} Lv.{upgrade.level}"
        name_surf = SMALL_FONT.render(name, True, COLORS['文字'])
        self.screen.blit(name_surf, (rect.x + 8, rect.y + 5))

        # 效果
        effect = upgrade.desc
        effect_surf = SMALL_FONT.render(effect, True, COLORS['主色调'])
        self.screen.blit(effect_surf, (rect.x + 8, rect.y + 20))

        # 价格
        price = upgrade.get_price()
        price_text = f"{price:,}金"
        price_color = COLORS['成功色'] if can_afford else COLORS['警告色']
        price_surf = SMALL_FONT.render(price_text, True, price_color)
        price_rect = price_surf.get_rect(right=rect.right - 8, centery=rect.centery)
        self.screen.blit(price_surf, price_rect)

    def draw_particles(self):
        """绘制粒子"""
        for p in self.particles[:]:
            p["x"] += p["vx"] * 0.016
            p["y"] += p["vy"] * 0.016
            p["life"] -= 0.03

            if p["life"] <= 0:
                self.particles.remove(p)
            else:
                pygame.draw.circle(self.screen, p["color"],
                                 (int(p["x"]), int(p["y"])),
                                 max(1, int(4 * p["life"])))

    def draw_offline_popup(self):
        """离线收益弹窗"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        popup_rect = pygame.Rect(250, 200, 400, 180)
        pygame.draw.rect(self.screen, COLORS['塔防区域'], popup_rect, border_radius=15)
        pygame.draw.rect(self.screen, COLORS['强调色'], popup_rect, 3, border_radius=15)

        title = HEADER_FONT.render("离线塔防收益", True, COLORS['强调色'])
        title_rect = title.get_rect(center=(450, 240))
        self.screen.blit(title, title_rect)

        time_text = f"离线时间: {self.offline_time}秒"
        time_surf = NORMAL_FONT.render(time_text, True, COLORS['文字'])
        time_rect = time_surf.get_rect(center=(450, 285))
        self.screen.blit(time_surf, time_rect)

        gold_text = f"获得金币: +{self.offline_gold:,}"
        gold_surf = COIN_FONT.render(gold_text, True, (255, 215, 0))
        gold_rect = gold_surf.get_rect(center=(450, 330))
        self.screen.blit(gold_surf, gold_rect)

    def draw_pause_overlay(self):
        """暂停遮罩"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        self.screen.blit(overlay, (0, 0))

        text = "已暂停 - 按空格继续"
        pause_surf = HEADER_FONT.render(text, True, COLORS['文字'])
        pause_rect = pause_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(pause_surf, pause_rect)

    def draw_game_over(self):
        """游戏结束画面"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # 标题
        title = TITLE_FONT.render("游戏结束", True, COLORS['危险色'])
        title_rect = title.get_rect(center=(450, 250))
        self.screen.blit(title, title_rect)

        # 统计
        stats = [
            f"到达波次: {self.wave}",
            f"获得金币: {self.gold:,}",
            f"建造塔数: {len(self.towers)}",
        ]

        for i, stat in enumerate(stats):
            stat_surf = NORMAL_FONT.render(stat, True, COLORS['文字'])
            stat_rect = stat_surf.get_rect(center=(450, 310 + i * 30))
            self.screen.blit(stat_surf, stat_rect)

        # 重玩提示
        hint = "点击任意处重新开始"
        hint_surf = SMALL_FONT.render(hint, True, COLORS['文字暗淡'])
        hint_rect = hint_surf.get_rect(center=(450, 450))
        self.screen.blit(hint_surf, hint_rect)

    def reset_game(self):
        """重置游戏"""
        self.gold = 100
        self.lives = 20
        self.wave = 0
        self.towers = []
        self.enemies = []
        self.projectiles = []
        self.occupied_slots = set()
        self.wave_in_progress = False
        self.game_over = False
        self.gold_multiplier = 1.0

        # 重置升级
        for upgrade in self.upgrades:
            upgrade.level = 0

    def run(self):
        """游戏主循环"""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0

            self.handle_events()

            if self.show_offline_popup:
                for event in pygame.event.get():
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.show_offline_popup = False
                continue

            self.update(dt)
            self.calculate_offline_earnings()
            self.draw()

        self.last_update_time = time.time()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
