#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
放置采矿游戏 - Idle Mining
自动采矿资源管理放置游戏，支持多种矿石和升级

游戏特色:
- 多种矿石类型，价值各不相同
- 自动采矿机系统
- 矿石加工和出售
- 离线收益支持
- 丰富的升级选项
"""

import pygame
import sys
import math
import random
import time
from datetime import datetime

# 初始化pygame
pygame.init()

# 游戏常量
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 650
FPS = 60

# 颜色定义
COLORS = {
    '背景': (25, 20, 30),
    '面板背景': (40, 35, 50),
    '矿石面板': (35, 30, 45),
    '主色调': (255, 180, 80),
    '强调色': (100, 200, 255),
    '文字': (240, 240, 245),
    '文字暗淡': (150, 145, 155),
    '成功色': (100, 255, 150),
    '警告色': (255, 150, 100),
    '按钮悬停': (60, 55, 75),
    '按钮正常': (50, 45, 60),
    '金币色': (255, 215, 0),
}

# 矿石定义
ORES = [
    {"名称": "煤炭", "颜色": (80, 80, 80), "基础价值": 1, "出现率": 0.35},
    {"名称": "铁矿", "颜色": (180, 140, 100), "基础价值": 3, "出现率": 0.28},
    {"名称": "铜矿", "颜色": (200, 140, 80), "基础价值": 5, "出现率": 0.20},
    {"名称": "银矿", "颜色": (200, 200, 210), "基础价值": 12, "出现率": 0.10},
    {"名称": "金矿", "颜色": (255, 215, 0), "基础价值": 30, "出现率": 0.05},
    {"名称": "钻石", "颜色": (100, 200, 255), "基础价值": 100, "出现率": 0.02},
]

# 字体设置
try:
    FONT_NAME = "microsoftyahei"
    TITLE_FONT = pygame.font.SysFont(FONT_NAME, 32, bold=True)
    HEADER_FONT = pygame.font.SysFont(FONT_NAME, 22, bold=True)
    NORMAL_FONT = pygame.font.SysFont(FONT_NAME, 16)
    SMALL_FONT = pygame.font.SysFont(FONT_NAME, 14)
    COIN_FONT = pygame.font.SysFont(FONT_NAME, 26, bold=True)
except:
    FONT_NAME = pygame.font.get_default_font()
    TITLE_FONT = pygame.font.Font(None, 42)
    HEADER_FONT = pygame.font.Font(None, 28)
    NORMAL_FONT = pygame.font.Font(None, 22)
    SMALL_FONT = pygame.font.Font(None, 18)
    COIN_FONT = pygame.font.Font(None, 34)


class OreVein:
    """矿脉类 - 游戏中的可点击矿石"""

    def __init__(self, x, y, ore_type):
        self.x = x
        self.y = y
        self.ore_type = ore_type
        self.mined = False
        self.respawn_timer = 0
        self.respawn_time = random.uniform(3, 8)
        self.anim_scale = 1.0
        self.anim_pulse = 0
        self.sparkles = []

    def update(self, dt):
        """更新矿脉状态"""
        self.anim_pulse += dt * 2
        self.anim_scale = 1.0 + math.sin(self.anim_pulse) * 0.05

        if self.mined:
            self.respawn_timer += dt
            if self.respawn_timer >= self.respawn_time:
                self.mined = False
                self.respawn_timer = 0
                self.respawn_time = random.uniform(3, 8)

        # 更新闪光效果
        for s in self.sparkles[:]:
            s["life"] -= dt * 2
            if s["life"] <= 0:
                self.sparkles.remove(s)

    def mine(self):
        """开采矿石"""
        if not self.mined:
            self.mined = True
            self.respawn_timer = 0
            # 创建闪光
            for _ in range(8):
                self.sparkles.append({
                    "x": random.uniform(-20, 20),
                    "y": random.uniform(-20, 20),
                    "life": 1.0
                })
            return True
        return False

    def draw(self, surface):
        """绘制矿脉"""
        if self.mined:
            return

        ore = ORES[self.ore_type]
        base_size = 35 * self.anim_scale

        # 发光效果
        for i in range(3):
            glow_alpha = 20 - i * 5
            glow_color = (*ore["颜色"][:3], glow_alpha)
            pygame.draw.circle(surface, ore["颜色"],
                             (self.x, self.y), int(base_size + i * 8))

        # 矿石主体
        pygame.draw.circle(surface, ore["颜色"], (self.x, self.y), int(base_size))
        pygame.draw.circle(surface, COLORS['背景'], (self.x, self.y), int(base_size - 8))

        # 闪光效果
        for s in self.sparkles:
            sx = self.x + s["x"]
            sy = self.y + s["y"]
            pygame.draw.circle(surface, (255, 255, 200),
                             (int(sx), int(sy)), max(1, int(3 * s["life"])))


class Miner:
    """矿工类 - 自动采矿单位"""

    def __init__(self, x, y, miner_type):
        self.x = x
        self.y = y
        self.miner_type = miner_type
        self.target_vein = None
        self.working = False
        self.work_timer = 0
        self.work_time = 2.0
        self.anim_angle = 0

        # 根据类型设置属性
        self._init_stats()

    def _init_stats(self):
        """根据矿工类型初始化属性"""
        configs = [
            {"速度": 1.0, "效率": 1.0, "颜色": (150, 150, 150)},  # 初级矿工
            {"速度": 1.5, "效率": 1.5, "颜色": (180, 150, 100)},  # 熟练矿工
            {"速度": 2.0, "效率": 2.5, "颜色": (200, 180, 100)},  # 高级矿工
            {"速度": 3.0, "效率": 4.0, "颜色": (100, 200, 150)},  # 专家矿工
        ]
        cfg = configs[min(self.miner_type, len(configs) - 1)]
        self.速度 = cfg["速度"]
        self.效率 = cfg["效率"]
        self.颜色 = cfg["颜色"]
        self.work_time = 2.0 / self.速度

    def update(self, dt, veins, game):
        """更新矿工行为"""
        self.anim_angle += dt * 5

        if self.target_vein is None or self.target_vein.mined:
            # 找一个新的矿石
            available = [v for v in veins if not v.mined]
            if available:
                self.target_vein = random.choice(available)
                self.working = False
                self.work_timer = 0

        if self.target_vein and not self.target_vein.mined:
            # 移向目标
            dx = self.target_vein.x - self.x
            dy = self.target_vein.y - self.y
            dist = math.sqrt(dx * dx + dy * dy)

            if dist > 40:
                # 移动
                speed = 100 * dt
                self.x += dx / dist * speed
                self.y += dy / dist * speed
                self.working = False
            else:
                # 采矿
                self.working = True
                self.work_timer += dt
                if self.work_timer >= self.work_time:
                    self.work_timer = 0
                    ore = ORES[self.target_vein.ore_type]
                    value = int(ore["基础价值"] * self.效率)
                    game.add_coins(value)
                    game.add_mined_ore(self.target_vein.ore_type)
                    self.target_vein.mine()

    def draw(self, surface):
        """绘制矿工"""
        # 矿工身体
        pygame.draw.circle(surface, self.颜色, (int(self.x), int(self.y)), 15)

        # 矿工工具（镐）动画
        if self.working:
            pick_angle = self.anim_angle
            pick_x = self.x + math.cos(pick_angle) * 20
            pick_y = self.y - 10 + math.sin(pick_angle) * 5
            pygame.draw.line(surface, (200, 150, 100), (int(self.x), int(self.y - 5)),
                           (int(pick_x), int(pick_y)), 3)
            pygame.draw.circle(surface, (150, 150, 150), (int(pick_x), int(pick_y)), 4)


class Upgrade:
    """升级项"""

    def __init__(self, 名称, 描述, 基础价格, 效果值, 效果类型, 最大等级=999):
        self.名称 = 名称
        self.描述 = 描述
        self.基础价格 = 基础价格
        self.效果值 = 效果值
        self.效果类型 = 效果类型
        self.最大等级 = 最大等级
        self.等级 = 0

    def 获取价格(self):
        return int(self.基础价格 * (1.15 ** self.等级))

    def 可升级(self, coins):
        return self.等级 < self.最大等级 and coins >= self.获取价格()

    def 升级(self):
        if self.等级 < self.最大等级:
            self.等级 += 1
            return True
        return False


class Game:
    """游戏主类"""

    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("放置采矿 - Idle Mining")
        self.clock = pygame.time.Clock()

        # 游戏状态
        self.coins = 0
        self.total_coins = 0
        self.运行中 = True
        self.暂停 = False

        # 矿石统计
        self.mined_ores = [0] * len(ORES)
        self.矿石价值倍率 = 1.0

        # 矿脉
        self.veins = []
        self._init_veins()

        # 矿工
        self.miners = []
        self.矿工类型 = 0

        # 升级
        self.upgrades = [
            Upgrade("矿石价值", "所有矿石出售价格+10%", 50, 0.1, "价值倍率"),
            Upgrade("采矿速度", "矿工采矿速度+15%", 100, 0.15, "采矿速度"),
            Upgrade("新矿工", "雇佣一个新矿工", 200, 1, "新矿工"),
            Upgrade("矿工效率", "所有矿工效率+20%", 500, 0.2, "矿工效率"),
            Upgrade("自动出售", "每秒自动出售库存", 1000, 1, "自动出售"),
            Upgrade("稀有探测", "稀有矿石出现率+5%", 2000, 0.05, "稀有探测"),
        ]

        # 按钮
        self.upgrade_buttons = []
        self._init_buttons()

        # 粒子效果
        self.particles = []

        # 离线收益
        self.最后更新时间 = time.time()
        self.离线收益 = 0
        self.离线时间 = 0
        self.显示离线弹窗 = False

        # UI动画
        self.coin_anim_value = 0
        self.stats_update_time = 0

    def _init_veins(self):
        """初始化矿脉"""
        positions = [
            (150, 150), (300, 120), (450, 140), (150, 280), (300, 250),
            (450, 270), (150, 410), (300, 380), (450, 400)
        ]
        for x, y in positions:
            ore_type = self._random_ore_type()
            self.veins.append(OreVein(x, y, ore_type))

    def _random_ore_type(self):
        """根据出现率随机选择矿石类型"""
        rand = random.random()
        cumulative = 0
        for i, ore in enumerate(ORES):
            cumulative += ore["出现率"]
            if rand <= cumulative:
                return i
        return 0

    def _init_buttons(self):
        """初始化升级按钮"""
        btn_width = 180
        btn_height = 50
        start_x = 600
        start_y = 90
        spacing = 60

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
                self.运行中 = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.运行中 = False
                elif event.key == pygame.K_SPACE:
                    self.暂停 = not self.暂停

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.handle_click(event.pos)

    def handle_click(self, pos):
        """处理点击"""
        # 检查离线弹窗
        if self.显示离线弹窗:
            self.显示离线弹窗 = False
            return

        # 检查升级按钮
        for btn in self.upgrade_buttons:
            if btn["rect"].collidepoint(pos):
                self.try_upgrade(btn["upgrade"])
                return

        # 检查矿脉点击
        for vein in self.veins:
            if not vein.mined:
                dx = pos[0] - vein.x
                dy = pos[1] - vein.y
                if dx * dx + dy * dy < 40 * 40:
                    if vein.mine():
                        ore = ORES[vein.ore_type]
                        value = int(ore["基础价值"] * self.矿石价值倍率)
                        self.add_coins(value)
                        self.add_mined_ore(vein.ore_type)
                        # 重生新矿石
                        vein.ore_type = self._random_ore_type()
                        # 粒子效果
                        self._spawn_particles(vein.x, vein.y, ore["颜色"], value)
                    return

    def add_coins(self, amount):
        """添加金币"""
        self.coins += amount
        self.total_coins += amount
        self.coin_anim_value = amount

    def add_mined_ore(self, ore_type):
        """记录已开采的矿石"""
        self.mined_ores[ore_type] += 1

    def _spawn_particles(self, x, y, color, value):
        """生成粒子效果"""
        for _ in range(6):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(50, 120)
            self.particles.append({
                "x": x,
                "y": y,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed - 50,
                "life": 1.0,
                "color": color,
                "value": value // 3 if random.random() > 0.5 else 0
            })

    def try_upgrade(self, upgrade):
        """尝试升级"""
        if upgrade.可升级(self.coins):
            price = upgrade.获取价格()
            self.coins -= price
            upgrade.升级()

            # 应用升级效果
            if upgrade.效果类型 == "新矿工":
                self._add_miner()
            elif upgrade.效果类型 == "矿石价值":
                self.矿石价值倍率 += upgrade.效果值
            elif upgrade.效果类型 == "采矿速度":
                for miner in self.miners:
                    miner.速度 *= (1 + upgrade.效果值)
                    miner.work_time = 2.0 / miner.速度
            elif upgrade.效果类型 == "矿工效率":
                for miner in self.miners:
                    miner.效率 *= (1 + upgrade.效果值)

    def _add_miner(self):
        """添加矿工"""
        spawn_x = random.randint(200, 400)
        spawn_y = random.randint(150, 450)
        miner = Miner(spawn_x, spawn_y, self.矿工类型)
        self.miners.append(miner)

    def update(self, dt):
        """更新游戏逻辑"""
        if self.暂停:
            return

        # 更新矿脉
        for vein in self.veins:
            vein.update(dt)

        # 更新矿工
        for miner in self.miners:
            miner.update(dt, self.veins, self)

        # 更新粒子
        for p in self.particles[:]:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["vy"] += 150 * dt
            p["life"] -= dt * 2
            if p["life"] <= 0:
                self.particles.remove(p)

        # 动画更新
        if self.coin_anim_value > 0:
            self.coin_anim_value = max(0, self.coin_anim_value - dt * 100)

    def calculate_offline_earnings(self):
        """计算离线收益"""
        current_time = time.time()
        elapsed = current_time - self.最后更新时间

        if elapsed > 10:
            self.离线时间 = int(elapsed)
            # 估算离线收益（基于矿工数量和基础产出）
            base_output = len(self.miners) * 0.5 if self.miners else 0.2
            offline_earnings = int(base_output * elapsed * self.矿石价值倍率 * 0.3)
            if offline_earnings > 0:
                self.add_coins(offline_earnings)
                self.离线收益 = offline_earnings
                self.显示离线弹窗 = True

        self.最后更新时间 = current_time

    def draw(self):
        """绘制游戏"""
        self.screen.fill(COLORS['背景'])

        # 绘制主采矿区域
        self.draw_mining_area()

        # 绘制侧边栏
        self.draw_sidebar()

        # 绘制粒子
        self.draw_particles()

        # 绘制离线弹窗
        if self.显示离线弹窗:
            self.draw_offline_popup()

        # 暂停提示
        if self.暂停:
            self.draw_pause_overlay()

        pygame.display.flip()

    def draw_mining_area(self):
        """绘制采矿区域"""
        # 背景面板
        panel_rect = pygame.Rect(30, 30, 540, 520)
        pygame.draw.rect(self.screen, COLORS['矿石面板'], panel_rect, border_radius=15)
        pygame.draw.rect(self.screen, COLORS['主色调'], panel_rect, 2, border_radius=15)

        # 标题
        title = TITLE_FONT.render("采矿场", True, COLORS['主色调'])
        title_rect = title.get_rect(center=(300, 60))
        self.screen.blit(title, title_rect)

        # 绘制矿脉
        for vein in self.veins:
            vein.draw(self.screen)

        # 绘制矿工
        for miner in self.miners:
            miner.draw(self.screen)

        # 矿石图例
        self.draw_ore_legend()

        # 统计信息
        self.draw_mining_stats()

    def draw_ore_legend(self):
        """绘制矿石图例"""
        legend_y = 470
        start_x = 50

        for i, ore in enumerate(ORES):
            x = start_x + (i % 3) * 180
            y = legend_y + (i // 3) * 30

            # 矿石图标
            pygame.draw.circle(self.screen, ore["颜色"], (x, y), 8)
            # 名称和价值
            text = f"{ore['名称']}: {int(ore['基础价值'] * self.矿石价值倍率)}金"
            text_surf = SMALL_FONT.render(text, True, COLORS['文字暗淡'])
            self.screen.blit(text_surf, (x + 15, y - 7))

    def draw_mining_stats(self):
        """绘制采矿统计"""
        stats_y = 550
        stats_text = f"矿工: {len(self.miners)} | 效率: x{self.矿石价值倍率:.1f}"
        stats_surf = SMALL_FONT.render(stats_text, True, COLORS['文字暗淡'])
        stats_rect = stats_surf.get_rect(center=(300, stats_y))
        self.screen.blit(stats_surf, stats_rect)

    def draw_sidebar(self):
        """绘制侧边栏"""
        sidebar_rect = pygame.Rect(590, 30, 280, 590)
        pygame.draw.rect(self.screen, COLORS['面板背景'], sidebar_rect, border_radius=15)
        pygame.draw.rect(self.screen, COLORS['强调色'], sidebar_rect, 2, border_radius=15)

        # 金币显示
        coin_text = f"{self.coins:,.0f}"
        coin_surf = COIN_FONT.render(coin_text, True, COLORS['金币色'])
        coin_rect = coin_surf.get_rect(center=(730, 70))
        self.screen.blit(coin_surf, coin_rect)

        # 金币图标
        pygame.draw.circle(self.screen, COLORS['金币色'], (620, 70), 12)

        # 标题
        upgrade_title = HEADER_FONT.render("升级", True, COLORS['强调色'])
        upgrade_rect = upgrade_title.get_rect(center=(730, 110))
        self.screen.blit(upgrade_title, upgrade_rect)

        # 升级按钮
        for btn in self.upgrade_buttons:
            self.draw_upgrade_button(btn)

    def draw_upgrade_button(self, btn):
        """绘制升级按钮"""
        upgrade = btn["upgrade"]
        rect = btn["rect"]
        can_afford = upgrade.可升级(self.coins)

        btn_color = COLORS['按钮悬停'] if can_afford else COLORS['按钮正常']
        if rect.collidepoint(pygame.mouse.get_pos()):
            btn_color = COLORS['按钮悬停']

        pygame.draw.rect(self.screen, btn_color, rect, border_radius=8)

        border_color = COLORS['成功色'] if can_afford else COLORS['文字暗淡']
        pygame.draw.rect(self.screen, border_color, rect, 2, border_radius=8)

        # 名称
        name_text = f"{upgrade.名称} Lv.{upgrade.等级}"
        name_surf = SMALL_FONT.render(name_text, True, COLORS['文字'])
        self.screen.blit(name_surf, (rect.x + 10, rect.y + 5))

        # 效果
        effect_text = upgrade.描述
        effect_surf = SMALL_FONT.render(effect_text, True, COLORS['主色调'])
        self.screen.blit(effect_surf, (rect.x + 10, rect.y + 22))

        # 价格
        price = upgrade.获取价格()
        price_text = f"{price:,}金"
        price_color = COLORS['成功色'] if can_afford else COLORS['警告色']
        price_surf = SMALL_FONT.render(price_text, True, price_color)
        price_rect = price_surf.get_rect(right=rect.right - 10, centery=rect.centery)
        self.screen.blit(price_surf, price_rect)

    def draw_particles(self):
        """绘制粒子"""
        for p in self.particles:
            pygame.draw.circle(self.screen, p["color"],
                             (int(p["x"]), int(p["y"])),
                             max(1, int(4 * p["life"])))

            if p["value"] > 0:
                text = f"+{p['value']}"
                text_surf = SMALL_FONT.render(text, True, COLORS['金币色'])
                text_rect = text_surf.get_rect(
                    center=(int(p["x"]), int(p["y"] - 15 * p["life"])))
                self.screen.blit(text_surf, text_rect)

    def draw_offline_popup(self):
        """绘制离线收益弹窗"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        popup_rect = pygame.Rect(250, 200, 400, 200)
        pygame.draw.rect(self.screen, COLORS['面板背景'], popup_rect, border_radius=15)
        pygame.draw.rect(self.screen, COLORS['强调色'], popup_rect, 3, border_radius=15)

        title = HEADER_FONT.render("离线采矿收益", True, COLORS['强调色'])
        title_rect = title.get_rect(center=(450, 240))
        self.screen.blit(title, title_rect)

        time_text = f"离线时间: {self.离线时间}秒"
        time_surf = NORMAL_FONT.render(time_text, True, COLORS['文字'])
        time_rect = time_surf.get_rect(center=(450, 290))
        self.screen.blit(time_surf, time_rect)

        earnings_text = f"获得金币: +{self.离线收益:,}"
        earnings_surf = COIN_FONT.render(earnings_text, True, COLORS['金币色'])
        earnings_rect = earnings_surf.get_rect(center=(450, 340))
        self.screen.blit(earnings_surf, earnings_rect)

        hint = SMALL_FONT.render("点击任意处继续", True, COLORS['文字暗淡'])
        hint_rect = hint.get_rect(center=(450, 380))
        self.screen.blit(hint, hint_rect)

    def draw_pause_overlay(self):
        """绘制暂停遮罩"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        self.screen.blit(overlay, (0, 0))

        pause_text = "已暂停 - 按空格继续"
        pause_surf = HEADER_FONT.render(pause_text, True, COLORS['文字'])
        pause_rect = pause_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(pause_surf, pause_rect)

    def run(self):
        """游戏主循环"""
        while self.运行中:
            dt = self.clock.tick(FPS) / 1000.0

            self.handle_events()

            if self.显示离线弹窗:
                for event in pygame.event.get():
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.显示离线弹窗 = False
                continue

            self.update(dt)
            self.calculate_offline_earnings()
            self.draw()

        self.最后更新时间 = time.time()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
