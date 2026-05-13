"""
文字德州扑克
简化版的德州扑克游戏
"""

import pygame
import sys
import random

pygame.init()

WIDTH, HEIGHT = 900, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("文字德州扑克")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
DARK_GRAY = (40, 40, 40)
GREEN = (0, 120, 0)
RED = (200, 50, 50)
BLUE = (0, 100, 200)
GOLD = (255, 215, 0)
PURPLE = (128, 0, 128)

suits = ['♠', '♥', '♦', '♣']
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
        self.face_up = True
    
    def value(self):
        if self.rank in ['J', 'Q', 'K']:
            return 10
        elif self.rank == 'A':
            return 11
        else:
            return int(self.rank)
    
    def draw(self, x, y):
        color = RED if self.suit in ['♥', '♦'] else BLACK
        
        bg = WHITE if self.face_up else DARK_GRAY
        pygame.draw.rect(screen, bg, (x, y, 60, 80), border_radius=5)
        pygame.draw.rect(screen, BLACK, (x, y, 60, 80), 2, border_radius=5)
        
        if self.face_up:
            rank_text = pygame.font.Font(None, 36).render(self.rank, True, color)
            suit_text = pygame.font.Font(None, 48).render(self.suit, True, color)
            screen.blit(rank_text, (x + 8, y + 10))
            screen.blit(suit_text, (x + 15, y + 35))

class TexasHoldem:
    def __init__(self):
        self.phase = "menu"
        self.deck = []
        self.player_hand = []
        self.ai_hand = []
        self.community = []
        self.pot = 0
        self.player_money = 1000
        self.ai_money = 1000
        self.bet = 0
        self.round = 0
        self.font_large = pygame.font.Font(None, 56)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 26)
    
    def create_deck(self):
        self.deck = []
        for suit in suits:
            for rank in ranks:
                self.deck.append(Card(suit, rank))
        random.shuffle(self.deck)
    
    def deal(self):
        self.create_deck()
        self.player_hand = [self.deck.pop(), self.deck.pop()]
        self.ai_hand = [self.deck.pop(), self.deck.pop()]
        self.community = []
        self.ai_hand[0].face_up = False
        self.ai_hand[1].face_up = False
        self.round = 0
        self.bet = 10
        self.pot = 20
        self.player_money -= 10
        self.ai_money -= 10
    
    def next_round(self):
        self.round += 1
        if self.round == 1:
            self.community.extend([self.deck.pop(), self.deck.pop(), self.deck.pop()])
        elif self.round == 2:
            self.community.append(self.deck.pop())
        elif self.round == 3:
            self.community.append(self.deck.pop())
        else:
            self.showdown()
    
    def showdown(self):
        for c in self.ai_hand:
            c.face_up = True
        self.phase = "showdown"
    
    def draw(self):
        screen.fill(GREEN)
        
        if self.phase == "menu":
            self.draw_menu()
        elif self.phase in ["game", "bet", "showdown"]:
            self.draw_game()
        
        pygame.display.flip()
    
    def draw_menu(self):
        title = self.font_large.render("德州扑克", True, GOLD)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        
        instructions = [
            "德州扑克简化版",
            "与电脑对战",
            "",
            "按 空格键 开始!"
        ]
        
        y = 220
        for line in instructions:
            text = self.font_medium.render(line, True, WHITE)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, y))
            y += 40
    
    def draw_game(self):
        # AI区域
        pygame.draw.rect(screen, (0, 80, 0), (WIDTH//2 - 200, 50, 400, 150), border_radius=10)
        ai_text = self.font_medium.render("电脑", True, WHITE)
        screen.blit(ai_text, (WIDTH//2 - ai_text.get_width()//2, 60))
        
        ai_money = self.font_small.render(f"💰 {self.ai_money}", True, GOLD)
        screen.blit(ai_money, (WIDTH//2 - ai_money.get_width()//2, 90))
        
        for i, card in enumerate(self.ai_hand):
            card.draw(WIDTH//2 - 70 + i * 70, 110)
        
        # 公共牌
        pygame.draw.rect(screen, (0, 100, 0), (WIDTH//2 - 220, 220, 440, 120), border_radius=10)
        for i, card in enumerate(self.community):
            card.draw(WIDTH//2 - 160 + i * 70, 250)
        
        pot_text = self.font_medium.render(f"底池: {self.pot}", True, GOLD)
        screen.blit(pot_text, (WIDTH//2 - pot_text.get_width()//2, 360))
        
        # 玩家区域
        pygame.draw.rect(screen, (0, 80, 0), (WIDTH//2 - 200, HEIGHT - 200, 400, 150), border_radius=10)
        player_text = self.font_medium.render("玩家", True, WHITE)
        screen.blit(player_text, (WIDTH//2 - player_text.get_width()//2, HEIGHT - 185))
        
        player_money = self.font_small.render(f"💰 {self.player_money}", True, GOLD)
        screen.blit(player_money, (WIDTH//2 - player_money.get_width()//2, HEIGHT - 155))
        
        for i, card in enumerate(self.player_hand):
            card.draw(WIDTH//2 - 70 + i * 70, HEIGHT - 135)
        
        # 按钮
        if self.phase == "bet" or self.phase == "game":
            buttons = [
                ("弃牌", RED, 150, HEIGHT - 50),
                ("跟注", BLUE, 350, HEIGHT - 50),
                ("加注", GOLD, 550, HEIGHT - 50)
            ]
            
            for text, color, x, y in buttons:
                btn = pygame.Rect(x, y, 160, 45)
                pygame.draw.rect(screen, color, btn, border_radius=8)
                t = self.font_medium.render(text, True, WHITE)
                screen.blit(t, (x + 45, y + 8))
        
        if self.phase == "showdown":
            result = self.font_large.render("摊牌!", True, YELLOW if 'YELLOW' in globals() else GOLD)
            screen.blit(result, (WIDTH//2 - result.get_width()//2, 420))
            
            restart = self.font_medium.render("按 R 重新开始", True, WHITE)
            screen.blit(restart, (WIDTH//2 - restart.get_width()//2, 480))
    
    def handle_click(self, pos):
        if self.phase == "bet" or self.phase == "game":
            buttons = [
                ("fold", 150, HEIGHT - 50),
                ("call", 350, HEIGHT - 50),
                ("raise", 550, HEIGHT - 50)
            ]
            
            for action, x, y in buttons:
                btn = pygame.Rect(x, y, 160, 45)
                if btn.collidepoint(pos):
                    if action == "fold":
                        self.ai_money += self.pot
                        self.phase = "showdown"
                    elif action == "call":
                        amount = min(self.bet, self.player_money)
                        self.player_money -= amount
                        self.pot += amount
                        self.next_round()
                    elif action == "raise":
                        amount = min(self.bet * 2, self.player_money)
                        self.player_money -= amount
                        self.ai_money -= min(amount, self.ai_money)
                        self.pot += amount * 2
                        self.next_round()
    
    def handle_key(self, key):
        if self.phase == "menu":
            if key == pygame.K_SPACE:
                self.deal()
                self.phase = "bet"
        elif self.phase == "showdown":
            if key == pygame.K_r:
                self.phase = "menu"

def main():
    game = TexasHoldem()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    game.handle_click(event.pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                else:
                    game.handle_key(event.key)
        
        game.draw()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
