import pygame
import random

pygame.init()

WIDTH, HEIGHT = 800, 600

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 128, 0)
RED = (255, 0, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("21点")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 40)
big_font = pygame.font.Font(None, 60)

def create_deck():
    suits = ['♠', '♥', '♦', '♣']
    ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    return [(rank, suit) for suit in suits for rank in ranks]

def draw_card(x, y, rank, suit, face_up=True):
    if face_up:
        pygame.draw.rect(screen, WHITE, (x, y, 70, 100), 2)
        pygame.draw.line(screen, WHITE, (x, y), (x+70, y+100), 2)
        pygame.draw.line(screen, WHITE, (x+70, y), (x, y+100), 2)
        text = font.render(f"{rank}{suit}", True, WHITE)
        screen.blit(text, (x + 10, y + 30))
    else:
        pygame.draw.rect(screen, RED, (x, y, 70, 100), 2)

def calculate_score(cards):
    score = 0
    aces = 0
    for rank, suit in cards:
        if rank in ['J', 'Q', 'K']:
            score += 10
        elif rank == 'A':
            aces += 1
            score += 11
        else:
            score += int(rank)
    
    while score > 21 and aces > 0:
        score -= 10
        aces -= 1
    
    return score

def blackjack():
    deck = create_deck()
    random.shuffle(deck)
    
    player_cards = [deck.pop() for _ in range(2)]
    dealer_cards = [deck.pop() for _ in range(2)]
    
    player_turn = True
    game_over = False
    result = None
    
    while not game_over:
        screen.fill(GREEN)
        
        mouse = pygame.mouse.get_pos()
        hit_button = pygame.Rect(WIDTH//2 - 100, HEIGHT - 150, 80, 40)
        stand_button = pygame.Rect(WIDTH//2, HEIGHT - 150, 80, 40)
        new_game_button = pygame.Rect(WIDTH//2 - 60, HEIGHT - 80, 120, 40)
        
        pygame.draw.rect(screen, BLACK, hit_button)
        pygame.draw.rect(screen, BLACK, stand_button)
        
        hit_text = font.render("要牌", True, WHITE)
        stand_text = font.render("停牌", True, WHITE)
        screen.blit(hit_text, (hit_button.x + 20, hit_button.y + 10))
        screen.blit(stand_text, (stand_button.x + 20, stand_button.y + 10))
        
        for i, (rank, suit) in enumerate(player_cards):
            draw_card(100 + i * 80, 100, rank, suit)
        
        dealer_score_text = font.render(f"庄家: {calculate_score([dealer_cards[0]])}", True, WHITE)
        screen.blit(dealer_score_text, (100, 50))
        
        for i, (rank, suit) in enumerate(dealer_cards):
            draw_card(100 + i * 80, 250, rank, suit, face_up=(i == 0 or not player_turn))
        
        player_score = calculate_score(player_cards)
        player_score_text = font.render(f"玩家: {player_score}", True, WHITE)
        screen.blit(player_score_text, (100, 350))
        
        if game_over:
            pygame.draw.rect(screen, BLACK, new_game_button)
            new_game_text = font.render("重新开始", True, WHITE)
            screen.blit(new_game_text, (new_game_button.x + 15, new_game_button.y + 10))
        
        if result:
            result_text = big_font.render(result, True, RED if "输" in result else WHITE)
            screen.blit(result_text, (WIDTH//2 - result_text.get_width()//2, HEIGHT//2))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if hit_button.collidepoint(mouse) and player_turn and not game_over:
                    player_cards.append(deck.pop())
                    if calculate_score(player_cards) > 21:
                        result = "玩家爆牌! 你输了!"
                        game_over = True
                elif stand_button.collidepoint(mouse) and player_turn and not game_over:
                    player_turn = False
                    while calculate_score(dealer_cards) < 17:
                        dealer_cards.append(deck.pop())
                    
                    player_score = calculate_score(player_cards)
                    dealer_score = calculate_score(dealer_cards)
                    
                    if dealer_score > 21:
                        result = "庄家爆牌! 你赢了!"
                    elif player_score > dealer_score:
                        result = "你赢了!"
                    elif player_score < dealer_score:
                        result = "你输了!"
                    else:
                        result = "平局!"
                    game_over = True
                elif new_game_button.collidepoint(mouse) and game_over:
                    blackjack()
                    return
        
        pygame.display.update()
        clock.tick(30)

if __name__ == "__main__":
    blackjack()