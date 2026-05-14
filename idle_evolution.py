#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
放置进化游戏 - Idle Evolution
生物进化模拟放置游戏，支持点击和自动升级进化

游戏特色:
- 点击生物获取进化点数
- 自动进化系统，离线也能获得收益
- 多阶段进化路线
- 丰富的升级选项
"""

import pygame
import sys
import math
import random
import time
from datetime import datetime, timedelta

# 初始化pygame
pygame.init()

# 游戏常量
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 650
FPS = 60

# 颜色定义
COLORS = {
    '背景': (20, 25, 35),
    '面板背景': (30, 35, 50),
    '主色调': (100, 200, 150),
    '强调色': (255, 200, 100),
    '文字': (240, 240, 245),
    '文字暗淡': (150, 155, 165),
    '成功色': (100, 255, 150),
    '警告色': (255, 150, 100),
    '按钮悬停': (60, 70, 90),
    '按钮正常': (45, 55, 70),
    '经验条背景': (35, 40, 50),
    '生命条': (255, 100, 100),
}

# 字体设置
try:
    FONT_NAME = "microsoftyahei"
    TITLE_FONT = pygame.font.SysFont(FONT_NAME, 36, bold=True)
    HEADER_FONT = pygame.font.SysFont(FONT_NAME, 24, bold=True)
    NORMAL_FONT = pygame.font.SysFont(FONT_NAME, 18)
    SMALL_FONT = pygame.font.SysFont(FONT_NAME, 14)
    POINTS_FONT = pygame.font.SysFont(FONT_NAME, 28, bold=True)
except:
    FONT_NAME = pygame.font.get_default_font()
    TITLE_FONT = pygame.font.Font(None, 48)
    HEADER_FONT = pygame.font.Font(None, 32)
    NORMAL_FONT = pygame.font.Font(None, 24)
    SMALL_FONT = pygame.font.Font(None, 18)
    POINTS_FONT = pygame.font.Font(None, 36)


class Creature:
    """生物类 - 代表一个可进化的生物"""

    # 进化阶段定义
    STAGES = [
        {"名称": "微生物", "图标": "o", "颜色": (100, 200, 100), "乘数": 1.0},
        {"名称": "原核生物", "图标": "O", "颜色": (100, 180, 200), "乘数": 2.5},
        {"名称": "真核细胞", "图标": "@", "颜色": (180, 100, 200), "乘数": 6},
        {"名称": "多细胞生物", "图标": "&", "颜色": (200, 150, 100), "乘数": 15},
        {"名称": "海洋生物", "图标": "~", "颜色": (100, 150, 255), "乘数": 40},
        {"名称": "两栖动物", "图标": "^", "颜色": (100, 200, 150), "乘数": 100},
        {"名称": "爬行动物", "图标": ">", "颜色": (200, 100, 100), "乘数": 250},
        {"名称": "哺乳动物", "图标": "%", "颜色": (255, 180, 100), "乘数": 600},
        {"名称": "灵长类", "图标": "?", "颜色": (255, 220, 100), "乘数": 1500},
        {"名称": "人类", "图标": "&", "颜色": (255, 255, 200), "乘数": 4000},
        {"名称": "超级生物", "图标": "*", "颜色": (255, 215, 0), "乘数": 10000},
    ]

    def __init__(self):
        self.名称 = "微生物"
        self.阶段 = 0
        self.经验值 = 0
        self.进化点数 = 0
        self.点击输出 = 1
        self.自动产出率 = 0  # 每秒产出
        self.进化进度 = 0.0  # 0-1之间
        self.动画角度 = 0
        self.动画缩放 = 1.0
        self.动画脉冲 = 0

        # 统计
        self.总点击次数 = 0
        self.总获得经验 = 0

    def 获取阶段信息(self):
        """获取当前阶段的详细信息"""
        return self.STAGES[self.阶段]

    def 获取下一阶段信息(self):
        """获取下一阶段信息"""
        if self.阶段 < len(self.STAGES) - 1:
            return self.STAGES[self.阶段 + 1]
        return None

    def 获取升级经验需求(self):
        """获取升级到下一阶段需要的经验值"""
        return int(100 * (2.5 ** self.阶段))

    def 添加经验(self, 数量):
        """添加经验值，处理进化逻辑"""
        基础经验 = 数量
        数量 = int(数量 * self.获取阶段信息()["乘数"])
        self.经验值 += 数量
        self.总获得经验 += 数量

        # 检查是否可以进化
        需求 = self.获取升级经验需求()
        while self.经验值 >= 需求 and self.阶段 < len(self.STAGES) - 1:
            self.经验值 -= 需求
            self.进化()
            需求 = self.获取升级经验需求()

        # 更新进化进度
        self.进化进度 = min(1.0, self.经验值 / 需求 if 需求 > 0 else 1.0)

    def 进化(self):
        """生物进化到下一阶段"""
        if self.阶段 < len(self.STAGES) - 1:
            self.阶段 += 1
            self.名称 = self.获取阶段信息()["名称"]
            # 进化时给予奖励
            奖励 = int(10 * (1.5 ** self.阶段))
            self.进化点数 += 奖励
            return True
        return False

    def 更新动画(self, dt):
        """更新动画状态"""
        self.动画角度 += dt * 0.5
        self.动画脉冲 += dt * 3
        self.动画缩放 = 1.0 + math.sin(self.动画脉冲) * 0.05


class Upgrade:
    """升级项类"""

    def __init__(self, 名称, 描述, 基础价格, 效果, 效果类型, 最大等级=999):
        self.名称 = 名称
        self.描述 = 描述
        self.基础价格 = 基础价格
        self.效果 = 效果  # 每级效果值
        self.效果类型 = 效果类型  # "点击", "自动", "倍率"
        self.最大等级 = 最大等级
        self.等级 = 0

    def 获取当前价格(self):
        """获取当前升级价格"""
        return int(self.基础价格 * (1.15 ** self.等级))

    def 获取效果值(self):
        """获取当前等级的总效果值"""
        return self.效果 * self.等级

    def 可升级(self, 进化点数):
        """检查是否可以升级"""
        return self.等级 < self.最大等级 and 进化点数 >= self.获取当前价格()

    def 升级(self):
        """执行升级"""
        if self.等级 < self.最大等级:
            self.等级 += 1
            return True
        return False


class Game:
    """游戏主类"""

    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("放置进化 - Idle Evolution")
        self.clock = pygame.time.Clock()

        # 游戏状态
        self.creature = Creature()
        self.运行中 = True
        self.暂停 = False

        # 离线收益
        self.最后更新时间 = time.time()
        self.离线时间 = 0
        self.离线收益 = 0

        # 粒子效果
        self.particles = []

        # 升级列表
        self.upgrades = [
            Upgrade("强化点击", "每次点击获得更多经验", 10, 1, "点击"),
            Upgrade("自动进化", "每秒自动获得经验", 50, 0.5, "自动"),
            Upgrade("进化效率", "增加所有经验获取", 100, 0.1, "倍率"),
            Upgrade("超级点击", "大幅增加点击输出", 500, 5, "点击"),
            Upgrade("进化加速", "增加自动产出", 1000, 2, "自动"),
            Upgrade("基因突变", "进化点数翻倍", 2500, 0.5, "倍率"),
        ]

        # UI按钮
        self.upgrade_buttons = []
        self._init_buttons()

        # 统计数据
        self.总游戏时间 = 0
        self.显示离线弹窗 = False

    def _init_buttons(self):
        """初始化升级按钮"""
        btn_width = 200
        btn_height = 45
        start_x = 650
        start_y = 80
        spacing = 55

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
                if event.button == 1:  # 左键点击
                    self.handle_click(event.pos)

            elif event.type == pygame.MOUSEMOTION:
                self.handle_mouse_move(event.pos)

    def handle_click(self, pos):
        """处理点击"""
        # 检查是否点击了生物区域
        if 50 < pos[0] < 550 and 50 < pos[1] < 550:
            self.on_creature_click()
            return

        # 检查升级按钮
        for btn in self.upgrade_buttons:
            if btn["rect"].collidepoint(pos):
                self.try_upgrade(btn["upgrade"])
                return

    def handle_mouse_move(self, pos):
        """处理鼠标移动"""
        self.mouse_pos = pos

    def on_creature_click(self):
        """生物被点击"""
        # 计算点击产出
        点击加成 = sum(u.获取效果值() for u in self.upgrades if u.效果类型 == "点击")
        倍率 = 1.0 + sum(u.获取效果值() for u in self.upgrades if u.效果类型 == "倍率")
        产出 = int((self.creature.点击输出 + 点击加成) * 倍率)

        self.creature.添加经验(产出)
        self.creature.总点击次数 += 1

        # 创建点击粒子
        self._spawn_click_particles(450, 300, 产出)

    def _spawn_click_particles(self, x, y, value):
        """生成点击粒子效果"""
        for _ in range(5):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(50, 150)
            self.particles.append({
                "x": x + random.randint(-30, 30),
                "y": y + random.randint(-30, 30),
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "life": 1.0,
                "value": value // 5,
                "color": self.creature.获取阶段信息()["颜色"]
            })

    def try_upgrade(self, upgrade):
        """尝试升级"""
        if upgrade.可升级(self.creature.进化点数):
            price = upgrade.获取当前价格()
            self.creature.进化点数 -= price
            upgrade.升级()

            # 升级粒子效果
            for _ in range(10):
                self.particles.append({
                    "x": random.randint(650, 850),
                    "y": random.randint(80, 400),
                    "vx": random.uniform(-50, 50),
                    "vy": random.uniform(-100, -50),
                    "life": 1.0,
                    "value": 0,
                    "color": COLORS['成功色']
                })

    def update(self, dt):
        """更新游戏逻辑"""
        if self.暂停:
            return

        # 更新游戏时间
        self.总游戏时间 += dt

        # 自动产出经验
        自动加成 = sum(u.获取效果值() for u in self.upgrades if u.效果类型 == "自动")
        if 自动加成 > 0:
            自动经验 = 自动加成 * dt
            self.creature.添加经验(自动经验)

        # 更新粒子
        self.update_particles(dt)

    def update_particles(self, dt):
        """更新粒子效果"""
        for p in self.particles[:]:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["vy"] += 200 * dt  # 重力
            p["life"] -= dt * 2
            if p["life"] <= 0:
                self.particles.remove(p)

    def calculate_offline_earnings(self):
        """计算离线收益"""
        当前时间 = time.time()
        间隔 = 当前时间 - self.最后更新时间

        # 如果离线超过10秒，计算收益
        if 间隔 > 10:
            self.离线时间 = int(间隔)
            自动加成 = sum(u.获取效果值() for u in self.upgrades if u.效果类型 == "自动")
            if 自动加成 > 0:
                # 离线收益为在线自动产出的50%
                self.离线收益 = int(自动加成 * 间隔 * 0.5)
                self.creature.添加经验(self.离线收益)
                self.显示离线弹窗 = True

        self.最后更新时间 = 当前时间

    def draw(self):
        """绘制游戏画面"""
        self.screen.fill(COLORS['背景'])

        # 绘制主面板
        self.draw_main_panel()

        # 绘制侧边栏
        self.draw_sidebar()

        # 绘制粒子
        self.draw_particles()

        # 绘制离线弹窗
        if self.显示离线弹窗:
            self.draw_offline_popup()

        # 绘制暂停提示
        if self.暂停:
            self.draw_pause_overlay()

        pygame.display.flip()

    def draw_main_panel(self):
        """绘制主面板（生物区域）"""
        # 主区域背景
        panel_rect = pygame.Rect(30, 30, 520, 520)
        pygame.draw.rect(self.screen, COLORS['面板背景'], panel_rect, border_radius=15)
        pygame.draw.rect(self.screen, COLORS['主色调'], panel_rect, 2, border_radius=15)

        # 绘制生物
        self.draw_creature()

        # 绘制经验条
        self.draw_exp_bar()

        # 绘制统计信息
        self.draw_stats()

    def draw_creature(self):
        """绘制生物"""
        cx, cy = 290, 280
        stage = self.creature.获取阶段信息()

        # 生物发光效果
        glow_radius = 80 * self.creature.动画缩放
        for i in range(5):
            alpha = 30 - i * 5
            glow_color = (*stage["颜色"][:3], alpha)
            pygame.draw.circle(self.screen, glow_color,
                             (cx, cy), int(glow_radius + i * 10))

        # 绘制生物主体
        base_radius = 60 * self.creature.动画缩放
        pygame.draw.circle(self.screen, stage["颜色"], (cx, cy), int(base_radius))
        pygame.draw.circle(self.screen, COLORS['背景'], (cx, cy), int(base_radius - 10))

        # 生物图标
        icon_text = stage["图标"]
        icon_surf = HEADER_FONT.render(icon_text, True, stage["颜色"])
        icon_rect = icon_surf.get_rect(center=(cx, cy))
        self.screen.blit(icon_surf, icon_rect)

        # 绘制生物名称
        name_text = f"{stage['名称']} (Lv.{self.creature.阶段 + 1})"
        name_surf = HEADER_FONT.render(name_text, True, COLORS['文字'])
        name_rect = name_surf.get_rect(center=(cx, cy + 120))
        self.screen.blit(name_surf, name_rect)

    def draw_exp_bar(self):
        """绘制经验条"""
        bar_x, bar_y = 70, 480
        bar_width, bar_height = 440, 30

        # 背景
        pygame.draw.rect(self.screen, COLORS['经验条背景'],
                        (bar_x, bar_y, bar_width, bar_height), border_radius=10)

        # 进度
        progress = self.creature.进化进度
        fill_width = int(bar_width * progress)
        if fill_width > 0:
            pygame.draw.rect(self.screen, COLORS['主色调'],
                           (bar_x, bar_y, fill_width, bar_height), border_radius=10)

        # 文字
        exp_text = f"{self.creature.经验值} / {self.creature.获取升级经验需求()}"
        exp_surf = SMALL_FONT.render(exp_text, True, COLORS['文字'])
        exp_rect = exp_surf.get_rect(center=(bar_x + bar_width // 2, bar_y + bar_height // 2))
        self.screen.blit(exp_surf, exp_rect)

        # 标签
        label_surf = SMALL_FONT.render("进化进度", True, COLORS['文字暗淡'])
        label_rect = label_surf.get_rect(bottomleft=(bar_x, bar_y - 5))
        self.screen.blit(label_surf, label_rect)

    def draw_stats(self):
        """绘制统计信息"""
        stats_y = 520
        stats = [
            f"点击次数: {self.creature.总点击次数:,}",
            f"总经验: {self.creature.总获得经验:,}",
            f"进化点数: {self.creature.进化点数:,.0f}",
        ]

        for i, stat in enumerate(stats):
            stat_surf = SMALL_FONT.render(stat, True, COLORS['文字暗淡'])
            stat_rect = stat_surf.get_rect(center=(290, stats_y + i * 20))
            self.screen.blit(stat_surf, stat_rect)

    def draw_sidebar(self):
        """绘制侧边栏（升级区域）"""
        # 侧边栏背景
        sidebar_rect = pygame.Rect(570, 30, 300, 590)
        pygame.draw.rect(self.screen, COLORS['面板背景'], sidebar_rect, border_radius=15)
        pygame.draw.rect(self.screen, COLORS['强调色'], sidebar_rect, 2, border_radius=15)

        # 标题
        title_surf = HEADER_FONT.render("进化升级", True, COLORS['强调色'])
        title_rect = title_surf.get_rect(center=(720, 60))
        self.screen.blit(title_surf, title_rect)

        # 进化点数显示
        points_text = f"进化点数: {self.creature.进化点数:,.0f}"
        points_surf = POINTS_FONT.render(points_text, True, COLORS['成功色'])
        points_rect = points_surf.get_rect(center=(720, 100))
        self.screen.blit(points_surf, points_rect)

        # 绘制升级按钮
        for btn in self.upgrade_buttons:
            self.draw_upgrade_button(btn)

    def draw_upgrade_button(self, btn):
        """绘制升级按钮"""
        upgrade = btn["upgrade"]
        rect = btn["rect"]
        can_afford = upgrade.可升级(self.creature.进化点数)

        # 按钮颜色
        if can_afford:
            btn_color = COLORS['按钮悬停']
        else:
            btn_color = COLORS['按钮正常']

        # 鼠标悬停效果
        if rect.collidepoint(pygame.mouse.get_pos()):
            btn_color = COLORS['按钮悬停'] if can_afford else COLORS['按钮正常']

        # 绘制按钮
        pygame.draw.rect(self.screen, btn_color, rect, border_radius=8)

        # 边框颜色
        border_color = COLORS['成功色'] if can_afford else COLORS['文字暗淡']
        pygame.draw.rect(self.screen, border_color, rect, 2, border_radius=8)

        # 升级名称
        name_text = f"{upgrade.名称} Lv.{upgrade.等级}"
        name_surf = SMALL_FONT.render(name_text, True, COLORS['文字'])
        self.screen.blit(name_surf, (rect.x + 10, rect.y + 5))

        # 效果描述
        effect_text = f"+{upgrade.效果}/级"
        effect_surf = SMALL_FONT.render(effect_text, True, COLORS['主色调'])
        self.screen.blit(effect_surf, (rect.x + 10, rect.y + 22))

        # 价格
        price = upgrade.获取当前价格()
        price_text = f"{price:,.0f}"
        price_color = COLORS['成功色'] if can_afford else COLORS['警告色']
        price_surf = SMALL_FONT.render(price_text, True, price_color)
        price_rect = price_surf.get_rect(right=rect.right - 10, centery=rect.centery)
        self.screen.blit(price_surf, price_rect)

    def draw_particles(self):
        """绘制粒子效果"""
        for p in self.particles:
            alpha = int(255 * p["life"])
            color = (*p["color"][:3], alpha)

            # 绘制粒子圆点
            pygame.draw.circle(self.screen, p["color"],
                             (int(p["x"]), int(p["y"])), max(1, int(5 * p["life"])))

            # 绘制数值文字
            if p["value"] > 0:
                font = SMALL_FONT
                text_surf = font.render(f"+{p['value']}", True, COLORS['成功色'])
                text_rect = text_surf.get_rect(center=(int(p["x"]), int(p["y"] - 20 * p["life"])))
                self.screen.blit(text_surf, text_rect)

    def draw_offline_popup(self):
        """绘制离线收益弹窗"""
        # 半透明遮罩
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        # 弹窗背景
        popup_rect = pygame.Rect(250, 200, 400, 200)
        pygame.draw.rect(self.screen, COLORS['面板背景'], popup_rect, border_radius=15)
        pygame.draw.rect(self.screen, COLORS['强调色'], popup_rect, 3, border_radius=15)

        # 标题
        title_surf = HEADER_FONT.render("离线收益", True, COLORS['强调色'])
        title_rect = title_surf.get_rect(center=(450, 240))
        self.screen.blit(title_surf, title_rect)

        # 离线时间
        time_text = f"离线时间: {self.离线时间}秒"
        time_surf = NORMAL_FONT.render(time_text, True, COLORS['文字'])
        time_rect = time_surf.get_rect(center=(450, 290))
        self.screen.blit(time_surf, time_rect)

        # 收益
        earnings_text = f"获得经验: +{self.离线收益:,}"
        earnings_surf = POINTS_FONT.render(earnings_text, True, COLORS['成功色'])
        earnings_rect = earnings_surf.get_rect(center=(450, 340))
        self.screen.blit(earnings_surf, earnings_rect)

        # 点击继续提示
        hint_text = "点击任意处继续"
        hint_surf = SMALL_FONT.render(hint_text, True, COLORS['文字暗淡'])
        hint_rect = hint_surf.get_rect(center=(450, 380))
        self.screen.blit(hint_surf, hint_rect)

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

            # 处理离线弹窗点击
            if self.显示离线弹窗:
                for event in pygame.event.get():
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.显示离线弹窗 = False
                continue

            self.update(dt)
            self.calculate_offline_earnings()
            self.draw()

        # 保存最后更新时间
        self.最后更新时间 = time.time()
        pygame.quit()
        sys.exit()


# 修复：修正事件类型比较
pygame.MOUSEMOTION = pygame.MOUSEMOTION


if __name__ == "__main__":
    game = Game()
    game.run()
