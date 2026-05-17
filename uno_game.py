import pygame
import os
import random

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

WIDTH, HEIGHT = 800, 600

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

COLORS = [RED, GREEN, BLUE, YELLOW]
VALUES = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("UNO游戏")

clock = pygame.time.Clock()
font = get_chinese_font(30)

class Card:
    def __init__(self, color, value):
        self.color = color
        self.value = value
    
    def can_play(self, other_card):
        return self.color == other_card.color or self.value == other_card.value
    
    def draw(self, x, y, width=70, height=100):
        pygame.draw.rect(screen, self.color, (x, y, width, height), border_radius=8)
        pygame.draw.rect(screen, WHITE, (x + 5, y + 5, width - 10, height - 10), border_radius=5)
        
        value_text = font.render(self.value, True, self.color)
        screen.blit(value_text, (x + width // 2 - 10, y + height // 2 - 15))

def create_deck():
    deck = []
    for color in COLORS:
        for value in VALUES:
            deck.append(Card(color, value))
            if value != '0':
                deck.append(Card(color, value))
    random.shuffle(deck)
    return deck

def uno_game():
    deck = create_deck()
    player_hand = deck[:7]
    ai_hand = deck[7:14]
    discard_pile = [deck[14]]
    draw_pile = deck[15:]
    
    player_turn = True
    game_over = False
    winner = None
    
    def draw_card():
        nonlocal draw_pile
        if len(draw_pile) == 0:
            top_card = discard_pile.pop()
            draw_pile = discard_pile
            random.shuffle(draw_pile)
            discard_pile = [top_card]
        return draw_pile.pop()
    
    while not game_over:
        screen.fill(GREEN)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN and player_turn:
                x, y = event.pos
                for i, card in enumerate(player_hand):
                    card_x = 50 + i * 80
                    card_y = HEIGHT - 150
                    if card_x < x < card_x + 70 and card_y < y < card_y + 100:
                        if card.can_play(discard_pile[-1]):
                            discard_pile.append(player_hand.pop(i))
                            player_turn = False
                        break
        
        if not player_turn and not game_over:
            pygame.time.wait(800)
            played = False
            for i, card in enumerate(ai_hand):
                if card.can_play(discard_pile[-1]):
                    discard_pile.append(ai_hand.pop(i))
                    played = True
                    break
            if not played:
                ai_hand.append(draw_card())
            player_turn = True
        
        for i, card in enumerate(ai_hand):
            card_x = 50 + i * 80
            card_y = 50
            pygame.draw.rect(screen, BLUE, (card_x, card_y, 70, 100), border_radius=8)
            pygame.draw.rect(screen, BLACK, (card_x + 10, card_y + 10, 50, 80), border_radius=5)
        
        discard_pile[-1].draw(WIDTH // 2 - 35, HEIGHT // 2 - 50)
        
        for i, card in enumerate(player_hand):
            card_x = 50 + i * 80
            card_y = HEIGHT - 150
            card.draw(card_x, card_y)
        
        player_count = font.render(f"玩家手牌: {len(player_hand)}", True, WHITE)
        ai_count = font.render(f"AI手牌: {len(ai_hand)}", True, WHITE)
        turn_text = font.render(f"轮到: {'玩家' if player_turn else 'AI'}", True, WHITE)
        
        screen.blit(player_count, (10, HEIGHT - 50))
        screen.blit(ai_count, (WIDTH - 150, 10))
        screen.blit(turn_text, (WIDTH // 2 - 50, 10))
        
        if len(player_hand) == 0:
            game_over = True
            winner = "玩家"
        elif len(ai_hand) == 0:
            game_over = True
            winner = "AI"
        
        pygame.display.update()
        clock.tick(30)
    
    screen.fill(BLACK)
    result_text = font.render(f"游戏结束! {winner}获胜!", True, WHITE)
    screen.blit(result_text, (WIDTH//2 - 100, HEIGHT//2))
    pygame.display.update()
    pygame.time.wait(3000)
    pygame.quit()

if __name__ == "__main__":
    uno_game()