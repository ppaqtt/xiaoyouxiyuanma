#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多人记忆挑战游戏 (Multiplayer Memory Challenge)
支持2-4人合作或对战记忆卡牌

模式:
- 合作模式: 所有玩家合作找出所有配对
- 对战模式: 玩家轮流翻开卡牌记忆,得分制

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
DARK_BLUE = (20, 20, 60)
GOLD = (255, 215, 0)

# 玩家颜色
PLAYER_COLORS = [RED, BLUE, GREEN, PURPLE]
PLAYER_NAMES = ["玩家 1", "玩家 2", "玩家 3", "玩家 4"]

# 卡牌符号 (使用emoji风格的Unicode符号)
CARD_SYMBOLS = [
    "🍎", "🍊", "🍋", "🍇", "🍓", "🍒", "🥝", "🍑",
    "🌟", "⭐", "🌙", "☀️", "🌈", "⚡", "🔥", "❄️",
    "🐶", "🐱", "🐼", "🐨", "🦁", "🐯", "🐸", "🦊",
    "🎈", "🎁", "🎀", "🎯", "🎲", "🎮", "🎸", "🎺",
    "🌸", "🌺", "🌻", "🌷", "🌹", "🍀", "🌴", "🌵",
    "🦋", "🐝", "🐞", "🦄", "🐬", "🐳", "🦩", "🦚"
]


class MemoryGame:
    """多人记忆游戏主类"""

    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("多人记忆挑战")
        self.clock = pygame.time.Clock()
        self.font_large = get_chinese_font(72)
        self.font_medium = get_chinese_font(48)
        self.font_small = get_chinese_font(36)
        self.font_tiny = get_chinese_font(28)

        # 游戏状态
        self.game_state = "menu"  # menu, mode_select, difficulty_select, playing, result
        self.game_mode = "coop"  # coop: 合作, battle: 对战
        self.num_players = 2
        self.current_player = 0
        self.difficulty = "easy"  # easy: 4x3, medium: 4x4, hard: 5x4, extreme: 6x4

        # 卡牌设置
        self.card_size = 80
        self.cards = []
        self.revealed = []  # 当前翻开的卡牌
        self.matched = []  # 已匹配的卡牌索引
        self.card_grid = (4, 3)  # 默认4x3网格

        # 游戏数据
        self.players = []
        self.round_score = 0  # 对战模式当前回合得分
        self.match_count = 0  # 合作模式配对计数
        self.turn_count = 0  # 总共翻牌次数
        self.start_time = 0
        self.elapsed_time = 0

        # 动画
        self.flip_animation = []
        self.match_anim = []
        self.score_popup = []

        # 合作模式特殊
        self.coop_attempts = 0

        self.init_players()

    def init_players(self):
        """初始化玩家数据"""
        self.players = []
        for i in range(self.num_players):
            self.players.append({
                "name": PLAYER_NAMES[i],
                "color": PLAYER_COLORS[i],
                "score": 0,
                "pairs": 0,
                "attempts": 0,
                "perfect_matches": 0
            })

    def get_difficulty_config(self):
        """根据难度获取配置"""
        configs = {
            "easy": {"cols": 4, "rows": 3, "pairs": 6},      # 12张卡
            "medium": {"cols": 4, "rows": 4, "pairs": 8},   # 16张卡
            "hard": {"cols": 5, "rows": 4, "pairs": 10},    # 20张卡
            "extreme": {"cols": 6, "rows": 4, "pairs": 12}  # 24张卡
        }
        return configs.get(self.difficulty, configs["easy"])

    def setup_cards(self):
        """设置卡牌"""
        config = self.get_difficulty_config()
        self.card_grid = (config["cols"], config["rows"])
        num_pairs = config["pairs"]

        # 计算卡牌大小和位置
        total_width = self.card_grid[0] * self.card_size + (self.card_grid[0] - 1) * 10
        total_height = self.card_grid[1] * self.card_size + (self.card_grid[1] - 1) * 10
        start_x = (SCREEN_WIDTH - total_width) // 2
        start_y = (SCREEN_HEIGHT - total_height - 100) // 2

        # 选择符号并随机分配
        selected_symbols = random.sample(CARD_SYMBOLS, num_pairs)
        card_symbols = selected_symbols * 2  # 每对两张
        random.shuffle(card_symbols)

        # 创建卡牌列表
        self.cards = []
        for idx, symbol in enumerate(card_symbols):
            row = idx // self.card_grid[0]
            col = idx % self.card_grid[0]
            x = start_x + col * (self.card_size + 10)
            y = start_y + row * (self.card_size + 10)

            self.cards.append({
                "symbol": symbol,
                "x": x,
                "y": y,
                "flipped": False,
                "matched": False,
                "flip_progress": 0
            })

        self.revealed = []
        self.matched = []
        self.match_count = 0
        self.turn_count = 0
        self.coop_attempts = 0
        self.start_time = pygame.time.get_ticks()

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

    def draw_card(self, card, index):
        """绘制单张卡牌"""
        rect = pygame.Rect(card["x"], card["y"], self.card_size, self.card_size)

        if card["matched"]:
            # 已匹配的卡牌 - 发光效果
            glow_rect = rect.inflate(8, 8)
            pygame.draw.rect(self.screen, GREEN, glow_rect, border_radius=12)
            pygame.draw.rect(self.screen, WHITE, glow_rect, 2, border_radius=12)

        if card["flipped"] or card["matched"]:
            # 翻开或已匹配 - 显示正面
            pygame.draw.rect(self.screen, WHITE, rect, border_radius=10)

            # 绘制符号
            font_size = min(48, int(self.card_size * 0.6))
            symbol_font = get_chinese_font(font_size)
            symbol_text = symbol_font.render(card["symbol"], True, BLACK)
            self.screen.blit(symbol_text, symbol_text.get_rect(center=rect.center))
        else:
            # 未翻开 - 显示背面
            pygame.draw.rect(self.screen, PURPLE, rect, border_radius=10)
            pygame.draw.rect(self.screen, WHITE, rect, 2, border_radius=10)

            # 背面装饰
            center_x = rect.centerx
            center_y = rect.centery
            for i in range(3):
                size = 15 + i * 10
                pygame.draw.circle(self.screen, WHITE, (center_x, center_y), size, 2)

        return rect

    def draw_player_panel(self):
        """绘制玩家信息面板"""
        panel_height = 80
        panel_y = SCREEN_HEIGHT - panel_height

        # 背景
        pygame.draw.rect(self.screen, DARK_GRAY, (0, panel_y, SCREEN_WIDTH, panel_height))

        if self.game_mode == "coop":
            # 合作模式 - 显示总进度
            config = self.get_difficulty_config()
            progress = self.match_count / config["pairs"]

            # 进度条
            bar_width = 400
            bar_x = (SCREEN_WIDTH - bar_width) // 2
            bar_y = panel_y + 15

            pygame.draw.rect(self.screen, GRAY, (bar_x, bar_y, bar_width, 30), border_radius=15)
            pygame.draw.rect(self.screen, GREEN, (bar_x, bar_y, int(bar_width * progress), 30), border_radius=15)

            progress_text = self.font_small.render(f"配对进度: {self.match_count}/{config['pairs']}", True, WHITE)
            self.screen.blit(progress_text, (bar_x + 10, bar_y + 3))

            # 翻牌次数
            attempts_text = self.font_tiny.render(f"翻牌次数: {self.turn_count}", True, LIGHT_GRAY)
            self.screen.blit(attempts_text, (bar_x, bar_y + 40))

        else:
            # 对战模式 - 显示当前玩家
            player = self.players[self.current_player]

            # 当前玩家高亮
            pygame.draw.rect(self.screen, player["color"],
                           (0, panel_y, SCREEN_WIDTH // self.num_players * (self.current_player + 1), panel_height))

            # 玩家信息
            player_width = SCREEN_WIDTH // self.num_players
            for i, p in enumerate(self.players):
                x = i * player_width + 20
                color = p["color"]

                # 名称和分数
                name_text = self.font_small.render(p["name"], True, WHITE)
                self.screen.blit(name_text, (x, panel_y + 10))

                score_text = self.font_medium.render(f"{p['score']}分", True, YELLOW)
                self.screen.blit(score_text, (x, panel_y + 40))

                pairs_text = self.font_tiny.render(f"配对:{p['pairs']}", True, LIGHT_GRAY)
                self.screen.blit(pairs_text, (x + 100, panel_y + 20))

                if i == self.current_player:
                    indicator = self.font_tiny.render("<<<", True, GREEN)
                    self.screen.blit(indicator, (x, panel_y + 65))

    def check_match(self):
        """检查两张卡是否匹配"""
        if len(self.revealed) != 2:
            return

        card1 = self.cards[self.revealed[0]]
        card2 = self.cards[self.revealed[1]]

        if card1["symbol"] == card2["symbol"]:
            # 匹配成功
            card1["matched"] = True
            card2["matched"] = True
            self.matched.extend(self.revealed)
            self.match_count += 1

            if self.game_mode == "coop":
                # 合作模式 - 所有玩家得分
                self.coop_attempts += 1
                base_score = 100
                time_bonus = max(0, 50 - self.turn_count % 10 * 5)
                for p in self.players:
                    p["score"] += base_score + time_bonus
                self.score_popup.append({
                    "text": f"+{base_score + time_bonus}",
                    "x": card1["x"] + self.card_size // 2,
                    "y": card1["y"],
                    "timer": 60
                })
            else:
                # 对战模式 - 当前玩家得分
                player = self.players[self.current_player]
                player["pairs"] += 1
                self.coop_attempts += 1
                base_score = 100
                streak_bonus = player["pairs"] * 10
                player["score"] += base_score + streak_bonus
                player["perfect_matches"] += 1

                self.score_popup.append({
                    "text": f"+{base_score + streak_bonus}",
                    "x": card1["x"] + self.card_size // 2,
                    "y": card1["y"],
                    "timer": 60,
                    "color": player["color"]
                })

            # 清空已翻开的卡
            self.revealed = []

            # 检查游戏是否结束
            config = self.get_difficulty_config()
            if self.match_count >= config["pairs"]:
                self.game_state = "result"

        else:
            # 不匹配
            if self.game_mode == "battle":
                player = self.players[self.current_player]
                player["attempts"] += 1

            # 翻回卡牌
            pygame.time.wait(800)  # 显示1秒
            card1["flipped"] = False
            card2["flipped"] = False
            self.revealed = []

            # 切换玩家（对战模式）
            if self.game_mode == "battle":
                self.current_player = (self.current_player + 1) % self.num_players

        self.turn_count += 1

    def draw_menu(self):
        """绘制主菜单"""
        self.screen.fill(DARK_BLUE)

        # 标题
        title = self.font_large.render("多人记忆挑战", True, YELLOW)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 120))
        self.screen.blit(title, title_rect)

        # 副标题
        subtitle = self.font_small.render("测试你的记忆力，和朋友们一决高下!", True, LIGHT_GRAY)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 180))
        self.screen.blit(subtitle, subtitle_rect)

        # 预览卡牌
        preview_y = 250
        preview_label = self.font_small.render("游戏预览:", True, WHITE)
        self.screen.blit(preview_label, (SCREEN_WIDTH // 2 - 60, preview_y))

        # 展示卡牌
        for i in range(6):
            x = SCREEN_WIDTH // 2 - 150 + i * 55
            rect = pygame.Rect(x, preview_y + 40, 45, 60)
            if i % 2 == 0:
                pygame.draw.rect(self.screen, PURPLE, rect, border_radius=8)
                pygame.draw.rect(self.screen, WHITE, rect, 2, border_radius=8)
            else:
                pygame.draw.rect(self.screen, WHITE, rect, border_radius=8)
                symbols = ["🍎", "🍊", "⭐"]
                text = self.font_tiny.render(symbols[i // 2], True, BLACK)
                self.screen.blit(text, text.get_rect(center=rect.center))

        # 玩家数量选择
        player_label = self.font_medium.render("选择玩家数量:", True, WHITE)
        self.screen.blit(player_label, (SCREEN_WIDTH // 2 - 120, 400))

        buttons = []
        for i in range(2, 5):
            rect = pygame.Rect(SCREEN_WIDTH // 2 - 150 + (i - 2) * 120, 460, 100, 80)
            color = GREEN if self.num_players == i else GRAY
            pygame.draw.rect(self.screen, color, rect, border_radius=10)
            pygame.draw.rect(self.screen, WHITE, rect, 2, border_radius=10)

            num_text = self.font_large.render(str(i), True, WHITE)
            self.screen.blit(num_text, num_text.get_rect(center=(rect.centerx, rect.centery - 10)))

            label = self.font_tiny.render("人", True, WHITE)
            self.screen.blit(label, label.get_rect(center=(rect.centerx, rect.centery + 25)))

            buttons.append(("players", i, rect))

        # 预览玩家
        preview_y = 560
        preview_label = self.font_small.render("玩家预览:", True, WHITE)
        self.screen.blit(preview_label, (SCREEN_WIDTH // 2 - 60, preview_y))

        for i in range(self.num_players):
            x = SCREEN_WIDTH // 2 - (self.num_players * 100) // 2 + i * 100 + 50
            pygame.draw.circle(self.screen, PLAYER_COLORS[i], (x, preview_y + 50), 30)
            name = self.font_tiny.render(PLAYER_NAMES[i], True, PLAYER_COLORS[i])
            self.screen.blit(name, name.get_rect(center=(x, preview_y + 95)))

        # 开始按钮
        start_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 680, 200, 60)
        mouse_pos = pygame.mouse.get_pos()
        self.draw_button(start_rect, "开始游戏", self.font_medium, GREEN, WHITE,
                        start_rect.collidepoint(mouse_pos))
        buttons.append(("start", start_rect))

        # 说明
        instructions = self.font_tiny.render(
            "操作说明: 点击卡牌翻开 | 鼠标操作",
            True, GRAY)
        self.screen.blit(instructions, (SCREEN_WIDTH // 2 - 180, 760))

        return buttons

    def draw_mode_select(self):
        """绘制模式选择界面"""
        self.screen.fill(DARK_BLUE)

        # 标题
        title = self.font_large.render("选择游戏模式", True, YELLOW)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)

        buttons = []

        # 合作模式
        coop_rect = pygame.Rect(150, 200, 400, 300)
        coop_color = GREEN if self.game_mode == "coop" else GRAY
        pygame.draw.rect(self.screen, coop_color, coop_rect, border_radius=20)
        pygame.draw.rect(self.screen, WHITE, coop_rect, 3, border_radius=20)

        coop_title = self.font_medium.render("合作模式", True, WHITE)
        self.screen.blit(coop_title, coop_title.get_rect(center=(coop_rect.centerx, coop_rect.y + 50)))

        coop_desc = [
            "所有玩家合作",
            "找出所有配对",
            "挑战最快速度",
            "",
            "玩家数: " + str(self.num_players)
        ]
        for i, desc in enumerate(coop_desc):
            text = self.font_small.render(desc, True, WHITE)
            self.screen.blit(text, text.get_rect(center=(coop_rect.centerx, coop_rect.y + 110 + i * 35)))

        buttons.append(("coop", coop_rect))

        # 对战模式
        battle_rect = pygame.Rect(650, 200, 400, 300)
        battle_color = ORANGE if self.game_mode == "battle" else GRAY
        pygame.draw.rect(self.screen, battle_color, battle_rect, border_radius=20)
        pygame.draw.rect(self.screen, WHITE, battle_rect, 3, border_radius=20)

        battle_title = self.font_medium.render("对战模式", True, WHITE)
        self.screen.blit(battle_title, battle_title.get_rect(center=(battle_rect.centerx, battle_rect.y + 50)))

        battle_desc = [
            "玩家轮流记忆",
            "找出配对得分",
            "连胜获得加成",
            "",
            "玩家数: " + str(self.num_players)
        ]
        for i, desc in enumerate(battle_desc):
            text = self.font_small.render(desc, True, WHITE)
            self.screen.blit(text, text.get_rect(center=(battle_rect.centerx, battle_rect.y + 110 + i * 35)))

        buttons.append(("battle", battle_rect))

        # 继续按钮
        continue_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 550, 200, 60)
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

        # 标题
        title = self.font_large.render("选择难度", True, YELLOW)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)

        # 模式提示
        mode_text = self.font_small.render(
            f"当前模式: {'合作模式' if self.game_mode == 'coop' else '对战模式'}",
            True, GREEN)
        self.screen.blit(mode_text, (SCREEN_WIDTH // 2 - 100, 160))

        buttons = []
        difficulties = [
            ("easy", "简单", "4x3 网格", "12张卡", GREEN),
            ("medium", "中等", "4x4 网格", "16张卡", YELLOW),
            ("hard", "困难", "5x4 网格", "20张卡", ORANGE),
            ("extreme", "极限", "6x4 网格", "24张卡", RED)
        ]

        for i, (key, name, grid, cards, color) in enumerate(difficulties):
            row = i // 2
            col = i % 2
            x = 200 + col * 400
            y = 220 + row * 150

            rect = pygame.Rect(x, y, 350, 120)
            diff_color = color if self.difficulty == key else GRAY
            pygame.draw.rect(self.screen, diff_color, rect, border_radius=15)
            pygame.draw.rect(self.screen, WHITE, rect, 2, border_radius=15)

            # 难度名称
            name_text = self.font_medium.render(name, True, WHITE)
            self.screen.blit(name_text, (x + 20, y + 15))

            # 详细信息
            grid_text = self.font_small.render(grid, True, LIGHT_GRAY)
            self.screen.blit(grid_text, (x + 20, y + 55))

            cards_text = self.font_small.render(cards, True, LIGHT_GRAY)
            self.screen.blit(cards_text, (x + 20, y + 85))

            buttons.append((key, rect))

        # 开始按钮
        start_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 550, 200, 70)
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

        # 顶部信息栏
        pygame.draw.rect(self.screen, DARK_GRAY, (0, 0, SCREEN_WIDTH, 60))

        # 标题
        title = self.font_small.render("记忆挑战", True, YELLOW)
        self.screen.blit(title, (20, 15))

        # 模式标签
        mode_text = self.font_tiny.render(
            f"模式: {'合作' if self.game_mode == 'coop' else '对战'} | 难度: {self.difficulty}",
            True, LIGHT_GRAY)
        self.screen.blit(mode_text, (200, 20))

        # 翻牌次数
        turn_text = self.font_tiny.render(f"翻牌次数: {self.turn_count}", True, WHITE)
        self.screen.blit(turn_text, (500, 20))

        # 用时
        if self.start_time > 0:
            self.elapsed_time = (pygame.time.get_ticks() - self.start_time) // 1000
            time_text = self.font_tiny.render(f"用时: {self.elapsed_time}秒", True, WHITE)
            self.screen.blit(time_text, (700, 20))

        # 绘制卡牌
        card_rects = []
        for idx, card in enumerate(self.cards):
            rect = self.draw_card(card, idx)
            card_rects.append((idx, rect))

        # 绘制分数弹出
        for popup in self.score_popup[:]:
            popup["timer"] -= 1
            popup["y"] -= 2

            color = popup.get("color", YELLOW)
            text = self.font_medium.render(popup["text"], True, color)
            self.screen.blit(text, (popup["x"] - text.get_width() // 2, popup["y"]))

            if popup["timer"] <= 0:
                self.score_popup.remove(popup)

        # 绘制玩家面板
        self.draw_player_panel()

        # 返回按钮
        back_rect = pygame.Rect(SCREEN_WIDTH - 120, 10, 100, 40)
        self.draw_button(back_rect, "菜单", self.font_tiny, GRAY, WHITE, False)

        return card_rects

    def draw_result_screen(self):
        """绘制结果界面"""
        self.screen.fill(DARK_BLUE)

        # 标题
        title = self.font_large.render("游戏结束!", True, YELLOW)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title, title_rect)

        # 用时
        time_text = self.font_medium.render(f"总用时: {self.elapsed_time}秒 | 翻牌次数: {self.turn_count}", True, WHITE)
        self.screen.blit(time_text, (SCREEN_WIDTH // 2 - 200, 140))

        # 玩家成绩
        if self.game_mode == "coop":
            # 合作模式
            sorted_players = sorted(self.players, key=lambda x: x["score"], reverse=True)

            for i, player in enumerate(sorted_players):
                y = 220 + i * 80

                pygame.draw.rect(self.screen, DARK_GRAY, (200, y, 800, 70), border_radius=10)

                # 排名
                rank = self.font_medium.render(f"#{i+1}", True, GOLD)
                self.screen.blit(rank, (230, y + 15))

                # 名称
                name = self.font_medium.render(player["name"], True, player["color"])
                self.screen.blit(name, (320, y + 15))

                # 分数
                score = self.font_medium.render(f"{player['score']}分", True, YELLOW)
                self.screen.blit(score, (500, y + 15))

                # 评价
                if self.turn_count <= len(self.cards) * 1.5:
                    rating = "完美!"
                    rating_color = GOLD
                elif self.turn_count <= len(self.cards) * 2:
                    rating = "优秀!"
                    rating_color = GREEN
                elif self.turn_count <= len(self.cards) * 2.5:
                    rating = "不错!"
                    rating_color = BLUE
                else:
                    rating = "加油!"
                    rating_color = GRAY

                rating_text = self.font_medium.render(rating, True, rating_color)
                self.screen.blit(rating_text, (700, y + 15))

        else:
            # 对战模式
            sorted_players = sorted(self.players, key=lambda x: x["score"], reverse=True)
            winner = sorted_players[0]

            # 冠军显示
            winner_label = self.font_small.render("冠军", True, GOLD)
            self.screen.blit(winner_label, (SCREEN_WIDTH // 2 - 30, 200))

            pygame.draw.circle(self.screen, winner["color"], (SCREEN_WIDTH // 2, 280), 60)
            crown = self.font_large.render("👑", True, GOLD)
            self.screen.blit(crown, (SCREEN_WIDTH // 2 - 30, 220))

            winner_name = self.font_medium.render(winner["name"], True, winner["color"])
            self.screen.blit(winner_name, winner_name.get_rect(center=(SCREEN_WIDTH // 2, 360)))

            winner_score = self.font_large.render(f"{winner['score']}分", True, YELLOW)
            self.screen.blit(winner_score, winner_score.get_rect(center=(SCREEN_WIDTH // 2, 400)))

            # 所有玩家排名
            for i, player in enumerate(sorted_players[1:], 1):
                y = 480 + (i - 1) * 60

                rank = self.font_small.render(f"#{i+1}", True, LIGHT_GRAY)
                self.screen.blit(rank, (300, y))

                name = self.font_small.render(player["name"], True, player["color"])
                self.screen.blit(name, (380, y))

                score = self.font_small.render(f"{player['score']}分", True, YELLOW)
                self.screen.blit(score, (550, y))

                pairs = self.font_tiny.render(f"配对:{player['pairs']}", True, LIGHT_GRAY)
                self.screen.blit(pairs, (700, y))

        buttons = []

        # 再来一局按钮
        retry_rect = pygame.Rect(SCREEN_WIDTH // 2 - 220, 650, 200, 60)
        mouse_pos = pygame.mouse.get_pos()
        self.draw_button(retry_rect, "再来一局", self.font_medium, GREEN, WHITE,
                        retry_rect.collidepoint(mouse_pos))
        buttons.append(("retry", retry_rect))

        # 重新选择按钮
        select_rect = pygame.Rect(SCREEN_WIDTH // 2 + 20, 650, 200, 60)
        self.draw_button(select_rect, "重新选择", self.font_medium, BLUE, WHITE,
                        select_rect.collidepoint(mouse_pos))
        buttons.append(("select", select_rect))

        # 菜单按钮
        menu_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 720, 200, 50)
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
                                self.setup_cards()
                                self.game_state = "playing"
                            elif elem[0] == "back":
                                self.game_state = "mode_select"

                elif screen_type == "game":
                    # 检查是否点击了卡牌
                    for idx, rect in elements:
                        if rect.collidepoint(mouse_pos) and idx not in self.matched:
                            card = self.cards[idx]
                            if not card["flipped"] and len(self.revealed) < 2:
                                card["flipped"] = True
                                self.revealed.append(idx)

                                # 检查是否翻开两张
                                if len(self.revealed) == 2:
                                    self.check_match()

                elif screen_type == "result":
                    for elem in elements:
                        if elem[1].collidepoint(mouse_pos):
                            if elem[0] == "retry":
                                self.setup_cards()
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
    game = MemoryGame()
    game.run()
