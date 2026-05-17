#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多人找不同游戏 (Multiplayer Spot the Difference)
合作找茬游戏，支持2-4人同时在两幅图片中找出不同之处

玩法:
- 两张相似的图片并排显示
- 玩家轮流点击找出不同之处
- 合作模式: 所有玩家一起找完所有不同
- 对战模式: 玩家竞争找出更多不同

作者: Party Game Collection
依赖: pygame
"""

import pygame
import os
import random
import sys
import math

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
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 200, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 200, 0)
PURPLE = (150, 50, 200)
ORANGE = (255, 150, 0)
PINK = (255, 100, 150)
CYAN = (0, 200, 200)
GRAY = (100, 100, 100)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (50, 50, 50)
DARK_BLUE = (20, 20, 80)
GOLD = (255, 215, 0)

# 玩家颜色
PLAYER_COLORS = [RED, BLUE, GREEN, PURPLE]
PLAYER_NAMES = ["玩家 1", "玩家 2", "玩家 3", "玩家 4"]

# 场景类型
SCENE_TYPES = [
    "room", "garden", "street", "beach", "forest", "mountain",
    "city", "village", "kitchen", "classroom", "office", "park"
]


class DifferenceSpot:
    """不同点检测区域"""
    def __init__(self, x, y, radius, description):
        self.x = x
        self.y = y
        self.radius = radius
        self.description = description
        self.found = False
        self.found_by = None


class Scene:
    """游戏场景"""
    def __init__(self, scene_type, difficulty):
        self.type = scene_type
        self.difficulty = difficulty
        self.differences = []
        self.generate_differences()

    def generate_differences(self):
        """生成不同点"""
        # 根据难度确定不同点数量
        num_diffs = {
            "easy": 4,
            "medium": 6,
            "hard": 8,
            "extreme": 10
        }.get(self.difficulty, 5)

        # 定义不同点位置和描述
        templates = {
            "room": [
                {"desc": "画框位置", "offsets": [(20, 30), (-15, 20)]},
                {"desc": "窗帘颜色", "offsets": [(50, 40), (-30, 25)]},
                {"desc": "台灯开关", "offsets": [(80, 60), (-25, 35)]},
                {"desc": "地毯图案", "offsets": [(100, 80), (15, -20)]},
                {"desc": "书本数量", "offsets": [(40, 50), (-40, 30)]},
                {"desc": "椅子位置", "offsets": [(70, 40), (-50, 20)]},
                {"desc": "花瓶形状", "offsets": [(30, 25), (20, -30)]},
                {"desc": "钟表时间", "offsets": [(60, 30), (-35, 40)]},
                {"desc": "植物大小", "offsets": [(45, 35), (25, -25)]},
                {"desc": "地板颜色", "offsets": [(80, 50), (-45, 45)]}
            ],
            "garden": [
                {"desc": "花朵颜色", "offsets": [(25, 40), (-20, 30)]},
                {"desc": "蝴蝶位置", "offsets": [(50, 30), (-35, 25)]},
                {"desc": "树叶形状", "offsets": [(70, 50), (-40, 35)]},
                {"desc": "水池倒影", "offsets": [(35, 45), (25, -30)]},
                {"desc": "小鸟数量", "offsets": [(60, 35), (-45, 40)]},
                {"desc": "栅栏高度", "offsets": [(45, 25), (30, -35)]},
                {"desc": "云朵形状", "offsets": [(80, 40), (-55, 30)]},
                {"desc": "草地颜色", "offsets": [(55, 50), (-30, 25)]},
                {"desc": "石子路径", "offsets": [(40, 30), (35, -40)]},
                {"desc": "藤蔓位置", "offsets": [(65, 45), (-50, 35)]}
            ],
            "street": [
                {"desc": "路灯形状", "offsets": [(30, 50), (-25, 40)]},
                {"desc": "汽车颜色", "offsets": [(55, 35), (-40, 30)]},
                {"desc": "招牌文字", "offsets": [(75, 45), (-55, 35)]},
                {"desc": "树木高度", "offsets": [(45, 55), (30, -40)]},
                {"desc": "行人数量", "offsets": [(60, 40), (-45, 25)]},
                {"desc": "窗户形状", "offsets": [(35, 30), (25, -35)]},
                {"desc": "路面裂缝", "offsets": [(80, 50), (-60, 40)]},
                {"desc": "交通标志", "offsets": [(50, 45), (-35, 50)]},
                {"desc": "花坛位置", "offsets": [(70, 35), (45, -45)]},
                {"desc": "垃圾桶", "offsets": [(40, 40), (-30, 30)]}
            ],
            "beach": [
                {"desc": "贝壳数量", "offsets": [(30, 60), (-25, 50)]},
                {"desc": "太阳位置", "offsets": [(55, 40), (-45, 35)]},
                {"desc": "伞的颜色", "offsets": [(75, 55), (-55, 45)]},
                {"desc": "海鸥数量", "offsets": [(45, 35), (35, -40)]},
                {"desc": "波浪大小", "offsets": [(60, 50), (-40, 30)]},
                {"desc": "沙滩椅", "offsets": [(35, 45), (30, -50)]},
                {"desc": "椰树位置", "offsets": [(80, 40), (-60, 50)]},
                {"desc": "水桶形状", "offsets": [(50, 55), (-35, 40)]},
                {"desc": "云朵形状", "offsets": [(70, 35), (45, -45)]},
                {"desc": "脚印方向", "offsets": [(40, 50), (-30, 55)]}
            ],
            "forest": [
                {"desc": "蘑菇数量", "offsets": [(25, 55), (-20, 45)]},
                {"desc": "松鼠位置", "offsets": [(50, 40), (-35, 30)]},
                {"desc": "树叶颜色", "offsets": [(70, 50), (-50, 40)]},
                {"desc": "小溪流向", "offsets": [(45, 45), (35, -35)]},
                {"desc": "鸟巢位置", "offsets": [(60, 35), (-45, 50)]},
                {"desc": "树根形状", "offsets": [(35, 50), (25, -45)]},
                {"desc": "花朵种类", "offsets": [(80, 45), (-55, 55)]},
                {"desc": "鹿的位置", "offsets": [(55, 55), (-40, 40)]},
                {"desc": "苔藓颜色", "offsets": [(65, 40), (45, -50)]},
                {"desc": "蜘蛛网", "offsets": [(40, 35), (-30, 45)]}
            ],
            "mountain": [
                {"desc": "山峰形状", "offsets": [(30, 45), (-25, 35)]},
                {"desc": "云雾位置", "offsets": [(55, 50), (-40, 40)]},
                {"desc": "树木种类", "offsets": [(75, 55), (-55, 45)]},
                {"desc": "老鹰数量", "offsets": [(45, 35), (35, -40)]},
                {"desc": "积雪位置", "offsets": [(60, 40), (-45, 55)]},
                {"desc": "瀑布流向", "offsets": [(35, 55), (30, -50)]},
                {"desc": "小路弯曲", "offsets": [(80, 45), (-60, 50)]},
                {"desc": "岩石颜色", "offsets": [(50, 50), (-35, 40)]},
                {"desc": "湖水颜色", "offsets": [(65, 35), (50, -45)]},
                {"desc": "阳光方向", "offsets": [(40, 45), (-30, 50)]}
            ]
        }

        # 添加更多场景类型
        for extra_scene in ["city", "village", "kitchen", "classroom", "office", "park"]:
            if extra_scene not in templates:
                templates[extra_scene] = templates["room"]  # 使用room模板

        # 选择模板
        available_templates = templates.get(self.type, templates["room"])
        selected = random.sample(available_templates, min(num_diffs, len(available_templates)))

        base_x, base_y = 100, 150
        img_width, img_height = 450, 350

        for i, template in enumerate(selected):
            # 确保不同点在图片范围内
            x = base_x + 50 + (i % 5) * 80 + random.randint(-20, 20)
            y = base_y + 30 + (i // 5) * 80 + random.randint(-20, 20)

            x = max(base_x + 30, min(base_x + img_width - 30, x))
            y = max(base_y + 30, min(base_y + img_height - 30, y))

            diff = DifferenceSpot(x, y, 25, template["desc"])
            self.differences.append(diff)


class SpotDiffGame:
    """多人找不同游戏主类"""

    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("多人找不同")
        self.clock = pygame.time.Clock()
        self.font_large = get_chinese_font(72)
        self.font_medium = get_chinese_font(48)
        self.font_small = get_chinese_font(36)
        self.font_tiny = get_chinese_font(28)

        # 游戏状态
        self.game_state = "menu"
        self.game_mode = "coop"  # coop: 合作, battle: 对战
        self.num_players = 2
        self.current_player = 0
        self.difficulty = "easy"

        # 游戏数据
        self.players = []
        self.scene = None
        self.found_differences = []
        self.total_differences = 0
        self.start_time = 0
        self.elapsed_time = 0
        self.hint_used = False
        self.hint_timer = 0

        # 动画
        self.click_effects = []
        self.score_popup = []
        self.celebration_timer = 0

        self.init_players()

    def init_players(self):
        """初始化玩家数据"""
        self.players = []
        for i in range(self.num_players):
            self.players.append({
                "name": PLAYER_NAMES[i],
                "color": PLAYER_COLORS[i],
                "score": 0,
                "found": 0,
                "wrong_clicks": 0
            })

    def setup_game(self):
        """设置游戏"""
        scene_type = random.choice(SCENE_TYPES)
        self.scene = Scene(scene_type, self.difficulty)
        self.total_differences = len(self.scene.differences)
        self.found_differences = []
        self.start_time = pygame.time.get_ticks()
        self.hint_used = False
        self.hint_timer = 0

    def draw_text(self, text, font, color, center=None, pos=None):
        """绘制文本"""
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if center:
            text_rect.center = center
        elif pos:
            text_rect.topleft = pos
        self.screen.blit(text_surface, text_rect)
        return text_rect

    def draw_button(self, rect, text, font, bg_color, text_color, hover=False):
        """绘制按钮"""
        if hover:
            bg_color = tuple(min(255, c + 30) for c in bg_color)
        pygame.draw.rect(self.screen, bg_color, rect, border_radius=10)
        pygame.draw.rect(self.screen, WHITE, rect, 2, border_radius=10)
        text_rect = font.render(text, True, text_color).get_rect(center=rect.center)
        self.screen.blit(font.render(text, True, text_color), text_rect)

    def draw_scene_preview(self, x, y, width, height, scene_type):
        """绘制场景预览"""
        # 背景
        pygame.draw.rect(self.screen, (80, 80, 100), (x, y, width, height), border_radius=10)
        pygame.draw.rect(self.screen, WHITE, (x, y, width, height), 2, border_radius=10)

        # 简单绘制场景背景
        colors = {
            "room": (139, 119, 101),
            "garden": (144, 238, 144),
            "street": (169, 169, 169),
            "beach": (238, 214, 175),
            "forest": (34, 139, 34),
            "mountain": (105, 105, 105),
            "city": (192, 192, 192),
            "village": (210, 180, 140),
            "kitchen": (255, 228, 196),
            "classroom": (230, 230, 250),
            "office": (245, 245, 220),
            "park": (143, 188, 143)
        }

        bg_color = colors.get(scene_type, (100, 100, 100))
        pygame.draw.rect(self.screen, bg_color, (x + 5, y + 5, width - 10, height - 10), border_radius=8)

        # 绘制简单的装饰元素
        center_x = x + width // 2
        center_y = y + height // 2

        pygame.draw.circle(self.screen, (135, 206, 235), (center_x - 50, center_y - 30), 30)
        pygame.draw.rect(self.screen, (139, 69, 19), (center_x + 20, center_y - 20, 60, 80), border_radius=5)
        pygame.draw.polygon(self.screen, GREEN, [(center_x - 80, center_y + 40), (center_x - 40, center_y - 20), (center_x, center_y + 40)])

    def draw_image_pair(self, scene):
        """绘制两幅图片及其不同点"""
        img_width, img_height = 450, 350
        gap = 40
        start_x = (SCREEN_WIDTH - img_width * 2 - gap) // 2
        start_y = 120

        # 左图标签
        left_label = self.font_small.render("原图", True, WHITE)
        self.screen.blit(left_label, (start_x + img_width // 2 - 30, start_y - 35))

        # 右图标签
        right_label = self.font_small.render("不同", True, WHITE)
        self.screen.blit(right_label, (start_x + img_width + gap + img_width // 2 - 30, start_y - 35))

        # 绘制图片背景
        for i, offset_x in enumerate([0, img_width + gap]):
            x = start_x + offset_x

            # 场景背景
            colors = {
                "room": (139, 119, 101),
                "garden": (144, 238, 144),
                "street": (169, 169, 169),
                "beach": (238, 214, 175),
                "forest": (34, 139, 34),
                "mountain": (105, 105, 105),
                "city": (192, 192, 192),
                "village": (210, 180, 140),
                "kitchen": (255, 228, 196),
                "classroom": (230, 230, 250),
                "office": (245, 245, 220),
                "park": (143, 188, 143)
            }

            bg_color = colors.get(scene.type, (100, 100, 100))

            # 外框
            pygame.draw.rect(self.screen, DARK_GRAY, (x - 5, start_y - 5, img_width + 10, img_height + 10), border_radius=15)
            pygame.draw.rect(self.screen, WHITE, (x - 5, start_y - 5, img_width + 10, img_height + 10), 2, border_radius=15)

            # 图片区域
            pygame.draw.rect(self.screen, bg_color, (x, start_y, img_width, img_height), border_radius=10)

            # 绘制简单场景元素
            self.draw_scene_elements(x, start_y, img_width, img_height, scene.type, i)

        # 存储图片区域用于点击检测
        self.left_image_rect = pygame.Rect(start_x, start_y, img_width, img_height)
        self.right_image_rect = pygame.Rect(start_x + img_width + gap, start_y, img_width, img_height)

        return [self.left_image_rect, self.right_image_rect]

    def draw_scene_elements(self, x, y, width, height, scene_type, is_modified):
        """绘制场景元素"""
        # 天空
        pygame.draw.rect(self.screen, (135, 206, 235), (x, y, width, height // 3), border_radius=10)

        # 地面
        ground_color = {
            "room": (139, 119, 101),
            "garden": (144, 238, 144),
            "street": (169, 169, 169),
            "beach": (238, 214, 175),
            "forest": (34, 139, 34),
            "mountain": (105, 105, 105)
        }.get(scene_type, (100, 150, 100))

        pygame.draw.rect(self.screen, ground_color, (x, y + height // 3 * 2, width, height // 3))

        # 太阳
        sun_x = x + 80 + (30 if is_modified else 0)
        sun_y = y + 50 + (-20 if is_modified else 0)
        pygame.draw.circle(self.screen, (255, 255, 0), (sun_x, sun_y), 25)

        # 房子/树木
        if scene_type in ["room", "kitchen", "classroom", "office"]:
            # 房子
            house_x = x + width // 2 - 50
            house_y = y + height // 2
            pygame.draw.rect(self.screen, (139, 69, 19), (house_x, house_y, 100, 80))  # 墙体
            pygame.draw.polygon(self.screen, (128, 0, 0), [(house_x - 10, house_y), (house_x + 50, house_y - 50), (house_x + 110, house_y)])  # 屋顶

            # 窗户
            win_color = (135, 206, 235) if is_modified else (255, 255, 200)
            pygame.draw.rect(self.screen, win_color, (house_x + 20, house_y + 20, 25, 25))  # 左窗
            pygame.draw.rect(self.screen, win_color, (house_x + 55, house_y + 20, 25, 25))  # 右窗

            # 门
            door_color = (101, 67, 33) if is_modified else (139, 69, 19)
            pygame.draw.rect(self.screen, door_color, (house_x + 40, house_y + 40, 20, 40))

        elif scene_type in ["garden", "park"]:
            # 树木
            tree_x = x + width // 3
            tree_y = y + height // 2

            # 树干
            pygame.draw.rect(self.screen, (139, 69, 19), (tree_x - 8, tree_y, 16, 60))

            # 树冠
            tree_color = (0, 100, 0) if is_modified else (0, 128, 0)
            pygame.draw.circle(self.screen, tree_color, (tree_x, tree_y - 10), 35)
            pygame.draw.circle(self.screen, tree_color, (tree_x - 20, tree_y + 10), 25)
            pygame.draw.circle(self.screen, tree_color, (tree_x + 20, tree_y + 10), 25)

            # 花朵
            for i in range(5):
                flower_x = x + 50 + i * 70 + (10 if is_modified else 0)
                flower_y = y + height - 40 + (-10 if is_modified else 0)
                pygame.draw.circle(self.screen, (255, 0, 127), (flower_x, flower_y), 8)

        elif scene_type in ["forest", "mountain"]:
            # 山
            pygame.draw.polygon(self.screen, (105, 105, 105), [(x + 50, y + height // 2 + 50), (x + 150, y + height // 2 - 50), (x + 250, y + height // 2 + 50)])

            # 雪顶
            snow_color = (255, 255, 255) if is_modified else (220, 220, 220)
            pygame.draw.polygon(self.screen, snow_color, [(x + 130, y + height // 2 - 50), (x + 150, y + height // 2 - 50), (x + 150, y + height // 2 - 30), (x + 130, y + height // 2 - 30)])

            # 树木
            for i in range(4):
                tree_x = x + 30 + i * 100
                tree_y = y + height // 2 + 30
                tree_color = (0, 80, 0) if is_modified else (0, 100, 0)
                pygame.draw.polygon(self.screen, tree_color, [(tree_x, tree_y + 50), (tree_x + 15, tree_y), (tree_x + 30, tree_y + 50)])

        elif scene_type in ["beach"]:
            # 海洋
            pygame.draw.rect(self.screen, (0, 119, 190), (x, y + height // 3, width, height // 3))

            # 波浪
            for i in range(5):
                wave_y = y + height // 2 + i * 20
                pygame.draw.arc(self.screen, (0, 191, 255), (x + 20 + i * 80, wave_y, 60, 15), 0, math.pi, 2)

            # 贝壳
            for i in range(3):
                shell_x = x + 80 + i * 120 + (20 if is_modified else 0)
                shell_y = y + height - 50 + (-15 if is_modified else 0)
                pygame.draw.ellipse(self.screen, (255, 200, 150), (shell_x, shell_y, 15, 10))

            # 伞
            umbrella_x = x + width - 100 + (25 if is_modified else 0)
            umbrella_y = y + height - 100 + (-30 if is_modified else 0)
            pygame.draw.polygon(self.screen, RED if is_modified else BLUE, [(umbrella_x - 30, umbrella_y + 40), (umbrella_x, umbrella_y), (umbrella_x + 30, umbrella_y + 40)])
            pygame.draw.line(self.screen, (139, 69, 19), (umbrella_x, umbrella_y), (umbrella_x, umbrella_y + 40), 3)

        elif scene_type in ["street", "city"]:
            # 建筑物
            for i in range(3):
                building_x = x + 50 + i * 130
                building_y = y + height // 2
                building_color = (100, 100, 100) if i == 1 and is_modified else (80, 80, 80)
                pygame.draw.rect(self.screen, building_color, (building_x, building_y, 80, 100))

                # 窗户
                for j in range(3):
                    for k in range(2):
                        window_x = building_x + 15 + j * 25
                        window_y = building_y + 15 + k * 35
                        win_color = (255, 255, 200) if (j + k) % 2 == 0 else (135, 206, 235)
                        pygame.draw.rect(self.screen, win_color, (window_x, window_y, 15, 20))

            # 路灯
            lamp_x = x + 30 + (40 if is_modified else 0)
            lamp_y = y + height // 2 + 30
            pygame.draw.line(self.screen, GRAY, (lamp_x, lamp_y + 50), (lamp_x, lamp_y), 4)
            pygame.draw.circle(self.screen, (255, 255, 150), (lamp_x, lamp_y - 5), 10)

        else:
            # 默认场景元素
            # 房子
            pygame.draw.rect(self.screen, (139, 69, 19), (x + width // 2 - 50, y + height // 2, 100, 80))
            pygame.draw.polygon(self.screen, (128, 0, 0), [(x + width // 2 - 60, y + height // 2), (x + width // 2, y + height // 2 - 50), (x + width // 2 + 60, y + height // 2)])

            # 树木
            pygame.draw.circle(self.screen, (0, 128, 0), (x + 80, y + height // 2 + 20), 30)
            pygame.draw.circle(self.screen, (0, 128, 0), (x + width - 80, y + height // 2 + 20), 30)

    def draw_progress(self):
        """绘制进度条"""
        bar_width = 600
        bar_x = (SCREEN_WIDTH - bar_width) // 2
        bar_y = 75

        # 背景
        pygame.draw.rect(self.screen, DARK_GRAY, (bar_x, bar_y, bar_width, 30), border_radius=15)

        # 进度
        progress = len(self.found_differences) / self.total_differences
        pygame.draw.rect(self.screen, GREEN, (bar_x, bar_y, int(bar_width * progress), 30), border_radius=15)

        # 文本
        found_text = self.font_small.render(f"已找到: {len(self.found_differences)}/{self.total_differences}", True, WHITE)
        self.screen.blit(found_text, (bar_x, bar_y + 35))

    def draw_player_panel(self):
        """绘制玩家面板"""
        panel_height = 80
        panel_y = SCREEN_HEIGHT - panel_height

        # 背景
        pygame.draw.rect(self.screen, DARK_GRAY, (0, panel_y, SCREEN_WIDTH, panel_height))

        if self.game_mode == "coop":
            # 合作模式 - 显示总体进度
            mode_text = self.font_small.render("合作模式 - 共同努力!", True, GREEN)
            self.screen.blit(mode_text, (20, panel_y + 25))

            # 显示总得分
            total_score = sum(p["score"] for p in self.players)
            score_text = self.font_medium.render(f"总分: {total_score}", True, YELLOW)
            self.screen.blit(score_text, (300, panel_y + 20))

        else:
            # 对战模式 - 显示当前玩家
            player_width = SCREEN_WIDTH // self.num_players
            for i, p in enumerate(self.players):
                x = i * player_width + 20
                color = p["color"]

                # 背景高亮
                if i == self.current_player:
                    pygame.draw.rect(self.screen, color, (i * player_width, panel_y, player_width, panel_height))
                    indicator = self.font_tiny.render("<<<", True, GREEN)
                    self.screen.blit(indicator, (x, panel_y + 60))

                # 信息
                name_text = self.font_small.render(p["name"], True, WHITE)
                self.screen.blit(name_text, (x, panel_y + 10))

                score_text = self.font_medium.render(f"{p['score']}分", True, YELLOW)
                self.screen.blit(score_text, (x, panel_y + 40))

                found_text = self.font_tiny.render(f"找到:{p['found']}", True, LIGHT_GRAY)
                self.screen.blit(found_text, (x + 100, panel_y + 20))

                wrong_text = self.font_tiny.render(f"误点:{p['wrong_clicks']}", True, LIGHT_GRAY)
                self.screen.blit(wrong_text, (x + 100, panel_y + 45))

    def draw_hint_button(self):
        """绘制提示按钮"""
        hint_rect = pygame.Rect(SCREEN_WIDTH - 130, 10, 120, 40)
        self.draw_button(hint_rect, "提示(3秒)", self.font_tiny, PURPLE, WHITE, False)
        return hint_rect

    def use_hint(self):
        """使用提示"""
        if not self.hint_used and self.found_differences:
            self.hint_used = True
            self.hint_timer = 180  # 3秒

            # 找一个未发现的差异并高亮
            for diff in self.scene.differences:
                if not diff.found:
                    diff.x = diff.x  # 保持原位置
                    break

    def check_click(self, pos):
        """检查点击是否找到不同"""
        # 确定点击的是哪张图片
        clicked_image = None
        offset_x = 0

        if self.left_image_rect.collidepoint(pos):
            clicked_image = "left"
            offset_x = 0
        elif self.right_image_rect.collidepoint(pos):
            clicked_image = "right"
            offset_x = self.left_image_rect.width + 40

        if clicked_image is None:
            return

        # 检查是否点击到差异点
        for diff in self.scene.differences:
            if diff.found:
                continue

            # 计算实际坐标（考虑图片位置偏移）
            diff_x = self.left_image_rect.x + (diff.x - 100)
            diff_y = diff.y

            # 检查点击是否在差异点范围内
            distance = math.sqrt((pos[0] - diff_x) ** 2 + (pos[1] - diff_y) ** 2)

            if distance <= diff.radius:
                # 找到不同点！
                diff.found = True
                diff.found_by = self.current_player if self.game_mode == "battle" else None
                self.found_differences.append(diff)

                # 添加点击效果
                self.click_effects.append({
                    "x": pos[0],
                    "y": pos[1],
                    "timer": 60,
                    "success": True,
                    "color": GREEN
                })

                # 更新分数
                if self.game_mode == "coop":
                    # 合作模式 - 所有玩家得分
                    base_score = 100
                    time_bonus = max(0, 50 - (self.elapsed_time // 10))
                    for p in self.players:
                        p["score"] += base_score + time_bonus

                    self.score_popup.append({
                        "text": f"+{base_score + time_bonus}",
                        "x": pos[0],
                        "y": pos[1],
                        "timer": 60,
                        "color": GREEN
                    })
                else:
                    # 对战模式 - 当前玩家得分
                    player = self.players[self.current_player]
                    player["found"] += 1
                    base_score = 100
                    combo_bonus = player["found"] * 10
                    player["score"] += base_score + combo_bonus

                    self.score_popup.append({
                        "text": f"+{base_score + combo_bonus}",
                        "x": pos[0],
                        "y": pos[1],
                        "timer": 60,
                        "color": player["color"]
                    })

                # 检查游戏是否结束
                if len(self.found_differences) >= self.total_differences:
                    self.game_state = "result"
                    self.celebration_timer = 180

                return

        # 点击错误
        if self.game_mode == "battle":
            player = self.players[self.current_player]
            player["wrong_clicks"] += 1
            player["score"] = max(0, player["score"] - 20)

            self.click_effects.append({
                "x": pos[0],
                "y": pos[1],
                "timer": 40,
                "success": False,
                "color": RED
            })

            # 切换玩家
            self.current_player = (self.current_player + 1) % self.num_players

    def draw_effects(self):
        """绘制特效"""
        # 绘制点击效果
        for effect in self.click_effects[:]:
            effect["timer"] -= 1
            effect["y"] -= 1

            color = effect["color"]
            size = 10 + (60 - effect["timer"]) * 2

            if effect["success"]:
                pygame.draw.circle(self.screen, color, (effect["x"], effect["y"]), size, 3)
                # 绘制勾
                pygame.draw.line(self.screen, color, (effect["x"] - 10, effect["y"]),
                               (effect["x"] - 3, effect["y"] + 7), 3)
                pygame.draw.line(self.screen, color, (effect["x"] - 3, effect["y"] + 7),
                               (effect["x"] + 10, effect["y"] - 10), 3)
            else:
                pygame.draw.circle(self.screen, color, (effect["x"], effect["y"]), size, 3)
                pygame.draw.line(self.screen, color, (effect["x"] - 8, effect["y"] - 8),
                               (effect["x"] + 8, effect["y"] + 8), 3)
                pygame.draw.line(self.screen, color, (effect["x"] + 8, effect["y"] - 8),
                               (effect["x"] - 8, effect["y"] + 8), 3)

            if effect["timer"] <= 0:
                self.click_effects.remove(effect)

        # 绘制分数弹出
        for popup in self.score_popup[:]:
            popup["timer"] -= 1
            popup["y"] -= 2

            text = self.font_medium.render(popup["text"], True, popup.get("color", YELLOW))
            self.screen.blit(text, (popup["x"] - text.get_width() // 2, popup["y"]))

            if popup["timer"] <= 0:
                self.score_popup.remove(popup)

        # 绘制已找到的差异标记
        for diff in self.scene.differences:
            if diff.found:
                # 绿色圆圈标记
                pygame.draw.circle(self.screen, GREEN, (diff.x, diff.y), diff.radius + 5, 3)
                pygame.draw.circle(self.screen, (0, 255, 0, 100), (diff.x, diff.y), diff.radius + 10, 2)

        # 提示效果
        if self.hint_timer > 0:
            self.hint_timer -= 1
            for diff in self.scene.differences:
                if not diff.found:
                    # 闪烁的圆圈
                    alpha = int(128 + 127 * math.sin(self.hint_timer * 0.2))
                    color = (255, 255, 0, alpha)
                    pygame.draw.circle(self.screen, (255, 255, 0), (diff.x, diff.y), diff.radius + 15, 4)
                    break

        # 庆祝动画
        if self.celebration_timer > 0:
            self.celebration_timer -= 1
            for i in range(10):
                x = random.randint(0, SCREEN_WIDTH)
                y = random.randint(0, SCREEN_HEIGHT)
                color = random.choice([RED, GREEN, BLUE, YELLOW, PURPLE, ORANGE])
                size = random.randint(5, 15)
                pygame.draw.circle(self.screen, color, (x, y), size)

    def draw_menu(self):
        """绘制主菜单"""
        self.screen.fill(DARK_BLUE)

        # 标题
        title = self.font_large.render("多人找不同", True, YELLOW)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)

        # 副标题
        subtitle = self.font_small.render("仔细观察，找出两幅图的不同之处!", True, LIGHT_GRAY)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 160))
        self.screen.blit(subtitle, subtitle_rect)

        # 预览图片
        preview_y = 220
        self.draw_scene_preview(200, preview_y, 350, 200, "garden")
        self.draw_scene_preview(650, preview_y, 350, 200, "garden")

        # VS标志
        vs_text = self.font_large.render("VS", True, WHITE)
        vs_rect = vs_text.get_rect(center=(570, preview_y + 100))
        self.screen.blit(vs_text, vs_rect)

        # 玩家数量选择
        player_label = self.font_medium.render("选择玩家数量:", True, WHITE)
        self.screen.blit(player_label, (SCREEN_WIDTH // 2 - 120, 460))

        buttons = []
        for i in range(2, 5):
            rect = pygame.Rect(SCREEN_WIDTH // 2 - 150 + (i - 2) * 120, 520, 100, 80)
            color = GREEN if self.num_players == i else GRAY
            pygame.draw.rect(self.screen, color, rect, border_radius=10)
            pygame.draw.rect(self.screen, WHITE, rect, 2, border_radius=10)

            num_text = self.font_large.render(str(i), True, WHITE)
            self.screen.blit(num_text, num_text.get_rect(center=(rect.centerx, rect.centery - 10)))

            label = self.font_tiny.render("人", True, WHITE)
            self.screen.blit(label, label.get_rect(center=(rect.centerx, rect.centery + 25)))

            buttons.append(("players", i, rect))

        # 预览玩家
        preview_y = 620
        preview_label = self.font_small.render("玩家预览:", True, WHITE)
        self.screen.blit(preview_label, (SCREEN_WIDTH // 2 - 60, preview_y))

        for i in range(self.num_players):
            x = SCREEN_WIDTH // 2 - (self.num_players * 100) // 2 + i * 100 + 50
            pygame.draw.circle(self.screen, PLAYER_COLORS[i], (x, preview_y + 50), 30)
            name = self.font_tiny.render(PLAYER_NAMES[i], True, PLAYER_COLORS[i])
            self.screen.blit(name, name.get_rect(center=(x, preview_y + 95)))

        # 开始按钮
        start_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 730, 200, 50)
        mouse_pos = pygame.mouse.get_pos()
        self.draw_button(start_rect, "开始游戏", self.font_medium, GREEN, WHITE,
                        start_rect.collidepoint(mouse_pos))
        buttons.append(("start", start_rect))

        return buttons

    def draw_mode_select(self):
        """绘制模式选择界面"""
        self.screen.fill(DARK_BLUE)

        title = self.font_large.render("选择游戏模式", True, YELLOW)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)

        buttons = []

        # 合作模式
        coop_rect = pygame.Rect(150, 200, 400, 280)
        coop_color = GREEN if self.game_mode == "coop" else GRAY
        pygame.draw.rect(self.screen, coop_color, coop_rect, border_radius=20)
        pygame.draw.rect(self.screen, WHITE, coop_rect, 3, border_radius=20)

        coop_title = self.font_medium.render("合作模式", True, WHITE)
        self.screen.blit(coop_title, coop_title.get_rect(center=(coop_rect.centerx, coop_rect.y + 40)))

        coop_desc = [
            "所有玩家一起找不同",
            "共同努力找出所有差异",
            "挑战最短时间",
            "",
            "玩家数: " + str(self.num_players)
        ]
        for i, desc in enumerate(coop_desc):
            text = self.font_small.render(desc, True, WHITE)
            self.screen.blit(text, text.get_rect(center=(coop_rect.centerx, coop_rect.y + 100 + i * 35)))

        buttons.append(("coop", coop_rect))

        # 对战模式
        battle_rect = pygame.Rect(650, 200, 400, 280)
        battle_color = ORANGE if self.game_mode == "battle" else GRAY
        pygame.draw.rect(self.screen, battle_color, battle_rect, border_radius=20)
        pygame.draw.rect(self.screen, WHITE, battle_rect, 3, border_radius=20)

        battle_title = self.font_medium.render("对战模式", True, WHITE)
        self.screen.blit(battle_title, battle_title.get_rect(center=(battle_rect.centerx, battle_rect.y + 40)))

        battle_desc = [
            "玩家轮流点击找不同",
            "找到得分，误点扣分",
            "找出更多者获胜",
            "",
            "玩家数: " + str(self.num_players)
        ]
        for i, desc in enumerate(battle_desc):
            text = self.font_small.render(desc, True, WHITE)
            self.screen.blit(text, text.get_rect(center=(battle_rect.centerx, battle_rect.y + 100 + i * 35)))

        buttons.append(("battle", battle_rect))

        # 继续按钮
        continue_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 520, 200, 60)
        mouse_pos = pygame.mouse.get_pos()
        self.draw_button(continue_rect, "继续", self.font_medium, BLUE, WHITE,
                        continue_rect.collidepoint(mouse_pos))
        buttons.append(("continue", continue_rect))

        # 返回按钮
        back_rect = pygame.Rect(50, 50, 120, 50)
        self.draw_button(back_rect, "返回", self.font_small, GRAY, WHITE,
                        back_rect.collidepoint(mouse_pos))
        buttons.append(("back", back_rect))

        return buttons

    def draw_difficulty_select(self):
        """绘制难度选择界面"""
        self.screen.fill(DARK_BLUE)

        title = self.font_large.render("选择难度", True, YELLOW)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)

        mode_text = self.font_small.render(
            f"当前模式: {'合作模式' if self.game_mode == 'coop' else '对战模式'}",
            True, GREEN)
        self.screen.blit(mode_text, (SCREEN_WIDTH // 2 - 100, 160))

        buttons = []
        difficulties = [
            ("easy", "简单", "4处不同", GREEN),
            ("medium", "中等", "6处不同", YELLOW),
            ("hard", "困难", "8处不同", ORANGE),
            ("extreme", "极限", "10处不同", RED)
        ]

        for i, (key, name, desc, color) in enumerate(difficulties):
            row = i // 2
            col = i % 2
            x = 200 + col * 400
            y = 220 + row * 150

            rect = pygame.Rect(x, y, 350, 120)
            diff_color = color if self.difficulty == key else GRAY
            pygame.draw.rect(self.screen, diff_color, rect, border_radius=15)
            pygame.draw.rect(self.screen, WHITE, rect, 2, border_radius=15)

            name_text = self.font_medium.render(name, True, WHITE)
            self.screen.blit(name_text, (x + 20, y + 25))

            desc_text = self.font_small.render(desc, True, LIGHT_GRAY)
            self.screen.blit(desc_text, (x + 20, y + 65))

            buttons.append((key, rect))

        # 开始按钮
        start_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 530, 200, 70)
        mouse_pos = pygame.mouse.get_pos()
        self.draw_button(start_rect, "开始游戏", self.font_large, GREEN, WHITE,
                        start_rect.collidepoint(mouse_pos))
        buttons.append(("start", start_rect))

        # 返回按钮
        back_rect = pygame.Rect(50, 50, 120, 50)
        self.draw_button(back_rect, "返回", self.font_small, GRAY, WHITE,
                        back_rect.collidepoint(mouse_pos))
        buttons.append(("back", back_rect))

        return buttons

    def draw_game_screen(self):
        """绘制游戏界面"""
        self.screen.fill(DARK_BLUE)

        # 更新计时
        if self.start_time > 0:
            self.elapsed_time = (pygame.time.get_ticks() - self.start_time) // 1000

        # 顶部信息栏
        pygame.draw.rect(self.screen, DARK_GRAY, (0, 0, SCREEN_WIDTH, 70))

        # 标题
        title = self.font_small.render("找不同", True, YELLOW)
        self.screen.blit(title, (20, 25))

        # 计时器
        time_text = self.font_medium.render(f"{self.elapsed_time}秒", True, WHITE)
        self.screen.blit(time_text, (150, 20))

        # 进度条
        self.draw_progress()

        # 提示按钮
        hint_rect = self.draw_hint_button()

        # 绘制图片
        image_rects = self.draw_image_pair(self.scene)

        # 绘制特效
        self.draw_effects()

        # 绘制玩家面板
        self.draw_player_panel()

        return image_rects + [hint_rect]

    def draw_result_screen(self):
        """绘制结果界面"""
        self.screen.fill(DARK_BLUE)

        # 庆祝动画
        if self.celebration_timer > 0:
            self.celebration_timer -= 1
            for i in range(15):
                x = random.randint(0, SCREEN_WIDTH)
                y = random.randint(0, SCREEN_HEIGHT)
                color = random.choice([RED, GREEN, BLUE, YELLOW, PURPLE, ORANGE, PINK, CYAN])
                size = random.randint(5, 20)
                pygame.draw.circle(self.screen, color, (x, y), size)

        # 标题
        title = self.font_large.render("恭喜完成!", True, GOLD)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title, title_rect)

        # 统计信息
        stats_text = self.font_medium.render(
            f"总用时: {self.elapsed_time}秒 | 找到: {len(self.found_differences)}/{self.total_differences}",
            True, WHITE)
        self.screen.blit(stats_text, (SCREEN_WIDTH // 2 - 250, 140))

        # 玩家成绩
        if self.game_mode == "coop":
            # 合作模式
            sorted_players = sorted(self.players, key=lambda x: x["score"], reverse=True)
            total_score = sum(p["score"] for p in self.players)

            coop_label = self.font_medium.render("合作模式 - 团队总分", True, GREEN)
            self.screen.blit(coop_label, (SCREEN_WIDTH // 2 - 130, 200))

            score_display = self.font_large.render(f"{total_score}", True, GOLD)
            score_rect = score_display.get_rect(center=(SCREEN_WIDTH // 2, 280))
            pygame.draw.circle(self.screen, DARK_GRAY, score_rect.center, 80, border_radius=15)
            self.screen.blit(score_display, score_rect)

            unit = self.font_small.render("总分", True, WHITE)
            self.screen.blit(unit, (SCREEN_WIDTH // 2 - 25, 340))

            # 评价
            if self.elapsed_time < 60:
                rating = "神速!"
                rating_color = GOLD
            elif self.elapsed_time < 120:
                rating = "厉害!"
                rating_color = GREEN
            elif self.elapsed_time < 180:
                rating = "不错!"
                rating_color = BLUE
            else:
                rating = "继续加油!"
                rating_color = GRAY

            rating_text = self.font_medium.render(rating, True, rating_color)
            self.screen.blit(rating_text, (SCREEN_WIDTH // 2 - 50, 380))

        else:
            # 对战模式
            sorted_players = sorted(self.players, key=lambda x: x["score"], reverse=True)
            winner = sorted_players[0]

            # 冠军
            winner_label = self.font_small.render("冠军", True, GOLD)
            self.screen.blit(winner_label, (SCREEN_WIDTH // 2 - 30, 200))

            pygame.draw.circle(self.screen, winner["color"], (SCREEN_WIDTH // 2, 280), 70)
            crown = self.font_large.render("👑", True, GOLD)
            self.screen.blit(crown, (SCREEN_WIDTH // 2 - 35, 210))

            winner_name = self.font_medium.render(winner["name"], True, winner["color"])
            self.screen.blit(winner_name, winner_name.get_rect(center=(SCREEN_WIDTH // 2, 360)))

            winner_score = self.font_large.render(f"{winner['score']}分", True, YELLOW)
            self.screen.blit(winner_score, winner_score.get_rect(center=(SCREEN_WIDTH // 2, 400)))

            # 其他玩家
            for i, player in enumerate(sorted_players[1:], 1):
                y = 480 + (i - 1) * 50

                rank = self.font_small.render(f"#{i+1}", True, LIGHT_GRAY)
                self.screen.blit(rank, (300, y))

                name = self.font_small.render(player["name"], True, player["color"])
                self.screen.blit(name, (380, y))

                score = self.font_small.render(f"{player['score']}分", True, YELLOW)
                self.screen.blit(score, (550, y))

                found = self.font_tiny.render(f"找:{player['found']} 误:{player['wrong_clicks']}", True, LIGHT_GRAY)
                self.screen.blit(found, (700, y))

        buttons = []

        # 再来一局
        retry_rect = pygame.Rect(SCREEN_WIDTH // 2 - 220, 620, 200, 60)
        mouse_pos = pygame.mouse.get_pos()
        self.draw_button(retry_rect, "再来一局", self.font_medium, GREEN, WHITE,
                        retry_rect.collidepoint(mouse_pos))
        buttons.append(("retry", retry_rect))

        # 重新选择
        select_rect = pygame.Rect(SCREEN_WIDTH // 2 + 20, 620, 200, 60)
        self.draw_button(select_rect, "重新选择", self.font_medium, BLUE, WHITE,
                        select_rect.collidepoint(mouse_pos))
        buttons.append(("select", select_rect))

        # 菜单
        menu_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 690, 200, 50)
        self.draw_button(menu_rect, "返回菜单", self.font_small, GRAY, WHITE,
                        menu_rect.collidepoint(mouse_pos))
        buttons.append(("menu", menu_rect))

        return buttons

    def handle_events(self, screen_type, elements):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                if screen_type == "menu":
                    for elem in elements:
                        if elem[0] == "players":
                            _, num, rect = elem
                            if rect.collidepoint(mouse_pos):
                                self.num_players = num
                                self.init_players()
                        elif elem[0] == "start" and elem[1].collidepoint(mouse_pos):
                            self.game_state = "mode_select"

                elif screen_type == "mode_select":
                    for elem in elements:
                        if elem[0] == "coop" and elem[1].collidepoint(mouse_pos):
                            self.game_mode = "coop"
                        elif elem[0] == "battle" and elem[1].collidepoint(mouse_pos):
                            self.game_mode = "battle"
                        elif elem[0] == "continue" and elem[1].collidepoint(mouse_pos):
                            self.game_state = "difficulty_select"
                        elif elem[0] == "back" and elem[1].collidepoint(mouse_pos):
                            self.game_state = "menu"

                elif screen_type == "difficulty_select":
                    for elem in elements:
                        if isinstance(elem[0], str) and elem[1].collidepoint(mouse_pos):
                            if elem[0] == "start":
                                self.setup_game()
                                self.game_state = "playing"
                            elif elem[0] == "back":
                                self.game_state = "mode_select"

                elif screen_type == "game":
                    # 检查是否点击了提示按钮
                    if len(elements) > 2 and elements[-1].collidepoint(mouse_pos):
                        self.use_hint()
                    else:
                        # 检查是否点击了图片
                        for rect in elements[:-1]:
                            if rect.collidepoint(mouse_pos):
                                self.check_click(mouse_pos)
                                break

                elif screen_type == "result":
                    for elem in elements:
                        if elem[1].collidepoint(mouse_pos):
                            if elem[0] == "retry":
                                self.setup_game()
                                self.game_state = "playing"
                            elif elem[0] == "select":
                                self.game_state = "mode_select"
                            elif elem[0] == "menu":
                                self.game_state = "menu"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if screen_type in ["playing", "result"]:
                        self.game_state = "menu"

        return None

    def run(self):
        """主游戏循环"""
        running = True

        while running:
            self.clock.tick(FPS)

            if self.game_state == "menu":
                elements = self.draw_menu()
                screen_type = "menu"
            elif self.game_state == "mode_select":
                elements = self.draw_mode_select()
                screen_type = "mode_select"
            elif self.game_state == "difficulty_select":
                elements = self.draw_difficulty_select()
                screen_type = "difficulty_select"
            elif self.game_state == "playing":
                elements = self.draw_game_screen()
                screen_type = "game"
            elif self.game_state == "result":
                elements = self.draw_result_screen()
                screen_type = "result"

            pygame.display.flip()

            result = self.handle_events(screen_type, elements)
            if result == "quit":
                running = False

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = SpotDiffGame()
    game.run()
