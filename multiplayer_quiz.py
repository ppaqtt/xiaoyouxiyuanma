#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多人知识竞赛游戏 (Multiplayer Quiz Game)
支持2-4人轮流答题，竞争答题

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

# 玩家颜色列表
PLAYER_COLORS = [RED, BLUE, GREEN, PURPLE]
PLAYER_NAMES = ["玩家 1", "玩家 2", "玩家 3", "玩家 4"]

# 知识竞赛题目库
QUIZ_QUESTIONS = {
    "常识": [
        {"q": "中国的首都是？", "options": ["北京", "上海", "广州", "深圳"], "answer": 0},
        {"q": "一年有几个季节？", "options": ["2个", "3个", "4个", "5个"], "answer": 2},
        {"q": "太阳从哪边升起？", "options": ["西边", "南边", "东边", "北边"], "answer": 2},
        {"q": "水在什么温度会结冰？", "options": ["0°C", "10°C", "-10°C", "100°C"], "answer": 0},
        {"q": "人体最大的器官是？", "options": ["心脏", "肝脏", "皮肤", "大脑"], "answer": 2},
        {"q": "地球是什么形状？", "options": ["方形", "圆形", "球形", "三角形"], "answer": 2},
        {"q": "一个星期有几天？", "options": ["5天", "6天", "7天", "8天"], "answer": 2},
        {"q": "中国最高的山是？", "options": ["华山", "黄山", "泰山", "珠穆朗玛峰"], "answer": 3},
        {"q": "一天有多少小时？", "options": ["12小时", "20小时", "24小时", "36小时"], "answer": 2},
        {"q": "彩虹有几种颜色？", "options": ["5种", "6种", "7种", "8种"], "answer": 2},
    ],
    "动物": [
        {"q": "什么动物被称为'森林之王'？", "options": ["老虎", "狮子", "大象", "熊"], "answer": 1},
        {"q": "兔子喜欢吃什么？", "options": ["肉", "鱼", "胡萝卜", "面包"], "answer": 2},
        {"q": "什么动物会下蛋？", "options": ["狗", "猫", "鸟", "兔子"], "answer": 2},
        {"q": "企鹅生活在什么地方？", "options": ["热带", "沙漠", "南极", "森林"], "answer": 2},
        {"q": "什么动物跑得最快？", "options": ["狮子", "猎豹", "马", "兔子"], "answer": 1},
        {"q": "鱼用什么呼吸？", "options": ["肺", "腮", "皮肤", "鼻子"], "answer": 1},
        {"q": "什么动物是'人类最好的朋友'？", "options": ["猫", "鸟", "狗", "鱼"], "answer": 2},
        {"q": "熊猫最喜欢吃什么？", "options": ["鱼", "肉", "竹子", "苹果"], "answer": 2},
        {"q": "变色龙会改变什么？", "options": ["形状", "大小", "颜色", "重量"], "answer": 2},
        {"q": "什么动物有8条腿？", "options": ["蚂蚁", "蜜蜂", "蜘蛛", "蜈蚣"], "answer": 2},
    ],
    "水果": [
        {"q": "什么水果是黄色的弯曲形状？", "options": ["苹果", "香蕉", "葡萄", "橙子"], "answer": 1},
        {"q": "什么水果表皮是红色的？", "options": ["香蕉", "苹果", "梨", "柚子"], "answer": 1},
        {"q": "葡萄长在什么上面？", "options": ["树上", "藤上", "地上", "灌木上"], "answer": 1},
        {"q": "什么水果切开是星星形状？", "options": ["苹果", "梨", "杨桃", "橙子"], "answer": 2},
        {"q": "西瓜是什么颜色的果肉？", "options": ["白色", "黄色", "红色", "绿色"], "answer": 2},
        {"q": "什么水果表面有很多小孔？", "options": ["苹果", "梨", "猕猴桃", "橙子"], "answer": 2},
        {"q": "榴莲被称为什么？", "options": ["水果之王", "水果之后", "水果王子", "水果公主"], "answer": 0},
        {"q": "柠檬是什么味道？", "options": ["甜的", "咸的", "酸的", "苦的"], "answer": 2},
        {"q": "草莓表面有什么？", "options": ["毛", "刺", "种子", "羽毛"], "answer": 2},
        {"q": "什么水果可以做成葡萄干？", "options": ["苹果", "梨", "葡萄", "香蕉"], "answer": 2},
    ],
    "数学": [
        {"q": "1 + 1 = ?", "options": ["1", "2", "3", "4"], "answer": 1},
        {"q": "2 × 3 = ?", "options": ["5", "6", "8", "9"], "answer": 1},
        {"q": "10 - 4 = ?", "options": ["4", "5", "6", "7"], "answer": 2},
        {"q": "15 ÷ 3 = ?", "options": ["3", "4", "5", "6"], "answer": 2},
        {"q": "正方形有几条边？", "options": ["3条", "4条", "5条", "6条"], "answer": 1},
        {"q": "三角形有几个角？", "options": ["2个", "3个", "4个", "5个"], "answer": 1},
        {"q": "圆形有几条边？", "options": ["0条", "1条", "2条", "无数条"], "answer": 3},
        {"q": "5 > 3 + ?", "options": ["1", "2", "3", "4"], "answer": 1},
        {"q": "0 ~ 9 中有几个数字？", "options": ["8个", "9个", "10个", "11个"], "answer": 2},
        {"q": "100比50多多少？", "options": ["30", "40", "50", "60"], "answer": 2},
    ],
    "地理": [
        {"q": "世界上最大的海洋是？", "options": ["大西洋", "印度洋", "北冰洋", "太平洋"], "answer": 3},
        {"q": "日本的首都是？", "options": ["大阪", "东京", "京都", "横滨"], "answer": 1},
        {"q": "法国的标志性建筑是？", "options": ["大本钟", "埃菲尔铁塔", "自由女神像", "悉尼歌剧院"], "answer": 1},
        {"q": "澳大利亚的动物代表是？", "options": ["大熊猫", "袋鼠", "北极熊", "老虎"], "answer": 1},
        {"q": "世界上最长的河是？", "options": ["亚马逊河", "长江", "尼罗河", "密西西比河"], "answer": 2},
        {"q": "韩国的首都是？", "options": ["釜山", "首尔", "仁川", "大邱"], "answer": 1},
        {"q": "印度位于哪个洲？", "options": ["欧洲", "非洲", "亚洲", "美洲"], "answer": 2},
        {"q": "新加坡的别称是？", "options": ["狮城", "花园城市", "鱼尾狮城", "以上都是"], "answer": 3},
        {"q": "非洲最高的山是？", "options": ["乞力马扎罗山", "富士山", "阿尔卑斯山", "喜马拉雅山"], "answer": 0},
        {"q": "北极在哪里？", "options": ["陆地", "海洋", "南边", "山顶"], "answer": 1},
    ]
}


class QuizGame:
    """多人知识竞赛游戏主类"""

    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("多人知识竞赛")
        self.clock = pygame.time.Clock()
        self.font_large = get_chinese_font(72)
        self.font_medium = get_chinese_font(48)
        self.font_small = get_chinese_font(36)
        self.font_tiny = get_chinese_font(28)

        # 游戏状态
        self.game_state = "menu"  # menu, playing, result
        self.num_players = 2
        self.current_player = 0
        self.question = None
        self.question_category = ""
        self.questions_answered = 0
        self.max_questions = 10
        self.time_left = 15  # 每题答题时间
        self.timer_event = pygame.USEREVENT + 1
        self.answer_feedback = None
        self.feedback_timer = 0

        # 玩家数据
        self.players = []
        self.init_players()

        # 动画变量
        self.anim_timer = 0
        self.question_displayed = False
        self.category_change_anim = 0

    def init_players(self):
        """初始化玩家数据"""
        self.players = []
        for i in range(self.num_players):
            self.players.append({
                "name": PLAYER_NAMES[i],
                "color": PLAYER_COLORS[i],
                "score": 0,
                "correct": 0,
                "wrong": 0,
                "streak": 0,
                "best_streak": 0
            })

    def draw_text(self, text, font, color, center=None, pos=None):
        """绘制文本的辅助函数"""
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
        pygame.draw.rect(self.screen, WHITE, rect, 3, border_radius=10)
        text_rect = font.render(text, True, text_color).get_rect(center=rect.center)
        self.screen.blit(font.render(text, True, text_color), text_rect)

    def draw_player_info(self, x, y, player, is_current, score_anim=0):
        """绘制玩家信息面板"""
        panel_width = 250
        panel_height = 120

        # 面板背景
        bg_color = player["color"] if is_current else GRAY
        if is_current:
            # 当前玩家高亮效果
            pygame.draw.rect(self.screen, player["color"], (x-5, y-5, panel_width+10, panel_height+10), border_radius=15)
            pygame.draw.rect(self.screen, WHITE, (x-5, y-5, panel_width+10, panel_height+10), 3, border_radius=15)

        pygame.draw.rect(self.screen, DARK_GRAY, (x, y, panel_width, panel_height), border_radius=10)

        # 玩家名称
        name_text = self.font_small.render(player["name"], True, WHITE)
        self.screen.blit(name_text, (x + 15, y + 15))

        # 分数（带动画效果）
        score_color = YELLOW if is_current else WHITE
        score_text = self.font_medium.render(f"{player['score']} 分", True, score_color)
        self.screen.blit(score_text, (x + 15, y + 45))

        # 连胜和统计
        stats_text = self.font_tiny.render(
            f"正确:{player['correct']} 错误:{player['wrong']} 连胜:{player['streak']}",
            True, LIGHT_GRAY)
        self.screen.blit(stats_text, (x + 15, y + 90))

        # 当前玩家指示器
        if is_current:
            indicator = self.font_tiny.render("<<< 当前", True, GREEN)
            self.screen.blit(indicator, (x + panel_width - 80, y + 15))

    def draw_category_bar(self, category):
        """绘制类别选择条"""
        bar_height = 60
        pygame.draw.rect(self.screen, DARK_GRAY, (0, SCREEN_HEIGHT - bar_height, SCREEN_WIDTH, bar_height))

        # 绘制所有类别
        categories = list(QUIZ_QUESTIONS.keys())
        bar_width = SCREEN_WIDTH // len(categories)

        for i, cat in enumerate(categories):
            rect = pygame.Rect(i * bar_width, SCREEN_HEIGHT - bar_height, bar_width, bar_height)
            if cat == category:
                pygame.draw.rect(self.screen, player["color"] if "player" in dir() else BLUE, rect)
            color = WHITE if cat == category else LIGHT_GRAY
            text = self.font_small.render(cat, True, color)
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)

    def new_question(self):
        """生成新题目"""
        # 随机选择类别
        self.question_category = random.choice(list(QUIZ_QUESTIONS.keys()))
        questions = QUIZ_QUESTIONS[self.question_category]
        self.question = random.choice(questions)
        self.question_displayed = True
        self.time_left = 15

        # 重置计时器
        pygame.time.set_timer(self.timer_event, 1000)

    def check_answer(self, selected_index):
        """检查答案并更新分数"""
        if self.question is None:
            return

        player = self.players[self.current_player]
        is_correct = selected_index == self.question["answer"]

        if is_correct:
            # 答对了！
            player["correct"] += 1
            player["streak"] += 1

            # 连胜奖励分数
            streak_bonus = min(player["streak"] * 5, 20)
            time_bonus = self.time_left * 2
            total_points = 10 + streak_bonus + time_bonus
            player["score"] += total_points

            if player["streak"] > player["best_streak"]:
                player["best_streak"] = player["streak"]

            self.answer_feedback = ("correct", f"正确! +{total_points}分")
        else:
            # 答错了
            player["wrong"] += 1
            player["streak"] = 0
            correct_answer = self.question["options"][self.question["answer"]]
            self.answer_feedback = ("wrong", f"错误! 正确答案是: {correct_answer}")

        self.feedback_timer = 90  # 显示1.5秒
        self.question_displayed = False

    def next_turn(self):
        """切换到下一个玩家"""
        self.current_player = (self.current_player + 1) % self.num_players
        self.questions_answered += 1
        self.answer_feedback = None

        if self.questions_answered >= self.max_questions:
            self.game_state = "result"
        else:
            self.new_question()

    def draw_question_screen(self):
        """绘制答题界面"""
        # 背景
        self.screen.fill(DARK_GRAY)

        # 顶部玩家信息栏
        header_height = 140
        pygame.draw.rect(self.screen, (30, 30, 30), (0, 0, SCREEN_WIDTH, header_height))

        # 绘制玩家信息
        player_width = SCREEN_WIDTH // self.num_players
        for i, player in enumerate(self.players):
            x = i * player_width + (player_width - 250) // 2
            self.draw_player_info(x, 10, player, i == self.current_player)

        # 进度条
        progress_width = (self.questions_answered / self.max_questions) * (SCREEN_WIDTH - 100)
        pygame.draw.rect(self.screen, GRAY, (50, 145, SCREEN_WIDTH - 100, 20), border_radius=10)
        pygame.draw.rect(self.screen, GREEN, (50, 145, progress_width, 20), border_radius=10)
        progress_text = self.font_tiny.render(f"进度: {self.questions_answered}/{self.max_questions}", True, WHITE)
        self.screen.blit(progress_text, (50, 148))

        # 题目区域
        question_y = 180

        # 类别标签
        category_text = self.font_medium.render(f"[ {self.question_category} ]", True, YELLOW)
        category_rect = category_text.get_rect(center=(SCREEN_WIDTH // 2, question_y + 30))
        self.screen.blit(category_text, category_rect)

        # 计时器
        timer_color = GREEN if self.time_left > 5 else (YELLOW if self.time_left > 3 else RED)
        timer_text = self.font_large.render(str(self.time_left), True, timer_color)
        timer_rect = timer_text.get_rect(center=(SCREEN_WIDTH - 80, question_y + 50))
        pygame.draw.circle(self.screen, timer_color, timer_rect.center, 45, 4)
        self.screen.blit(timer_text, timer_rect)

        # 题目卡片
        card_rect = pygame.Rect(100, question_y + 60, SCREEN_WIDTH - 200, 180)
        pygame.draw.rect(self.screen, (50, 50, 80), card_rect, border_radius=15)
        pygame.draw.rect(self.screen, PLAYER_COLORS[self.current_player], card_rect, 3, border_radius=15)

        # 题目文本
        q_text = self.font_medium.render(self.question["q"], True, WHITE)
        q_rect = q_text.get_rect(center=(SCREEN_WIDTH // 2, question_y + 130))
        self.screen.blit(q_text, q_rect)

        # 选项区域
        option_start_y = question_y + 260
        option_height = 70
        option_width = (SCREEN_WIDTH - 250) // 2

        # 4个选项布局 (2x2)
        positions = [
            (75, option_start_y),
            (75 + option_width + 50, option_start_y),
            (75, option_start_y + option_height + 20),
            (75 + option_width + 50, option_start_y + option_height + 20)
        ]

        option_buttons = []
        for i, (option_text, pos) in enumerate(zip(self.question["options"], positions)):
            rect = pygame.Rect(pos[0], pos[1], option_width, option_height)
            option_buttons.append((rect, i))

            # 选项背景
            colors = [BLUE, GREEN, PURPLE, ORANGE]
            pygame.draw.rect(self.screen, colors[i], rect, border_radius=10)
            pygame.draw.rect(self.screen, WHITE, rect, 2, border_radius=10)

            # 选项标签
            labels = ["A", "B", "C", "D"]
            label_bg = pygame.Rect(pos[0] - 5, pos[1] + 10, 40, 50)
            pygame.draw.rect(self.screen, WHITE, label_bg, border_radius=8)
            label_text = self.font_medium.render(labels[i], True, colors[i])
            self.screen.blit(label_text, label_text.get_rect(center=label_bg.center))

            # 选项文本
            text = self.font_small.render(option_text, True, WHITE)
            text_rect = text.get_rect(center=(pos[0] + option_width // 2 + 10, pos[1] + option_height // 2))
            self.screen.blit(text, text_rect)

        # 答案反馈
        if self.answer_feedback:
            feedback_type, feedback_text = self.answer_feedback
            if feedback_type == "correct":
                feedback_color = GREEN
            else:
                feedback_color = RED

            feedback_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, option_start_y + 180, 400, 60)
            pygame.draw.rect(self.screen, feedback_color, feedback_rect, border_radius=10)
            feedback_surface = self.font_medium.render(feedback_text, True, WHITE)
            self.screen.blit(feedback_surface, feedback_surface.get_rect(center=feedback_rect.center))

        return option_buttons

    def draw_result_screen(self):
        """绘制结果界面"""
        self.screen.fill(DARK_GRAY)

        # 标题
        title = self.font_large.render("游戏结束!", True, YELLOW)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)

        # 排序玩家（按分数）
        sorted_players = sorted(self.players, key=lambda x: x["score"], reverse=True)

        # 排名显示
        for i, player in enumerate(sorted_players):
            y = 200 + i * 100

            # 排名
            medals = ["🥇", "🥈", "🥉", ""]
            rank_text = self.font_large.render(f"{i + 1}", True, WHITE)
            self.screen.blit(rank_text, (200, y))

            # 玩家名称
            name_text = self.font_medium.render(player["name"], True, player["color"])
            self.screen.blit(name_text, (300, y))

            # 分数
            score_text = self.font_medium.render(f"{player['score']} 分", True, YELLOW)
            self.screen.blit(score_text, (500, y))

            # 统计
            stats_text = self.font_small.render(
                f"正确:{player['correct']} 错误:{player['wrong']} 最高连胜:{player['best_streak']}",
                True, LIGHT_GRAY)
            self.screen.blit(stats_text, (700, y))

        # 按钮
        retry_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 650, 200, 60)
        menu_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 720, 200, 50)

        mouse_pos = pygame.mouse.get_pos()
        self.draw_button(retry_rect, "再来一局", self.font_medium, GREEN, WHITE,
                        retry_rect.collidepoint(mouse_pos))
        self.draw_button(menu_rect, "返回菜单", self.font_small, BLUE, WHITE,
                        menu_rect.collidepoint(mouse_pos))

        return [("retry", retry_rect), ("menu", menu_rect)]

    def draw_menu(self):
        """绘制主菜单"""
        self.screen.fill(DARK_GRAY)

        # 标题
        title = self.font_large.render("多人知识竞赛", True, YELLOW)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)

        # 副标题
        subtitle = self.font_small.render("考验你的知识储备，和朋友们一决高下!", True, LIGHT_GRAY)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 210))
        self.screen.blit(subtitle, subtitle_rect)

        # 玩家数量选择
        player_label = self.font_medium.render("选择玩家数量:", True, WHITE)
        self.screen.blit(player_label, (SCREEN_WIDTH // 2 - 150, 300))

        # 玩家数量按钮
        buttons = []
        for i in range(2, 5):
            rect = pygame.Rect(SCREEN_WIDTH // 2 - 150 + (i - 2) * 120, 360, 100, 80)
            color = GREEN if self.num_players == i else GRAY
            pygame.draw.rect(self.screen, color, rect, border_radius=10)
            pygame.draw.rect(self.screen, WHITE, rect, 2, border_radius=10)

            num_text = self.font_large.render(str(i), True, WHITE)
            self.screen.blit(num_text, num_text.get_rect(center=(rect.centerx, rect.centery - 10)))

            label = self.font_tiny.render("人", True, WHITE)
            self.screen.blit(label, label.get_rect(center=(rect.centerx, rect.centery + 25)))

            buttons.append((i, rect))

        # 预览玩家
        preview_y = 480
        preview_label = self.font_small.render("玩家预览:", True, WHITE)
        self.screen.blit(preview_label, (SCREEN_WIDTH // 2 - 100, preview_y))

        for i in range(self.num_players):
            x = SCREEN_WIDTH // 2 - (self.num_players * 100) // 2 + i * 100 + 50
            pygame.draw.circle(self.screen, PLAYER_COLORS[i], (x, preview_y + 50), 30)
            name = self.font_tiny.render(PLAYER_NAMES[i], True, PLAYER_COLORS[i])
            self.screen.blit(name, name.get_rect(center=(x, preview_y + 95)))

        # 开始按钮
        start_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 620, 200, 70)
        mouse_pos = pygame.mouse.get_pos()
        self.draw_button(start_rect, "开始游戏", self.font_medium, GREEN, WHITE,
                        start_rect.collidepoint(mouse_pos))

        buttons.append(("start", start_rect))

        # 游戏说明
        instructions = self.font_tiny.render(
            "操作说明: 1-4键选择答案 | 鼠标点击选项 | ESC返回菜单",
            True, GRAY)
        self.screen.blit(instructions, (SCREEN_WIDTH // 2 - 250, 750))

        return buttons

    def handle_events(self, buttons):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.MOUSEBUTTONDOWN:
                for btn in buttons:
                    if isinstance(btn[0], str):
                        if btn[1].collidepoint(event.pos):
                            if btn[0] == "start":
                                self.game_state = "playing"
                                self.questions_answered = 0
                                self.current_player = 0
                                self.new_question()
                            elif btn[0] == "retry":
                                self.init_players()
                                self.game_state = "playing"
                                self.questions_answered = 0
                                self.current_player = 0
                                self.new_question()
                            elif btn[0] == "menu":
                                self.game_state = "menu"
                            return None
                    elif isinstance(btn[0], int):
                        if btn[1].collidepoint(event.pos):
                            self.num_players = btn[0]
                            self.init_players()

            if event.type == pygame.KEYDOWN:
                if self.game_state == "menu":
                    if event.key == pygame.K_1:
                        self.num_players = 2
                        self.init_players()
                    elif event.key == pygame.K_2:
                        self.num_players = 3
                        self.init_players()
                    elif event.key == pygame.K_3:
                        self.num_players = 4
                        self.init_players()
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self.game_state = "playing"
                        self.questions_answered = 0
                        self.current_player = 0
                        self.new_question()

                elif self.game_state == "playing" and self.answer_feedback is None:
                    # 键盘选择答案
                    key_map = {
                        pygame.K_1: 0,
                        pygame.K_a: 0,
                        pygame.K_2: 1,
                        pygame.K_b: 1,
                        pygame.K_3: 2,
                        pygame.K_c: 2,
                        pygame.K_4: 3,
                        pygame.K_d: 3
                    }
                    if event.key in key_map:
                        self.check_answer(key_map[event.key])

                elif event.key == pygame.K_ESCAPE:
                    if self.game_state in ["playing", "result"]:
                        self.game_state = "menu"

            if event.type == self.timer_event and self.game_state == "playing":
                if self.time_left > 0 and self.answer_feedback is None:
                    self.time_left -= 1
                elif self.time_left == 0 and self.answer_feedback is None:
                    # 超时处理
                    player = self.players[self.current_player]
                    player["wrong"] += 1
                    player["streak"] = 0
                    correct_answer = self.question["options"][self.question["answer"]]
                    self.answer_feedback = ("wrong", f"时间到! 正确答案是: {correct_answer}")
                    self.feedback_timer = 90

            if event.type == pygame.MOUSEBUTTONDOWN and self.game_state == "playing":
                # 检查是否点击了选项
                if self.answer_feedback is None and self.question:
                    option_width = (SCREEN_WIDTH - 250) // 2
                    option_start_y = 460
                    option_height = 70

                    positions = [
                        (75, option_start_y),
                        (75 + option_width + 50, option_start_y),
                        (75, option_start_y + option_height + 20),
                        (75 + option_width + 50, option_start_y + option_height + 20)
                    ]

                    for i, pos in enumerate(positions):
                        rect = pygame.Rect(pos[0], pos[1], option_width, option_height)
                        if rect.collidepoint(event.pos):
                            self.check_answer(i)
                            break

        # 处理反馈计时器
        if self.feedback_timer > 0:
            self.feedback_timer -= 1
            if self.feedback_timer == 0:
                self.next_turn()

        return None

    def run(self):
        """主游戏循环"""
        running = True

        while running:
            self.clock.tick(FPS)

            if self.game_state == "menu":
                buttons = self.draw_menu()
            elif self.game_state == "playing":
                buttons = self.draw_question_screen()
            elif self.game_state == "result":
                buttons = self.draw_result_screen()

            pygame.display.flip()

            result = self.handle_events(buttons)
            if result == "quit":
                running = False

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = QuizGame()
    game.run()
