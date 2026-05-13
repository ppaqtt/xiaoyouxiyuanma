import pygame
import random

pygame.init()

WIDTH, HEIGHT = 800, 600

BLACK = (0, 0, 0)
GREEN = (0, 120, 0)
WHITE = (255, 255, 255)
RED = (200, 0, 0)
BLUE = (0, 0, 200)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("接龙游戏")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 30)

SUITS = ['♠', '♥', '♦', '♣']
RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']

class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.face_up = False
        self.x = 0
        self.y = 0
        self.dragging = False
    
    def color(self):
        return RED if self.suit in ['♥', '♦'] else BLACK
    
    def value(self):
        if self.rank == 'A':
            return 1
        elif self.rank == 'J':
            return 11
        elif self.rank == 'Q':
            return 12
        elif self.rank == 'K':
            return 13
        else:
            return int(self.rank)
    
    def draw(self):
        pygame.draw.rect(screen, WHITE, (self.x, self.y, 70, 100), border_radius=5)
        if self.face_up:
            color = self.color()
            text = font.render(f"{self.rank}{self.suit}", True, color)
            screen.blit(text, (self.x + 10, self.y + 35))
        else:
            pygame.draw.rect(screen, BLUE, (self.x + 5, self.y + 5, 60, 90), border_radius=3)
        
        pygame.draw.rect(screen, BLACK, (self.x, self.y, 70, 100), 2, border_radius=5)

def create_deck():
    deck = [Card(rank, suit) for suit in SUITS for rank in RANKS]
    random.shuffle(deck)
    return deck

def solitaire():
    deck = create_deck()
    
    piles = []
    for i in range(7):
        pile = []
        for j in range(i + 1):
            card = deck.pop()
            card.x = 50 + i * 100
            card.y = 200 + j * 30
            if j == i:
                card.face_up = True
            pile.append(card)
        piles.append(pile)
    
    stock = deck
    waste = []
    foundations = [[] for _ in range(4)]
    
    selected = None
    
    running = True
    while running:
        screen.fill(GREEN)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                
                if 50 <= x <= 120 and 50 <= y <= 150 and stock:
                    waste.append(stock.pop())
                    waste[-1].x = 200
                    waste[-1].y = 50
                    waste[-1].face_up = True
                    if len(stock) == 0:
                        stock = list(reversed(waste))
                        waste = []
                        for card in stock:
                            card.face_up = False
                            card.x = 50
                            card.y = 50
                
                for i, pile in enumerate(piles):
                    for j, card in enumerate(reversed(pile)):
                        if card.face_up and (card.x <= x <= card.x + 70 and card.y <= y <= card.y + 100):
                            selected = (i, len(pile) - 1 - j)
                            break
                    if selected:
                        break
        
        if waste:
            waste[-1].draw()
        
        for i, pile in enumerate(piles):
            for card in pile:
                card.x = 50 + i * 100
                card.draw()
        
        pygame.draw.rect(screen, WHITE, (50, 50, 70, 100), 2, border_radius=5)
        
        for i in range(4):
            pygame.draw.rect(screen, WHITE, (450 + i * 100, 50, 70, 100), 2, border_radius=5)
        
        pygame.display.update()
        clock.tick(30)

if __name__ == "__main__":
    solitaire()