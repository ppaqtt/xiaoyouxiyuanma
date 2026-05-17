#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
梭哈扑克游戏 (Stud Poker)
玩家与电脑对战的五人座梭哈游戏

游戏规则:
- 使用一副52张扑克牌
- 每位玩家发5张牌
- 从第2张牌开始依次亮牌
- 梭哈牌型（从大到小）：
  1. 皇家同花顺 (Royal Flush)
  2. 同花顺 (Straight Flush)
  3. 四条 (Four of a Kind)
  4. 葫芦 (Full House)
  5. 同花 (Flush)
  6. 顺子 (Straight)
  7. 三条 (Three of a Kind)
  8. 两对 (Two Pair)
  9. 一对 (One Pair)
  10. 高牌 (High Card)
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
CARD_WIDTH = 80
CARD_HEIGHT = 112
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

# 花色定义
SUITS = ['spade', 'heart', 'club', 'diamond']
SUIT_SYMBOLS = {'spade': '♠', 'heart': '♥', 'club': '♣', 'diamond': '♦'}
SUIT_COLORS = {'spade': BLACK, 'heart': RED, 'club': BLACK, 'diamond': RED}

# 点数定义
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
RANK_VALUES = {rank: value for value, rank in enumerate(RANKS, 2)}

class Card:
    """扑克牌类"""
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
        self.value = RANK_VALUES[rank]
        self.face_up = True
    
    def __str__(self):
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
        self.cards = [Card(suit, rank) for suit in SUITS for rank in RANKS]
        random.shuffle(self.cards)
    
    def deal(self, num=1):
        """发牌"""
        cards = []
        for _ in range(num):
            if self.cards:
                cards.append(self.cards.pop())
        return cards

class Hand:
    """手牌类"""
    def __init__(self, cards=None):
        self.cards = cards if cards else []
        self.revealed = 0  # 已亮牌数量
    
    def add_card(self, card):
        self.cards.append(card)
    
    def sort_by_value(self):
        """按点数排序"""
        self.cards.sort(key=lambda c: c.value)
    
    def get_ranks(self):
        """获取所有点数"""
        return [c.value for c in self.cards]
    
    def get_suits(self):
        """获取所有花色"""
        return [c.suit for c in self.cards]
    
    def is_royal_flush(self):
        """皇家同花顺: A,K,Q,J,10同花色"""
        if self.is_flush() and self.is_straight():
            ranks = sorted(self.get_ranks())
            return ranks == [10, 11, 12, 13, 14]
        return False
    
    def is_straight_flush(self):
        """同花顺"""
        return self.is_flush() and self.is_straight()
    
    def is_four_of_a_kind(self):
        """四条"""
        ranks = self.get_ranks()
        return any(ranks.count(r) == 4 for r in set(ranks))
    
    def is_full_house(self):
        """葫芦"""
        ranks = self.get_ranks()
        return len(set(ranks)) == 2 and not self.is_four_of_a_kind()
    
    def is_flush(self):
        """同花"""
        suits = self.get_suits()
        return len(set(suits)) == 1
    
    def is_straight(self):
        """顺子"""
        ranks = sorted(set(self.get_ranks()))
        if len(ranks) != 5:
            return False
        # A2345特殊顺子
        if ranks == [2, 3, 4, 5, 14]:
            return True
        return max(ranks) - min(ranks) == 4
    
    def is_three_of_a_kind(self):
        """三条"""
        ranks = self.get_ranks()
        return any(ranks.count(r) == 3 for r in set(ranks))
    
    def is_two_pair(self):
        """两对"""
        ranks = self.get_ranks()
        pairs = [r for r in set(ranks) if ranks.count(r) == 2]
        return len(pairs) == 2
    
    def is_one_pair(self):
        """一对"""
        ranks = self.get_ranks()
        return any(ranks.count(r) == 2 for r in set(ranks))
    
    def get_hand_rank(self):
        """获取牌型等级"""
        if self.is_royal_flush(): return 10
        if self.is_straight_flush(): return 9
        if self.is_four_of_a_kind(): return 8
        if self.is_full_house(): return 7
        if self.is_flush(): return 6
        if self.is_straight(): return 5
        if self.is_three_of_a_kind(): return 4
        if self.is_two_pair(): return 3
        if self.is_one_pair(): return 2
        return 1
    
    def get_hand_name(self):
        """获取牌型名称"""
        names = {
            10: "皇家同花顺",
            9: "同花顺",
            8: "四条",
            7: "葫芦",
            6: "同花",
            5: "顺子",
            4: "三条",
            3: "两对",
            2: "一对",
            1: "高牌"
        }
        return names[self.get_hand_rank()]
    
    def compare_with(self, other):
        """比较两手牌的大小"""
        self_rank = self.get_hand_rank()
        other_rank = other.get_hand_rank()
        
        if self_rank != other_rank:
            return 1 if self_rank > other_rank else -1
        
        # 同牌型时比较点数
        self_sorted = sorted(self.get_ranks(), reverse=True)
        other_sorted = sorted(other.get_ranks(), reverse=True)
        
        for s, o in zip(self_sorted, other_sorted):
            if s != o:
                return 1 if s > o else -1
        return 0

class Player:
    """玩家类"""
    def __init__(self, name, is_human=False):
        self.name = name
        self.is_human = is_human
        self.hand = Hand()
        self.folded = False
        self.all_in = False
        self.bet = 0
        self.seat_pos = (0, 0)

class StudPokerGame:
    """梭哈游戏主类"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("梭哈扑克 - Stud Poker")
        self.clock = pygame.time.Clock()
        self.font = get_chinese_font(36)
        self.font_large = get_chinese_font(48)
        self.font_small = get_chinese_font(24)
        
        self.deck = Deck()
        self.players = []
        self.current_phase = 0  # 0:开始 1:第一轮 2:第二轮 3:第三轮 4:第四轮 5:结束
        self.game_state = "betting"  # betting, result
        self.message = ""
        self.winner = None
        
        self.init_players()
        self.load_card_images()
    
    def load_card_images(self):
        """加载扑克牌图片"""
        self.card_back = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
        self.card_back.fill(DARK_BLUE)
        # 画牌背花纹
        for i in range(0, CARD_WIDTH, 10):
            pygame.draw.line(self.card_back, GOLD, (i, 0), (i, CARD_HEIGHT), 1)
        for i in range(0, CARD_HEIGHT, 10):
            pygame.draw.line(self.card_back, GOLD, (0, i), (CARD_WIDTH, i), 1)
    
    def init_players(self):
        """初始化玩家"""
        self.players = [
            Player("玩家", is_human=True),
            Player("电脑1", is_human=False),
            Player("电脑2", is_human=False),
            Player("电脑3", is_human=False),
            Player("电脑4", is_human=False),
        ]
        # 设置座位位置
        positions = [
            (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT - 180),  # 玩家底部中央
            (50, SCREEN_HEIGHT // 2 - 100),                    # 左侧
            (200, 80),                                          # 顶部左侧
            (SCREEN_WIDTH // 2 - 100, 30),                     # 顶部中央
            (SCREEN_WIDTH - 180, 80),                          # 顶部右侧
        ]
        for i, player in enumerate(self.players):
            player.seat_pos = positions[i]
    
    def start_new_round(self):
        """开始新一轮"""
        self.deck.reset()
        self.current_phase = 0
        self.game_state = "betting"
        self.message = "开始发牌..."
        self.winner = None
        
        # 重置玩家状态
        for player in self.players:
            player.hand = Hand()
            player.folded = False
            player.bet = 0
        
        # 发底牌
        for _ in range(5):
            for player in self.players:
                card = self.deck.deal()[0]
                if player.is_human:
                    card.face_up = True
                else:
                    card.face_up = False
                player.hand.add_card(card)
            
            # 显示亮牌阶段
            self.current_phase += 1
            if self.current_phase == 1:
                self.message = "第一轮亮牌 - 发第2张"
            elif self.current_phase == 2:
                self.message = "第二轮亮牌 - 发第3张"
            elif self.current_phase == 3:
                self.message = "第三轮亮牌 - 发第4张"
            elif self.current_phase == 4:
                self.message = "第四轮亮牌 - 发第5张"
                # 最后一张亮牌后开始比牌
                for player in self.players:
                    player.hand.sort_by_value()
                    card.face_up = True
                self.game_state = "revealing"
        
        # 亮所有暗牌
        for player in self.players:
            for card in player.hand.cards:
                card.face_up = True
        
        self.determine_winner()
    
    def determine_winner(self):
        """确定赢家"""
        active_players = [p for p in self.players if not p.folded]
        if not active_players:
            self.winner = None
            return
        
        best_player = active_players[0]
        for player in active_players[1:]:
            if player.hand.compare_with(best_player.hand) > 0:
                best_player = player
        
        self.winner = best_player
        self.game_state = "result"
        
        if self.winner.is_human:
            self.message = f"恭喜！你获得了胜利！牌型：{self.winner.hand.get_hand_name()}"
        else:
            self.message = f"{self.winner.name}获胜！牌型：{self.winner.hand.get_hand_name()}"
    
    def draw_card(self, surface, card, x, y, face_up=True):
        """绘制单张扑克牌"""
        if face_up and card:
            # 白色卡片背景
            pygame.draw.rect(surface, WHITE, (x, y, CARD_WIDTH, CARD_HEIGHT))
            pygame.draw.rect(surface, BLACK, (x, y, CARD_WIDTH, CARD_HEIGHT), 2)
            
            # 绘制花色符号
            color = SUIT_COLORS[card.suit]
            symbol = SUIT_SYMBOLS[card.suit]
            
            # 显示点数
            font_rank = get_chinese_font(28)
            text = font_rank.render(f"{card.rank}", True, color)
            surface.blit(text, (x + 5, y + 5))
            
            # 绘制大符号
            font_symbol = get_chinese_font(48)
            symbol_text = font_symbol.render(symbol, True, color)
            symbol_rect = symbol_text.get_rect(center=(x + CARD_WIDTH // 2, y + CARD_HEIGHT // 2 + 5))
            surface.blit(symbol_text, symbol_rect)
            
            # 右下角显示
            text2 = font_rank.render(f"{card.rank}", True, color)
            rotated = pygame.transform.rotate(text2, 180)
            surface.blit(rotated, (x + CARD_WIDTH - 20, y + CARD_HEIGHT - 22))
        else:
            # 牌背面
            surface.blit(self.card_back, (x, y))
    
    def draw_player_area(self, surface, player, index):
        """绘制玩家区域"""
        x, y = player.seat_pos
        
        # 玩家名称
        name_text = self.font.render(player.name, True, GOLD if player.is_human else WHITE)
        name_rect = name_text.get_rect(center=(x + 100, y - 30))
        surface.blit(name_text, name_rect)
        
        # 玩家状态
        if player.folded:
            status = self.font_small.render("已弃牌", True, GRAY)
            surface.blit(status, (x + 60, y - 55))
        elif self.game_state == "result" and self.winner == player:
            status = self.font_small.render("胜者!", True, GOLD)
            surface.blit(status, (x + 60, y - 55))
        
        # 手牌
        if player.is_human:
            # 玩家手牌水平显示
            card_y = y + 20
            for i, card in enumerate(player.hand.cards):
                self.draw_card(surface, card, x + i * (CARD_WIDTH + 10), card_y, card.face_up)
        else:
            # 电脑玩家手牌紧凑显示
            card_y = y + 15
            for i, card in enumerate(player.hand.cards):
                offset = 0 if i < 3 else 5
                self.draw_card(surface, card, x + i * (CARD_WIDTH // 2 + 5), card_y + offset, card.face_up)
        
        # 牌型名称
        if self.game_state in ["result", "revealing"] and not player.folded:
            hand_name = player.hand.get_hand_name()
            hand_text = self.font_small.render(hand_name, True, LIGHT_BLUE)
            surface.blit(hand_text, (x + 60, y + CARD_HEIGHT + 30))
    
    def draw_table(self, surface):
        """绘制牌桌"""
        # 牌桌背景
        surface.fill(GREEN_TABLE)
        
        # 椭圆形牌桌
        center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        pygame.draw.ellipse(surface, DARK_GREEN, 
                           (center_x - 400, center_y - 250, 800, 500), 0)
        pygame.draw.ellipse(surface, GREEN_TABLE, 
                           (center_x - 380, center_y - 230, 760, 460), 0)
        
        # 牌桌边缘
        pygame.draw.ellipse(surface, BROWN, 
                           (center_x - 410, center_y - 260, 820, 520), 8)
    
    def draw_info(self, surface):
        """绘制信息面板"""
        # 信息面板背景
        info_rect = pygame.Rect(20, SCREEN_HEIGHT - 60, SCREEN_WIDTH - 40, 50)
        pygame.draw.rect(surface, BLACK, info_rect, 0)
        pygame.draw.rect(surface, GOLD, info_rect, 2)
        
        # 消息文本
        text = self.font.render(self.message, True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 35))
        surface.blit(text, text_rect)
    
    def draw_buttons(self, surface):
        """绘制按钮"""
        # 新游戏按钮
        new_game_rect = pygame.Rect(SCREEN_WIDTH - 150, 20, 130, 40)
        pygame.draw.rect(surface, BROWN, new_game_rect)
        pygame.draw.rect(surface, GOLD, new_game_rect, 2)
        text = self.font.render("新游戏", True, WHITE)
        text_rect = text.get_rect(center=new_game_rect.center)
        surface.blit(text, text_rect)
        return new_game_rect
    
    def draw_rules(self, surface):
        """绘制规则说明"""
        rules = [
            "梭哈规则说明:",
            "1. 每位玩家发5张牌",
            "2. 从第2张开始依次亮牌",
            "3. 最后比较牌型大小",
            "牌型大小: 皇家同花顺 > 同花顺 > 四条 > 葫芦 > 同花 > 顺子 > 三条 > 两对 > 一对 > 高牌"
        ]
        
        y = 20
        for i, rule in enumerate(rules):
            if i == 0:
                text = self.font_small.render(rule, True, GOLD)
            else:
                text = self.font_small.render(rule, True, WHITE)
            surface.blit(text, (20, y))
            y += 22
    
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
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    if self.game_state in ["result"]:
                        self.start_new_round()
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        
        # 检查新游戏按钮
        new_game_rect = pygame.Rect(SCREEN_WIDTH - 150, 20, 130, 40)
        if mouse_clicked and new_game_rect.collidepoint(mouse_pos):
            self.start_new_round()
        
        # 自动开始游戏
        if self.game_state == "betting" and self.current_phase == 0:
            self.start_new_round()
    
    def update(self):
        """更新游戏状态"""
        pass
    
    def draw(self):
        """绘制游戏画面"""
        self.draw_table(self.screen)
        self.draw_rules(self.screen)
        self.draw_buttons(self.screen)
        
        # 绘制所有玩家
        for i, player in enumerate(self.players):
            self.draw_player_area(self.screen, player, i)
        
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
    game = StudPokerGame()
    game.run()

if __name__ == "__main__":
    main()
