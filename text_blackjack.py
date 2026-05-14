"""
文字21点
经典的21点游戏
"""

import pygame
import sys
import random

pygame.init()

WIDTH, HEIGHT = 850, 620
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("文字21点")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
DARK_GRAY = (50, 50, 50)
GREEN = (0, 120, 0)
RED = (200, 50, 50)
BLUE = (0, 100, 200)
GOLD = (255, 215, 0)

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
        pygame.draw.rect(screen, bg, (x, y, 60, 85), border_radius=5)
        pygame.draw.rect(screen, BLACK, (x, y, 60, 85), 2, border_radius=5)
        
        if self.face_up:
            font1 = pygame.font.Font(None, 32)
            font2 = pygame.font.Font(None, 48)
            rank_text = font1.render(self.rank, True, color)
            suit_text = font2.render(self.suit, True, color)
            screen.blit(rank_text, (x + 8, y + 8))
            screen.blit(suit_text, (x + 15, y + 38))

class Blackjack:
    def __init__(self):
        self.phase = "menu"
        self.deck = []
        self.player_hand = []
        self.dealer_hand = []
        self.player_money = 1000
        self.bet = 50
        self.font_large = pygame.font.Font(None, 56)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 26)
    
    def create_deck(self):
        self.deck = []
        for _ in range(6):
            for suit in suits:
                for rank in ranks:
                    self.deck.append(Card(suit, rank))
        random.shuffle(self.deck)
    
    def deal(self):
        self.create_deck()
        self.player_hand = [self.deck.pop(), self.deck.pop()]
        self.dealer_hand = [self.deck.pop(), self.deck.pop()]
        self.dealer_hand[1].face_up = False
        self.phase = "player_turn"
    
    def hit(self):
        self.player_hand.append(self.deck.pop())
        if self.get_value(self.player_hand) > 21:
            self.end_game(False)
    
    def stand(self):
        self.dealer_hand[1].face_up = True
        
        while self.get_value(self.dealer_hand) < 17:
            self.dealer_hand.append(self.deck.pop())
        
        dealer_score = self.get_value(self.dealer_hand)
        player_score = self.get_value(self.player_hand)
        
        if dealer_score > 21 or player_score > dealer_score:
            self.end_game(True)
        elif player_score < dealer_score:
            self.end_game(False)
        else:
            self.end_game(None)
    
    def get_value(self, hand):
        value = 0
        aces = 0
        
        for card in hand:
            value += card.value()
            if card.rank == 'A':
                aces += 1
        
        while value > 21 and aces > 0:
            value -= 10
            aces -= 1
        
        return value
    
    def end_game(self, player_won):
        self.phase = "gameover"
        
        if player_won is True:
            self.player_money += self.bet
        elif player_won is False:
            self.player_money -= self.bet
    
    def draw(self):
        screen.fill(GREEN)
        
        if self.phase == "menu":
            self.draw_menu()
        else:
            self.draw_game()
        
        pygame.display.flip()
    
    def draw_menu(self):
        title = self.font_large.render("21点", True, GOLD)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        
        instructions = [
            "二十一点游戏",
            "Hit 要牌",
            "Stand 停牌",
            "",
            "按 空格键 开始!"
        ]
        
        y = 220
        for line in instructions:
            text = self.font_medium.render(line, True, WHITE)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, y))
            y += 40
    
    def draw_game(self):
        # 庄家区域
        pygame.draw.rect(screen, (0, 80, 0), (WIDTH//2 - 250, 40, 500, 150), border_radius=10)
        dealer_text = self.font_medium.render("庄家", True, WHITE)
        screen.blit(dealer_text, (WIDTH//2 - dealer_text.get_width()//2, 50))
        
        for i, card in enumerate(self.dealer_hand):
            card.draw(WIDTH//2 - 100 + i * 70, 80)
        
        if self.dealer_hand[1].face_up:
            score = self.font_small.render(f"点数: {self.get_value(self.dealer_hand)}", True, WHITE)
            screen.blit(score, (WIDTH//2 - score.get_width()//2, 175))
        
        # 玩家区域
        pygame.draw.rect(screen, (0, 80, 0), (WIDTH//2 - 250, HEIGHT - 230, 500, 150), border_radius=10)
        player_text = self.font_medium.render("玩家", True, WHITE)
        screen.blit(player_text, (WIDTH//2 - player_text.get_width()//2, HEIGHT - 220))
        
        for i, card in enumerate(self.player_hand):
            card.draw(WIDTH//2 - 100 + i * 70, HEIGHT - 190)
        
        score = self.font_small.render(f"点数: {self.get_value(self.player_hand)}", True, WHITE)
        screen.blit(score, (WIDTH//2 - score.get_width()//2, HEIGHT - 85))
        
        # 金钱和下注
        money = self.font_medium.render(f"💰 {self.player_money}", True, GOLD)
        screen.blit(money, (50, HEIGHT - 70))
        
        bet_text = self.font_small.render(f"下注: {self.bet}", True, WHITE)
        screen.blit(bet_text, (50, HEIGHT - 35))
        
        # 按钮
        if self.phase == "player_turn":
            buttons = [
                ("Hit (要牌)", BLUE, WIDTH//2 - 180, HEIGHT - 45),
                ("Stand (停牌)", RED, WIDTH//2 + 20, HEIGHT - 45)
            ]
            
            for text, color, x, y in buttons:
                btn = pygame.Rect(x, y, 160, 45)
                pygame.draw.rect(screen, color, btn, border_radius=8)
                t = self.font_medium.render(text, True, WHITE)
                screen.blit(t, (x + 15, y + 8))
        
        if self.phase == "gameover":
            # 显示结果
            player_score = self.get_value(self.player_hand)
            dealer_score = self.get_value(self.dealer_hand)
            
            result = ""
            if player_score > 21:
                result = "爆牌了! 你输了!"
            elif dealer_score > 21:
                result = "庄家爆牌! 你赢了!"
            elif player_score > dealer_score:
                result = "你赢了!"
            elif player_score < dealer_score:
                result = "你输了!"
            else:
                result = "平局!"
            
            result_text = self.font_large.render(result, True, YELLOW if 'YELLOW' in globals() else GOLD)
            screen.blit(result_text, (WIDTH//2 - result_text.get_width()//2, HEIGHT//2 - 30))
            
            restart = self.font_medium.render("按 R 再来一局", True, WHITE)
            screen.blit(restart, (WIDTH//2 - restart.get_width()//2, HEIGHT//2 + 40))
    
    def handle_click(self, pos):
        if self.phase == "player_turn":
            buttons = [
                ("hit", WIDTH//2 - 180, HEIGHT - 45),
                ("stand", WIDTH//2 + 20, HEIGHT - 45)
            ]
            
            for action, x, y in buttons:
                btn = pygame.Rect(x, y, 160, 45)
                if btn.collidepoint(pos):
                    if action == "hit":
                        self.hit()
                    elif action == "stand":
                        self.stand()
    
    def handle_key(self, key):
        if self.phase == "menu":
            if key == pygame.K_SPACE:
                self.deal()
        elif self.phase == "gameover":
            if key == pygame.K_r:
                self.phase = "menu"

def main():
    game = Blackjack()
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
