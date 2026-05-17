#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
地理知识问答 - Geography Quiz
一个关于世界各国地理知识的问答游戏，帮助用户学习国家、首都、货币等知识。

功能：
- 多种题型：选择题、判断题
- 多个类别：首都、国旗、货币、大洲、人口
- 即时反馈和分数统计
- 学习模式和挑战模式
- 详细的答案解释

作者：科学教育游戏集合
版本：1.0
"""

import pygame
import os
import random
import sys

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
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("地理知识问答 - Geography Quiz")

# 颜色定义
COLORS = {
    'background': (240, 248, 255),
    'primary': (70, 130, 180),
    'secondary': (100, 149, 237),
    'accent': (255, 140, 0),
    'text': (50, 50, 50),
    'white': (255, 255, 255),
    'black': (0, 0, 0),
    'gray': (128, 128, 128),
    'light_gray': (220, 220, 220),
    'green': (34, 139, 34),
    'red': (220, 20, 60),
    'blue': (30, 144, 255),
    'yellow': (255, 215, 0),
    'purple': (138, 43, 226),
    'orange': (255, 165, 0),
    'correct': (50, 205, 50),
    'wrong': (255, 69, 0),
}

# 字体设置
font_large = None
font_medium = None
font_small = None

def init_fonts():
    """初始化字体"""
    global font_large, font_medium, font_small
    font_large = get_chinese_font(48)
    font_medium = get_chinese_font(32)
    font_small = get_chinese_font(24)

init_fonts()

# 按钮类
class Button:
    """可点击的按钮类"""
    def __init__(self, x, y, width, height, text, color=COLORS['primary'], hover_color=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color if hover_color else tuple(min(c + 30, 255) for c in color)
        self.is_hovered = False
        self.enabled = True

    def draw(self, surface):
        """绘制按钮"""
        if not self.enabled:
            color = COLORS['gray']
        else:
            color = self.hover_color if self.is_hovered else self.color

        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, COLORS['black'], self.rect, 2, border_radius=10)

        text_surf = font_small.render(self.text, True, COLORS['white'])
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        """检查鼠标是否悬停"""
        if self.enabled:
            self.is_hovered = self.rect.collidepoint(pos)

    def is_clicked(self, pos):
        """检查按钮是否被点击"""
        return self.enabled and self.rect.collidepoint(pos)

# 答案选项类
class AnswerOption:
    """答案选项类"""
    def __init__(self, x, y, width, height, text, is_correct=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.is_correct = is_correct
        self.is_selected = False
        self.show_result = False

    def draw(self, surface):
        """绘制选项"""
        if self.show_result:
            if self.is_correct:
                color = COLORS['correct']
            elif self.is_selected:
                color = COLORS['wrong']
            else:
                color = COLORS['light_gray']
        else:
            color = COLORS['white'] if not self.is_selected else COLORS['secondary']

        pygame.draw.rect(surface, color, self.rect, border_radius=10)

        if self.show_result:
            border_color = COLORS['correct'] if self.is_correct else COLORS['wrong']
            pygame.draw.rect(surface, border_color, self.rect, 3, border_radius=10)

            # 绘制对勾或叉号
            center = self.rect.center
            if self.is_correct:
                pygame.draw.circle(surface, COLORS['correct'], center, 15)
                check_text = font_medium.render("V", True, COLORS['white'])
                check_rect = check_text.get_rect(center=center)
                surface.blit(check_text, check_rect)
            elif self.is_selected:
                pygame.draw.circle(surface, COLORS['wrong'], center, 15)
                cross_text = font_medium.render("X", True, COLORS['white'])
                cross_rect = cross_text.get_rect(center=center)
                surface.blit(cross_text, cross_rect)
        else:
            pygame.draw.rect(surface, COLORS['primary'], self.rect, 2, border_radius=10)

        # 绘制选项文字
        text_surf = font_small.render(self.text, True, COLORS['text'])
        text_rect = text_surf.get_rect(midleft=(self.rect.x + 50, self.rect.centery))
        surface.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        """检查是否被点击"""
        return self.rect.collidepoint(pos)

# 国家数据
COUNTRIES = {
    # 亚洲
    "中国": {"capital": "北京", "currency": "人民币 (CNY)", "continent": "亚洲", "population": "14亿+", "flag_color": "红色"},
    "日本": {"capital": "东京", "currency": "日元 (JPY)", "continent": "亚洲", "population": "1.26亿", "flag_color": "白色+红色"},
    "韩国": {"capital": "首尔", "currency": "韩元 (KRW)", "continent": "亚洲", "population": "5180万", "flag_color": "白色+红蓝"},
    "印度": {"capital": "新德里", "currency": "卢比 (INR)", "continent": "亚洲", "population": "14亿+", "flag_color": "橙白绿+蓝轮"},
    "泰国": {"capital": "曼谷", "currency": "泰铢 (THB)", "continent": "亚洲", "population": "7000万", "flag_color": "红白蓝白红"},
    "越南": {"capital": "河内", "currency": "越南盾 (VND)", "continent": "亚洲", "population": "9800万", "flag_color": "红色+五角星"},
    "新加坡": {"capital": "新加坡", "currency": "新加坡元 (SGD)", "continent": "亚洲", "population": "590万", "flag_color": "红白"},
    "马来西亚": {"capital": "吉隆坡", "currency": "林吉特 (MYR)", "continent": "亚洲", "population": "3300万", "flag_color": "红白14条"},
    "印度尼西亚": {"capital": "雅加达", "currency": "印尼盾 (IDR)", "continent": "亚洲", "population": "2.7亿", "flag_color": "红白"},
    "菲律宾": {"capital": "马尼拉", "currency": "比索 (PHP)", "continent": "亚洲", "population": "1.1亿", "flag_color": "蓝红黄白三角"},
    "土耳其": {"capital": "安卡拉", "currency": "里拉 (TRY)", "continent": "亚洲/欧洲", "population": "8500万", "flag_color": "红白+新月"},

    # 欧洲
    "英国": {"capital": "伦敦", "currency": "英镑 (GBP)", "continent": "欧洲", "population": "6700万", "flag_color": "蓝白红"},
    "法国": {"capital": "巴黎", "currency": "欧元 (EUR)", "continent": "欧洲", "population": "6700万", "flag_color": "蓝白红"},
    "德国": {"capital": "柏林", "currency": "欧元 (EUR)", "continent": "欧洲", "population": "8300万", "flag_color": "黑红金"},
    "意大利": {"capital": "罗马", "currency": "欧元 (EUR)", "continent": "欧洲", "population": "6000万", "flag_color": "绿白红"},
    "西班牙": {"capital": "马德里", "currency": "欧元 (EUR)", "continent": "欧洲", "population": "4700万", "flag_color": "红黄红"},
    "葡萄牙": {"capital": "里斯本", "currency": "欧元 (EUR)", "continent": "欧洲", "population": "1000万", "flag_color": "绿红+徽章"},
    "荷兰": {"capital": "阿姆斯特丹", "currency": "欧元 (EUR)", "continent": "欧洲", "population": "1750万", "flag_color": "红白蓝"},
    "比利时": {"capital": "布鲁塞尔", "currency": "欧元 (EUR)", "continent": "欧洲", "population": "1150万", "flag_color": "黑黄红"},
    "瑞士": {"capital": "伯尔尼", "currency": "瑞士法郎 (CHF)", "continent": "欧洲", "population": "870万", "flag_color": "红白十字"},
    "奥地利": {"capital": "维也纳", "currency": "欧元 (EUR)", "continent": "欧洲", "population": "900万", "flag_color": "红白红"},
    "瑞典": {"capital": "斯德哥尔摩", "currency": "瑞典克朗 (SEK)", "continent": "欧洲", "population": "1040万", "flag_color": "蓝黄十字"},
    "挪威": {"capital": "奥斯陆", "currency": "挪威克朗 (NOK)", "continent": "欧洲", "population": "540万", "flag_color": "红白蓝十字"},
    "丹麦": {"capital": "哥本哈根", "currency": "丹麦克朗 (DKK)", "continent": "欧洲", "population": "580万", "flag_color": "红白十字"},
    "芬兰": {"capital": "赫尔辛基", "currency": "欧元 (EUR)", "continent": "欧洲", "population": "550万", "flag_color": "白蓝十字"},
    "波兰": {"capital": "华沙", "currency": "兹罗提 (PLN)", "continent": "欧洲", "population": "3800万", "flag_color": "白红"},
    "俄罗斯": {"capital": "莫斯科", "currency": "卢布 (RUB)", "continent": "欧洲/亚洲", "population": "1.44亿", "flag_color": "白蓝红"},
    "希腊": {"capital": "雅典", "currency": "欧元 (EUR)", "continent": "欧洲", "population": "1070万", "flag_color": "蓝白+十字"},

    # 美洲
    "美国": {"capital": "华盛顿", "currency": "美元 (USD)", "continent": "北美洲", "population": "3.3亿", "flag_color": "红白蓝星条"},
    "加拿大": {"capital": "渥太华", "currency": "加元 (CAD)", "continent": "北美洲", "population": "3800万", "flag_color": "红白红+枫叶"},
    "墨西哥": {"capital": "墨西哥城", "currency": "比索 (MXN)", "continent": "北美洲", "population": "1.3亿", "flag_color": "绿白红+鹰"},
    "巴西": {"capital": "巴西利亚", "currency": "雷亚尔 (BRL)", "continent": "南美洲", "population": "2.15亿", "flag_color": "绿黄蓝球"},
    "阿根廷": {"capital": "布宜诺斯艾利斯", "currency": "比索 (ARS)", "continent": "南美洲", "population": "4500万", "flag_color": "浅蓝白浅蓝+太阳"},
    "智利": {"capital": "圣地亚哥", "currency": "比索 (CLP)", "continent": "南美洲", "population": "1900万", "flag_color": "白红蓝+星"},
    "秘鲁": {"capital": "利马", "currency": "索尔 (PEN)", "continent": "南美洲", "population": "3300万", "flag_color": "红白红+国徽"},
    "哥伦比亚": {"capital": "波哥大", "currency": "比索 (COP)", "continent": "南美洲", "population": "5100万", "flag_color": "黄蓝红"},

    # 非洲
    "埃及": {"capital": "开罗", "currency": "埃镑 (EGP)", "continent": "非洲", "population": "1.04亿", "flag_color": "红白黑+鹰"},
    "南非": {"capital": "比勒陀利亚", "currency": "兰特 (ZAR)", "continent": "非洲", "population": "6000万", "flag_color": "六色+Y"},
    "尼日利亚": {"capital": "阿布贾", "currency": "奈拉 (NGN)", "continent": "非洲", "population": "2.2亿", "flag_color": "绿白绿"},
    "肯尼亚": {"capital": "内罗毕", "currency": "肯尼亚先令 (KES)", "continent": "非洲", "population": "5500万", "flag_color": "黑红绿+盾"},
    "摩洛哥": {"capital": "拉巴特", "currency": "迪拉姆 (MAD)", "continent": "非洲", "population": "3700万", "flag_color": "红+绿星"},

    # 大洋洲
    "澳大利亚": {"capital": "堪培拉", "currency": "澳元 (AUD)", "continent": "大洋洲", "population": "2600万", "flag_color": "蓝白+联邦星"},
    "新西兰": {"capital": "惠灵顿", "currency": "新西兰元 (NZD)", "continent": "大洋洲", "population": "510万", "flag_color": "蓝白+南十字"},
}

# 问题类型
QUESTION_TYPES = [
    ("首都", "capital"),
    ("货币", "currency"),
    ("大洲", "continent"),
    ("人口", "population"),
    ("国旗特点", "flag_color"),
]

class GeographyQuiz:
    """地理知识问答游戏"""

    def __init__(self):
        self.running = True
        self.clock = pygame.time.Clock()
        self.mode = "menu"  # menu, category, quiz, result, learn

        # 游戏状态
        self.score = 0
        self.total_questions = 10
        self.current_question = 0
        self.current_question_data = None
        self.answer_options = []
        self.answered = False
        self.correct_answer = None

        # 分类选择
        self.selected_category = None

        # 学习模式
        self.learn_index = 0
        self.learn_countries = list(COUNTRIES.keys())

        # 统计
        self.correct_count = 0
        self.wrong_count = 0
        self.streak = 0
        self.best_streak = 0

        # 创建按钮
        self.create_buttons()

    def create_buttons(self):
        """创建按钮"""
        # 主菜单按钮
        button_width = 300
        button_height = 60
        start_x = (SCREEN_WIDTH - button_width) // 2

        self.menu_buttons = [
            Button(start_x, 180, button_width, button_height, "开始答题挑战", COLORS['primary']),
            Button(start_x, 260, button_width, button_height, "选择分类学习", COLORS['green']),
            Button(start_x, 340, button_width, button_height, "浏览所有国家", COLORS['purple']),
            Button(start_x, 420, button_width, button_height, "退出", COLORS['gray']),
        ]

        # 分类按钮
        self.category_buttons = []
        categories = [
            ("首都问答", COLORS['blue']),
            ("货币问答", COLORS['green']),
            ("大洲问答", COLORS['purple']),
            ("人口问答", COLORS['orange']),
            ("国旗特点问答", COLORS['red']),
            ("综合问答", COLORS['accent']),
        ]

        for i, (name, color) in enumerate(categories):
            x = 100 + (i % 3) * 300
            y = 150 + (i // 3) * 120
            self.category_buttons.append(Button(x, y, 250, 80, name, color))

        # 返回按钮
        self.back_button = Button(20, 20, 100, 40, "返回", COLORS['gray'])

        # 下一题按钮
        self.next_button = Button(SCREEN_WIDTH // 2 - 75, 500, 150, 50, "下一题", COLORS['accent'])

        # 学习模式按钮
        self.prev_country = Button(100, 500, 120, 50, "上一个", COLORS['blue'])
        self.next_country = Button(SCREEN_WIDTH - 220, 500, 120, 50, "下一个", COLORS['green'])

    def generate_question(self):
        """生成问题"""
        if self.selected_category and self.selected_category != "综合":
            question_type = self.selected_category
        else:
            # 随机选择问题类型
            question_type = random.choice(QUESTION_TYPES)[1]

        # 选择一个国家作为问题主体
        country = random.choice(list(COUNTRIES.keys()))
        country_data = COUNTRIES[country]

        # 根据问题类型生成问题
        if question_type == "capital":
            question = f"{country}的首都是哪里？"
            correct_answer = country_data["capital"]
            options = self.generate_options(correct_answer, "capital")
        elif question_type == "currency":
            question = f"{country}使用什么货币？"
            correct_answer = country_data["currency"]
            options = self.generate_options(correct_answer, "currency")
        elif question_type == "continent":
            question = f"{country}位于哪个大洲？"
            correct_answer = country_data["continent"]
            options = self.generate_options(correct_answer, "continent")
        elif question_type == "population":
            question = f"{country}大约有多少人口？"
            correct_answer = country_data["population"]
            options = self.generate_options(correct_answer, "population")
        elif question_type == "flag_color":
            question = f"{country}国旗的主要特点是什么？"
            correct_answer = country_data["flag_color"]
            options = self.generate_options(correct_answer, "flag_color")

        # 创建答案选项
        self.answer_options = []
        y_positions = [180, 260, 340, 420]

        for i, (text, is_correct) in enumerate(options):
            option = AnswerOption(100, y_positions[i], SCREEN_WIDTH - 200, 60, text, is_correct)
            self.answer_options.append(option)

        self.current_question_data = {
            "country": country,
            "question": question,
            "correct_answer": correct_answer,
            "type": question_type,
        }

    def generate_options(self, correct_answer, question_type):
        """生成选项"""
        options = [(correct_answer, True)]

        # 根据问题类型获取不同的答案池
        all_countries = list(COUNTRIES.keys())

        if question_type == "capital":
            answer_pool = set(COUNTRIES[c]["capital"] for c in all_countries)
        elif question_type == "currency":
            answer_pool = set(COUNTRIES[c]["currency"] for c in all_countries)
        elif question_type == "continent":
            answer_pool = set(COUNTRIES[c]["continent"] for c in all_countries)
        elif question_type == "population":
            answer_pool = set(COUNTRIES[c]["population"] for c in all_countries)
        elif question_type == "flag_color":
            answer_pool = set(COUNTRIES[c]["flag_color"] for c in all_countries)
        else:
            answer_pool = set()

        # 移除正确答案
        answer_pool.discard(correct_answer)
        answer_pool = list(answer_pool)
        random.shuffle(answer_pool)

        # 添加干扰选项
        for _ in range(3):
            if answer_pool:
                options.append((answer_pool.pop(), False))

        # 随机打乱选项顺序
        random.shuffle(options)

        return options

    def draw_menu(self):
        """绘制主菜单"""
        # 标题
        title = font_large.render("地理知识问答", True, COLORS['primary'])
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 80))
        screen.blit(title, title_rect)

        # 副标题
        subtitle = font_medium.render("学习世界各国地理知识", True, COLORS['gray'])
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 120))
        screen.blit(subtitle, subtitle_rect)

        # 绘制装饰地球
        self.draw_decorative_globe()

        # 绘制按钮
        for button in self.menu_buttons:
            button.draw(screen)

        # 统计信息
        if self.best_streak > 0:
            stats = font_small.render(f"最高连胜: {self.best_streak}", True, COLORS['accent'])
            screen.blit(stats, (SCREEN_WIDTH // 2 - 60, 550))

    def draw_decorative_globe(self):
        """绘制装饰性地球"""
        center_x = SCREEN_WIDTH - 150
        center_y = 150
        radius = 60

        # 绘制圆形背景
        pygame.draw.circle(screen, COLORS['blue'], (center_x, center_y), radius)
        pygame.draw.circle(screen, COLORS['green'], (center_x, center_y), radius * 0.7)

        # 绘制经纬线
        pygame.draw.circle(screen, COLORS['white'], (center_x, center_y), radius, 2)
        pygame.draw.ellipse(screen, COLORS['white'],
                           (center_x - radius, center_y - radius // 2, radius * 2, radius), 1)
        pygame.draw.line(screen, COLORS['white'], (center_x, center_y - radius),
                        (center_x, center_y + radius), 1)
        pygame.draw.line(screen, COLORS['white'], (center_x - radius, center_y),
                        (center_x + radius, center_y), 1)

    def draw_category_select(self):
        """绘制分类选择界面"""
        title = font_large.render("选择答题分类", True, COLORS['primary'])
        screen.blit(title, (SCREEN_WIDTH // 2 - 150, 60))

        subtitle = font_small.render("选择一个主题开始学习", True, COLORS['gray'])
        screen.blit(subtitle, (SCREEN_WIDTH // 2 - 100, 100))

        # 绘制分类按钮
        for button in self.category_buttons:
            button.draw(screen)

        self.back_button.draw(screen)

    def draw_quiz(self):
        """绘制问答界面"""
        # 返回按钮
        self.back_button.draw(screen)

        # 进度
        progress = f"第 {self.current_question + 1} / {self.total_questions} 题"
        progress_text = font_medium.render(progress, True, COLORS['primary'])
        screen.blit(progress_text, (SCREEN_WIDTH // 2 - 60, 70))

        # 分数
        score_text = font_small.render(f"得分: {self.score}", True, COLORS['green'])
        screen.blit(score_text, (20, 70))

        # 连胜
        if self.streak > 0:
            streak_text = font_small.render(f"连胜: {self.streak}", True, COLORS['accent'])
            screen.blit(streak_text, (20, 100))

        # 问题
        question = self.current_question_data["question"]
        question_text = font_large.render(question, True, COLORS['text'])
        question_rect = question_text.get_rect(center=(SCREEN_WIDTH // 2, 140))
        screen.blit(question_text, question_rect)

        # 国家名称高亮显示
        country = self.current_question_data["country"]
        hint = font_small.render(f"提示: 这是一个{self.current_question_data['type']}问题", True, COLORS['gray'])
        screen.blit(hint, (SCREEN_WIDTH // 2 - 100, 520))

        # 绘制答案选项
        for option in self.answer_options:
            option.draw(screen)

        # 下一题按钮（答题后显示）
        if self.answered:
            self.next_button.draw(screen)

            # 显示正确答案解释
            if self.answer_options:
                correct_opt = [o for o in self.answer_options if o.is_correct]
                if correct_opt:
                    explanation = f"正确答案是: {correct_opt[0].text}"
                    exp_text = font_small.render(explanation, True, COLORS['green'])
                    screen.blit(exp_text, (100, 560))

    def draw_result(self):
        """绘制结果界面"""
        # 标题
        title = font_large.render("答题结果", True, COLORS['primary'])
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        screen.blit(title, title_rect)

        # 分数
        score_text = font_large.render(f"最终得分: {self.score}", True, COLORS['green'])
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 180))
        screen.blit(score_text, score_rect)

        # 统计
        stats = [
            f"正确: {self.correct_count} 题",
            f"错误: {self.wrong_count} 题",
            f"正确率: {self.correct_count * 100 // self.total_questions}%",
            f"最高连胜: {self.best_streak}",
        ]

        for i, stat in enumerate(stats):
            stat_text = font_medium.render(stat, True, COLORS['text'])
            screen.blit(stat_text, (SCREEN_WIDTH // 2 - 80, 240 + i * 50))

        # 评价
        if self.correct_count >= self.total_questions * 0.8:
            rating = "太棒了！你是地理达人！"
            rating_color = COLORS['green']
        elif self.correct_count >= self.total_questions * 0.5:
            rating = "不错！继续努力！"
            rating_color = COLORS['blue']
        else:
            rating = "加油！多学习地理知识！"
            rating_color = COLORS['orange']

        rating_text = font_medium.render(rating, True, rating_color)
        rating_rect = rating_text.get_rect(center=(SCREEN_WIDTH // 2, 480))
        screen.blit(rating_text, rating_rect)

        # 按钮
        again_button = Button(SCREEN_WIDTH // 2 - 250, 540, 150, 50, "再来一次", COLORS['primary'])
        menu_button = Button(SCREEN_WIDTH // 2 + 100, 540, 150, 50, "返回菜单", COLORS['gray'])

        again_button.draw(screen)
        menu_button.draw(screen)

        # 检查按钮点击
        if again_button.is_clicked(pygame.mouse.get_pos()):
            self.start_quiz()
        if menu_button.is_clicked(pygame.mouse.get_pos()):
            self.mode = "menu"
            self.reset_stats()

    def draw_learn_mode(self):
        """绘制学习模式界面"""
        # 返回按钮
        self.back_button.draw(screen)

        # 标题
        title = font_large.render("浏览所有国家", True, COLORS['primary'])
        screen.blit(title, (SCREEN_WIDTH // 2 - 100, 60))

        # 导航信息
        nav_text = font_small.render(f"{self.learn_index + 1} / {len(self.learn_countries)}", True, COLORS['gray'])
        screen.blit(nav_text, (SCREEN_WIDTH // 2 - 20, 100))

        # 获取当前国家
        country_name = self.learn_countries[self.learn_index]
        country_data = COUNTRIES[country_name]

        # 国家名称
        name_text = font_large.render(country_name, True, COLORS['primary'])
        name_rect = name_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        screen.blit(name_text, name_rect)

        # 国家信息面板
        panel_rect = pygame.Rect(200, 180, SCREEN_WIDTH - 400, 280)
        pygame.draw.rect(screen, COLORS['white'], panel_rect, border_radius=15)
        pygame.draw.rect(screen, COLORS['primary'], panel_rect, 3, border_radius=15)

        # 绘制信息
        info_items = [
            ("首都", country_data["capital"]),
            ("货币", country_data["currency"]),
            ("大洲", country_data["continent"]),
            ("人口", country_data["population"]),
            ("国旗特点", country_data["flag_color"]),
        ]

        for i, (label, value) in enumerate(info_items):
            y = 200 + i * 50

            # 标签
            label_text = font_medium.render(f"{label}:", True, COLORS['primary'])
            screen.blit(label_text, (240, y))

            # 值
            value_text = font_medium.render(str(value), True, COLORS['text'])
            screen.blit(value_text, (420, y))

        # 导航按钮
        self.prev_country.draw(screen)
        self.next_country.draw(screen)

        # 提示
        hint = font_small.render("使用左右箭头键或点击按钮浏览", True, COLORS['gray'])
        screen.blit(hint, (SCREEN_WIDTH // 2 - 130, 560))

    def start_quiz(self):
        """开始答题"""
        self.mode = "quiz"
        self.current_question = 0
        self.score = 0
        self.correct_count = 0
        self.wrong_count = 0
        self.streak = 0
        self.generate_question()

    def next_question(self):
        """下一题"""
        self.current_question += 1

        if self.current_question >= self.total_questions:
            self.mode = "result"
            if self.streak > self.best_streak:
                self.best_streak = self.streak
        else:
            self.answered = False
            self.generate_question()

    def check_answer(self, selected_option):
        """检查答案"""
        if self.answered:
            return

        self.answered = True

        # 显示结果
        for option in self.answer_options:
            option.is_selected = (option == selected_option)
            option.show_result = True

        # 更新分数和统计
        if selected_option.is_correct:
            self.score += 10
            self.correct_count += 1
            self.streak += 1
            if self.streak > self.best_streak:
                self.best_streak = self.streak
        else:
            self.wrong_count += 1
            self.streak = 0

    def reset_stats(self):
        """重置统计"""
        self.score = 0
        self.correct_count = 0
        self.wrong_count = 0
        self.streak = 0
        self.current_question = 0

    def draw(self):
        """绘制游戏画面"""
        # 清屏
        screen.fill(COLORS['background'])

        if self.mode == "menu":
            self.draw_menu()
        elif self.mode == "category":
            self.draw_category_select()
        elif self.mode == "quiz":
            self.draw_quiz()
        elif self.mode == "result":
            self.draw_result()
        elif self.mode == "learn":
            self.draw_learn_mode()

        pygame.display.flip()

    def handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.MOUSEMOTION:
                # 更新按钮悬停状态
                if self.mode == "menu":
                    for button in self.menu_buttons:
                        button.check_hover(event.pos)
                elif self.mode == "category":
                    for button in self.category_buttons:
                        button.check_hover(event.pos)
                    self.back_button.check_hover(event.pos)
                elif self.mode == "quiz":
                    self.back_button.check_hover(event.pos)
                    if self.answered:
                        self.next_button.check_hover(event.pos)
                    for option in self.answer_options:
                        option.is_hovered = option.rect.collidepoint(event.pos)
                elif self.mode == "learn":
                    self.back_button.check_hover(event.pos)
                    self.prev_country.check_hover(event.pos)
                    self.next_country.check_hover(event.pos)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.mode == "menu":
                    if self.menu_buttons[0].is_clicked(event.pos):
                        self.selected_category = "综合"
                        self.start_quiz()
                    elif self.menu_buttons[1].is_clicked(event.pos):
                        self.mode = "category"
                    elif self.menu_buttons[2].is_clicked(event.pos):
                        self.mode = "learn"
                        self.learn_index = 0
                        self.learn_countries = list(COUNTRIES.keys())
                        random.shuffle(self.learn_countries)
                    elif self.menu_buttons[3].is_clicked(event.pos):
                        self.running = False

                elif self.mode == "category":
                    if self.back_button.is_clicked(event.pos):
                        self.mode = "menu"
                    for i, button in enumerate(self.category_buttons):
                        if button.is_clicked(event.pos):
                            self.selected_category = QUESTION_TYPES[i][1] if i < len(QUESTION_TYPES) else "综合"
                            self.start_quiz()

                elif self.mode == "quiz":
                    if self.back_button.is_clicked(event.pos):
                        self.mode = "menu"
                        self.reset_stats()
                    elif self.answered and self.next_button.is_clicked(event.pos):
                        self.next_question()
                    else:
                        # 检查答案选项
                        for option in self.answer_options:
                            if option.is_clicked(event.pos):
                                self.check_answer(option)

                elif self.mode == "learn":
                    if self.back_button.is_clicked(event.pos):
                        self.mode = "menu"
                    elif self.prev_country.is_clicked(event.pos):
                        self.learn_index = (self.learn_index - 1) % len(self.learn_countries)
                    elif self.next_country.is_clicked(event.pos):
                        self.learn_index = (self.learn_index + 1) % len(self.learn_countries)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.mode == "menu":
                        self.running = False
                    else:
                        self.mode = "menu"
                        if self.mode != "learn":
                            self.reset_stats()
                elif self.mode == "learn":
                    if event.key == pygame.K_LEFT:
                        self.learn_index = (self.learn_index - 1) % len(self.learn_countries)
                    elif event.key == pygame.K_RIGHT:
                        self.learn_index = (self.learn_index + 1) % len(self.learn_countries)

    def run(self):
        """运行游戏"""
        while self.running:
            self.handle_events()
            self.draw()
            self.clock.tick(60)

        pygame.quit()

# 主函数
def main():
    """主函数"""
    game = GeographyQuiz()
    game.run()

if __name__ == "__main__":
    main()
