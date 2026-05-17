#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
斗地主扑克游戏 (Landlord)
三人斗地主游戏，玩家与两个电脑玩家对战

游戏规则:
- 使用一副54张牌（包含大小王）
- 三位玩家，地主获得额外3张底牌
- 牌型包括：单张、对子、三条、顺子、连对、飞机、炸弹、火箭等
- 支持叫地主功能
- 农民与地主对战，先出完手牌者获胜
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

# 游戏常量
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
CARD_WIDTH = 60
CARD_HEIGHT = 90
HAND_CARD_WIDTH = 35
HAND_CARD_HEIGHT = 70
FPS = 60

# 颜色定义
GREEN_TABLE = (34, 102, 51)
DARK_GREEN = (25, 76, 38)
GOLD = (255, 215, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 20, 60)
LIGHT_BLUE = (173, 216, 230)
DARK_BLUE = (0, 0, 139)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
BROWN = (139, 90, 43)
PURPLE = (128, 0, 128)

# 花色和点数定义
SUITS = ['spade', 'heart', 'club', 'diamond']
SUIT_SYMBOLS = {'spade': '♠', 'heart': '♥', 'club': '♣', 'diamond': '♦'}
SUIT_COLORS = {'spade': BLACK, 'heart': RED, 'club': BLACK, 'diamond': RED}

# 斗地主点数定义（3最小，小王次之，大王最大）
RANKS = ['3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A', '2', 'small_joker', 'big_joker']
RANK_VALUES = {rank: value for value, rank in enumerate(RANKS)}

class Card:
    """扑克牌类"""
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
        self.value = RANK_VALUES[rank]
        self.face_up = True
    
    def is_joker(self):
        """是否为王牌"""
        return self.rank in ['small_joker', 'big_joker']
    
    def is_red_joker(self):
        """是否为大王"""
        return self.rank == 'big_joker'
    
    def __str__(self):
        if self.rank == 'small_joker':
            return "小王"
        elif self.rank == 'big_joker':
            return "大王"
        return f"{SUIT_SYMBOLS[self.suit]}{self.rank}"
    
    def __repr__(self):
        return self.__str__()

class Deck:
    """牌堆类"""
    def __init__(self):
        self.cards = []
        self.reset()
    
    def reset(self):
        """重新初始化牌堆"""
        self.cards = []
        # 添加普通牌
        for suit in SUITS:
            for rank in RANKS[:-2]:  # 去掉大小王
                self.cards.append(Card(suit, rank))
        # 添加大小王
        self.cards.append(Card(None, 'small_joker'))
        self.cards.append(Card(None, 'big_joker'))
        random.shuffle(self.cards)
    
    def deal(self, num=1):
        """发牌"""
        cards = []
        for _ in range(num):
            if self.cards:
                cards.append(self.cards.pop())
        return cards

class LandlordGame:
    """斗地主游戏主类"""
    
    # 牌型定义
    SINGLE = 1
    PAIR = 2
    TRIPLE = 3
    STRAIGHT = 4
    STRAIGHT_PAIR = 5
    TRIPLE_WITH_SINGLE = 6
    TRIPLE_WITH_PAIR = 7
    BOMB = 8
    ROCKET = 9
    FOUR_WITH_TWO = 10
    FOUR_WITH_TWO_PAIRS = 11
    
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("斗地主 - Landlord")
        self.clock = pygame.time.Clock()
        self.font = get_chinese_font(36)
        self.font_large = get_chinese_font(48)
        self.font_small = get_chinese_font(24)
        
        self.deck = Deck()
        self.players = []  # 0:玩家, 1:左电脑, 2:右电脑
        self.landlord_cards = []  # 底牌
        self.landlord = None  # 地主玩家索引
        self.current_player = 0  # 当前出牌玩家
        self.last_player = -1  # 上一轮出牌玩家
        self.last_cards = []  # 上一手牌
        self.last_card_type = 0  # 上一手牌类型
        self.game_state = "dealing"  # dealing, bidding, playing, ending
        self.message = ""
        self.winner = None
        
        # 叫地主相关
        self.bid_values = [0, 0, 0]  # 叫分
        self.current_bidder = 0
        self.max_bid = 0
        self.max_bidder = -1
        
        # 出牌相关
        self.selected_cards = []
        self.pass_count = 0  # 连续不出次数
        
        self.load_card_images()
        self.init_players()
    
    def load_card_images(self):
        """加载扑克牌图片"""
        self.card_back = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
        self.card_back.fill(DARK_BLUE)
        for i in range(0, CARD_WIDTH, 8):
            pygame.draw.line(self.card_back, GOLD, (i, 0), (i, CARD_HEIGHT), 1)
        for i in range(0, CARD_HEIGHT, 8):
            pygame.draw.line(self.card_back, GOLD, (0, i), (CARD_WIDTH, i), 1)
        
        # 小牌背（电脑玩家用）
        self.card_back_small = pygame.Surface((HAND_CARD_WIDTH, HAND_CARD_HEIGHT))
        self.card_back_small.fill(DARK_BLUE)
        for i in range(0, HAND_CARD_WIDTH, 6):
            pygame.draw.line(self.card_back_small, GOLD, (i, 0), (i, HAND_CARD_HEIGHT), 1)
        for i in range(0, HAND_CARD_HEIGHT, 6):
            pygame.draw.line(self.card_back_small, GOLD, (0, i), (HAND_CARD_WIDTH, i), 1)
    
    def init_players(self):
        """初始化玩家"""
        self.players = [
            {"name": "玩家", "is_human": True, "cards": [], "role": ""},
            {"name": "左电脑", "is_human": False, "cards": [], "role": ""},
            {"name": "右电脑", "is_human": False, "cards": [], "role": ""},
        ]
    
    def start_new_game(self):
        """开始新游戏"""
        self.deck.reset()
        self.landlord_cards = []
        self.landlord = None
        self.current_player = 0
        self.last_player = -1
        self.last_cards = []
        self.last_card_type = 0
        self.game_state = "dealing"
        self.message = "发牌中..."
        self.winner = None
        self.bid_values = [0, 0, 0]
        self.max_bid = 0
        self.max_bidder = -1
        self.selected_cards = []
        self.pass_count = 0
        
        for p in self.players:
            p["cards"] = []
            p["role"] = ""
        
        # 发牌
        for _ in range(17):
            for player in self.players:
                card = self.deck.deal()[0]
                player["cards"].append(card)
        
        # 底牌
        self.landlord_cards = self.deck.deal(3)
        
        # 排序手牌
        for player in self.players:
            player["cards"].sort(key=lambda c: c.value)
        
        # 开始叫地主
        self.game_state = "bidding"
        self.current_bidder = random.randint(0, 2)
        self.message = f"{self.players[self.current_bidder]['name']}请叫地主"
    
    def can_bid(self, player_idx, bid_value):
        """检查是否可以叫这个分"""
        if bid_value > 0 and bid_value <= 3 and bid_value > self.max_bid:
            return True
        return False
    
    def do_bid(self, player_idx, bid_value):
        """执行叫地主"""
        self.bid_values[player_idx] = bid_value
        if bid_value > self.max_bid:
            self.max_bid = bid_value
            self.max_bidder = player_idx
        
        # 叫了3分直接结束叫地主
        if bid_value == 3:
            self.landlord = self.max_bidder
            self.finish_bidding()
            return
        
        # 检查是否所有玩家都跳过或有人叫地主
        all_passed = all(b == 0 for b in self.bid_values)
        
        # 三个玩家都跳过
        if all_passed and self.bid_values[(player_idx + 1) % 3] == 0:
            self.current_bidder = (self.current_bidder + 1) % 3
        else:
            self.current_bidder = (self.current_bidder + 1) % 3
            # 如果最高分玩家的下一个已经叫过，跳过
            while self.bid_values[self.current_bidder] == 0 and self.current_bidder != self.max_bidder:
                if all(b == 0 for b in self.bid_values):
                    break
                self.current_bidder = (self.current_bidder + 1) % 3
        
        # 所有玩家都跳过且没人叫地主
        if self.bid_values[self.current_bidder] == 0 and self.max_bidder == -1:
            # 重新发牌
            self.message = "无人叫地主，重新发牌..."
            pygame.time.wait(1000)
            self.start_new_game()
            return
        
        # 如果轮到最高分者，自动通过
        if self.current_bidder == self.max_bidder:
            # 只有两个玩家没叫完才结束
            remaining = [i for i in range(3) if i != self.max_bidder and self.bid_values[i] == 0]
            if len(remaining) == 0:
                self.finish_bidding()
                return
        
        self.message = f"{self.players[self.current_bidder]['name']}请叫地主 (当前最高:{self.max_bid})"
    
    def finish_bidding(self):
        """结束叫地主"""
        if self.landlord is None:
            self.landlord = self.max_bidder
        
        # 地主获得底牌
        self.players[self.landlord]["cards"].extend(self.landlord_cards)
        self.players[self.landlord]["cards"].sort(key=lambda c: c.value)
        
        self.players[self.landlord]["role"] = "地主"
        for i in range(3):
            if i != self.landlord:
                self.players[i]["role"] = "农民"
        
        self.game_state = "playing"
        self.current_player = self.landlord
        self.last_player = -1
        self.last_cards = []
        self.message = f"游戏开始！{self.players[self.landlord]['name']}是地主！"
    
    def get_card_type(self, cards):
        """识别牌型"""
        if not cards:
            return 0, 0
        
        n = len(cards)
        values = [c.value for c in cards]
        unique_values = set(values)
        
        # 统计各点数的牌数
        counts = {}
        for v in values:
            counts[v] = counts.get(v, 0) + 1
        count_values = sorted(counts.values(), reverse=True)
        
        # 王炸
        if n == 2:
            if all(c.is_joker() for c in cards):
                return self.ROCKET, 0
        
        # 单张
        if n == 1:
            return self.SINGLE, values[0]
        
        # 对子
        if n == 2 and count_values == [2]:
            return self.PAIR, values[0]
        
        # 三条
        if n == 3 and count_values == [3]:
            return self.TRIPLE, values[0]
        
        # 炸弹
        if n == 4 and count_values == [4]:
            return self.BOMB, values[0]
        
        # 三带一
        if n == 4 and count_values == [3, 1]:
            return self.TRIPLE_WITH_SINGLE, max(v for v, c in counts.items() if c == 3)
        
        # 三带一对
        if n == 5 and count_values == [3, 2]:
            return self.TRIPLE_WITH_PAIR, max(v for v, c in counts.items() if c == 3)
        
        # 四带两单
        if n == 6 and count_values == [4, 1, 1]:
            return self.FOUR_WITH_TWO, max(v for v, c in counts.items() if c == 4)
        
        # 四带两对
        if n == 6 and count_values == [4, 2, 2]:
            return self.FOUR_WITH_TWO_PAIRS, max(v for v, c in counts.items() if c == 4)
        
        # 单顺
        if n >= 5 and count_values == [1] * n:
            sorted_vals = sorted(values)
            is_straight = all(sorted_vals[i+1] - sorted_vals[i] == 1 for i in range(n-1))
            if is_straight:
                return self.STRAIGHT, max(values)
        
        # 双顺
        if n >= 6 and n % 2 == 0 and count_values == [2] * (n // 2):
            sorted_vals = sorted(unique_values)
            if all(sorted_vals[i+1] - sorted_vals[i] == 1 for i in range(len(sorted_vals)-1)):
                return self.STRAIGHT_PAIR, max(unique_values)
        
        return 0, 0
    
    def can_play_cards(self, cards):
        """检查是否可以出牌"""
        if not cards:
            return False
        
        card_type, main_value = self.get_card_type(cards)
        
        # 必须出牌
        if self.last_player == -1 or self.last_player == self.current_player:
            return card_type > 0
        
        last_type, last_value = self.last_card_type, self.get_main_value(self.last_cards)
        
        # 王炸最大
        if card_type == self.ROCKET:
            return True
        
        # 炸弹必须比之前的炸弹大，或者比所有牌都大
        if card_type == self.BOMB:
            if last_type == self.ROCKET:
                return False
            if last_type == self.BOMB:
                return main_value > last_value
            return True
        
        # 必须出相同的牌型
        if card_type != last_type:
            return False
        
        return main_value > last_value
    
    def get_main_value(self, cards):
        """获取主要值（三条取三张的值，炸弹取四张的值等）"""
        if not cards:
            return 0
        values = [c.value for c in cards]
        counts = {}
        for v in values:
            counts[v] = counts.get(v, 0) + 1
        
        # 找最多的那个
        max_count = max(counts.values())
        for v, c in sorted(counts.items(), key=lambda x: (-x[1], -x[0])):
            if c == max_count:
                return v
        return values[0]
    
    def play_cards(self, player_idx, cards):
        """出牌"""
        if not self.can_play_cards(cards):
            return False
        
        # 移除出的牌
        for card in cards:
            if card in self.players[player_idx]["cards"]:
                self.players[player_idx]["cards"].remove(card)
        
        self.last_cards = cards
        self.last_card_type, _ = self.get_card_type(cards)
        self.last_player = player_idx
        self.pass_count = 0
        
        # 检查是否获胜
        if len(self.players[player_idx]["cards"]) == 0:
            self.game_state = "ending"
            landlord_win = (player_idx == self.landlord)
            self.winner = "地主" if landlord_win else "农民"
            
            if player_idx == 0:
                self.message = "恭喜！你获胜了！"
            elif landlord_win:
                self.message = f"{self.players[player_idx]['name']}获胜，地主赢了！"
            else:
                self.message = f"{self.players[player_idx]['name']}获胜，农民赢了！"
            return True
        
        # 下一个玩家
        self.current_player = (self.current_player + 1) % 3
        
        if self.current_player == 0:
            self.message = "请选择要出的牌"
        else:
            self.message = f"{self.players[self.current_player]['name']}思考中..."
        
        return True
    
    def ai_play(self):
        """AI出牌"""
        player = self.players[self.current_player]
        cards = player["cards"]
        
        if self.last_player == -1 or self.last_player == self.current_player:
            # 可以出任何牌
            # 优先出最小的单张
            if cards:
                single = min(cards, key=lambda c: c.value)
                return [single]
        else:
            # 必须大过上家
            last_type, last_value = self.last_card_type, self.get_main_value(self.last_cards)
            
            # 检查王炸
            jokers = [c for c in cards if c.is_joker()]
            if len(jokers) == 2:
                return jokers
            
            # 检查炸弹
            values = [c.value for c in cards]
            for v in set(values):
                if values.count(v) == 4:
                    if last_type != self.BOMB or v > last_value:
                        return [c for c in cards if c.value == v]
            
            # 找能出的最小牌
            for card in sorted(cards, key=lambda c: c.value):
                if self.can_play_cards([card]):
                    return [card]
        
        # 无法出牌，pass
        return []
    
    def draw_card(self, surface, card, x, y, face_up=True, small=False):
        """绘制单张扑克牌"""
        width = HAND_CARD_WIDTH if small else CARD_WIDTH
        height = HAND_CARD_HEIGHT if small else CARD_HEIGHT
        
        if face_up and card:
            # 白色卡片背景
            pygame.draw.rect(surface, WHITE, (x, y, width, height))
            pygame.draw.rect(surface, BLACK, (x, y, width, height), 2)
            
            # 绘制
            if card.is_joker():
                color = RED if card.is_red_joker() else DARK_BLUE
                symbol = "大" if card.is_red_joker() else "小"
                text_rank = "王"
            else:
                color = SUIT_COLORS[card.suit]
                symbol = SUIT_SYMBOLS[card.suit]
                text_rank = card.rank
            
            # 显示点数
            font_rank = pygame.font.Font(None, 22 if small else 28)
            text = font_rank.render(f"{text_rank}", True, color)
            surface.blit(text, (x + 3, y + 3))
            
            # 绘制大符号
            font_symbol = pygame.font.Font(None, 36 if small else 48)
            symbol_text = font_symbol.render(symbol, True, color)
            symbol_rect = symbol_text.get_rect(center=(x + width // 2, y + height // 2))
            surface.blit(symbol_text, symbol_rect)
            
            # 右下角显示
            text2 = font_rank.render(f"{text_rank}", True, color)
            rotated = pygame.transform.rotate(text2, 180)
            surface.blit(rotated, (x + width - 15, y + height - 18))
        else:
            # 牌背面
            if small:
                surface.blit(self.card_back_small, (x, y))
            else:
                surface.blit(self.card_back, (x, y))
    
    def draw_player_area(self, surface, player, index):
        """绘制玩家区域"""
        is_current = (index == self.current_player and self.game_state == "playing")
        
        if index == 0:
            # 玩家 - 底部
            x = SCREEN_WIDTH // 2 - len(player["cards"]) * HAND_CARD_WIDTH // 2
            y = SCREEN_HEIGHT - 120
            
            # 绘制手牌
            for i, card in enumerate(player["cards"]):
                card_x = x + i * HAND_CARD_WIDTH
                is_selected = card in self.selected_cards
                offset = -10 if is_selected else 0
                self.draw_card(surface, card, card_x, y + offset, True, True)
            
            # 选中提示
            if self.selected_cards:
                hint = self.font_small.render(f"已选{len(self.selected_cards)}张", True, GOLD)
                surface.blit(hint, (x, y - 25))
        
        elif index == 1:
            # 左电脑 - 左侧
            x = 20
            y = SCREEN_HEIGHT // 2 - len(player["cards"]) * HAND_CARD_HEIGHT // 2
            
            for i, card in enumerate(player["cards"]):
                card_y = y + i * 5
                self.draw_card(surface, card, x, card_y, False, True)
        
        else:
            # 右电脑 - 右侧
            x = SCREEN_WIDTH - HAND_CARD_WIDTH - 20
            y = SCREEN_HEIGHT // 2 - len(player["cards"]) * HAND_CARD_HEIGHT // 2
            
            for i, card in enumerate(player["cards"]):
                card_y = y + i * 5
                self.draw_card(surface, card, x, card_y, False, True)
        
        # 玩家名称和角色
        name = player["name"]
        role = player["role"]
        card_count = len(player["cards"])
        
        font = get_chinese_font(28)
        
        if index == 0:
            text = font.render(f"{name} ({card_count}张) {role}", True, GOLD if is_current else WHITE)
            surface.blit(text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 150))
        elif index == 1:
            text = font.render(f"{name} {role}", True, GOLD if is_current else WHITE)
            surface.blit(text, (20, SCREEN_HEIGHT // 2 - 80))
            count_text = font.render(f"{card_count}张", True, WHITE)
            surface.blit(count_text, (20, SCREEN_HEIGHT // 2 + 80))
        else:
            text = font.render(f"{name} {role}", True, GOLD if is_current else WHITE)
            surface.blit(text, (SCREEN_WIDTH - 100, SCREEN_HEIGHT // 2 - 80))
            count_text = font.render(f"{card_count}张", True, WHITE)
            surface.blit(count_text, (SCREEN_WIDTH - 100, SCREEN_HEIGHT // 2 + 80))
        
        # 当前出牌者指示
        if is_current:
            if index == 0:
                indicator_pos = (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 175)
            elif index == 1:
                indicator_pos = (80, SCREEN_HEIGHT // 2 - 20)
            else:
                indicator_pos = (SCREEN_WIDTH - 110, SCREEN_HEIGHT // 2 - 20)
            
            pygame.draw.circle(surface, RED, indicator_pos, 8)
    
    def draw_landlord_cards(self, surface):
        """绘制底牌"""
        if self.landlord_cards:
            x = SCREEN_WIDTH // 2 - 50
            y = 20
            
            for i, card in enumerate(self.landlord_cards):
                self.draw_card(surface, card, x + i * 30, y, True, False)
            
            text = self.font_small.render("底牌:", True, WHITE)
            surface.blit(text, (x - 50, y + 30))
    
    def draw_last_cards(self, surface):
        """绘制上家出的牌"""
        if self.last_cards and self.last_player >= 0:
            player = self.players[self.last_player]
            
            if self.last_player == 0:
                x = SCREEN_WIDTH // 2 - len(self.last_cards) * 25
                y = SCREEN_HEIGHT // 2 + 50
            elif self.last_player == 1:
                x = 100
                y = SCREEN_HEIGHT // 2 - 50
            else:
                x = SCREEN_WIDTH - 200
                y = SCREEN_HEIGHT // 2 - 50
            
            for i, card in enumerate(self.last_cards):
                self.draw_card(surface, card, x + i * 30, y, True, False)
            
            name = self.players[self.last_player]["name"]
            text = self.font_small.render(f"{name}出的牌:", True, LIGHT_BLUE)
            surface.blit(text, (x, y - 20))
    
    def draw_table(self, surface):
        """绘制牌桌"""
        surface.fill(GREEN_TABLE)
        
        # 椭圆形牌桌
        center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        pygame.draw.ellipse(surface, DARK_GREEN, 
                           (center_x - 400, center_y - 200, 800, 400), 0)
        pygame.draw.ellipse(surface, GREEN_TABLE, 
                           (center_x - 380, center_y - 180, 760, 360), 0)
        pygame.draw.ellipse(surface, BROWN, 
                           (center_x - 410, center_y - 210, 820, 420), 8)
    
    def draw_bidding_buttons(self, surface):
        """绘制叫地主按钮"""
        if self.game_state != "bidding":
            return
        
        if self.current_bidder != 0:
            return
        
        buttons = []
        y = SCREEN_HEIGHT // 2 + 50
        
        # 不叫按钮
        rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, y, 80, 40)
        pygame.draw.rect(surface, GRAY, rect)
        text = self.font.render("不叫", True, WHITE)
        surface.blit(text, (rect.centerx - 20, rect.centery - 12))
        buttons.append(("pass", rect))
        
        # 叫分按钮
        for bid in [1, 2, 3]:
            if bid > self.max_bid:
                rect = pygame.Rect(SCREEN_WIDTH // 2 - 50 + (bid - 1) * 60, y, 50, 40)
                color = GOLD if bid == 3 else BROWN
                pygame.draw.rect(surface, color, rect)
                text = self.font.render(f"{bid}分", True, WHITE)
                surface.blit(text, (rect.centerx - 20, rect.centery - 12))
                buttons.append((str(bid), rect))
        
        return buttons
    
    def draw_action_buttons(self, surface):
        """绘制出牌按钮"""
        if self.game_state != "playing" or self.current_player != 0:
            return
        
        buttons = []
        y = SCREEN_HEIGHT // 2 + 50
        
        # 不出按钮
        if self.last_player != 0 and self.last_player != -1:
            rect = pygame.Rect(SCREEN_WIDTH // 2 - 180, y, 80, 40)
            pygame.draw.rect(surface, GRAY, rect)
            text = self.font.render("不出", True, WHITE)
            surface.blit(text, (rect.centerx - 20, rect.centery - 12))
            buttons.append(("pass", rect))
        
        # 出牌按钮
        rect = pygame.Rect(SCREEN_WIDTH // 2 - 30, y, 80, 40)
        pygame.draw.rect(surface, BROWN, rect)
        text = self.font.render("出牌", True, WHITE)
        surface.blit(text, (rect.centerx - 20, rect.centery - 12))
        buttons.append(("play", rect))
        
        # 新游戏按钮
        rect = pygame.Rect(SCREEN_WIDTH // 2 + 100, y, 80, 40)
        pygame.draw.rect(surface, DARK_BLUE, rect)
        text = self.font.render("新游戏", True, WHITE)
        surface.blit(text, (rect.centerx - 30, rect.centery - 12))
        buttons.append(("new", rect))
        
        return buttons
    
    def draw_info(self, surface):
        """绘制信息面板"""
        info_rect = pygame.Rect(20, SCREEN_HEIGHT - 50, SCREEN_WIDTH - 40, 40)
        pygame.draw.rect(surface, BLACK, info_rect, 0)
        pygame.draw.rect(surface, GOLD, info_rect, 2)
        
        text = self.font.render(self.message, True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
        surface.blit(text, text_rect)
    
    def draw_rules(self, surface):
        """绘制规则说明"""
        rules = [
            "斗地主规则:",
            "1. 三人游戏，发17张牌，留3张底牌",
            "2. 玩家轮流叫地主（1-3分）",
            "3. 地主获得底牌，与两位农民对战",
            "4. 先出完手牌者获胜"
        ]
        
        font = get_chinese_font(20)
        y = SCREEN_HEIGHT - 180
        for rule in rules:
            text = font.render(rule, True, LIGHT_GRAY)
            surface.blit(text, (20, y))
            y += 18
    
    def handle_events(self):
        """处理事件"""
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_clicked = True
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        
        # 处理叫地主
        if self.game_state == "bidding" and self.current_bidder == 0:
            buttons = self.draw_bidding_buttons(self.screen)
            if buttons and mouse_clicked:
                for action, rect in buttons:
                    if rect.collidepoint(mouse_pos):
                        if action == "pass":
                            self.do_bid(0, 0)
                        else:
                            self.do_bid(0, int(action))
        
        # 处理出牌
        if self.game_state == "playing" and self.current_player == 0:
            # 点击选择牌
            if mouse_clicked:
                x = SCREEN_WIDTH // 2 - len(self.players[0]["cards"]) * HAND_CARD_WIDTH // 2
                y = SCREEN_HEIGHT - 120
                
                for i, card in enumerate(self.players[0]["cards"]):
                    card_x = x + i * HAND_CARD_WIDTH
                    card_rect = pygame.Rect(card_x, y - 10, HAND_CARD_WIDTH, HAND_CARD_HEIGHT + 10)
                    
                    if card_rect.collidepoint(mouse_pos):
                        if card in self.selected_cards:
                            self.selected_cards.remove(card)
                        else:
                            self.selected_cards.append(card)
                        break
            
            # 点击按钮
            buttons = self.draw_action_buttons(self.screen)
            if buttons and mouse_clicked:
                for action, rect in buttons:
                    if rect.collidepoint(mouse_pos):
                        if action == "pass":
                            self.play_cards(0, [])
                        elif action == "play":
                            if self.selected_cards and self.can_play_cards(self.selected_cards):
                                self.play_cards(0, self.selected_cards[:])
                                self.selected_cards = []
                        elif action == "new":
                            self.start_new_game()
    
    def ai_turn(self):
        """AI出牌回合"""
        if self.game_state == "playing" and not self.players[self.current_player]["is_human"]:
            pygame.time.wait(800)  # 模拟思考时间
            
            if self.last_player == self.current_player or self.last_player == -1:
                # 可以出任何牌
                cards_to_play = self.ai_play()
                if cards_to_play:
                    self.play_cards(self.current_player, cards_to_play)
            else:
                # 需要大过上家
                cards_to_play = self.ai_play()
                if cards_to_play:
                    self.play_cards(self.current_player, cards_to_play)
                else:
                    # 不出
                    self.play_cards(self.current_player, [])
    
    def update(self):
        """更新游戏状态"""
        if self.game_state == "ending":
            return
        
        # AI回合
        if self.game_state == "playing" and not self.players[self.current_player]["is_human"]:
            self.ai_turn()
        
        # 自动开始新游戏
        if self.game_state == "dealing":
            pygame.time.wait(500)
            self.start_new_game()
    
    def draw(self):
        """绘制游戏画面"""
        self.draw_table(self.screen)
        self.draw_rules(self.screen)
        
        # 绘制所有玩家
        for i, player in enumerate(self.players):
            self.draw_player_area(self.screen, player, i)
        
        # 绘制底牌
        self.draw_landlord_cards(self.screen)
        
        # 绘制上家出的牌
        self.draw_last_cards(self.screen)
        
        # 绘制按钮
        self.draw_bidding_buttons(self.screen)
        self.draw_action_buttons(self.screen)
        
        self.draw_info(self.screen)
        
        pygame.display.flip()
    
    def run(self):
        """游戏主循环"""
        running = True
        while running:
            self.clock.tick(FPS)
            
            self.handle_events()
            self.update()
            self.draw()
        
        pygame.quit()

def main():
    """主函数"""
    game = LandlordGame()
    game.run()

if __name__ == "__main__":
    main()
