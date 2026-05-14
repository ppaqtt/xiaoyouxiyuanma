#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文字冒险RPG游戏 - 失落王国的传说
Visual Narrative RPG Game - Legend of the Lost Kingdom

玩家扮演一名年轻勇士，在失落王国中展开冒险
通过选择影响剧情走向，体验战斗与解谜的乐趣
"""

import pygame
import sys
import random
import os

# 初始化Pygame
pygame.init()

# 游戏常量
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# 颜色定义
COLORS = {
    'bg_dark': (20, 20, 40),
    'bg_medium': (40, 40, 80),
    'gold': (255, 215, 0),
    'silver': (192, 192, 192),
    'red': (220, 50, 50),
    'green': (50, 200, 50),
    'blue': (100, 150, 255),
    'white': (255, 255, 255),
    'gray': (150, 150, 150),
    'purple': (180, 100, 200),
    'orange': (255, 165, 0),
    'brown': (139, 90, 43),
    'cream': (255, 253, 208),
}

# 字体设置
def get_font(size):
    """获取中文字体"""
    try:
        return pygame.font.Font("C:/Windows/Fonts/msyh.ttc", size)
    except:
        try:
            return pygame.font.Font("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc", size)
        except:
            return pygame.font.Font(None, size)

class Player:
    """玩家角色类"""
    def __init__(self, name):
        self.name = name
        self.level = 1
        self.exp = 0
        self.max_hp = 100
        self.hp = 100
        self.max_mp = 50
        self.mp = 50
        self.attack = 15
        self.defense = 10
        self.gold = 100
        self.inventory = []
        self.equipment = {
            'weapon': None,
            'armor': None,
            'accessory': None
        }
        self.skills = ['普通攻击', '强力一击']
        self.flags = {}
        self.current_chapter = 1
        self.reputation = 0  # 声望

    def level_up(self):
        """升级"""
        exp_needed = self.level * 100
        if self.exp >= exp_needed:
            self.level += 1
            self.exp -= exp_needed
            self.max_hp += 20
            self.hp = self.max_hp
            self.max_mp += 10
            self.mp = self.max_mp
            self.attack += 5
            self.defense += 3
            return True
        return False

    def add_item(self, item):
        """添加物品"""
        self.inventory.append(item)

    def use_item(self, item_name):
        """使用物品"""
        for item in self.inventory:
            if item['name'] == item_name:
                if item['type'] == 'hp_potion':
                    heal = item['value']
                    self.hp = min(self.hp + heal, self.max_hp)
                elif item['type'] == 'mp_potion':
                    recover = item['value']
                    self.mp = min(self.mp + recover, self.max_mp)
                self.inventory.remove(item)
                return True
        return False

class Enemy:
    """敌人类"""
    def __init__(self, name, hp, attack, defense, exp_reward, gold_reward, description=""):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.exp_reward = exp_reward
        self.gold_reward = gold_reward
        self.description = description

class Game:
    """游戏主类"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("失落王国的传说 - 文字冒险RPG")
        self.clock = pygame.time.Clock()
        self.font_title = get_font(48)
        self.font_large = get_font(32)
        self.font_normal = get_font(24)
        self.font_small = get_font(18)

        self.running = True
        self.game_state = 'menu'  # menu, playing, battle, dialog, game_over, ending
        self.current_scene = None
        self.dialog_queue = []
        self.current_dialog = None
        self.battle_state = None
        self.player = None
        self.story_progress = 0

        # 背景图片缓存
        self.backgrounds = {}

    def create_background(self, color1, color2, title=""):
        """创建渐变背景"""
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

        if button_rect.collidepoint(mouse):
            pygame.draw.rect(self.screen, hover_color, button_rect, border_radius=10)
            if click[0] == 1 and action:
                return action()
        else:
            pygame.draw.rect(self.screen, color, button_rect, border_radius=10)

        pygame.draw.rect(self.screen, COLORS['gold'], button_rect, 3, border_radius=10)
        self.draw_text(text, self.font_normal, COLORS['white'], x + width // 2, y + height // 2, center=True)
        return None

    def draw_dialog_box(self, text, speaker=""):
        """绘制对话框"""
        box_height = 200
        box_y = SCREEN_HEIGHT - box_height - 20

        # 对话框背景
        dialog_rect = pygame.Rect(50, box_y, SCREEN_WIDTH - 100, box_height)
        pygame.draw.rect(self.screen, (30, 30, 50), dialog_rect, border_radius=15)
        pygame.draw.rect(self.screen, COLORS['gold'], dialog_rect, 3, border_radius=15)

        # 说话者名称
        if speaker:
            name_rect = pygame.Rect(70, box_y - 25, 150, 40)
            pygame.draw.rect(self.screen, COLORS['purple'], name_rect, border_radius=8)
            self.draw_text(speaker, self.font_normal, COLORS['white'],
                          name_rect.centerx, name_rect.centery, center=True)

        # 对话文本 - 支持多行
        lines = self.wrap_text(text, self.font_normal, SCREEN_WIDTH - 140)
        y_offset = box_y + 20
        for line in lines[:5]:  # 最多显示5行
            self.draw_text(line, self.font_normal, COLORS['cream'], 90, y_offset)
            y_offset += 35

        # 继续提示
        self.draw_text("[点击继续]", self.font_small, COLORS['gray'],
                      SCREEN_WIDTH - 150, box_y + box_height - 30)

    def wrap_text(self, text, font, max_width):
        """文本自动换行"""
        words = text.split('')
        lines = []
        current_line = ""

        for char in text:
            test_line = current_line + char
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = char

        if current_line:
            lines.append(current_line)

        return lines if lines else [text]

    def draw_character_status(self, player):
        """绘制角色状态面板"""
        # 状态面板背景
        panel_rect = pygame.Rect(20, 20, 280, 300)
        pygame.draw.rect(self.screen, (20, 20, 40), panel_rect, border_radius=15)
        pygame.draw.rect(self.screen, COLORS['blue'], panel_rect, 2, border_radius=15)

        # 角色名称和等级
        self.draw_text(f"【{player.name}】", self.font_large, COLORS['gold'], 40, 35)
        self.draw_text(f"等级: Lv.{player.level}", self.font_normal, COLORS['silver'], 40, 75)

        # HP条
        self.draw_text("生命值", self.font_small, COLORS['red'], 40, 110)
        hp_ratio = player.hp / player.max_hp
        pygame.draw.rect(self.screen, (100, 30, 30), (40, 130, 200, 20), border_radius=5)
        pygame.draw.rect(self.screen, COLORS['red'], (40, 130, int(200 * hp_ratio), 20), border_radius=5)
        self.draw_text(f"{player.hp}/{player.max_hp}", self.font_small, COLORS['white'], 140, 133, center=True)

        # MP条
        self.draw_text("魔法值", self.font_small, COLORS['blue'], 40, 160)
        mp_ratio = player.mp / player.max_mp
        pygame.draw.rect(self.screen, (30, 30, 100), (40, 180, 200, 20), border_radius=5)
        pygame.draw.rect(self.screen, COLORS['blue'], (40, 180, int(200 * mp_ratio), 20), border_radius=5)
        self.draw_text(f"{player.mp}/{player.max_mp}", self.font_small, COLORS['white'], 140, 183, center=True)

        # 经验条
        exp_needed = player.level * 100
        self.draw_text("经验值", self.font_small, COLORS['purple'], 40, 210)
        exp_ratio = player.exp / exp_needed
        pygame.draw.rect(self.screen, (60, 30, 80), (40, 230, 200, 15), border_radius=5)
        pygame.draw.rect(self.screen, COLORS['purple'], (40, 230, int(200 * exp_ratio), 15), border_radius=5)
        self.draw_text(f"{player.exp}/{exp_needed}", self.font_small, COLORS['white'], 140, 231, center=True)

        # 属性
        self.draw_text(f"攻击力: {player.attack}  防御力: {player.defense}", self.font_small, COLORS['gray'], 40, 260)
        self.draw_text(f"金币: {player.gold}", self.font_small, COLORS['orange'], 40, 285)

    def draw_inventory(self, player):
        """绘制物品栏"""
        panel_rect = pygame.Rect(20, 340, 280, 400)
        pygame.draw.rect(self.screen, (20, 20, 40), panel_rect, border_radius=15)
        pygame.draw.rect(self.screen, COLORS['gold'], panel_rect, 2, border_radius=15)

        self.draw_text("物品栏", self.font_large, COLORS['gold'], 40, 355)

        y_pos = 400
        for i, item in enumerate(player.inventory[:8]):  # 最多显示8个物品
            color = COLORS['green'] if item['type'] == 'hp_potion' else COLORS['blue']
            self.draw_text(f"{item['icon']} {item['name']}", self.font_small, color, 40, y_pos)
            y_pos += 30

        if not player.inventory:
            self.draw_text("(空)", self.font_small, COLORS['gray'], 40, y_pos)

    def main_menu(self):
        """主菜单"""
        # 背景
        bg = self.create_background((10, 10, 30), (30, 30, 80))
        self.screen.blit(bg, (0, 0))

        # 装饰边框
        for i in range(5):
            pygame.draw.rect(self.screen, COLORS['gold'], (20+i, 20+i, SCREEN_WIDTH-40-i*2, SCREEN_HEIGHT-40-i*2), 1, border_radius=20)

        # 标题
        self.draw_text("失落王国的传说", self.font_title, COLORS['gold'], SCREEN_WIDTH // 2, 150, center=True)
        self.draw_text("LEGEND OF THE LOST KINGDOM", self.font_normal, COLORS['silver'], SCREEN_WIDTH // 2, 210, center=True)

        # 副标题
        self.draw_text("文字冒险RPG", self.font_large, COLORS['purple'], SCREEN_WIDTH // 2, 280, center=True)

        # 菜单按钮
        self.draw_button("开始新游戏", SCREEN_WIDTH // 2 - 150, 400, 300, 60, COLORS['bg_medium'], COLORS['blue'], lambda: self.start_new_game())
        self.draw_button("继续游戏", SCREEN_WIDTH // 2 - 150, 480, 300, 60, COLORS['bg_medium'], COLORS['green'], lambda: self.continue_game())
        self.draw_button("游戏说明", SCREEN_WIDTH // 2 - 150, 560, 300, 60, COLORS['bg_medium'], COLORS['purple'], lambda: self.show_help())
        self.draw_button("退出游戏", SCREEN_WIDTH // 2 - 150, 640, 300, 60, COLORS['bg_medium'], COLORS['red'], lambda: self.quit_game())

        # 底部提示
        self.draw_text("v1.0 - 剧情爱好者版", self.font_small, COLORS['gray'], SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40, center=True)

    def start_new_game(self):
        """开始新游戏"""
        self.game_state = 'name_input'
        self.name_input = ""

    def name_input_screen(self):
        """角色名称输入界面"""
        bg = self.create_background((10, 10, 30), (30, 30, 80))
        self.screen.blit(bg, (0, 0))

        self.draw_text("创建你的角色", self.font_title, COLORS['gold'], SCREEN_WIDTH // 2, 100, center=True)
        self.draw_text("请输入角色名称:", self.font_large, COLORS['white'], SCREEN_WIDTH // 2, 200, center=True)

        # 输入框
        input_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, 280, 400, 60)
        pygame.draw.rect(self.screen, COLORS['bg_medium'], input_rect, border_radius=10)
        pygame.draw.rect(self.screen, COLORS['gold'], input_rect, 3, border_radius=10)
        self.draw_text(self.name_input + "|", self.font_large, COLORS['white'], SCREEN_WIDTH // 2, 303, center=True)

        # 职业选择
        self.draw_text("选择你的职业:", self.font_large, COLORS['white'], SCREEN_WIDTH // 2, 400, center=True)

        y_pos = 460
        self.draw_button("战士 - 攻防兼备", SCREEN_WIDTH // 2 - 200, y_pos, 400, 50, COLORS['bg_medium'], COLORS['red'],
                        lambda: self.create_character("战士"))
        self.draw_button("法师 - 魔法强大", SCREEN_WIDTH // 2 - 200, y_pos + 60, 400, 50, COLORS['bg_medium'], COLORS['blue'],
                        lambda: self.create_character("法师"))
        self.draw_button("刺客 - 敏捷致命", SCREEN_WIDTH // 2 - 200, y_pos + 120, 400, 50, COLORS['bg_medium'], COLORS['purple'],
                        lambda: self.create_character("刺客"))

    def create_character(self, profession):
        """创建角色"""
        name = self.name_input if self.name_input else "无名勇士"
        self.player = Player(name)

        # 根据职业调整属性
        if profession == "战士":
            self.player.max_hp = 120
            self.player.hp = 120
            self.player.attack = 18
            self.player.defense = 15
            self.player.skills.append("横扫千军")
        elif profession == "法师":
            self.player.max_mp = 80
            self.player.mp = 80
            self.player.attack = 25
            self.player.defense = 5
            self.player.skills.append("火球术")
            self.player.skills.append("冰霜新星")
        else:  # 刺客
            self.player.attack = 22
            self.player.defense = 8
            self.player.skills.append("暗影突袭")
            self.player.skills.append("毒刃")

        # 初始物品
        self.player.add_item({'name': '生命药水', 'type': 'hp_potion', 'value': 50, 'icon': '♥'})
        self.player.add_item({'name': '魔法药水', 'type': 'mp_potion', 'value': 30, 'icon': '◆'})

        self.profession = profession
        self.game_state = 'intro'
        self.intro_phase = 0

    def intro_screen(self):
        """游戏介绍"""
        bg = self.create_background((10, 10, 30), (50, 30, 20))
        self.screen.blit(bg, (0, 0))

        intros = [
            "很久以前，在遥远的东方，有一个繁荣昌盛的王国——艾瑟尔王国。",
            "然而，黑暗势力正在暗中滋生，一股神秘的力量威胁着王国的安宁。",
            f"你，{self.player.name}，是一名年轻的{self.profession}，",
            "立志要成为拯救王国的英雄。",
            "这一天，平静的小镇突然遭遇了袭击...",
            "你的冒险故事，就此展开！",
        ]

        self.draw_text("序章: 命运的开始", self.font_title, COLORS['gold'], SCREEN_WIDTH // 2, 50, center=True)

        y_pos = 150
        for i, line in enumerate(intros[:self.intro_phase + 1]):
            alpha = 255 if i < self.intro_phase else 180
            self.draw_text(line, self.font_normal, (255, 255, 255), SCREEN_WIDTH // 2, y_pos, center=True)
            y_pos += 50

        if self.intro_phase < len(intros) - 1:
            self.draw_button("继续", SCREEN_WIDTH // 2 - 100, 600, 200, 50, COLORS['bg_medium'], COLORS['green'],
                            lambda: setattr(self, 'intro_phase', self.intro_phase + 1))
        else:
            self.draw_button("踏上旅程", SCREEN_WIDTH // 2 - 100, 600, 200, 50, COLORS['bg_medium'], COLORS['gold'],
                            lambda: self.start_chapter1())

    def start_chapter1(self):
        """第一章"""
        self.game_state = 'story'
        self.current_scene = 'village_entrance'
        self.show_story_scene()

    def show_story_scene(self):
        """显示故事场景"""
        scenes = {
            'village_entrance': {
                'bg': (30, 50, 30),
                'title': '第一章: 小镇的危机',
                'story': [
                    ("旁白", "清晨的阳光洒在宁静的格林村，你从睡梦中醒来。"),
                    ("旁白", "突然，远处传来一阵骚动和尖叫声..."),
                    ("士兵", "救命啊！有怪物袭击村庄！"),
                    ("旁白", "你冲出小屋，只见村口火光冲天，一群哥布林正在肆虐。"),
                    ("旁白", "作为村里的年轻人，你必须做出选择："),
                ],
                'choices': [
                    ('拿起武器冲向哥布林', 'fight_goblin'),
                    ('先救困在火中的村民', 'save_villagers'),
                    ('去寻找村长的帮助', 'find_elder'),
                ]
            },
            'fight_goblin': {
                'bg': (50, 30, 30),
                'title': '战斗！哥布林巢穴',
                'story': [
                    ("旁白", "你毫不犹豫地冲向哥布林群，拔出佩剑。"),
                    ("旁白", "战斗一触即发！"),
                    ("哥布林", "人类！杀了他们！"),
                ],
                'choices': [
                    ('正面迎战', 'battle_goblin'),
                    ('使用技能快速解决', 'use_skill'),
                ]
            },
            'save_villagers': {
                'bg': (80, 50, 30),
                'title': '火海救人',
                'story': [
                    ("旁白", "你冲进熊熊大火中，冒着浓烟寻找幸存者。"),
                    ("旁白", "在废墟中，你发现了一名受伤的老人和两个孩子。"),
                    ("老人", "咳咳...谢谢你，年轻人..."),
                    ("旁白", "你将所有人救出火场，但错过了追击哥布林的时机。"),
                ],
                'choices': [
                    ('护送村民去安全的地方', 'escort_villagers'),
                    ('安顿好后继续追击', 'pursue_goblins'),
                ]
            },
            'find_elder': {
                'bg': (30, 40, 60),
                'title': '寻找村长',
                'story': [
                    ("旁白", "你快步前往村长家，希望能得到一些帮助。"),
                    ("村长", "年轻人，我正需要你！"),
                    ("村长", "这是皇家骑士团的令牌，能召集附近的士兵。"),
                    ("旁白", "你获得了【骑士令牌】！"),
                ],
                'choices': [
                    ('立刻召集士兵', 'call_soldiers'),
                    ('询问袭击的原因', 'ask_reason'),
                ]
            },
        }

        if self.current_scene in scenes:
            scene = scenes[self.current_scene]
            bg = self.create_background((10, 10, 20), scene['bg'])
            self.screen.blit(bg, (0, 0))

            # 标题
            self.draw_text(scene['title'], self.font_title, COLORS['gold'], SCREEN_WIDTH // 2, 30, center=True)

            # 故事内容
            self.story_index = getattr(self, 'story_index', 0)
            self.scene_data = scene

            y_pos = 100
            for i, (speaker, text) in enumerate(self.story_lines if hasattr(self, 'story_lines') else []):
                color = COLORS['cream']
                if speaker != "旁白":
                    color = COLORS['green'] if speaker in ["士兵", "村长", "老人", "智者"] else COLORS['orange']
                self.draw_text(f"{speaker}: {text}", self.font_normal, color, 100, y_pos)
                y_pos += 40

            # 显示更多按钮
            if self.story_index < len(scene['story']):
                if not hasattr(self, 'story_lines') or len(self.story_lines) < self.story_index + 1:
                    self.draw_button("继续", SCREEN_WIDTH // 2 - 100, 500, 200, 50, COLORS['bg_medium'], COLORS['blue'],
                                    lambda: self.advance_story())
            else:
                # 显示选项
                self.draw_text("你会怎么做?", self.font_large, COLORS['gold'], SCREEN_WIDTH // 2, 450, center=True)
                y_pos = 500
                for i, (choice_text, next_scene) in enumerate(scene['choices']):
                    self.draw_button(choice_text, SCREEN_WIDTH // 2 - 250, y_pos, 500, 45, COLORS['bg_medium'], COLORS['purple'],
                                    lambda n=next_scene: self.go_to_scene(n))
                    y_pos += 55

            # 角色状态
            self.draw_character_status(self.player)
            self.draw_inventory(self.player)
        else:
            # 战斗场景
            self.battle_intro()

    def advance_story(self):
        """推进故事"""
        if not hasattr(self, 'story_lines'):
            self.story_lines = []
        if not hasattr(self, 'story_index'):
            self.story_index = 0

        if self.story_index < len(self.scene_data['story']):
            self.story_lines.append(self.scene_data['story'][self.story_index])
            self.story_index += 1

    def go_to_scene(self, scene_name):
        """切换场景"""
        self.current_scene = scene_name
        self.story_index = 0
        self.story_lines = []
        if scene_name == 'battle_goblin' or scene_name == 'use_skill':
            self.start_battle('哥布林', 40, 12, 5, 20, 15)
        elif scene_name == 'call_soldiers':
            self.player.reputation += 10
            self.show_dialog("召集士兵后，哥布林很快被击退。你获得了村民的感激！")
        elif scene_name == 'ask_reason':
            self.show_dialog("村长告诉你，这次袭击可能是黑暗森林里的邪恶魔王派来的...")
        elif scene_name == 'escort_villagers':
            self.show_dialog("你将村民护送到安全的地方。一位商人感激地送给你一件礼物。")
            self.player.add_item({'name': '防御戒指', 'type': 'accessory', 'value': 5, 'icon': '○'})
        elif scene_name == 'pursue_goblins':
            self.start_battle('哥布林首领', 60, 18, 8, 40, 30)
        else:
            self.show_dialog("你的选择影响了故事的走向...")

    def show_dialog(self, message):
        """显示对话"""
        self.game_state = 'dialog'
        self.current_dialog = message
        self.dialog_speaker = "系统"

    def start_battle(self, enemy_name, hp, atk, df, exp_r, gold_r):
        """开始战斗"""
        self.game_state = 'battle'
        self.enemy = Enemy(enemy_name, hp, atk, df, exp_r, gold_r)
        self.battle_state = 'player_turn'
        self.battle_log = []
        self.add_battle_log(f"遭遇 {enemy_name}！")

    def add_battle_log(self, message):
        """添加战斗日志"""
        self.battle_log.append(message)
        if len(self.battle_log) > 5:
            self.battle_log.pop(0)

    def battle_screen(self):
        """战斗界面"""
        bg = self.create_background((50, 20, 20), (20, 10, 30))
        self.screen.blit(bg, (0, 0))

        self.draw_text("=== 战 斗 ===", self.font_title, COLORS['red'], SCREEN_WIDTH // 2, 30, center=True)

        # 敌人信息
        enemy_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 80, 300, 150)
        pygame.draw.rect(self.screen, (40, 20, 20), enemy_rect, border_radius=15)
        pygame.draw.rect(self.screen, COLORS['red'], enemy_rect, 2, border_radius=15)

        self.draw_text(self.enemy.name, self.font_large, COLORS['orange'], SCREEN_WIDTH // 2, 100, center=True)
        hp_ratio = self.enemy.hp / self.enemy.max_hp
        pygame.draw.rect(self.screen, (100, 30, 30), (SCREEN_WIDTH // 2 - 120, 140, 240, 25), border_radius=5)
        pygame.draw.rect(self.screen, COLORS['red'], (SCREEN_WIDTH // 2 - 120, 140, int(240 * hp_ratio), 25), border_radius=5)
        self.draw_text(f"HP: {self.enemy.hp}/{self.enemy.max_hp}", self.font_normal, COLORS['white'], SCREEN_WIDTH // 2, 145, center=True)

        # 战斗日志
        log_rect = pygame.Rect(50, 250, SCREEN_WIDTH - 100, 150)
        pygame.draw.rect(self.screen, (20, 20, 30), log_rect, border_radius=10)
        y_pos = 265
        for log in self.battle_log:
            self.draw_text(log, self.font_normal, COLORS['cream'], 70, y_pos)
            y_pos += 28

        # 玩家状态
        self.draw_character_status(self.player)

        # 技能按钮
        if self.battle_state == 'player_turn':
            self.draw_text("选择行动:", self.font_large, COLORS['gold'], SCREEN_WIDTH // 2, 550, center=True)

            y_pos = 600
            for i, skill in enumerate(self.player.skills[:4]):
                color = COLORS['blue'] if '攻击' in skill or '突袭' in skill else COLORS['purple']
                self.draw_button(skill, 200 + (i % 2) * 400, y_pos, 180, 50, COLORS['bg_medium'], color,
                                lambda s=skill: self.use_skill(s))

            # 物品按钮
            self.draw_button("使用物品", 200, y_pos + 60, 180, 50, COLORS['bg_medium'], COLORS['green'],
                            lambda: self.use_item_battle())
            self.draw_button("防御", 600, y_pos + 60, 180, 50, COLORS['bg_medium'], COLORS['silver'],
                            lambda: self.defend())
            self.draw_button("逃跑", 400, y_pos + 120, 200, 45, COLORS['bg_medium'], COLORS['red'],
                            lambda: self.try_escape())

    def use_skill(self, skill):
        """使用技能"""
        if skill == "普通攻击":
            damage = max(1, self.player.attack - self.enemy.defense // 2 + random.randint(-3, 3))
        elif skill == "强力一击":
            damage = max(1, self.player.attack * 2 - self.enemy.defense // 2)
            self.player.mp -= 10
        elif skill == "横扫千军":
            damage = max(1, self.player.attack * 1 + self.player.defense - self.enemy.defense // 2)
            self.player.mp -= 15
        elif skill == "火球术":
            damage = max(1, self.player.attack * 2 + 10 - self.enemy.defense // 2)
            self.player.mp -= 20
        elif skill == "冰霜新星":
            damage = max(1, self.player.attack * 1 + 5)
            self.player.mp -= 25
        elif skill == "暗影突袭":
            damage = max(1, self.player.attack * 2 + random.randint(5, 15))
            self.player.mp -= 15
        elif skill == "毒刃":
            damage = max(1, self.player.attack * 1 + random.randint(10, 20))
            self.player.mp -= 10

        self.enemy.hp -= damage
        self.add_battle_log(f"你对{self.enemy.name}使用{skill}，造成 {damage} 点伤害！")

        if self.enemy.hp <= 0:
            self.battle_victory()
        else:
            self.battle_state = 'enemy_turn'
            self.enemy_turn()

    def use_item_battle(self):
        """战斗中物品使用"""
        if self.player.inventory:
            self.game_state = 'item_select'
            self.show_item_selection()
        else:
            self.add_battle_log("没有可使用的物品！")

    def show_item_selection(self):
        """显示物品选择界面"""
        bg = self.create_background((20, 30, 20), (40, 50, 40))
        self.screen.blit(bg, (0, 0))

        self.draw_text("选择物品", self.font_title, COLORS['gold'], SCREEN_WIDTH // 2, 100, center=True)

        y_pos = 200
        for item in self.player.inventory:
            self.draw_button(f"{item['icon']} {item['name']} (+{item['value']})",
                           SCREEN_WIDTH // 2 - 200, y_pos, 400, 50, COLORS['bg_medium'], COLORS['green'],
                           lambda i=item: self.battle_use_item(i))
            y_pos += 60

        self.draw_button("返回", SCREEN_WIDTH // 2 - 100, 600, 200, 50, COLORS['bg_medium'], COLORS['gray'],
                        lambda: setattr(self, 'game_state', 'battle'))

    def battle_use_item(self, item):
        """战斗中使用的物品"""
        self.player.use_item(item['name'])
        if item['type'] == 'hp_potion':
            self.add_battle_log(f"你使用了{item['name']}，恢复了 {item['value']} HP！")
        else:
            self.add_battle_log(f"你使用了{item['name']}，恢复了 {item['value']} MP！")
        self.game_state = 'battle'
        self.battle_state = 'enemy_turn'
        self.enemy_turn()

    def defend(self):
        """防御"""
        self.player_temp_defense = self.player.defense * 2
        self.add_battle_log("你进入防御姿态！")
        self.battle_state = 'enemy_turn'
        self.enemy_turn()

    def try_escape(self):
        """尝试逃跑"""
        if random.random() > 0.5:
            self.add_battle_log("逃跑成功！")
            self.game_state = 'story'
            self.current_scene = 'village_entrance'
        else:
            self.add_battle_log("逃跑失败！")
            self.battle_state = 'enemy_turn'
            self.enemy_turn()

    def enemy_turn(self):
        """敌人回合"""
        pygame.time.wait(500)
        defense = getattr(self, 'player_temp_defense', self.player.defense)
        damage = max(1, self.enemy.attack - defense // 2 + random.randint(-2, 2))
        self.player.hp -= damage
        self.add_battle_log(f"{self.enemy.name}攻击你，造成 {damage} 点伤害！")
        self.player_temp_defense = None

        if self.player.hp <= 0:
            self.battle_defeat()
        else:
            self.battle_state = 'player_turn'

    def battle_victory(self):
        """战斗胜利"""
        self.add_battle_log(f"你击败了{self.enemy.name}！")
        self.player.exp += self.enemy.exp_reward
        self.player.gold += self.enemy.gold_reward
        self.add_battle_log(f"获得 {self.enemy.exp_reward} 经验值和 {self.enemy.gold_reward} 金币！")

        # 检查升级
        if self.player.level_up():
            self.add_battle_log(f"升级了！现在是 Lv.{self.player.level}！")

        self.game_state = 'battle_result'
        self.battle_result = 'victory'

    def battle_defeat(self):
        """战斗失败"""
        self.game_state = 'battle_result'
        self.battle_result = 'defeat'

    def battle_result_screen(self):
        """战斗结果界面"""
        bg = self.create_background((50, 20, 20), (20, 10, 30))
        self.screen.blit(bg, (0, 0))

        if self.battle_result == 'victory':
            self.draw_text("胜 利", self.font_title, COLORS['gold'], SCREEN_WIDTH // 2, 200, center=True)
            self.draw_text("你获得了战斗的胜利！", self.font_large, COLORS['green'], SCREEN_WIDTH // 2, 300, center=True)

            # 战利品
            self.draw_text(f"经验 +{self.enemy.exp_reward}", self.font_normal, COLORS['purple'], SCREEN_WIDTH // 2, 400, center=True)
            self.draw_text(f"金币 +{self.enemy.gold_reward}", self.font_normal, COLORS['orange'], SCREEN_WIDTH // 2, 440, center=True)

            self.draw_button("继续冒险", SCREEN_WIDTH // 2 - 100, 550, 200, 50, COLORS['bg_medium'], COLORS['gold'],
                            lambda: self.continue_adventure())
        else:
            self.draw_text("失 败", self.font_title, COLORS['red'], SCREEN_WIDTH // 2, 200, center=True)
            self.draw_text("你倒在了战场上...", self.font_large, COLORS['gray'], SCREEN_WIDTH // 2, 300, center=True)

            self.draw_button("重新开始", SCREEN_WIDTH // 2 - 100, 550, 200, 50, COLORS['bg_medium'], COLORS['red'],
                            lambda: self.restart_game())

    def continue_adventure(self):
        """继续冒险"""
        self.story_progress += 1
        if self.story_progress >= 3:
            self.game_state = 'chapter2'
        else:
            self.game_state = 'story'
            self.current_scene = 'chapter1_continue'

    def show_help(self):
        """显示帮助"""
        self.game_state = 'help'

    def help_screen(self):
        """帮助界面"""
        bg = self.create_background((20, 20, 40), (40, 40, 80))
        self.screen.blit(bg, (0, 0))

        self.draw_text("游戏说明", self.font_title, COLORS['gold'], SCREEN_WIDTH // 2, 30, center=True)

        helps = [
            "【操作说明】",
            "- 使用鼠标点击选择选项",
            "- 不同的选择会影响剧情走向",
            "",
            "【战斗系统】",
            "- 普通攻击: 基础伤害",
            "- 技能攻击: 消耗MP，造成更高伤害",
            "- 防御: 减少受到的伤害",
            "- 物品: 使用药水恢复HP/MP",
            "",
            "【角色养成】",
            "- 战斗获得经验和金币",
            "- 升级提升角色属性",
            "- 购买装备强化战斗力",
            "",
            "【游戏目标】",
            "- 探索失落王国的秘密",
            "- 击败黑暗势力",
            "- 揭开王国的历史真相",
        ]

        y_pos = 80
        for line in helps:
            color = COLORS['gold'] if line.startswith("【") else COLORS['cream']
            self.draw_text(line, self.font_normal, color, 100, y_pos)
            y_pos += 32

        self.draw_button("返回主菜单", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 50, COLORS['bg_medium'], COLORS['blue'],
                        lambda: setattr(self, 'game_state', 'menu'))

    def continue_game(self):
        """继续游戏（示例）"""
        self.show_dialog("暂无存档，请开始新游戏！")

    def quit_game(self):
        """退出游戏"""
        self.running = False

    def restart_game(self):
        """重新开始"""
        self.game_state = 'menu'
        self.player = None
        self.story_progress = 0

    def run(self):
        """游戏主循环"""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if self.game_state == 'name_input':
                        if event.key == pygame.K_RETURN and self.name_input:
                            self.create_character("战士")  # 默认职业
                        elif event.key == pygame.K_BACKSPACE:
                            self.name_input = self.name_input[:-1]
                        else:
                            if len(self.name_input) < 12:
                                self.name_input += event.unicode

            # 根据游戏状态渲染
            if self.game_state == 'menu':
                self.main_menu()
            elif self.game_state == 'name_input':
                self.name_input_screen()
            elif self.game_state == 'intro':
                self.intro_screen()
            elif self.game_state == 'story':
                self.show_story_scene()
            elif self.game_state == 'battle':
                self.battle_screen()
            elif self.game_state == 'battle_result':
                self.battle_result_screen()
            elif self.game_state == 'item_select':
                self.show_item_selection()
            elif self.game_state == 'dialog':
                self.dialog_screen()
            elif self.game_state == 'help':
                self.help_screen()
            elif self.game_state == 'chapter2':
                self.chapter2_intro()

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

    def dialog_screen(self):
        """对话框界面"""
        bg = self.create_background((20, 20, 40), (40, 40, 80))
        self.screen.blit(bg, (0, 0))
        self.draw_dialog_box(self.current_dialog, self.dialog_speaker)

        # 点击继续
        click = pygame.mouse.get_pressed()
        if click[0]:
            self.game_state = 'menu'

    def chapter2_intro(self):
        """第二章介绍"""
        bg = self.create_background((40, 20, 60), (80, 40, 100))
        self.screen.blit(bg, (0, 0))

        self.draw_text("第二章: 王国的秘密", self.font_title, COLORS['gold'], SCREEN_WIDTH // 2, 100, center=True)

        story = [
            "击败哥布林后，你在格林村赢得了英雄的称号。",
            "但你知道，这只是更大危机的冰山一角...",
            "一位神秘的旅行者带来了消息：",
            "艾瑟尔王国的王子失踪了！",
            "国王正在召集各地的勇士，前往王都。",
            "你的下一段冒险，即将开始...",
        ]

        y_pos = 200
        for line in story:
            self.draw_text(line, self.font_normal, COLORS['cream'], SCREEN_WIDTH // 2, y_pos, center=True)
            y_pos += 50

        self.draw_button("继续主线剧情", SCREEN_WIDTH // 2 - 120, 600, 240, 50, COLORS['bg_medium'], COLORS['gold'],
                        lambda: self.start_chapter2_main())

    def start_chapter2_main(self):
        """开始第二章主线"""
        self.game_state = 'ending'
        self.ending_type = 'good'

    def run(self):
        """主循环"""
        while self.running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif self.game_state == 'name_input':
                        if event.key == pygame.K_RETURN:
                            self.create_character("战士")
                        elif event.key == pygame.K_BACKSPACE:
                            self.name_input = self.name_input[:-1]
                        else:
                            if len(self.name_input) < 12 and event.unicode:
                                self.name_input += event.unicode

            # 渲染
            if self.game_state == 'menu':
                self.main_menu()
            elif self.game_state == 'name_input':
                self.name_input_screen()
            elif self.game_state == 'intro':
                self.intro_screen()
            elif self.game_state == 'story':
                self.show_story_scene()
            elif self.game_state == 'battle':
                self.battle_screen()
            elif self.game_state == 'battle_result':
                self.battle_result_screen()
            elif self.game_state == 'item_select':
                self.show_item_selection()
            elif self.game_state == 'dialog':
                self.dialog_screen()
            elif self.game_state == 'help':
                self.help_screen()
            elif self.game_state == 'chapter2':
                self.chapter2_intro()
            elif self.game_state == 'ending':
                self.ending_screen()

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()

    def ending_screen(self):
        """结局画面"""
        bg = self.create_background((20, 10, 30), (60, 30, 80))
        self.screen.blit(bg, (0, 0))

        endings = {
            'good': ("英雄的传说", "你成为了艾瑟尔王国的传奇英雄，", "王国迎来了和平与繁荣。", COLORS['gold']),
            'bad': ("悲剧的终章", "你未能阻止黑暗势力，", "王国陷入了永恒的黑暗...", COLORS['red']),
            'secret': ("隐藏结局", "你发现了王国的真正秘密...", COLORS['purple']),
        }

        title, *lines, color = endings.get(self.ending_type, endings['good'])

        self.draw_text(title, self.font_title, color, SCREEN_WIDTH // 2, 150, center=True)

        y_pos = 280
        for line in lines:
            self.draw_text(line, self.font_large, COLORS['cream'], SCREEN_WIDTH // 2, y_pos, center=True)
            y_pos += 60

        self.draw_text(f"最终等级: Lv.{self.player.level}", self.font_normal, COLORS['silver'], SCREEN_WIDTH // 2, y_pos + 50, center=True)
        self.draw_text(f"获得金币: {self.player.gold}", self.font_normal, COLORS['orange'], SCREEN_WIDTH // 2, y_pos + 90, center=True)

        self.draw_button("回到主菜单", SCREEN_WIDTH // 2 - 100, 600, 200, 50, COLORS['bg_medium'], COLORS['blue'],
                        lambda: setattr(self, 'game_state', 'menu'))

if __name__ == "__main__":
    game = Game()
    game.run()
