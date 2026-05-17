#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
卡牌构建游戏（简化版DBG）
使用pygame制作
操作说明：
- 鼠标左键点击使用手牌
- 点击商店卡牌购买（需要金币）
- 点击'结束回合'结束回合
"""

import pygame
import os
import sys
import random

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

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (244, 67, 54)
GREEN = (76, 175, 80)
BLUE = (33, 150, 243)
YELLOW = (255, 235, 59)
PURPLE = (156, 39, 176)
ORANGE = (255, 152, 0)
GRAY = (158, 158, 158)
DARK_GRAY = (48, 48, 48)
CARD_BG = (66, 66, 66)
DARK_CARD_BG = (33, 33, 33)

# 窗口大小
WIDTH, HEIGHT = 1200, 800

# 卡牌类型
CARD_TYPES = [
    # 攻击卡牌
    {'name': '斩击', 'type': 'attack', 'cost': 1, 'effect': {'damage': 6}, 'desc': '造成6点伤害', 'color': RED, 'price': 0},
    {'name': '重击', 'type': 'attack', 'cost': 2, 'effect': {'damage': 12}, 'desc': '造成12点伤害', 'color': RED, 'price': 50},
    {'name': '连斩', 'type': 'attack', 'cost': 1, 'effect': {'damage': 4, 'draw': 1}, 'desc': '造成4点伤害，抽1张牌', 'color': RED, 'price': 75},
    {'name': '火球', 'type': 'attack', 'cost': 2, 'effect': {'damage': 15}, 'desc': '造成15点伤害', 'color': ORANGE, 'price': 100},
    
    # 防御卡牌
    {'name': '格挡', 'type': 'defense', 'cost': 1, 'effect': {'block': 5}, 'desc': '获得5点护甲', 'color': BLUE, 'price': 0},
    {'name': '铁壁', 'type': 'defense', 'cost': 2, 'effect': {'block': 12}, 'desc': '获得12点护甲', 'color': BLUE, 'price': 60},
    {'name': '坚守', 'type': 'defense', 'cost': 1, 'effect': {'block': 8}, 'desc': '获得8点护甲', 'color': BLUE, 'price': 50},
    
    # 特殊卡牌
    {'name': '抽牌', 'type': 'utility', 'cost': 1, 'effect': {'draw': 2}, 'desc': '抽2张牌', 'color': GREEN, 'price': 80},
    {'name': '蓄力', 'type': 'utility', 'cost': 0, 'effect': {'energy': 1}, 'desc': '获得1点能量', 'color': YELLOW, 'price': 120},
    {'name': '治愈', 'type': 'utility', 'cost': 1, 'effect': {'heal': 8}, 'desc': '恢复8点生命', 'color': GREEN, 'price': 100},
    {'name': '强化', 'type': 'utility', 'cost': 1, 'effect': {'strength': 2}, 'desc': '本次战斗攻击力+2', 'color': PURPLE, 'price': 90},
]

class Card:
    def __init__(self, card_data):
        self.name = card_data['name']
        self.type = card_data['type']
        self.cost = card_data['cost']
        self.effect = card_data['effect']
        self.desc = card_data['desc']
        self.color = card_data['color']
        self.price = card_data['price']

class Character:
    def __init__(self, name, max_hp, is_player=False):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.block = 0
        self.strength = 0
        self.is_player = is_player
        self.next_action = None
        self.action_cooldown = 0

class CardGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('卡牌构建游戏')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('simhei', 20)
        self.large_font = pygame.font.SysFont('simhei', 36)
        self.small_font = pygame.font.SysFont('simhei', 14)
        
        self.game_state = 'combat'  # combat, shop
        self.turn = 1
        self.gold = 100
        self.floor = 1
        
        # 玩家牌组
        self.deck = []
        self.hand = []
        self.discard = []
        self.energy = 3
        self.max_energy = 3
        
        self.player = Character('玩家', 80, is_player=True)
        self.enemy = None
        
        self.init_deck()
        self.spawn_enemy()
        self.draw_cards(5)

    def init_deck(self):
        for _ in range(5):
            self.deck.append(Card(CARD_TYPES[0]))  # 斩击
        for _ in range(4):
            self.deck.append(Card(CARD_TYPES[4]))  # 格挡
        random.shuffle(self.deck)

    def spawn_enemy(self):
        enemy_hp = 50 + self.floor * 15
        self.enemy = Character('敌人', enemy_hp)
        self.plan_enemy_action()

    def plan_enemy_action(self):
        actions = ['attack', 'attack', 'defend', 'buff']
        self.enemy.next_action = random.choice(actions)
        self.enemy.action_cooldown = 1

    def draw_cards(self, num):
        for _ in range(num):
            if not self.deck:
                self.deck = self.discard
                self.discard = []
                random.shuffle(self.deck)
            if self.deck:
                self.hand.append(self.deck.pop())

    def play_card(self, card_index):
        if card_index < 0 or card_index >= len(self.hand):
            return
        
        card = self.hand[card_index]
        if self.energy < card.cost:
            return
        
        self.energy -= card.cost
        self.apply_card_effect(card)
        self.discard.append(self.hand.pop(card_index))
        
        if self.enemy.hp <= 0:
            self.gold += 30 + self.floor * 10
            self.floor += 1
            self.game_state = 'shop'

    def apply_card_effect(self, card):
        effect = card.effect
        
        if 'damage' in effect:
            damage = effect['damage'] + self.player.strength
            if self.enemy.block > 0:
                blocked = min(self.enemy.block, damage)
                self.enemy.block -= blocked
                damage -= blocked
            self.enemy.hp -= damage
        
        if 'block' in effect:
            self.player.block += effect['block']
        
        if 'draw' in effect:
            self.draw_cards(effect['draw'])
        
        if 'energy' in effect:
            self.energy += effect['energy']
        
        if 'heal' in effect:
            self.player.hp = min(self.player.max_hp, self.player.hp + effect['heal'])
        
        if 'strength' in effect:
            self.player.strength += effect['strength']

    def end_turn(self):
        # 敌人行动
        self.enemy_turn()
        
        if self.player.hp <= 0:
            self.__init__()
            return
        
        if self.enemy.hp <= 0:
            return
        
        # 开始新回合
        self.turn += 1
        self.energy = self.max_energy
        self.player.block = 0
        self.enemy.block = 0
        self.discard.extend(self.hand)
        self.hand = []
        self.draw_cards(5)

    def enemy_turn(self):
        if self.enemy.next_action == 'attack':
            damage = 10 + self.floor * 3
            if self.player.block > 0:
                blocked = min(self.player.block, damage)
                self.player.block -= blocked
                damage -= blocked
            self.player.hp -= damage
        elif self.enemy.next_action == 'defend':
            self.enemy.block += 8 + self.floor
        elif self.enemy.next_action == 'buff':
            pass
        
        self.plan_enemy_action()

    def buy_card(self, card):
        if self.gold >= card.price:
            self.gold -= card.price
            self.deck.append(Card(card))

    def leave_shop(self):
        self.game_state = 'combat'
        self.turn = 1
        self.player.strength = 0
        self.player.block = 0
        self.spawn_enemy()
        self.discard.extend(self.hand)
        self.hand = []
        self.deck.extend(self.discard)
        self.discard = []
        random.shuffle(self.deck)
        self.draw_cards(5)

    def draw_card(self, card, x, y, scale=1.0, is_shop=False, is_clickable=True):
        card_w = 120 * scale
        card_h = 180 * scale
        
        color = card.color
        pygame.draw.rect(self.screen, DARK_CARD_BG, (x, y, card_w, card_h), border_radius=10)
        pygame.draw.rect(self.screen, color, (x, y, card_w, card_h), 3, border_radius=10)
        
        # 费用
        cost_text = self.font.render(str(card.cost), True, YELLOW)
        pygame.draw.circle(self.screen, DARK_GRAY, (x + 20, y + 20), 18)
        self.screen.blit(cost_text, (x + 20 - cost_text.get_width()//2, y + 20 - cost_text.get_height()//2))
        
        # 名称
        name_text = self.font.render(card.name, True, WHITE)
        self.screen.blit(name_text, (x + card_w//2 - name_text.get_width()//2, y + 50))
        
        # 描述
        desc_lines = [card.desc[i:i+12] for i in range(0, len(card.desc), 12)]
        for i, line in enumerate(desc_lines):
            desc_text = self.small_font.render(line, True, GRAY)
            self.screen.blit(desc_text, (x + card_w//2 - desc_text.get_width()//2, y + 90 + i * 20))
        
        if is_shop:
            price_text = self.font.render(f"{card.price}G", True, YELLOW)
            self.screen.blit(price_text, (x + card_w//2 - price_text.get_width()//2, y + card_h - 30))

    def draw_character(self, char, x, y):
        # 人物框
        pygame.draw.rect(self.screen, DARK_GRAY, (x, y, 200, 250), border_radius=10)
        
        # 名称
        name_text = self.large_font.render(char.name, True, WHITE)
        self.screen.blit(name_text, (x + 100 - name_text.get_width()//2, y + 20))
        
        # 血条
        hp_ratio = max(0, char.hp / char.max_hp)
        pygame.draw.rect(self.screen, BLACK, (x + 20, y + 70, 160, 30))
        pygame.draw.rect(self.screen, RED, (x + 20, y + 70, 160 * hp_ratio, 30))
        hp_text = self.font.render(f"{max(0, char.hp)}/{char.max_hp}", True, WHITE)
        self.screen.blit(hp_text, (x + 100 - hp_text.get_width()//2, y + 75))
        
        # 护甲
        if char.block > 0:
            pygame.draw.rect(self.screen, BLUE, (x + 20, y + 110, 160, 25))
            block_text = self.font.render(f"护甲: {char.block}", True, WHITE)
            self.screen.blit(block_text, (x + 100 - block_text.get_width()//2, y + 112))
        
        # 力量
        if char.strength > 0:
            pygame.draw.rect(self.screen, RED, (x + 20, y + 140, 160, 25))
            str_text = self.font.render(f"力量: {char.strength}", True, WHITE)
            self.screen.blit(str_text, (x + 100 - str_text.get_width()//2, y + 142))
        
        # 敌人意图
        if not char.is_player and char.next_action:
            intent_text = self.font.render(f"意图: {'攻击' if char.next_action == 'attack' else '防御'}", True, YELLOW)
            self.screen.blit(intent_text, (x + 100 - intent_text.get_width()//2, y + 180))

    def draw_ui(self):
        if self.game_state == 'combat':
            # 能量
            pygame.draw.rect(self.screen, DARK_GRAY, (50, 50, 150, 50), border_radius=10)
            energy_text = self.large_font.render(f"能量: {self.energy}/{self.max_energy}", True, YELLOW)
            self.screen.blit(energy_text, (70, 55))
            
            # 楼层和金币
            info_text = self.font.render(f"楼层: {self.floor} | 金币: {self.gold}", True, WHITE)
            self.screen.blit(info_text, (WIDTH - 300, 60))
            
            # 牌堆信息
            deck_info = f"牌堆: {len(self.deck)} | 弃牌: {len(self.discard)}"
            deck_text = self.font.render(deck_info, True, GRAY)
            self.screen.blit(deck_text, (WIDTH - 300, 100))
            
            # 结束回合按钮
            end_btn = pygame.Rect(WIDTH - 180, HEIGHT - 280, 150, 50)
            pygame.draw.rect(self.screen, GREEN, end_btn, border_radius=10)
            end_text = self.font.render("结束回合", True, WHITE)
            self.screen.blit(end_text, (WIDTH - 180 + 75 - end_text.get_width()//2, HEIGHT - 280 + 12))
            self.end_btn = end_btn

    def draw_combat(self):
        self.screen.fill(BLACK)
        
        # 绘制人物
        self.draw_character(self.player, 150, 150)
        self.draw_character(self.enemy, WIDTH - 350, 150)
        
        # 绘制手牌
        card_spacing = 140
        start_x = (WIDTH - len(self.hand) * card_spacing) // 2 + 20
        self.card_rects = []
        for i, card in enumerate(self.hand):
            x = start_x + i * card_spacing
            y = HEIGHT - 220
            self.draw_card(card, x, y)
            self.card_rects.append(pygame.Rect(x, y, 120, 180))
        
        self.draw_ui()

    def draw_shop(self):
        self.screen.fill(DARK_GRAY)
        
        title = self.large_font.render(f"商店 - 金币: {self.gold}", True, YELLOW)
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 30))
        
        # 可购买的卡牌
        shop_cards = random.sample([c for c in CARD_TYPES if c['price'] > 0], 6)
        self.shop_card_rects = []
        
        start_x = (WIDTH - 4 * 140) // 2
        for i, card_data in enumerate(shop_cards):
            row = i // 4
            col = i % 4
            x = start_x + col * 140
            y = 100 + row * 220
            card = Card(card_data)
            self.draw_card(card, x, y, is_shop=True)
            self.shop_card_rects.append((pygame.Rect(x, y, 120, 180), card_data))
        
        # 离开商店按钮
        leave_btn = pygame.Rect(WIDTH//2 - 100, HEIGHT - 100, 200, 50)
        pygame.draw.rect(self.screen, BLUE, leave_btn, border_radius=10)
        leave_text = self.font.render("继续冒险", True, WHITE)
        self.screen.blit(leave_text, (WIDTH//2 - leave_text.get_width()//2, HEIGHT - 90))
        self.leave_btn = leave_btn

    def handle_click(self, pos):
        x, y = pos
        
        if self.game_state == 'combat':
            for i, rect in enumerate(self.card_rects):
                if rect.collidepoint(x, y):
                    self.play_card(i)
                    return
            if hasattr(self, 'end_btn') and self.end_btn.collidepoint(x, y):
                self.end_turn()
        elif self.game_state == 'shop':
            for rect, card_data in self.shop_card_rects:
                if rect.collidepoint(x, y):
                    self.buy_card(card_data)
                    return
            if hasattr(self, 'leave_btn') and self.leave_btn.collidepoint(x, y):
                self.leave_shop()

    def run(self):
        running = True
        while running:
            if self.game_state == 'combat':
                self.draw_combat()
            elif self.game_state == 'shop':
                self.draw_shop()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(pygame.mouse.get_pos())
                    
            pygame.display.flip()
            self.clock.tick(60)
            
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    game = CardGame()
    print("=== 卡牌构建游戏 ===")
    print("操作说明：")
    print("- 鼠标左键点击手牌使用卡牌")
    print("- 点击'结束回合'让敌人行动并开始新回合")
    print("- 击败敌人后进入商店购买新卡牌")
    print("- 在商店点击卡牌购买，点击'继续冒险'开始下一层")
    game.run()
