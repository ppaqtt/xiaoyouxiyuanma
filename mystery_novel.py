#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
解谜小说游戏 - 玫瑰庄园的秘密
Mystery Novel Game - Secrets of Rose Manor

玩家扮演一名侦探，在维多利亚时代的庄园中调查一起神秘案件
通过收集线索、审讯嫌疑人、解开谜题，揭开真相
"""

import pygame
import sys
import random

# 初始化Pygame
pygame.init()

# 游戏常量
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# 颜色定义
COLORS = {
    'bg_dark': (20, 15, 15),
    'bg_room': (40, 30, 35),
    'parchment': (245, 235, 210),
    'gold': (218, 165, 32),
    'silver': (192, 192, 192),
    'red': (180, 50, 50),
    'green': (80, 160, 80),
    'blue': (80, 120, 180),
    'white': (255, 255, 255),
    'black': (30, 30, 30),
    'gray': (120, 120, 120),
    'purple': (150, 100, 160),
    'brown': (139, 90, 43),
    'cream': (255, 253, 220),
    'crimson': (180, 30, 30),
    'ink': (40, 30, 50),
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
    return pygame.font.Font(None, size)

class Detective:
    """侦探类"""
    def __init__(self, name):
        self.name = name
        self.skill = {
            'observation': 50,   # 观察力
            'deduction': 50,     # 推理能力
            'interrogation': 50, # 审讯技巧
            'intuition': 50,     # 直觉
        }
        self.clues_collected = []
        self.notes = []
        self.suspects_interviewed = []
        self.theory = None
        self.accusation_ready = False

class Clue:
    """线索类"""
    def __init__(self, name, description, location, importance, hint=""):
        self.name = name
        self.description = description
        self.location = location
        self.importance = importance  # 1-5星
        self.hint = hint
        self.discovered = False
        self.related_clues = []

class Suspect:
    """嫌疑人类"""
    def __init__(self, name, role, description, alibi, possible_guilty=False):
        self.name = name
        self.role = role
        self.description = description
        self.alibi = alibi
        self.possible_guilty = possible_guilty
        self.statements = []
        self.secrets = []
        self.relationship_with_victim = ""

class Case:
    """案件类"""
    def __init__(self):
        self.title = "玫瑰庄园的秘密"
        self.intro = "维多利亚时代的英国，在一个暴风雨的夜晚，玫瑰庄园的主人突然死亡..."
        self.victim = "雷蒙德·罗斯伯爵"
        self.location = "玫瑰庄园"
        self.time = "1888年10月15日"
        self.clues = []
        self.suspects = []
        self.rooms = []
        self.setup_case()

    def setup_case(self):
        """设置案件"""
        # 受害者
        self.victim_info = {
            'name': '雷蒙德·罗斯伯爵',
            'age': 58,
            'description': '玫瑰庄园的主人，一位富有的贵族',
            'cause': '毒杀',
            'time': '晚上10点至11点之间',
        }

        # 线索
        self.clues = [
            Clue("空的药瓶", "一个标有\"剧毒\"的空药瓶，被丢弃在壁炉旁", "书房", 5,
                 "毒药是如何进入受害者体内的？"),
            Clue("撕毁的信", "一封被撕成两半的信，内容提到\"秘密\"和\"不能让人知道\"", "书房抽屉", 4,
                 "这封信是写给谁的？"),
            Clue("可疑的脚印", "从后门延伸到书房的泥土脚印，尺码较小", "走廊", 3,
                 "谁有可能是这个脚印的主人？"),
            Clue("收藏室钥匙", "一把打开收藏室的钥匙，上面有新鲜的发丝", "受害者口袋", 5,
                 "收藏室里有什么秘密？"),
            Clue("宴会出席名单", "列出了当晚所有出席宴会的人名", "大厅", 2,
                 "每个人都有不在场证明吗？"),
            Clue("破碎的酒杯", "在伯爵酒杯中发现残留的液体", "餐厅", 5,
                 "这液体是什么？"),
            Clue("管家的日志", "日志中提到伯爵最近收到一封威胁信", "管家房间", 4,
                 "威胁信的内容是什么？"),
            Clue("情书的碎片", "写给伯爵的情书，但署名被撕掉了", "收藏室", 3,
                 "伯爵有外遇吗？"),
        ]

        # 嫌疑人
        self.suspects = [
            Suspect("艾琳·罗斯", "伯爵夫人", "40岁，伯爵的第二任妻子，出身商人家庭",
                   "声称在卧室休息，但无人能证明", possible_guilty=True),
            Suspect("维克多·罗斯", "侄子", "28岁，伯爵的侄子，欠债累累",
                   "在花园散步，有人看到他进出庄园", possible_guilty=False),
            Suspect("汉斯医生", "家庭医生", "55岁，伯爵的私人医生多年",
                   "在书房为伯爵检查身体至9点", possible_guilty=False),
            Suspect("格蕾丝", "女仆", "25岁，在庄园工作3年",
                   "在厨房准备茶水，期间有人看到她离开", possible_guilty=True),
            Suspect("托马斯", "管家", "60岁，在庄园服务30年",
                   "在门厅整理，直到听到尖叫声", possible_guilty=False),
        ]

        # 房间
        self.rooms = [
            {"name": "大厅", "description": "豪华的大厅，壁炉燃烧着火焰", "clues": ["宴会出席名单"]},
            {"name": "书房", "description": "伯爵的私人书房，书架上满是古籍", "clues": ["空的药瓶", "撕毁的信"]},
            {"name": "餐厅", "description": "长长的餐桌，烛光摇曳", "clues": ["破碎的酒杯"]},
            {"name": "收藏室", "description": "存放着各种珍奇异宝", "clues": ["情书的碎片", "收藏室钥匙"]},
            {"name": "走廊", "description": "昏暗的走廊，墙上的画像注视着来客", "clues": ["可疑的脚印"]},
            {"name": "管家房间", "description": "简洁整齐的房间", "clues": ["管家的日志"]},
            {"name": "卧室", "description": "伯爵夫人的卧室", "clues": []},
            {"name": "厨房", "description": "女仆们工作的地方", "clues": []},
        ]

class Game:
    """游戏主类"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("玫瑰庄园的秘密 - 解谜小说游戏")
        self.clock = pygame.time.Clock()
        self.running = True

        # 字体
        self.font_title = get_font(48)
        self.font_large = get_font(32)
        self.font_normal = get_font(24)
        self.font_small = get_font(18)
        self.font_cursive = get_font(28)  # 手写风格

        # 游戏状态
        self.game_state = 'menu'
        self.detective = None
        self.case = None
        self.current_room = None
        self.current_suspect = None
        self.clues_in_view = []
        self.investigation_progress = 0
        self.day = 1

        # 动画效果
        self.ink_effect = 0
        self.page_turn = 0

    def create_background(self, color1, color2):
        """创建背景"""
        surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            pygame.draw.line(surface, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        return surface

    def draw_text(self, text, font, color, x, y, center=False):
        """绘制文本"""
        text_surface = font.render(text, True, color)
        if center:
            rect = text_surface.get_rect(center=(x, y))
        else:
            rect = text_surface.get_rect(topleft=(x, y))
        self.screen.blit(text_surface, rect)
        return rect.bottom

    def draw_button(self, text, x, y, width, height, color, hover_color, action=None):
        """绘制按钮"""
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        button_rect = pygame.Rect(x, y, width, height)
        hovered = button_rect.collidepoint(mouse)

        if hovered:
            pygame.draw.rect(self.screen, hover_color, button_rect, border_radius=8)
            if click[0] == 1 and action:
                pygame.time.wait(150)
                return action()
        else:
            pygame.draw.rect(self.screen, color, button_rect, border_radius=8)

        pygame.draw.rect(self.screen, COLORS['gold'], button_rect, 2, border_radius=8)
        self.draw_text(text, self.font_normal, COLORS['cream'], x + width // 2, y + height // 2, center=True)
        return None

    def draw_paper_frame(self, x, y, width, height):
        """绘制羊皮纸边框"""
        rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, COLORS['parchment'], rect, border_radius=5)
        pygame.draw.rect(self.screen, COLORS['brown'], rect, 3, border_radius=5)

    def draw_notebook(self, x, y, width, height):
        """绘制笔记本样式"""
        rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, COLORS['parchment'], rect, border_radius=10)
        pygame.draw.rect(self.screen, COLORS['brown'], rect, 4, border_radius=10)

        # 装饰角
        for corner_x, corner_y in [(x+5, y+5), (x+width-5, y+5), (x+5, y+height-5), (x+width-5, y+height-5)]:
            pygame.draw.circle(self.screen, COLORS['gold'], corner_x, 5)

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

    def main_menu(self):
        """主菜单"""
        bg = self.create_background((10, 10, 20), (40, 30, 30))
        self.screen.blit(bg, (0, 0))

        # 装饰边框
        for i in range(3):
            pygame.draw.rect(self.screen, COLORS['gold'],
                           (30 + i*5, 30 + i*5, SCREEN_WIDTH - 60 - i*10, SCREEN_HEIGHT - 60 - i*10),
                           1, border_radius=20)

        # 标题
        self.draw_text("玫瑰庄园的秘密", self.font_title, COLORS['gold'], SCREEN_WIDTH // 2, 100, center=True)
        self.draw_text("SECRETS OF ROSE MANOR", self.font_normal, COLORS['silver'], SCREEN_WIDTH // 2, 170, center=True)

        # 副标题
        self.draw_text("— 一个维多利亚时代的侦探故事 —", self.font_cursive, COLORS['cream'],
                      SCREEN_WIDTH // 2, 230, center=True)

        # 案件描述框
        self.draw_paper_frame(150, 280, 900, 200)
        intro_text = [
            "1888年，英格兰。在一个暴风雨的夜晚，",
            "玫瑰庄园的主人雷蒙德·罗斯伯爵突然死亡。",
            "",
            "作为著名的侦探，你被邀请调查这起神秘的死亡案件。",
            "只有找出真相，才能让死者安息..."
        ]
        y_pos = 300
        for line in intro_text:
            self.draw_text(line, self.font_normal, COLORS['ink'], SCREEN_WIDTH // 2, y_pos, center=True)
            y_pos += 35

        # 按钮
        self.draw_button("开始调查", SCREEN_WIDTH // 2 - 150, 520, 300, 60, COLORS['ink'], COLORS['crimson'])
        self.draw_button("继续案件", SCREEN_WIDTH // 2 - 150, 600, 300, 60, COLORS['ink'], COLORS['green'])
        self.draw_button("退出游戏", SCREEN_WIDTH // 2 - 150, 680, 300, 60, COLORS['ink'], COLORS['gray'])

    def detective_setup(self):
        """侦探设定"""
        bg = self.create_background((20, 15, 15), (50, 40, 40))
        self.screen.blit(bg, (0, 0))

        self.draw_text("创建你的侦探", self.font_title, COLORS['gold'], SCREEN_WIDTH // 2, 50, center=True)

        # 侦探名称
        self.draw_text("侦探名称:", self.font_large, COLORS['cream'], 200, 150)
        input_rect = pygame.Rect(450, 140, 400, 50)
        pygame.draw.rect(self.screen, COLORS['parchment'], input_rect, border_radius=8)
        pygame.draw.rect(self.screen, COLORS['gold'], input_rect, 2, border_radius=8)
        name = getattr(self, 'detective_name', '') + "|"
        self.draw_text(name, self.font_large, COLORS['ink'], 650, 158, center=True)

        # 技能选择
        self.draw_text("选择你的专长:", self.font_large, COLORS['cream'], 200, 250)

        specialties = [
            ("观察力 - 善于发现隐藏线索", 'observation', 70, 50),
            ("推理能力 - 擅长分析证据", 'deduction', 70, 100),
            ("审讯技巧 - 能从嫌疑人处获得信息", 'interrogation', 70, 150),
            ("直觉 - 能凭直觉找到关键线索", 'intuition', 70, 200),
        ]

        y_pos = 300
        for text, skill, x, y in specialties:
            self.draw_button(text, x + 100, y_pos, 500, 45, COLORS['ink'], COLORS['purple'],
                           lambda s=skill: self.select_specialty(s))
            y_pos += 60

        self.draw_button("确认创建", SCREEN_WIDTH // 2 - 100, 650, 200, 50, COLORS['ink'], COLORS['green'])
        self.draw_button("返回", SCREEN_WIDTH // 2 - 100, 720, 200, 50, COLORS['ink'], COLORS['gray'])

    def select_specialty(self, skill):
        """选择专长"""
        self.selected_specialty = skill

    def create_detective(self):
        """创建侦探"""
        name = getattr(self, 'detective_name', '') or "福尔摩斯"
        self.detective = Detective(name)

        # 设置专长加成
        if hasattr(self, 'selected_specialty'):
            self.detective.skill[self.selected_specialty] = 80

        # 创建案件
        self.case = Case()

        # 初始线索
        self.detective.clues_collected = []
        self.game_state = 'case_intro'

    def case_intro_screen(self):
        """案件介绍"""
        bg = self.create_background((15, 10, 25), (45, 35, 50))
        self.screen.blit(bg, (0, 0))

        # 标题
        self.draw_text(f"案件: {self.case.title}", self.font_title, COLORS['gold'], SCREEN_WIDTH // 2, 30, center=True)

        # 案件信息框
        self.draw_paper_frame(100, 100, 1000, 400)

        info_lines = [
            f"受害者: {self.case.victim_info['name']}",
            f"年龄: {self.case.victim_info['age']}岁",
            f"死亡地点: {self.case.location}",
            f"死亡时间: {self.case.victim_info['time']}",
            f"死因: {self.case.victim_info['cause']}",
            "",
            "案件简介:",
            self.case.intro,
        ]

        y_pos = 120
        for line in info_lines:
            if line.startswith("受害者") or line.startswith("案件:"):
                self.draw_text(line, self.font_normal, COLORS['crimson'], 150, y_pos)
            else:
                self.draw_text(line, self.font_normal, COLORS['ink'], 150, y_pos)
            y_pos += 35

        # 开始调查按钮
        self.draw_button("开始调查", SCREEN_WIDTH // 2 - 120, 550, 240, 60, COLORS['ink'], COLORS['gold'])
        self.draw_button("返回主菜单", SCREEN_WIDTH // 2 - 120, 630, 240, 50, COLORS['ink'], COLORS['gray'])

    def investigation_screen(self):
        """调查界面"""
        bg = self.create_background((20, 15, 15), (50, 40, 40))
        self.screen.blit(bg, (0, 0))

        # 标题栏
        pygame.draw.rect(self.screen, COLORS['ink'], (0, 0, SCREEN_WIDTH, 60))
        self.draw_text(f"案件: {self.case.title}", self.font_title, COLORS['gold'], 100, 15)
        self.draw_text(f"调查进度: {len(self.detective.clues_collected)}/{len(self.case.clues)} 线索",
                       self.font_normal, COLORS['cream'], SCREEN_WIDTH - 400, 18)
        self.draw_text(f"第 {self.day} 天", self.font_normal, COLORS['silver'], SCREEN_WIDTH // 2, 18, center=True)

        # 左侧面板 - 地点选择
        self.draw_notebook(20, 80, 350, 500)

        self.draw_text("调查地点", self.font_large, COLORS['gold'], 195, 100, center=True)
        pygame.draw.line(self.screen, COLORS['brown'], (50, 140), (340, 140), 2)

        y_pos = 160
        for room in self.case.rooms:
            color = COLORS['green'] if room['clues'] else COLORS['gray']
            self.draw_button(f"  {room['name']}", 50, y_pos, 300, 45, COLORS['ink'], color,
                           lambda r=room: self.enter_room(r))
            y_pos += 52

        # 中间面板 - 嫌疑人
        self.draw_notebook(390, 80, 350, 500)

        self.draw_text("嫌疑人", self.font_large, COLORS['gold'], 565, 100, center=True)
        pygame.draw.line(self.screen, COLORS['brown'], (420, 140), (710, 140), 2)

        y_pos = 160
        for suspect in self.case.suspects:
            interviewed = "V" if suspect.name in self.detective.suspects_interviewed else ""
            color = COLORS['green'] if interviewed else COLORS['crimson']
            self.draw_button(f"{suspect.name} ({suspect.role}) {interviewed}",
                           420, y_pos, 300, 45, COLORS['ink'], color,
                           lambda s=suspect: self.interview_suspect(s))
            y_pos += 52

        # 右侧面板 - 笔记本
        self.draw_notebook(760, 80, 420, 500)

        self.draw_text("调查笔记", self.font_large, COLORS['gold'], 970, 100, center=True)
        pygame.draw.line(self.screen, COLORS['brown'], (790, 140), (950, 140), 2)

        y_pos = 160
        self.draw_text("已收集线索:", self.font_small, COLORS['silver'], 790, y_pos)
        y_pos += 30

        for clue in self.detective.clues_collected:
            self.draw_text(f"• {clue.name}", self.font_small, COLORS['cream'], 800, y_pos)
            y_pos += 28

        if not self.detective.clues_collected:
            self.draw_text("(暂无线索)", self.font_small, COLORS['gray'], 800, y_pos)

        # 推理按钮
        y_pos = 420
        self.draw_button("整理线索", 790, y_pos, 180, 45, COLORS['ink'], COLORS['blue'])
        self.draw_button("提出指控", 790, y_pos + 55, 180, 45, COLORS['ink'], COLORS['crimson'])
        self.draw_button("查看嫌疑人关系", 790, y_pos + 110, 180, 45, COLORS['ink'], COLORS['purple'])

        # 底部操作栏
        pygame.draw.rect(self.screen, COLORS['ink'], (0, SCREEN_HEIGHT - 80, SCREEN_WIDTH, 80))
        self.draw_button("返回案件", 100, SCREEN_HEIGHT - 65, 150, 45, COLORS['ink'], COLORS['gray'])
        self.draw_text(f"侦探: {self.detective.name} | 技能: 观察力 {self.detective.skill['observation']} "
                      f"推理 {self.detective.skill['deduction']} 审讯 {self.detective.skill['interrogation']} "
                      f"直觉 {self.detective.skill['intuition']}",
                      self.font_small, COLORS['silver'], 300, SCREEN_HEIGHT - 45)

    def enter_room(self, room):
        """进入房间"""
        self.current_room = room
        self.game_state = 'room_exploration'
        self.room_clue_index = 0

    def room_exploration_screen(self):
        """房间探索"""
        bg = self.create_background((30, 20, 20), (60, 45, 45))
        self.screen.blit(bg, (0, 0))

        room = self.current_room

        # 房间标题
        pygame.draw.rect(self.screen, COLORS['ink'], (0, 0, SCREEN_WIDTH, 70))
        self.draw_text(f"探索: {room['name']}", self.font_title, COLORS['gold'], SCREEN_WIDTH // 2, 15, center=True)
        self.draw_button("返回", 50, 15, 100, 40, COLORS['ink'], COLORS['gray'])

        # 房间描述
        self.draw_paper_frame(50, 100, 500, 300)
        self.draw_text("房间描述", self.font_large, COLORS['gold'], 300, 120, center=True)
        self.draw_text(room['description'], self.font_normal, COLORS['ink'], 80, 170)

        # 可搜索物品
        self.draw_text("可搜索物品:", self.font_large, COLORS['gold'], 600, 120)

        search_items = [
            "书架", "桌子", "椅子", "窗户", "地毯",
            "抽屉", "壁炉", "柜子", "床", "窗帘"
        ]

        y_pos = 170
        for i, item in enumerate(search_items):
            col = i % 2
            row = i // 2
            self.draw_button(item, 600 + col * 280, y_pos + row * 55, 250, 45, COLORS['ink'], COLORS['purple'],
                           lambda it=item: self.search_item(it))

        # 线索提示
        if room['clues']:
            self.draw_text(f"提示: 这个房间可能藏有 {len(room['clues'])} 条线索",
                         self.font_small, COLORS['silver'], 80, 380)
        else:
            self.draw_text("这个房间似乎没有明显线索...",
                         self.font_small, COLORS['gray'], 80, 380)

    def search_item(self, item):
        """搜索物品"""
        room = self.current_room

        # 根据搜索技能和随机因素决定是否发现线索
        success_chance = self.detective.skill['observation'] / 100 + 0.1
        if random.random() < success_chance:
            if room['clues']:
                clue = self.case.clues[[c.name for c in self.case.clues].index(room['clues'][0])]
                if clue not in self.detective.clues_collected:
                    self.detective.clues_collected.append(clue)
                    clue.discovered = True
                    self.show_clue_found(clue)
                else:
                    self.show_search_result(f"你之前已经发现了这里的重要线索。")
            else:
                self.show_search_result(f"你在{item}上发现了一些灰尘，没有其他特别的东西。")
        else:
            self.show_search_result(f"你在{item}上没有发现任何有价值的东西。")

    def show_clue_found(self, clue):
        """显示发现的线索"""
        self.game_state = 'clue_found'
        self.found_clue = clue

    def clue_found_screen(self):
        """线索发现界面"""
        bg = self.create_background((40, 30, 20), (80, 60, 40))
        self.screen.blit(bg, (0, 0))

        # 新线索标记
        self.draw_text("发现新线索!", self.font_title, COLORS['gold'], SCREEN_WIDTH // 2, 50, center=True)

        # 线索卡片
        self.draw_paper_frame(200, 120, 800, 450)

        clue = self.found_clue
        self.draw_text(f"【{clue.name}】", self.font_large, COLORS['crimson'], SCREEN_WIDTH // 2, 160, center=True)

        stars = "★" * clue.importance + "☆" * (5 - clue.importance)
        self.draw_text(f"重要性: {stars}", self.font_normal, COLORS['gold'], SCREEN_WIDTH // 2, 210, center=True)

        self.draw_text(f"地点: {clue.location}", self.font_small, COLORS['gray'], SCREEN_WIDTH // 2, 260, center=True)

        # 线索描述
        self.draw_text(clue.description, self.font_normal, COLORS['ink'], SCREEN_WIDTH // 2, 310, center=True)

        # 侦探笔记
        self.draw_text("侦探笔记:", self.font_small, COLORS['silver'], 250, 400)
        self.draw_paper_frame(230, 420, 740, 120)
        self.draw_text(f"你的推理: {clue.hint}", self.font_normal, COLORS['ink'], 260, 440)

        self.draw_button("收入笔记本", SCREEN_WIDTH // 2 - 100, 580, 200, 50, COLORS['ink'], COLORS['gold'])

    def show_search_result(self, text):
        """显示搜索结果"""
        self.search_result_text = text
        self.game_state = 'search_result'

    def search_result_screen(self):
        """搜索结果界面"""
        bg = self.create_background((20, 20, 30), (40, 40, 60))
        self.screen.blit(bg, (0, 0))

        self.draw_paper_frame(150, 250, 900, 200)

        self.draw_text("搜索结果", self.font_large, COLORS['gold'], SCREEN_WIDTH // 2, 280, center=True)
        self.draw_text(getattr(self, 'search_result_text', ''), self.font_normal, COLORS['cream'],
                      SCREEN_WIDTH // 2, 350, center=True)

        self.draw_button("继续搜索", SCREEN_WIDTH // 2 - 100, 480, 200, 50, COLORS['ink'], COLORS['green'])
        self.draw_button("返回", SCREEN_WIDTH // 2 - 100, 550, 200, 50, COLORS['ink'], COLORS['gray'])

    def interview_suspect(self, suspect):
        """审讯嫌疑人"""
        self.current_suspect = suspect
        self.game_state = 'interrogation'
        self.interrogation_phase = 0

    def interrogation_screen(self):
        """审讯界面"""
        bg = self.create_background((30, 20, 30), (60, 45, 60))
        self.screen.blit(bg, (0, 0))

        suspect = self.current_suspect

        # 嫌疑人信息框
        pygame.draw.rect(self.screen, COLORS['ink'], (0, 0, SCREEN_WIDTH, 100))
        self.draw_text(f"审讯: {suspect.name}", self.font_title, COLORS['gold'], 100, 25)
        self.draw_text(f"身份: {suspect.role} | {suspect.description}", self.font_small, COLORS['silver'], 100, 65)
        self.draw_button("返回", SCREEN_WIDTH - 150, 30, 100, 40, COLORS['ink'], COLORS['gray'])

        # 对话区域
        self.draw_paper_frame(50, 120, 700, 400)

        # 嫌疑人陈述
        self.draw_text("嫌疑人陈述:", self.font_normal, COLORS['gold'], 80, 140)

        alibi_text = f"\"关于那晚的行踪：{suspect.alibi}\""
        self.draw_text(alibi_text, self.font_normal, COLORS['cream'], 80, 190)

        # 可询问的问题
        self.draw_text("询问选项:", self.font_normal, COLORS['gold'], 80, 300)

        questions = [
            "当晚你在做什么？",
            "你和伯爵是什么关系？",
            "你知道谁可能想害伯爵吗？",
            "有什么要补充的吗？",
        ]

        y_pos = 350
        for i, q in enumerate(questions):
            self.draw_button(q, 80, y_pos, 300, 40, COLORS['ink'], COLORS['purple'],
                           lambda qi=i: self.ask_question(qi))

        # 嫌疑人对话
        suspect_responses = [
            [
                "我已经说过了，我在房间里休息。",
                "我们只是普通的家族关系。",
                "这...我不太清楚伯爵的敌人。",
                "没有了，我知道的都说了。",
            ],
            [
                "你为什么一直追问？",
                "伯爵对我...还算客气。",
                "也许是他的侄子？听说欠了很多钱。",
                "我说的都是实话！",
            ],
        ]

        # 侧边信息
        self.draw_notebook(780, 120, 370, 400)

        self.draw_text("嫌疑人档案", self.font_large, COLORS['gold'], 965, 140, center=True)
        pygame.draw.line(self.screen, COLORS['brown'], (810, 180), (920, 180), 2)

        info = [
            f"姓名: {suspect.name}",
            f"年龄: 未知",
            f"与死者关系: {suspect.relationship_with_victim or '待调查'}",
            "",
            "已知信息:",
            f"不在场证明: {suspect.alibi}",
        ]

        y_pos = 200
        for line in info:
            self.draw_text(line, self.font_small, COLORS['cream'], 810, y_pos)
            y_pos += 30

        # 审讯进度
        interviewed = suspect.name in self.detective.suspects_interviewed
        self.draw_text(f"审讯状态: {'已完成' if interviewed else '进行中'}",
                      self.font_small, COLORS['green'] if interviewed else COLORS['orange'], 810, 380)

        if not interviewed:
            self.draw_button("完成审讯", 810, 420, 150, 40, COLORS['ink'], COLORS['gold'],
                           lambda: self.finish_interrogation())

    def ask_question(self, q_index):
        """提问"""
        responses = {
            0: "我再想想...当时我在卧室看书，大约9点就睡了。",
            1: "我们是夫妻关系，虽然最近有些...摩擦。",
            2: "伯爵有很多敌人，比如那个债主，或者...我听说他有外遇。",
            3: "我知道的就这些了，请相信我。",
        }

        suspect = self.current_suspect
        skill_bonus = self.detective.skill['interrogation'] / 50

        # 根据问题类型给出不同回应
        if q_index == 0:  # 行踪
            self.last_response = "关于那晚的行踪，我刚才已经说过了，我在卧室休息。"
        elif q_index == 1:  # 关系
            self.last_response = "我们是夫妻，但最近因为一些...财务问题产生了矛盾。"
        elif q_index == 2:  # 敌人
            # 高审讯技巧可能获得更多信息
            if skill_bonus > 1.2:
                self.last_response = "好吧...我承认，我知道伯爵有一个秘密情人。这个秘密可能是动机。"
                if suspect not in self.detective.suspects_interviewed:
                    self.detective.skill['interrogation'] += 5
            else:
                self.last_response = "我怎么会知道？我又不是伯爵肚子里的蛔虫。"
        else:  # 补充
            self.last_response = "没有更多了。"

        self.show_interrogation_response()

    def show_interrogation_response(self):
        """显示审讯回应"""
        self.game_state = 'interrogation_response'

    def finish_interrogation(self):
        """完成审讯"""
        suspect = self.current_suspect
        if suspect.name not in self.detective.suspects_interviewed:
            self.detective.suspects_interviewed.append(suspect.name)
            self.detective.skill['interrogation'] += 10

        self.game_state = 'investigation'

    def accusation_screen(self):
        """指控界面"""
        bg = self.create_background((30, 10, 10), (60, 20, 20))
        self.screen.blit(bg, (0, 0))

        self.draw_text("提出指控", self.font_title, COLORS['crimson'], SCREEN_WIDTH // 2, 30, center=True)

        # 线索检查
        critical_clues = ['空的药瓶', '破碎的酒杯', '收藏室钥匙']
        found_critical = [c for c in self.detective.clues_collected if c.name in critical_clues]

        if len(found_critical) < 2:
            self.draw_text("警告: 你收集的关键线索还不够多！", self.font_large, COLORS['orange'],
                          SCREEN_WIDTH // 2, 100, center=True)
            self.draw_text(f"当前关键线索: {len(found_critical)}/3", self.font_normal, COLORS['cream'],
                          SCREEN_WIDTH // 2, 150, center=True)
        else:
            self.draw_text(f"已收集 {len(found_critical)}/3 关键线索", self.font_large, COLORS['green'],
                          SCREEN_WIDTH // 2, 100, center=True)

        # 选择凶手
        self.draw_text("选择你认为的凶手:", self.font_large, COLORS['gold'], SCREEN_WIDTH // 2, 220, center=True)

        y_pos = 280
        for suspect in self.case.suspects:
            self.draw_button(f"{suspect.name} - {suspect.role}",
                           300, y_pos, 600, 50, COLORS['ink'], COLORS['crimson'],
                           lambda s=suspect: self.make_accusation(s))
            y_pos += 65

        self.draw_button("返回调查", SCREEN_WIDTH // 2 - 100, 650, 200, 50, COLORS['ink'], COLORS['gray'])

    def make_accusation(self, suspect):
        """做出指控"""
        self.selected_suspect = suspect
        self.game_state = 'accusation_result'

    def accusation_result_screen(self):
        """指控结果"""
        bg = self.create_background((20, 20, 30), (40, 40, 60))
        self.screen.blit(bg, (0, 0))

        # 真相揭晓
        guilty_suspect = [s for s in self.case.suspects if s.possible_guilty][0]

        if self.selected_suspect.possible_guilty:
            # 正确指控
            self.draw_text("推理正确!", self.font_title, COLORS['gold'], SCREEN_WIDTH // 2, 80, center=True)

            result_bg = self.create_background((20, 50, 20), (40, 100, 40))
            self.screen.blit(result_bg, (150, 150))
            self.draw_paper_frame(180, 180, 840, 400)

            lines = [
                f"凶手就是: {guilty_suspect.name}",
                "",
                "案件真相:",
                f"{guilty_suspect.name} 因与伯爵存在不可调和的矛盾，",
                "在红酒中下毒，导致伯爵在数小时后毒发身亡。",
                "",
                "关键证据:",
                "• 空的药瓶中检测出与酒杯残留物相同的毒药",
                "• 收藏室中有{guilty_suspect.name}与伯爵争吵的证据",
                "• 破碎的酒杯是最关键的物证",
            ]

            y_pos = 210
            for line in lines:
                color = COLORS['cream'] if not line.startswith("凶手") and not line.startswith("案件") else COLORS['gold']
                self.draw_text(line, self.font_normal, color, SCREEN_WIDTH // 2, y_pos, center=True)
                y_pos += 32

            self.draw_button("结案", SCREEN_WIDTH // 2 - 80, 620, 160, 50, COLORS['ink'], COLORS['gold'])
        else:
            # 错误指控
            self.draw_text("推理错误...", self.font_title, COLORS['crimson'], SCREEN_WIDTH // 2, 80, center=True)

            self.draw_paper_frame(180, 180, 840, 350)

            lines = [
                f"你指控的 {self.selected_suspect.name} 是无辜的。",
                "",
                "虽然他/她有嫌疑，但证据不足以证明其罪行。",
                "真正的凶手仍然逍遥法外...",
                "",
                "提示: 仔细检查关键线索之间的关联。",
            ]

            y_pos = 210
            for line in lines:
                self.draw_text(line, self.font_normal, COLORS['cream'], SCREEN_WIDTH // 2, y_pos, center=True)
                y_pos += 35

            self.draw_button("继续调查", SCREEN_WIDTH // 2 - 100, 570, 200, 50, COLORS['ink'], COLORS['gold'])
            self.draw_button("重新指控", SCREEN_WIDTH // 2 - 100, 640, 200, 50, COLORS['ink'], COLORS['gray'])

    def run(self):
        """主循环"""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.game_state in ['investigation', 'room_exploration', 'interrogation']:
                            self.game_state = 'investigation'
                    elif event.key == pygame.K_RETURN:
                        if self.game_state == 'detective_setup':
                            self.create_detective()

            # 点击处理
            click = pygame.mouse.get_pressed()
            if click[0]:
                mx, my = pygame.mouse.get_pos()
                self.handle_click(mx, my)
                pygame.time.wait(100)

            # 渲染
            if self.game_state == 'menu':
                self.main_menu()
            elif self.game_state == 'detective_setup':
                self.detective_setup()
            elif self.game_state == 'case_intro':
                self.case_intro_screen()
            elif self.game_state == 'investigation':
                self.investigation_screen()
            elif self.game_state == 'room_exploration':
                self.room_exploration_screen()
            elif self.game_state == 'clue_found':
                self.clue_found_screen()
            elif self.game_state == 'search_result':
                self.search_result_screen()
            elif self.game_state == 'interrogation':
                self.interrogation_screen()
            elif self.game_state == 'interrogation_response':
                self.interrogation_response_screen()
            elif self.game_state == 'accusation':
                self.accusation_screen()
            elif self.game_state == 'accusation_result':
                self.accusation_result_screen()

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

    def handle_click(self, x, y):
        """处理点击"""
        if self.game_state == 'menu':
            if 370 <= x <= 670:
                if 520 <= y <= 580:
                    self.game_state = 'detective_setup'
                elif 600 <= y <= 660:
                    # 继续 - 检查是否有存档
                    self.show_message("暂无存档")
                elif 680 <= y <= 740:
                    self.running = False

        elif self.game_state == 'detective_setup':
            if 450 <= y <= 500:
                if 450 <= x <= 850:
                    pass  # 名字输入区域
            elif 650 <= y <= 700:
                if 500 <= x <= 700:
                    self.create_detective()
            elif 720 <= y <= 770:
                if 500 <= x <= 700:
                    self.game_state = 'menu'
            # 技能选择
            elif 300 <= y <= 560:
                if 170 <= x <= 670:
                    if 300 <= y <= 350:
                        self.select_specialty('observation')
                    elif 360 <= y <= 410:
                        self.select_specialty('deduction')
                    elif 420 <= y <= 470:
                        self.select_specialty('interrogation')
                    elif 480 <= y <= 530:
                        self.select_specialty('intuition')

        elif self.game_state == 'case_intro':
            if 480 <= y <= 540:
                if 480 <= x <= 720:
                    self.game_state = 'investigation'
            elif 630 <= y <= 680:
                if 480 <= x <= 720:
                    self.game_state = 'menu'

        elif self.game_state == 'investigation':
            # 地点按钮
            for i, room in enumerate(self.case.rooms):
                if 50 <= x <= 350:
                    if 160 + i * 52 <= y <= 160 + i * 52 + 45:
                        self.enter_room(room)
                        return

            # 嫌疑人按钮
            for i, suspect in enumerate(self.case.suspects):
                if 420 <= x <= 720:
                    if 160 + i * 52 <= y <= 160 + i * 52 + 45:
                        self.interview_suspect(suspect)
                        return

            # 推理按钮
            if 790 <= x <= 970:
                if 420 <= y <= 465:
                    self.show_deduction()
                elif 475 <= y <= 520:
                    self.game_state = 'accusation'
                elif 530 <= y <= 575:
                    self.show_suspect_relations()

            # 返回
            if 100 <= x <= 250 and SCREEN_HEIGHT - 65 <= y <= SCREEN_HEIGHT - 20:
                self.game_state = 'case_intro'

        elif self.game_state == 'room_exploration':
            # 返回按钮
            if 50 <= x <= 150 and 15 <= y <= 55:
                self.game_state = 'investigation'
            # 搜索物品
            for i in range(10):
                col = i % 2
                row = i // 2
                if 600 + col * 280 <= x <= 850 + col * 280:
                    if 170 + row * 55 <= y <= 215 + row * 55:
                        items = ["书架", "桌子", "椅子", "窗户", "地毯", "抽屉", "壁炉", "柜子", "床", "窗帘"]
                        self.search_item(items[i])
                        return

        elif self.game_state == 'clue_found':
            if 500 <= x <= 700 and 580 <= y <= 630:
                self.game_state = 'investigation'

        elif self.game_state == 'search_result':
            if 500 <= x <= 700:
                if 480 <= y <= 530:
                    self.game_state = 'room_exploration'
                elif 550 <= y <= 600:
                    self.game_state = 'investigation'

        elif self.game_state == 'interrogation':
            if SCREEN_WIDTH - 150 <= x <= SCREEN_WIDTH - 50 and 30 <= y <= 70:
                self.game_state = 'investigation'
            # 问题按钮
            if 80 <= x <= 380:
                for i in range(4):
                    if 350 + i * 50 <= y <= 390 + i * 50:
                        self.ask_question(i)
                        return
            # 完成审讯
            if 810 <= x <= 960 and 420 <= y <= 460:
                self.finish_interrogation()

        elif self.game_state == 'interrogation_response':
            self.finish_interrogation()

        elif self.game_state == 'accusation':
            if 500 <= y <= 550:
                if 450 <= x <= 650:
                    self.game_state = 'investigation'
            else:
                for i, suspect in enumerate(self.case.suspects):
                    if 300 <= y <= 280 + i * 65 + 50:
                        self.make_accusation(suspect)
                        return

        elif self.game_state == 'accusation_result':
            if 480 <= x <= 640:
                if 620 <= y <= 670:
                    self.game_state = 'menu'
                elif 570 <= y <= 620:
                    self.game_state = 'investigation'
                elif 640 <= y <= 690:
                    self.game_state = 'accusation'

    def show_deduction(self):
        """显示推理界面"""
        self.game_state = 'deduction'
        self.deduction_page = 0

    def show_suspect_relations(self):
        """显示嫌疑人关系"""
        self.game_state = 'relations'

    def show_message(self, msg):
        """显示消息"""
        self.temp_message = msg
        self.temp_timer = 120

if __name__ == "__main__":
    game = Game()
    game.run()
