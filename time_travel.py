#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
穿越时空游戏 - 时间悖论
Time Travel Game - Temporal Paradox

玩家扮演一名时间特工，穿越不同时代解决历史谜题
通过选择分支改变历史，影响未来的走向
"""

import pygame
import os
import sys
import random
import math

# 初始化Pygame
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
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# 颜色定义
COLORS = {
    'bg_dark': (10, 10, 30),
    'bg_time1': (60, 30, 20),   # 远古时代 - 棕红色
    'bg_time2': (20, 40, 60),   # 古代 - 深蓝色
    'bg_time3': (40, 50, 40),   # 中世纪 - 绿色
    'bg_time4': (50, 30, 50),   # 近现代 - 紫色
    'bg_time5': (30, 50, 50),   # 未来 - 青色
    'gold': (255, 215, 0),
    'silver': (192, 192, 192),
    'red': (220, 50, 50),
    'green': (50, 200, 50),
    'blue': (100, 180, 255),
    'white': (255, 255, 255),
    'gray': (120, 120, 120),
    'purple': (180, 100, 200),
    'orange': (255, 165, 0),
    'cyan': (0, 255, 255),
    'cream': (255, 253, 208),
    'time_glow': (200, 150, 255),
}

# 字体设置
def get_font(size):
    """获取字体"""
    fonts = [
        "C:/Windows/Fonts/msyh.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
    ]
    for font_path in fonts:
        try:
            return pygame.font.Font(font_path, size)
        except:
            continue
    return get_chinese_font(size)

class TimeAgent:
    """时间特工类"""
    def __init__(self, codename):
        self.codename = codename
        self.mission_level = 1
        self.temporal_energy = 100
        self.max_energy = 100
        self.knowledge = 50      # 知识值
        self.intuition = 50      # 直觉值
        self.paradox_risk = 0    # 悖论风险
        self.inventory = []
        self.visited_eras = []
        self.completed_missions = []
        self.time_anomalies_fixed = 0
        self.relationships = {}  # 与历史人物的关系

    def use_temporal_energy(self, amount):
        """使用时间能量"""
        if self.temporal_energy >= amount:
            self.temporal_energy -= amount
            return True
        return False

    def add_anomaly(self):
        """增加悖论风险"""
        self.paradox_risk += 5
        if self.paradox_risk >= 100:
            return True  # 游戏失败条件
        return False

class TimeEra:
    """时代类"""
    def __init__(self, name, year, description, bg_colors, difficulty, missions):
        self.name = name
        self.year = year
        self.description = description
        self.bg_colors = bg_colors
        self.difficulty = difficulty
        self.missions = missions
        self.events = []
        self.key_figures = []

class TemporalDevice:
    """时间设备类"""
    def __init__(self):
        self.charging = False
        self.charge_level = 100
        self.current_mode = 'normal'  # normal, stealth, analysis

    def charge(self, amount=5):
        """充能"""
        self.charge_level = min(100, self.charge_level + amount)

class Game:
    """游戏主类"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("时间悖论 - 穿越时空游戏")
        self.clock = pygame.time.Clock()
        self.running = True

        # 字体
        self.font_title = get_font(48)
        self.font_large = get_font(32)
        self.font_normal = get_font(24)
        self.font_small = get_font(18)

        # 游戏状态
        self.game_state = 'menu'
        self.agent = None
        self.temporal_device = TemporalDevice()
        self.current_era = None
        self.current_mission = None
        self.current_scene = 'arrival'
        self.dialog_text = []
        self.dialog_index = 0
        self.time_portal_effect = 0

        # 时间和时代数据
        self.eras = self.init_eras()

    def init_eras(self):
        """初始化时代数据"""
        return {
            'ancient': TimeEra(
                "远古文明",
                "公元前3000年",
                "苏美尔城邦时期，美索不达米亚平原上诞生了最早的文字",
                (COLORS['bg_time1'], (80, 50, 30)),
                1,
                ['artifact', 'prophecy', 'collapse']
            ),
            'dynasty': TimeEra(
                "秦汉盛世",
                "公元前206年",
                "中国历史上第一个大一统王朝刚刚建立",
                (COLORS['bg_time2'], (30, 60, 90)),
                2,
                ['unification', 'secret', 'betrayal']
            ),
            'medieval': TimeEra(
                "骑士时代",
                "公元1180年",
                "欧洲中世纪，骑士精神和王国战争交织的时代",
                (COLORS['bg_time3'], (60, 80, 60)),
                3,
                ['quest', 'tournament', 'conspiracy']
            ),
            'modern': TimeEra(
                "工业革命",
                "公元1888年",
                "蒸汽机和电气改变了人类社会的面貌",
                (COLORS['bg_time4'], (80, 50, 80)),
                4,
                ['invention', 'revolution', 'mystery']
            ),
            'future': TimeEra(
                "星际纪元",
                "公元2457年",
                "人类已经殖民了多个星系，但新的危机正在酝酿",
                (COLORS['bg_time5'], (50, 80, 80)),
                5,
                ['crisis', 'revelation', 'choice']
            ),
        }

    def create_background(self, color1, color2, offset=0):
        """创建动态渐变背景"""
        surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        for y in range(SCREEN_HEIGHT):
            ratio = (y + offset * 10) % SCREEN_HEIGHT / SCREEN_HEIGHT
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            pygame.draw.line(surface, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        return surface

    def draw_time_particles(self, surface):
        """绘制时间粒子效果"""
        time = pygame.time.get_ticks() / 1000
        for i in range(20):
            x = (math.sin(time + i) * 0.5 + 0.5) * SCREEN_WIDTH
            y = (i / 20) * SCREEN_HEIGHT + math.sin(time * 2 + i * 0.5) * 20
            size = 2 + math.sin(time * 3 + i) * 1
            pygame.draw.circle(surface, COLORS['time_glow'], (int(x), int(y)), int(size), 1)

    def draw_text(self, text, font, color, x, y, center=False):
        """绘制文本"""
        text_surface = font.render(text, True, color)
        if center:
            rect = text_surface.get_rect(center=(x, y))
        else:
            rect = text_surface.get_rect(topleft=(x, y))
        self.screen.blit(text_surface, rect)
        return rect.bottom

    def draw_button(self, text, x, y, width, height, color, hover_color, action=None, icon=None):
        """绘制按钮"""
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        button_rect = pygame.Rect(x, y, width, height)
        hovered = button_rect.collidepoint(mouse)

        if hovered:
            pygame.draw.rect(self.screen, hover_color, button_rect, border_radius=12)
            if click[0] == 1 and action:
                pygame.time.wait(100)
                return action()
        else:
            pygame.draw.rect(self.screen, color, button_rect, border_radius=12)

        pygame.draw.rect(self.screen, COLORS['cyan'], button_rect, 2, border_radius=12)

        # 图标
        if icon:
            self.draw_text(icon, self.font_small, COLORS['white'], x + 20, y + height // 2 - 10)

        self.draw_text(text, self.font_normal, COLORS['white'], x + width // 2, y + height // 2, center=True)
        return None

    def draw_dialog_box(self, speaker, text, era_info=None):
        """绘制对话框"""
        box_height = 180
        box_y = SCREEN_HEIGHT - box_height - 30

        # 对话框
        dialog_rect = pygame.Rect(60, box_y, SCREEN_WIDTH - 120, box_height)
        pygame.draw.rect(self.screen, (20, 20, 40), dialog_rect, border_radius=15)
        pygame.draw.rect(self.screen, COLORS['cyan'], dialog_rect, 2, border_radius=15)

        # 说话者
        if speaker:
            name_rect = pygame.Rect(80, box_y - 30, 200, 40)
            pygame.draw.rect(self.screen, COLORS['purple'], name_rect, border_radius=8)
            self.draw_text(speaker, self.font_normal, COLORS['white'],
                          name_rect.centerx, name_rect.centery, center=True)

        # 时代信息
        if era_info:
            self.draw_text(f"[{era_info}]", self.font_small, COLORS['time_glow'],
                          SCREEN_WIDTH - 180, box_y + 15)

        # 文本
        lines = self.wrap_text(text, self.font_normal, SCREEN_WIDTH - 200)
        y_pos = box_y + 20
        for line in lines[:4]:
            self.draw_text(line, self.font_normal, COLORS['cream'], 100, y_pos)
            y_pos += 35

        # 继续提示
        self.draw_text("[点击继续]", self.font_small, COLORS['gray'],
                      SCREEN_WIDTH - 160, box_y + box_height - 30)

    def wrap_text(self, text, font, max_width):
        """文本换行"""
        lines = []
        current = ""
        for char in text:
            test = current + char
            if font.size(test)[0] <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = char
        if current:
            lines.append(current)
        return lines if lines else [text]

    def draw_time_device_ui(self):
        """绘制时间设备UI"""
        # 能量条
        pygame.draw.rect(self.screen, (30, 30, 50), (20, 20, 250, 80), border_radius=10)
        pygame.draw.rect(self.screen, COLORS['cyan'], (20, 20, 250, 80), 2, border_radius=10)

        self.draw_text("时间装置", self.font_small, COLORS['cyan'], 30, 30)
        self.draw_text(f"能量: {self.temporal_device.charge_level}%", self.font_small, COLORS['white'], 30, 55)

        # 能量条
        energy_rect = pygame.Rect(30, 75, 200, 15)
        pygame.draw.rect(self.screen, (50, 50, 80), energy_rect, border_radius=5)
        pygame.draw.rect(self.screen, COLORS['cyan'],
                        (30, 75, int(200 * self.temporal_device.charge_level / 100), 15), border_radius=5)

    def draw_agent_status(self, agent):
        """绘制特工状态"""
        panel_rect = pygame.Rect(20, 120, 250, 200)
        pygame.draw.rect(self.screen, (20, 20, 40), panel_rect, border_radius=10)
        pygame.draw.rect(self.screen, COLORS['purple'], panel_rect, 2, border_radius=10)

        self.draw_text(f"特工代号: {agent.codename}", self.font_normal, COLORS['gold'], 35, 135)
        self.draw_text(f"任务等级: Lv.{agent.mission_level}", self.font_small, COLORS['silver'], 35, 170)

        # 知识/直觉
        self.draw_text(f"知识: {agent.knowledge}", self.font_small, COLORS['blue'], 35, 200)
        self.draw_text(f"直觉: {agent.intuition}", self.font_small, COLORS['green'], 35, 225)

        # 悖论风险
        self.draw_text(f"悖论风险: {agent.paradox_risk}%", self.font_small,
                      COLORS['red'] if agent.paradox_risk > 50 else COLORS['orange'], 35, 250)

        if agent.paradox_risk > 70:
            self.draw_text("警告: 接近临界点!", self.font_small, COLORS['red'], 35, 275)

    def draw_era_timeline(self):
        """绘制时间线"""
        timeline_y = SCREEN_HEIGHT - 60
        pygame.draw.line(self.screen, COLORS['gray'], (50, timeline_y), (SCREEN_WIDTH - 50, timeline_y), 2)

        eras = list(self.eras.keys())
        for i, era_key in enumerate(eras):
            x = 100 + i * 220
            era = self.eras[era_key]

            # 节点
            color = COLORS['green'] if era_key in self.agent.visited_eras else COLORS['gray']
            pygame.draw.circle(self.screen, color, (x, timeline_y), 12)

            # 时代名称
            visited = "V" if era_key in self.agent.visited_eras else ""
            self.draw_text(f"{era.year}", self.font_small, color, x, timeline_y - 40, center=True)
            self.draw_text(f"{era.name[:3]}{visited}", self.font_small, COLORS['white'], x, timeline_y + 15, center=True)

    def main_menu(self):
        """主菜单"""
        self.time_portal_effect = (self.time_portal_effect + 1) % 360
        bg = self.create_background((5, 5, 20), (30, 20, 50), self.time_portal_effect)
        self.draw_time_particles(bg)
        self.screen.blit(bg, (0, 0))

        # 装饰边框
        for i in range(3):
            pygame.draw.rect(self.screen, COLORS['cyan'], 
                           (30 + i*5, 30 + i*5, SCREEN_WIDTH - 60 - i*10, SCREEN_HEIGHT - 60 - i*10),
                           1, border_radius=25)

        # 标题
        title_y = 120 + math.sin(self.time_portal_effect * 0.02) * 5
        self.draw_text("时间悖论", self.font_title, COLORS['cyan'], SCREEN_WIDTH // 2, title_y, center=True)
        self.draw_text("TEMPORAL PARADOX", self.font_normal, COLORS['time_glow'], SCREEN_WIDTH // 2, title_y + 60, center=True)
        self.draw_text("穿越时空的冒险之旅", self.font_large, COLORS['gold'], SCREEN_WIDTH // 2, title_y + 120, center=True)

        # 按钮
        self.draw_button("开始任务", SCREEN_WIDTH // 2 - 150, 380, 300, 60, COLORS['bg_dark'], COLORS['cyan'])
        self.draw_button("继续任务", SCREEN_WIDTH // 2 - 150, 460, 300, 60, COLORS['bg_dark'], COLORS['green'])
        self.draw_button("任务简报", SCREEN_WIDTH // 2 - 150, 540, 300, 60, COLORS['bg_dark'], COLORS['purple'])
        self.draw_button("退出", SCREEN_WIDTH // 2 - 150, 620, 300, 60, COLORS['bg_dark'], COLORS['red'])

        # 底部信息
        self.draw_text("时间特工总部 | 行动代号: Chronos", self.font_small, COLORS['gray'], SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40, center=True)

    def agent_setup_screen(self):
        """特工设定界面"""
        bg = self.create_background((10, 10, 30), (40, 30, 70))
        self.screen.blit(bg, (0, 0))

        self.draw_text("任务简报", self.font_title, COLORS['gold'], SCREEN_WIDTH // 2, 50, center=True)
        self.draw_text("TIME AGENT REGISTRATION", self.font_normal, COLORS['silver'], SCREEN_WIDTH // 2, 110, center=True)

        # 任务描述
        mission_text = [
            "特工，你的任务是穿越不同历史时代，",
            "调查并修复时间异常，防止历史被篡改。",
            "",
            "警告：过多的时间干预可能导致悖论累积，",
            "当悖论风险达到100%时，时间线将崩溃。",
            "",
            "请输入你的特工代号：",
        ]

        y_pos = 180
        for line in mission_text:
            color = COLORS['red'] if "警告" in line else COLORS['cream']
            self.draw_text(line, self.font_normal, color, SCREEN_WIDTH // 2, y_pos, center=True)
            y_pos += 40

        # 输入框
        input_rect = pygame.Rect(SCREEN_WIDTH // 2 - 180, y_pos + 20, 360, 50)
        pygame.draw.rect(self.screen, COLORS['bg_dark'], input_rect, border_radius=10)
        pygame.draw.rect(self.screen, COLORS['cyan'], input_rect, 2, border_radius=10)
        self.draw_text(getattr(self, 'agent_name', '') + "_", self.font_large, COLORS['white'],
                       SCREEN_WIDTH // 2, y_pos + 38, center=True)

        y_pos += 100
        self.draw_button("确认", SCREEN_WIDTH // 2 - 80, y_pos, 160, 50, COLORS['bg_dark'], COLORS['green'])
        self.draw_button("返回", SCREEN_WIDTH // 2 - 80, y_pos + 70, 160, 50, COLORS['bg_dark'], COLORS['gray'])

    def era_selection_screen(self):
        """时代选择界面"""
        bg = self.create_background((10, 10, 30), (30, 40, 60))
        self.screen.blit(bg, (0, 0))

        self.draw_text("选择目标时代", self.font_title, COLORS['gold'], SCREEN_WIDTH // 2, 30, center=True)
        self.draw_time_device_ui()

        y_pos = 120
        for i, (era_key, era) in enumerate(self.eras.items()):
            x = 100 + (i % 3) * 350
            y = 120 + (i // 3) * 250

            # 时代卡片
            card_rect = pygame.Rect(x, y, 320, 220)
            pygame.draw.rect(self.screen, COLORS['bg_dark'], card_rect, border_radius=15)
            pygame.draw.rect(self.screen, COLORS['gold'], card_rect, 2, border_radius=15)

            # 时代名称
            self.draw_text(era.name, self.font_large, COLORS['gold'], x + 160, y + 20, center=True)
            self.draw_text(era.year, self.font_normal, COLORS['silver'], x + 160, y + 60, center=True)

            # 描述
            lines = self.wrap_text(era.description, self.font_small, 280)
            text_y = y + 100
            for line in lines[:3]:
                self.draw_text(line, self.font_small, COLORS['cream'], x + 160, text_y, center=True)
                text_y += 25

            # 难度
            difficulty_color = COLORS['green'] if era.difficulty <= 2 else COLORS['orange'] if era.difficulty <= 4 else COLORS['red']
            self.draw_text(f"难度: {'★' * era.difficulty}", self.font_small, difficulty_color, x + 160, y + 180, center=True)

            # 已访问标记
            if era_key in self.agent.visited_eras:
                self.draw_text("[已访问]", self.font_small, COLORS['green'], x + 160, y + 200, center=True)

    def mission_briefing(self, era_key):
        """任务简报"""
        era = self.eras[era_key]
        bg = self.create_background(era.bg_colors[0], era.bg_colors[1])
        self.screen.blit(bg, (0, 0))

        self.draw_text(f"任务简报 - {era.name}", self.font_title, COLORS['gold'], SCREEN_WIDTH // 2, 30, center=True)
        self.draw_time_device_ui()

        # 时代描述
        briefing = [
            f"目标时代: {era.year}",
            f"地点: {era.name}",
            f"任务难度: {'★' * era.difficulty}",
            "",
            "任务目标:",
        ]

        missions = {
            'ancient': ['寻找失落的时间碎片', '调查预言的真相', '阻止文明提前崩溃'],
            'dynasty': ['协助完成历史统一大业', '寻找帝王秘籍', '揭露宫廷阴谋'],
            'medieval': ['完成圣杯任务', '参加骑士比武', '调查王国密谋'],
            'modern': ['保护发明的诞生', '阻止革命失败', '解开世纪之谜'],
            'future': ['应对星际危机', '揭露重大秘密', '做出最终抉择'],
        }

        y_pos = 120
        for line in briefing:
            self.draw_text(line, self.font_normal, COLORS['white'], 100, y_pos)
            y_pos += 35

        for i, mission in enumerate(missions.get(era_key, [])):
            self.draw_text(f"  {i+1}. {mission}", self.font_normal, COLORS['cyan'], 100, y_pos)
            y_pos += 35

        # 时间能量消耗提示
        energy_cost = era.difficulty * 15
        self.draw_text(f"预计能量消耗: {energy_cost}%", self.font_small, COLORS['orange'], 100, y_pos + 30)

        # 行动按钮
        y_pos = 500
        self.draw_button("开始任务", 200, y_pos, 180, 50, COLORS['bg_dark'], COLORS['green'])
        self.draw_button("返回选择", 500, y_pos, 180, 50, COLORS['bg_dark'], COLORS['gray'])
        self.draw_button("返回主菜单", 800, y_pos, 180, 50, COLORS['bg_dark'], COLORS['red'])

    def time_travel_animation(self, era_key):
        """时间旅行动画"""
        era = self.eras[era_key]
        energy_cost = era.difficulty * 15

        if not self.agent.use_temporal_energy(energy_cost):
            self.show_error_message("时间能量不足！")
            return

        self.game_state = 'traveling'
        self.travel_progress = 0
        self.target_era = era_key

    def traveling_screen(self):
        """旅行中界面"""
        era = self.eras[self.target_era]

        # 动态背景
        t = pygame.time.get_ticks() / 100
        bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        for y in range(SCREEN_HEIGHT):
            wave = math.sin(y * 0.05 + t) * 30
            r = int(era.bg_colors[0][0] + wave)
            g = int(era.bg_colors[0][1] + wave)
            b = int(era.bg_colors[0][2] + wave)
            pygame.draw.line(bg, (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))), (0, y), (SCREEN_WIDTH, y))
        self.screen.blit(bg, (0, 0))

        # 时间裂缝效果
        for i in range(30):
            angle = t * 2 + i * 0.5
            x = SCREEN_WIDTH // 2 + math.cos(angle) * (100 + i * 10)
            y = SCREEN_HEIGHT // 2 + math.sin(angle) * (50 + i * 5)
            size = 2 + (i % 3)
            pygame.draw.circle(self.screen, COLORS['time_glow'], (int(x), int(y)), size)

        # 中心文字
        self.draw_text("时间传送中...", self.font_title, COLORS['cyan'], SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50, center=True)
        self.draw_text(era.year, self.font_large, COLORS['gold'], SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20, center=True)
        self.draw_text(era.name, self.font_large, COLORS['white'], SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70, center=True)

        # 进度条
        self.travel_progress += 2
        progress_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 + 150, 400, 30)
        pygame.draw.rect(self.screen, COLORS['bg_dark'], progress_rect, border_radius=15)
        pygame.draw.rect(self.screen, COLORS['cyan'], (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 + 150,
                        int(400 * self.travel_progress / 100), 30), border_radius=15)

        if self.travel_progress >= 100:
            self.arrive_at_era(self.target_era)

    def arrive_at_era(self, era_key):
        """抵达时代"""
        self.current_era = era_key
        self.agent.visited_eras.append(era_key)
        self.game_state = 'mission'
        self.current_scene = 'arrival'
        self.show_arrival_scene()

    def show_arrival_scene(self):
        """显示抵达场景"""
        era = self.eras[self.current_era]
        bg = self.create_background(era.bg_colors[0], era.bg_colors[1])
        self.screen.blit(bg, (0, 0))

        # 时代标识
        era_tag = pygame.Rect(SCREEN_WIDTH // 2 - 100, 20, 200, 50)
        pygame.draw.rect(self.screen, COLORS['gold'], era_tag, border_radius=10)
        self.draw_text(f"{era.name} | {era.year}", self.font_normal, COLORS['bg_dark'],
                      SCREEN_WIDTH // 2, 38, center=True)

        self.draw_time_device_ui()
        self.draw_agent_status(self.agent)

        # 场景内容
        scenes = {
            'ancient': {
                'arrival': [
                    ("时间特工", "我到达了美索不达米亚平原...这就是传说中的苏美尔文明吗？"),
                    ("当地人", "异乡人，你从哪里来？你的服饰好生奇怪。"),
                    ("时间特工", "我来自远方...请问这里最近发生了什么异常的事吗？"),
                    ("当地人", "预言师说，一块来自天空的神秘石板将决定我们文明的命运。"),
                ],
                'choices': [
                    ('调查神秘石板', 'investigate'),
                    ('寻找预言师', 'prophet'),
                    ('收集情报', 'gather_info'),
                ]
            },
            'dynasty': {
                'arrival': [
                    ("时间特工", "秦朝...始皇帝统一六国不久后的时代。"),
                    ("士兵", "站住！你是何人？为何穿着如此怪异？"),
                    ("时间特工", "我...我来自西域的使者，来觐见陛下。"),
                    ("士兵", "哼，跟我来吧。陛下正在寻找能人异士。"),
                ],
                'choices': [
                    ('随士兵入宫', 'palace'),
                    ('趁机逃走调查', 'escape'),
                    ('表明身份协助', 'reveal'),
                ]
            },
            'medieval': {
                'arrival': [
                    ("时间特工", "欧洲中世纪...空气中弥漫着骑士精神的气息。"),
                    ("骑士", "旅人，你来参加比武大会吗？"),
                    ("时间特工", "是的，我听闻这里是英雄聚集之地。"),
                    ("骑士", "小心了，今年的比武不太平，有人暗中作祟。"),
                ],
                'choices': [
                    ('参加比武', 'tournament'),
                    ('调查阴谋', 'conspiracy'),
                    ('寻找圣杯传说', 'grail'),
                ]
            },
            'modern': {
                'arrival': [
                    ("时间特工", "维多利亚时代...工业革命的浪潮正在改变世界。"),
                    ("发明家", "太好了！我需要一个助手来完成我的伟大发明！"),
                    ("时间特工", "您的发明是...??"),
                    ("发明家", "电能！它将照亮整个世界——如果没人阻止的话。"),
                ],
                'choices': [
                    ('协助发明', 'invention'),
                    ('调查威胁', 'threat'),
                    ('探索城市', 'explore'),
                ]
            },
            'future': {
                'arrival': [
                    ("时间特工", "2457年...人类的足迹已经遍布星系。"),
                    ("AI管家", "检测到时间异常。欢迎回来，时间特工。"),
                    ("时间特工", "情况如何？"),
                    ("AI管家", "不太好...星际议会发现了时间操纵的迹象。"),
                ],
                'choices': [
                    ('前往议会', 'council'),
                    ('调查异常源头', 'anomaly'),
                    ('寻找盟友', 'ally'),
                ]
            },
        }

        scene_data = scenes.get(self.current_era, scenes['ancient'])

        # 对话显示
        y_pos = 150
        if hasattr(self, 'dialog_lines'):
            for speaker, text in self.dialog_lines:
                color = COLORS['cyan'] if speaker == "时间特工" else COLORS['orange']
                self.draw_text(f"{speaker}: {text}", self.font_normal, color, 100, y_pos)
                y_pos += 40

        # 继续或选项
        if hasattr(self, 'dialog_index') and self.dialog_index < len(scene_data['arrival']):
            if not hasattr(self, 'dialog_lines') or len(self.dialog_lines) < self.dialog_index + 1:
                pass
            else:
                self.draw_button("继续", SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT - 150, 160, 45,
                               COLORS['bg_dark'], COLORS['blue'])
        else:
            self.draw_text("你决定怎么做？", self.font_large, COLORS['gold'], SCREEN_WIDTH // 2, SCREEN_HEIGHT - 200, center=True)
            y_pos = SCREEN_HEIGHT - 160
            for choice, next_scene in scene_data['choices']:
                self.draw_button(choice, SCREEN_WIDTH // 2 - 200, y_pos, 400, 45,
                               COLORS['bg_dark'], COLORS['purple'])
                y_pos += 55

    def advance_dialog(self):
        """推进对话"""
        era_scenes = {
            'ancient': [
                ("时间特工", "我到达了美索不达米亚平原...这就是传说中的苏美尔文明吗？"),
                ("当地人", "异乡人，你从哪里来？你的服饰好生奇怪。"),
                ("时间特工", "我来自远方...请问这里最近发生了什么异常的事吗？"),
                ("当地人", "预言师说，一块来自天空的神秘石板将决定我们文明的命运。"),
            ],
            'dynasty': [
                ("时间特工", "秦朝...始皇帝统一六国不久后的时代。"),
                ("士兵", "站住！你是何人？为何穿着如此怪异？"),
                ("时间特工", "我...我来自西域的使者，来觐见陛下。"),
                ("士兵", "哼，跟我来吧。陛下正在寻找能人异士。"),
            ],
            'medieval': [
                ("时间特工", "欧洲中世纪...空气中弥漫着骑士精神的气息。"),
                ("骑士", "旅人，你来参加比武大会吗？"),
                ("时间特工", "是的，我听闻这里是英雄聚集之地。"),
                ("骑士", "小心了，今年的比武不太平，有人暗中作祟。"),
            ],
            'modern': [
                ("时间特工", "维多利亚时代...工业革命的浪潮正在改变世界。"),
                ("发明家", "太好了！我需要一个助手来完成我的伟大发明！"),
                ("时间特工", "您的发明是...?"),
                ("发明家", "电能！它将照亮整个世界——如果没人阻止的话。"),
            ],
            'future': [
                ("时间特工", "2457年...人类的足迹已经遍布星系。"),
                ("AI管家", "检测到时间异常。欢迎回来，时间特工。"),
                ("时间特工", "情况如何？"),
                ("AI管家", "不太好...星际议会发现了时间操纵的迹象。"),
            ],
        }

        if not hasattr(self, 'dialog_lines'):
            self.dialog_lines = []

        scenes = era_scenes.get(self.current_era, era_scenes['ancient'])
        if self.dialog_index < len(scenes):
            self.dialog_lines.append(scenes[self.dialog_index])
            self.dialog_index += 1

    def select_choice(self, choice_key):
        """选择分支"""
        consequences = {
            'investigate': ("你发现了时间碎片的秘密！", 'knowledge', 15, 20),
            'prophet': ("预言师揭示了真相...", 'intuition', 20, 15),
            'gather_info': ("你收集了大量情报。", 'knowledge', 10, 10),
            'palace': ("你进入了皇宫...", 'knowledge', 15, 25),
            'escape': ("你逃脱并开始调查。", 'intuition', 10, 20),
            'reveal': ("你冒险表明了身份。", 'paradox', 30, -10),
            'tournament': ("你参加了骑士比武！", 'knowledge', 20, 20),
            'conspiracy': ("你发现了阴谋的线索。", 'intuition', 15, 15),
            'grail': ("圣杯传说原来是...", 'knowledge', 25, 30),
            'invention': ("你协助完成了发明！", 'knowledge', 20, 25),
            'threat': ("威胁来自...", 'intuition', 15, 20),
            'explore': ("你探索了工业革命的城市。", 'knowledge', 10, 15),
            'council': ("星际议会正在召开...", 'knowledge', 15, 20),
            'anomaly': ("异常的源头是...", 'intuition', 20, 25),
            'ally': ("你找到了可靠的盟友。", 'knowledge', 10, 15),
        }

        if choice_key in consequences:
            msg, stat, val, paradox = consequences[choice_key]
            self.show_choice_result(msg, stat, val, paradox)

    def show_choice_result(self, message, stat, value, paradox):
        """显示选择结果"""
        bg = self.create_background((20, 20, 40), (50, 50, 100))
        self.screen.blit(bg, (0, 0))

        era = self.eras[self.current_era]
        self.draw_text(f"{era.name} - 任务结果", self.font_title, COLORS['gold'], SCREEN_WIDTH // 2, 50, center=True)

        # 结果显示
        self.draw_text(message, self.font_large, COLORS['cream'], SCREEN_WIDTH // 2, 200, center=True)

        # 属性变化
        result_y = 300
        if stat == 'knowledge':
            self.agent.knowledge += value
            self.draw_text(f"知识 +{value}", self.font_normal, COLORS['blue'], SCREEN_WIDTH // 2, result_y, center=True)
        elif stat == 'intuition':
            self.agent.intuition += value
            self.draw_text(f"直觉 +{value}", self.font_normal, COLORS['green'], SCREEN_WIDTH // 2, result_y, center=True)

        self.agent.paradox_risk = max(0, self.agent.paradox_risk + paradox)
        if paradox > 0:
            self.draw_text(f"悖论风险 +{paradox}%", self.font_normal, COLORS['red'], SCREEN_WIDTH // 2, result_y + 50, center=True)
        else:
            self.draw_text(f"悖论风险 {paradox}%", self.font_normal, COLORS['green'], SCREEN_WIDTH // 2, result_y + 50, center=True)

        # 任务完成检查
        self.agent.completed_missions.append(f"{self.current_era}_{self.current_scene}")
        self.agent.time_anomalies_fixed += 1

        # 恢复能量
        self.temporal_device.charge_level = min(100, self.temporal_device.charge_level + 10)

        # 检查悖论
        if self.agent.paradox_risk >= 100:
            self.game_state = 'game_over'
        else:
            # 继续按钮
            if len(self.agent.visited_eras) >= 3:
                self.draw_button("返回总部", SCREEN_WIDTH // 2 - 100, 500, 200, 50, COLORS['bg_dark'], COLORS['gold'])
            else:
                self.draw_button("继续任务", SCREEN_WIDTH // 2 - 100, 450, 200, 50, COLORS['bg_dark'], COLORS['green'])
                self.draw_button("返回选择时代", SCREEN_WIDTH // 2 - 100, 520, 200, 50, COLORS['bg_dark'], COLORS['gray'])
                self.draw_button("返回总部", SCREEN_WIDTH // 2 - 100, 590, 200, 50, COLORS['bg_dark'], COLORS['red'])

    def game_over_screen(self):
        """游戏结束"""
        bg = self.create_background((80, 10, 10), (20, 5, 5))
        self.screen.blit(bg, (0, 0))

        # 时间崩溃效果
        for i in range(50):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            pygame.draw.line(self.screen, COLORS['red'], (x, y), (x + 20, y), 2)

        self.draw_text("时间线崩溃", self.font_title, COLORS['red'], SCREEN_WIDTH // 2, 150, center=True)
        self.draw_text("由于过度干预历史，时间悖论无法挽回...", self.font_normal, COLORS['cream'], SCREEN_WIDTH // 2, 250, center=True)

        # 统计
        self.draw_text(f"访问时代数: {len(self.agent.visited_eras)}", self.font_normal, COLORS['silver'], SCREEN_WIDTH // 2, 350, center=True)
        self.draw_text(f"修复异常数: {self.agent.time_anomalies_fixed}", self.font_normal, COLORS['green'], SCREEN_WIDTH // 2, 400, center=True)
        self.draw_text(f"最终知识: {self.agent.knowledge}", self.font_normal, COLORS['blue'], SCREEN_WIDTH // 2, 450, center=True)
        self.draw_text(f"最终直觉: {self.agent.intuition}", self.font_normal, COLORS['cyan'], SCREEN_WIDTH // 2, 500, center=True)

        self.draw_button("重新开始", SCREEN_WIDTH // 2 - 100, 600, 200, 50, COLORS['bg_dark'], COLORS['gold'])

    def run(self):
        """主循环"""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.game_state in ['era_selection', 'mission']:
                            self.game_state = 'menu'
                    elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        if self.game_state == 'mission':
                            if hasattr(self, 'dialog_index') and self.dialog_index < 4:
                                self.advance_dialog()

            # 点击处理
            click = pygame.mouse.get_pressed()
            if click[0]:
                mx, my = pygame.mouse.get_pos()
                self.handle_click(mx, my)
                pygame.time.wait(100)

            # 渲染
            if self.game_state == 'menu':
                self.main_menu()
            elif self.game_state == 'setup':
                self.agent_setup_screen()
            elif self.game_state == 'era_selection':
                self.era_selection_screen()
            elif self.game_state == 'briefing':
                self.mission_briefing(self.current_era)
            elif self.game_state == 'traveling':
                self.traveling_screen()
            elif self.game_state == 'mission':
                self.show_arrival_scene()
            elif self.game_state == 'choice_result':
                pass  # 结果在show_choice_result中
            elif self.game_state == 'game_over':
                self.game_over_screen()

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

    def handle_click(self, x, y):
        """处理点击"""
        # 菜单按钮
        if self.game_state == 'menu':
            if 370 <= x <= 670:
                if 380 <= y <= 440:
                    self.game_state = 'setup'
                    self.agent_name = ''
                elif 460 <= y <= 520:
                    self.game_state = 'era_selection'
                    if not self.agent:
                        self.agent = TimeAgent("特工001")
                elif 540 <= y <= 600:
                    self.show_mission_overview()
                elif 620 <= y <= 680:
                    self.running = False

        elif self.game_state == 'setup':
            if 460 <= y <= 510 and 520 <= x <= 680:
                if self.agent_name:
                    self.agent = TimeAgent(self.agent_name)
                    self.game_state = 'era_selection'
            elif 530 <= y <= 580 and 520 <= x <= 680:
                self.game_state = 'menu'

        elif self.game_state == 'era_selection':
            # 时代卡片点击
            for i, era_key in enumerate(self.eras.keys()):
                col = i % 3
                row = i // 3
                cx = 100 + col * 350
                cy = 120 + row * 250
                if cx <= x <= cx + 320 and cy <= y <= cy + 220:
                    self.current_era = era_key
                    self.game_state = 'briefing'

        elif self.game_state == 'briefing':
            if 200 <= y <= 250:
                if 200 <= x <= 380:
                    self.time_travel_animation(self.current_era)
                elif 500 <= x <= 680:
                    self.game_state = 'era_selection'
            elif 620 <= y <= 670 and 800 <= x <= 980:
                self.game_state = 'menu'

        elif self.game_state == 'mission':
            # 对话继续
            if hasattr(self, 'dialog_index') and self.dialog_index < 4:
                if 900 <= x <= 1100 and 600 <= y <= 650:
                    self.advance_dialog()
            else:
                # 选择分支
                scenes = {
                    'ancient': [('investigate', 250), ('prophet', 305), ('gather_info', 360)],
                    'dynasty': [('palace', 250), ('escape', 305), ('reveal', 360)],
                    'medieval': [('tournament', 250), ('conspiracy', 305), ('grail', 360)],
                    'modern': [('invention', 250), ('threat', 305), ('explore', 360)],
                    'future': [('council', 250), ('anomaly', 305), ('ally', 360)],
                }
                era_choices = scenes.get(self.current_era, scenes['ancient'])
                for choice, cy in era_choices:
                    if 300 <= y <= cy + 45 and 400 <= x <= 800:
                        self.select_choice(choice)

        elif self.game_state == 'choice_result':
            if 450 <= y <= 500:
                self.game_state = 'era_selection'
            elif 520 <= y <= 570:
                self.game_state = 'era_selection'
            elif 590 <= y <= 640:
                self.game_state = 'menu'

        elif self.game_state == 'game_over':
            if 500 <= y <= 550:
                self.game_state = 'menu'
                self.agent = None

    def show_mission_overview(self):
        """显示任务总览"""
        self.game_state = 'overview'
        self.overview_page = 0

    def show_error_message(self, msg):
        """显示错误信息"""
        self.error_message = msg
        self.error_timer = 60

if __name__ == "__main__":
    game = Game()
    game.run()
