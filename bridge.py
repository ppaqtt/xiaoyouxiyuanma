#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
桥牌游戏 (Bridge)
四人桥牌游戏，玩家与三个电脑玩家对战（简化版）

游戏规则:
- 四人游戏，对家组队（南北 vs 东西）
- 使用一副52张牌
- 叫牌阶段确定定约（将牌花色+阶数）
- 打牌阶段，完成定约得分，未完成扣分
- 简化规则：
  * 叫牌只有花色定约（无无将）
  * 简化的计分系统
  * 4人轮流出牌，一轮4张牌比大小
"""

import pygame
import random
import sys

# 初始化pygame
pygame.init()

# 游戏常量
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 850
CARD_WIDTH = 70
CARD_HEIGHT = 100
HAND_CARD_WIDTH = 35
HAND_CARD_HEIGHT = 65
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
PURPLE = (75, 0, 130)

# 花色和点数定义
SUITS = ['spade', 'heart', 'club', 'diamond']
SUIT_SYMBOLS = {'spade': '♠', 'heart': '♥', 'club': '♣', 'diamond': '♦'}
SUIT_COLORS = {'spade': BLACK, 'heart': RED, 'club': BLACK, 'diamond': RED}
SUIT_ORDER = ['clubs', 'diamonds', 'hearts', 'spades']  # 从低到高
SUIT_NAMES = {'clubs': '梅花', 'diamonds': '方块', 'hearts': '红心', 'spades': '黑桃', 'no_trump': '无将'}

# 桥牌点数定义（A最大，2最小）
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
RANK_VALUES = {rank: value for value, rank in enumerate(RANKS, 2)}
BRIDGE_POINTS = {'A': 4, 'K': 3, 'Q': 2, 'J': 1}

class Card:
    """扑克牌类"""
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
        self.value = RANK_VALUES[rank]
        self.bridge_value = BRIDGE_POINTS.get(rank, 0)
        self.face_up = True
    
    def get_bridge_suit_value(self, trump_suit):
        """获取在叫牌中的花色值"""
        if self.suit == trump_suit:
            return 100 + self.value
        return self.value
    
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

class BridgePlayer:
    """桥牌玩家类"""
    def __init__(self, name, is_human, team, position):
        self.name = name
        self.is_human = is_human
        self.team = team  # 'NS' 或 'EW'
        self.position = position  # 0:北, 1:东, 2:南, 3:西
        self.hand = []
        self.won_tricks = 0
    
    def count_points(self, trump_suit=None):
        """计算手牌点数（用于叫牌）"""
        points = 0
        for card in self.hand:
            if card.suit == trump_suit:
                # 将牌有额外的价值
                if card.rank == 'A':
                    points += 3
                elif card.rank == 'K':
                    points += 2
                elif card.rank == 'Q':
                    points += 1
            else:
                points += card.bridge_value
        return points

class BridgeGame:
    """桥牌游戏主类"""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("桥牌 - Bridge")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 32)
        self.font_large = pygame.font.Font(None, 44)
        self.font_small = pygame.font.Font(None, 22)
        
        self.deck = Deck()
        self.players = []
        self.current_player = 0
        self.dealer = 0  # 当前庄家
        
        # 叫牌相关
        self.bidding_history = []  # 叫牌历史
        self.current_contract = None  # 当前定约 (suit, level, bidder_team)
        self.bidding_won = False
        self.bidding_finished = False
        
        # 打牌相关
        self.current_trick = []  # 当前轮的牌
        self.trick_winner = -1
        self.tricks_won = {'NS': 0, 'EW': 0}  # 各队赢的墩数
        self.declarer = -1  # 定约方
        self.dummy = -1  # 明手
        self.trump_suit = None
        
        # 游戏状态
        self.game_state = "dealing"  # dealing, bidding, playing, scoring
        self.message = ""
        self.scores = {'NS': 0, 'EW': 0}
        
        self.selected_card = None
        self.ai_delay = 0
        
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
        
        self.card_back_small = pygame.Surface((HAND_CARD_WIDTH, HAND_CARD_HEIGHT))
        self.card_back_small.fill(DARK_BLUE)
        for i in range(0, HAND_CARD_WIDTH, 6):
            pygame.draw.line(self.card_back_small, GOLD, (i, 0), (i, HAND_CARD_HEIGHT), 1)
        for i in range(0, HAND_CARD_HEIGHT, 6):
            pygame.draw.line(self.card_back_small, GOLD, (0, i), (HAND_CARD_WIDTH, i), 1)
    
    def init_players(self):
        """初始化玩家"""
        self.players = [
            BridgePlayer("北家", False, 'NS', 0),
            BridgePlayer("东家", False, 'EW', 1),
            BridgePlayer("南家(你)", True, 'NS', 2),
            BridgePlayer("西家", False, 'EW', 3),
        ]
    
    def start_new_game(self):
        """开始新一局"""
        self.deck.reset()
        self.bidding_history = []
        self.current_contract = None
        self.bidding_finished = False
        self.bidding_won = False
        self.current_trick = []
        self.trick_winner = -1
        self.tricks_won = {'NS': 0, 'EW': 0}
        self.selected_card = None
        self.trump_suit = None
        
        # 重置玩家手牌
        for player in self.players:
            player.hand = []
            player.won_tricks = 0
        
        # 发牌
        for _ in range(13):
            for player in self.players:
                card = self.deck.deal()[0]
                player.hand.append(card)
        
        # 排序手牌
        for player in self.players:
            player.hand.sort(key=lambda c: c.value)
        
        self.game_state = "bidding"
        self.current_player = self.dealer
        self.message = f"{self.players[self.dealer].name}开始叫牌"
    
    def get_valid_bids(self, player):
        """获取当前玩家可以叫的牌"""
        bids = []
        
        # 必须比当前定约高
        current_suit = None
        current_level = 0
        if self.current_contract:
            current_suit = self.current_contract[0]
            current_level = self.current_contract[1]
        
        suits = ['clubs', 'diamonds', 'hearts', 'spades', 'no_trump']
        
        for level in range(1, 8):
            for i, suit in enumerate(suits):
                # 检查是否比当前定约高
                if self.current_contract:
                    if level < current_level:
                        continue
                    if level == current_level:
                        if SUIT_ORDER.index(suit) <= SUIT_ORDER.index(current_suit):
                            continue
                
                bids.append((suit, level))
                break  # 每级别只加一次
            else:
                continue
            break
        
        return bids
    
    def do_bid(self, player_idx, suit, level):
        """执行叫牌"""
        player = self.players[player_idx]
        self.bidding_history.append({
            'player': player_idx,
            'suit': suit,
            'level': level,
            'team': player.team
        })
        
        self.current_contract = (suit, level, player.team)
        
        suit_name = SUIT_NAMES.get(suit, suit)
        self.message = f"{player.name}叫{level}{suit_name}"
        
        # 检查是否连续3家PASS
        if len(self.bidding_history) >= 4:
            last_4 = self.bidding_history[-4:]
            if all(b['suit'] is None for b in last_4):
                self.finish_bidding()
                return
        
        # 下一个叫牌者
        self.current_player = (self.current_player + 1) % 4
    
    def pass_bid(self, player_idx):
        """跳过叫牌"""
        self.bidding_history.append({
            'player': player_idx,
            'suit': None,
            'level': 0,
            'team': self.players[player_idx].team
        })
        
        # 检查是否3家都PASS
        recent_bids = [b for b in self.bidding_history[-3:] if b['suit'] is not None]
        
        # 3家PASS结束叫牌
        pass_count = 0
        for b in reversed(self.bidding_history):
            if b['suit'] is None:
                pass_count += 1
            else:
                break
        
        if pass_count >= 3 and recent_bids:
            self.finish_bidding()
            return
        
        self.message = f"{self.players[player_idx].name}不叫"
        self.current_player = (self.current_player + 1) % 4
    
    def finish_bidding(self):
        """结束叫牌"""
        self.bidding_finished = True
        
        if not self.current_contract:
            # 全部PASS，重新发牌
            self.message = "全部不叫，重新发牌"
            pygame.time.wait(1500)
            self.start_new_game()
            return
        
        suit, level, winning_team = self.current_contract
        self.trump_suit = suit
        
        # 确定定约方
        self.declarer = self.bidding_history[-1]['player']
        self.dummy = (self.declarer + 2) % 4  # 明手是对家
        
        # 确定明手位置（庄家对面）
        suit_name = SUIT_NAMES.get(suit, suit)
        declarer_name = self.players[self.declarer].name
        dummy_name = self.players[self.dummy].name
        
        self.message = f"定约：{level}{suit_name}，{declarer_name}定约，{dummy_name}为明手"
        
        pygame.time.wait(1500)
        self.game_state = "playing"
        self.current_player = (self.declarer + 1) % 4  # 明手左边家先出
    
    def play_card(self, player_idx, card):
        """出牌"""
        player = self.players[player_idx]
        
        if card in player.hand:
            player.hand.remove(card)
        
        self.current_trick.append({
            'player': player_idx,
            'card': card,
            'team': player.team
        })
        
        if len(self.current_trick) == 4:
            self.resolve_trick()
    
    def resolve_trick(self):
        """结算当前轮"""
        lead_card = self.current_trick[0]['card']
        lead_suit = lead_card.suit
        
        # 找最大牌
        max_card = self.current_trick[0]['card']
        max_idx = 0
        
        for i, play in enumerate(self.current_trick[1:], 1):
            card = play['card']
            
            # 将牌吃将牌
            if self.trump_suit != 'no_trump':
                if card.suit == self.trump_suit and max_card.suit != self.trump_suit:
                    max_card = card
                    max_idx = i
                elif card.suit == self.trump_suit and max_card.suit == self.trump_suit:
                    if card.value > max_card.value:
                        max_card = card
                        max_idx = i
                elif card.suit == lead_suit and max_card.suit == lead_suit:
                    if card.value > max_card.value:
                        max_card = card
                        max_idx = i
            else:
                # 无将时，同花色比大小
                if card.suit == lead_suit and card.value > max_card.value:
                    max_card = card
                    max_idx = i
        
        winner = self.current_trick[max_idx]['player']
        winner_team = self.current_trick[max_idx]['team']
        
        self.tricks_won[winner_team] += 1
        self.trick_winner = winner
        self.current_player = winner
        
        winner_name = self.players[winner].name
        self.message = f"{winner_name}赢了这墩 ({self.tricks_won['NS']}-{self.tricks_won['EW']})"
        
        # 清空当前轮
        pygame.time.wait(800)
        self.current_trick = []
        
        # 检查游戏是否结束
        total_cards = sum(len(p.hand) for p in self.players)
        if total_cards == 0:
            self.end_game()
    
    def end_game(self):
        """结束游戏"""
        self.game_state = "scoring"
        
        level, suit, declarer_team = self.current_contract[1], self.current_contract[0], self.current_contract[2]
        
        # 计算定约方赢的墩数
        declarer_tricks = self.tricks_won[declarer_team]
        tricks_needed = level + 6  # 6墩基础 + 定约阶数
        
        if declarer_tricks >= tricks_needed:
            # 定约成功
            over_tricks = declarer_tricks - tricks_needed
            base_score = level * 30 if suit != 'no_trump' else 30
            if suit in ['hearts', 'diamonds']:
                base_score = level * 30
            elif suit in ['clubs', 'spades']:
                base_score = level * 30
            else:
                base_score = level * 30
            
            score = base_score * 100 + over_tricks * 100
            
            if declarer_team == 'NS':
                self.scores['NS'] += score
                self.scores['EW'] -= score
            else:
                self.scores['EW'] += score
                self.scores['NS'] -= score
            
            self.message = f"定约成功！{declarer_team}方得{score}分 ({declarer_tricks}/{tricks_needed})"
        else:
            # 定约失败
            under_tricks = tricks_needed - declarer_tricks
            penalty = under_tricks * 100
            
            if declarer_team == 'NS':
                self.scores['NS'] -= penalty
                self.scores['EW'] += penalty
            else:
                self.scores['EW'] -= penalty
                self.scores['NS'] += penalty
            
            self.message = f"定约失败！{declarer_team}方扣{penalty}分 ({declarer_tricks}/{tricks_needed})"
    
    def ai_should_play(self, player_idx):
        """AI决定出牌"""
        player = self.players[player_idx]
        
        # 庄家的AI自动出明手牌
        if player_idx == self.dummy and self.trick_winner == self.declarer:
            # 轮到明手，由庄家控制
            return None
        
        # 找到可以出的牌
        if len(self.current_trick) == 0:
            # 首攻，随便出一张
            return player.hand[0] if player.hand else None
        
        # 跟牌
        lead_suit = self.current_trick[0]['card'].suit
        same_suit_cards = [c for c in player.hand if c.suit == lead_suit]
        
        if same_suit_cards:
            # 有同花色，出最小的
            return min(same_suit_cards, key=lambda c: c.value)
        else:
            # 没有同花色，随便出一张
            return player.hand[0] if player.hand else None
    
    def can_follow_suit(self, player_idx, card):
        """检查是否必须跟花色"""
        if len(self.current_trick) == 0:
            return True
        
        lead_suit = self.current_trick[0]['card'].suit
        
        if card.suit != lead_suit:
            # 检查是否有同花色
            player = self.players[player_idx]
            same_suit_cards = [c for c in player.hand if c.suit == lead_suit]
            if same_suit_cards:
                return False  # 必须跟同花色
        return True
    
    def draw_card(self, surface, card, x, y, face_up=True, small=False, highlight=False):
        """绘制单张扑克牌"""
        width = HAND_CARD_WIDTH if small else CARD_WIDTH
        height = HAND_CARD_HEIGHT if small else CARD_HEIGHT
        
        if face_up and card:
            # 高亮效果
            if highlight:
                pygame.draw.rect(surface, GOLD, (x - 2, y - 2, width + 4, height + 4), 3)
            
            # 白色卡片背景
            pygame.draw.rect(surface, WHITE, (x, y, width, height))
            pygame.draw.rect(surface, BLACK, (x, y, width, height), 2)
            
            color = SUIT_COLORS[card.suit]
            symbol = SUIT_SYMBOLS[card.suit]
            
            # 显示点数
            font_rank = pygame.font.Font(None, 20 if small else 26)
            text = font_rank.render(f"{card.rank}", True, color)
            surface.blit(text, (x + 3, y + 3))
            
            # 绘制大符号
            font_symbol = pygame.font.Font(None, 32 if small else 42)
            symbol_text = font_symbol.render(symbol, True, color)
            symbol_rect = symbol_text.get_rect(center=(x + width // 2, y + height // 2))
            surface.blit(symbol_text, symbol_rect)
            
            # 右下角显示
            text2 = font_rank.render(f"{card.rank}", True, color)
            rotated = pygame.transform.rotate(text2, 180)
            surface.blit(rotated, (x + width - 14, y + height - 16))
        else:
            if small:
                surface.blit(self.card_back_small, (x, y))
            else:
                surface.blit(self.card_back, (x, y))
    
    def draw_player_hand(self, surface, player, index):
        """绘制玩家手牌"""
        is_current = (index == self.current_player and self.game_state == "playing")
        
        if index == 2:  # 玩家在南
            x = SCREEN_WIDTH // 2 - len(player.hand) * HAND_CARD_WIDTH // 2
            y = SCREEN_HEIGHT - 140
            
            for i, card in enumerate(player.hand):
                offset = 0
                if self.selected_card == card:
                    offset = -15
                elif is_current and i == len(player.hand) - 1:
                    offset = -5
                
                self.draw_card(surface, card, x + i * HAND_CARD_WIDTH, y + offset, True, True)
        
        elif index == 0:  # 北（明手）
            x = SCREEN_WIDTH // 2 - len(player.hand) * HAND_CARD_WIDTH // 2
            y = 60
            
            # 明手手牌正面朝上
            for i, card in enumerate(player.hand):
                self.draw_card(surface, card, x + i * HAND_CARD_WIDTH, y, True, True)
        
        elif index == 1:  # 东
            x = SCREEN_WIDTH - 80
            y = SCREEN_HEIGHT // 2 - len(player.hand) * HAND_CARD_HEIGHT // 2
            
            for i, card in enumerate(player.hand):
                self.draw_card(surface, card, x, y + i * 6, False, True)
        
        else:  # 西
            x = 20
            y = SCREEN_HEIGHT // 2 - len(player.hand) * HAND_CARD_HEIGHT // 2
            
            for i, card in enumerate(player.hand):
                self.draw_card(surface, card, x, y + i * 6, False, True)
        
        # 玩家名称
        team = "NS队" if player.team == "NS" else "EW队"
        name_color = GOLD if player.is_human else WHITE
        
        font = pygame.font.Font(None, 28)
        
        if index == 2:
            text = font.render(f"{player.name} [{team}]", True, name_color)
            surface.blit(text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 165))
        elif index == 0:
            text = font.render(f"{player.name} [{team}]", True, name_color)
            surface.blit(text, (SCREEN_WIDTH // 2 - 80, 35))
        elif index == 1:
            text = font.render(f"{player.name} [{team}]", True, name_color)
            surface.blit(text, (SCREEN_WIDTH - 130, SCREEN_HEIGHT // 2 - 80))
        else:
            text = font.render(f"{player.name} [{team}]", True, name_color)
            surface.blit(text, (20, SCREEN_HEIGHT // 2 - 80))
        
        # 当前出牌者指示
        if is_current:
            indicator_pos = {
                0: (SCREEN_WIDTH // 2, 45),
                1: (SCREEN_WIDTH - 95, SCREEN_HEIGHT // 2),
                2: (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 155),
                3: (35, SCREEN_HEIGHT // 2)
            }
            pygame.draw.circle(surface, RED, indicator_pos[index], 8)
    
    def draw_current_trick(self, surface):
        """绘制当前轮的牌"""
        if not self.current_trick:
            return
        
        positions = {
            0: (SCREEN_WIDTH // 2 - 30, SCREEN_HEIGHT // 2 - 180),  # 北
            1: (SCREEN_WIDTH // 2 + 50, SCREEN_HEIGHT // 2 - 40),  # 东
            2: (SCREEN_WIDTH // 2 - 30, SCREEN_HEIGHT // 2 + 20),  # 南
            3: (SCREEN_WIDTH // 2 - 90, SCREEN_HEIGHT // 2 - 40),  # 西
        }
        
        for play in self.current_trick:
            x, y = positions[play['player']]
            self.draw_card(surface, play['card'], x, y, True, False)
    
    def draw_bidding_info(self, surface):
        """绘制叫牌信息"""
        # 叫牌历史面板
        panel_rect = pygame.Rect(SCREEN_WIDTH - 250, 100, 230, 200)
        pygame.draw.rect(surface, BLACK, panel_rect, 0)
        pygame.draw.rect(surface, GOLD, panel_rect, 2)
        
        font = pygame.font.Font(None, 22)
        title = font.render("叫牌记录:", True, GOLD)
        surface.blit(title, (SCREEN_WIDTH - 240, 110))
        
        y = 135
        for i, bid in enumerate(self.bidding_history[-8:]):  # 最多显示8条
            player_name = self.players[bid['player']].name
            if bid['suit']:
                suit_name = SUIT_NAMES.get(bid['suit'], '')
                text = font.render(f"{player_name}: {bid['level']}{suit_name}", True, WHITE)
            else:
                text = font.render(f"{player_name}: PASS", True, GRAY)
            surface.blit(text, (SCREEN_WIDTH - 240, y))
            y += 22
        
        # 当前定约
        if self.current_contract:
            suit, level, team = self.current_contract
            suit_name = SUIT_NAMES.get(suit, '')
            contract_text = font.render(f"当前定约: {level}{suit_name}", True, LIGHT_BLUE)
            surface.blit(contract_text, (SCREEN_WIDTH - 240, y + 10))
    
    def draw_score(self, surface):
        """绘制分数"""
        font = pygame.font.Font(None, 28)
        
        # NS队分数
        ns_text = font.render(f"NS队: {self.scores['NS']:+d}", True, GOLD)
        surface.blit(ns_text, (SCREEN_WIDTH // 2 - 60, 10))
        
        # EW队分数
        ew_text = font.render(f"EW队: {self.scores['EW']:+d}", True, WHITE)
        surface.blit(ew_text, (SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT - 35))
    
    def draw_table(self, surface):
        """绘制牌桌"""
        surface.fill(GREEN_TABLE)
        
        center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        
        # 外圈
        pygame.draw.ellipse(surface, BROWN, 
                           (center_x - 450, center_y - 300, 900, 600), 10)
        
        # 中圈
        pygame.draw.ellipse(surface, DARK_GREEN, 
                           (center_x - 420, center_y - 270, 840, 540), 0)
        
        # 内圈
        pygame.draw.ellipse(surface, GREEN_TABLE, 
                           (center_x - 380, center_y - 230, 760, 460), 0)
        
        # 中心装饰
        font = pygame.font.Font(None, 60)
        center_text = font.render("桥", True, GOLD)
        center_rect = center_text.get_rect(center=(center_x, center_y))
        surface.blit(center_text, center_rect)
    
    def draw_bidding_buttons(self, surface):
        """绘制叫牌按钮"""
        if self.game_state != "bidding" or self.current_player != 2:
            return
        
        buttons = []
        y_start = SCREEN_HEIGHT // 2 + 80
        
        # PASS按钮
        rect = pygame.Rect(SCREEN_WIDTH // 2 - 180, y_start, 80, 40)
        pygame.draw.rect(surface, GRAY, rect)
        text = self.font.render("PASS", True, WHITE)
        surface.blit(text, (rect.centerx - 22, rect.centery - 10))
        buttons.append(('pass', rect))
        
        # 叫牌按钮
        valid_bids = self.get_valid_bids(self.players[2])
        x = SCREEN_WIDTH // 2 - 80
        
        for suit, level in valid_bids[:8]:  # 最多显示8个
            suit_name = SUIT_NAMES.get(suit, '')
            label = f"{level}{suit_name}"
            
            color = SUIT_COLORS.get(SUITS[('clubs', 'diamonds', 'hearts', 'spades').index(suit) if suit != 'no_trump' else 'spade'], BROWN)
            
            rect = pygame.Rect(x, y_start, 60, 40)
            pygame.draw.rect(surface, color, rect)
            text = self.font_small.render(label, True, WHITE)
            surface.blit(text, (rect.centerx - 20, rect.centery - 8))
            buttons.append(((suit, level), rect))
            x += 70
        
        return buttons
    
    def draw_play_button(self, surface):
        """绘制出牌按钮"""
        if self.game_state != "playing" or self.current_player != 2:
            return
        
        # 新游戏按钮
        rect = pygame.Rect(SCREEN_WIDTH - 120, SCREEN_HEIGHT - 60, 100, 40)
        pygame.draw.rect(surface, BROWN, rect)
        text = self.font.render("新游戏", True, WHITE)
        surface.blit(text, (rect.centerx - 30, rect.centery - 10))
        return rect
    
    def draw_info(self, surface):
        """绘制信息面板"""
        info_rect = pygame.Rect(20, SCREEN_HEIGHT - 55, SCREEN_WIDTH - 280, 45)
        pygame.draw.rect(surface, BLACK, info_rect, 0)
        pygame.draw.rect(surface, GOLD, info_rect, 2)
        
        text = self.font.render(self.message, True, WHITE)
        surface.blit(text, (30, SCREEN_HEIGHT - 45))
    
    def draw_rules(self, surface):
        """绘制规则说明"""
        rules = [
            "桥牌规则:",
            "1. 四人对战，南北vs东西",
            "2. 轮流叫牌，确定定约",
            "3. 定约方需完成定约墩数",
            "4. 简化的叫牌和计分系统"
        ]
        
        font = pygame.font.Font(None, 18)
        y = SCREEN_HEIGHT - 180
        for rule in rules:
            text = font.render(rule, True, LIGHT_GRAY)
            surface.blit(text, (20, y))
            y += 16
    
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
        
        # 处理叫牌
        if self.game_state == "bidding" and self.current_player == 2:
            buttons = self.draw_bidding_buttons(self.screen)
            if buttons and mouse_clicked:
                for action, rect in buttons:
                    if rect.collidepoint(mouse_pos):
                        if action == 'pass':
                            self.pass_bid(2)
                        else:
                            suit, level = action
                            self.do_bid(2, suit, level)
        
        # 处理出牌
        if self.game_state == "playing" and self.current_player == 2:
            # 点击选择牌
            if mouse_clicked:
                player = self.players[2]
                x = SCREEN_WIDTH // 2 - len(player.hand) * HAND_CARD_WIDTH // 2
                y = SCREEN_HEIGHT - 140
                
                for i, card in enumerate(player.hand):
                    card_x = x + i * HAND_CARD_WIDTH
                    card_rect = pygame.Rect(card_x, y - 15, HAND_CARD_WIDTH, HAND_CARD_HEIGHT + 15)
                    
                    if card_rect.collidepoint(mouse_pos):
                        if self.can_follow_suit(2, card):
                            if self.selected_card == card:
                                # 出牌
                                self.play_card(2, card)
                                self.selected_card = None
                            else:
                                self.selected_card = card
                        else:
                            self.message = "必须跟同花色！"
                        break
        
        # 新游戏按钮
        new_game_rect = self.draw_play_button(self.screen)
        if new_game_rect and mouse_clicked and new_game_rect.collidepoint(mouse_pos):
            self.dealer = (self.dealer + 1) % 4
            self.start_new_game()
    
    def ai_turn(self):
        """AI出牌"""
        if self.game_state == "playing" and not self.players[self.current_player]["is_human"]:
            # 检查是否是明手
            if self.current_player == self.dummy and self.trick_winner == self.declarer:
                # 庄家控制明手
                return
            
            if self.ai_delay <= 0:
                card = self.ai_should_play(self.current_player)
                if card:
                    self.play_card(self.current_player, card)
                self.ai_delay = 30  # 延迟帧数
            else:
                self.ai_delay -= 1
    
    def update(self):
        """更新游戏状态"""
        # AI回合
        if self.game_state == "playing":
            self.ai_turn()
        
        # 自动开始
        if self.game_state == "dealing":
            pygame.time.wait(500)
            self.start_new_game()
    
    def draw(self):
        """绘制游戏画面"""
        self.draw_table(self.screen)
        self.draw_rules(self.screen)
        self.draw_score(self.screen)
        
        # 绘制所有玩家手牌
        for i, player in enumerate(self.players):
            self.draw_player_hand(self.screen, player, i)
        
        # 绘制当前轮的牌
        self.draw_current_trick(self.screen)
        
        # 叫牌信息
        if self.game_state == "bidding":
            self.draw_bidding_info(self.screen)
        
        # 按钮
        self.draw_bidding_buttons(self.screen)
        self.draw_play_button(self.screen)
        
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
    game = BridgeGame()
    game.run()

if __name__ == "__main__":
    main()
