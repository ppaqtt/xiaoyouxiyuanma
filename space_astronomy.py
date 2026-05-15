import pygame
import random
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("太空探索")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)

planets = [
    {"name": "水星", "color": (169, 169, 169), "distance": 100, "size": 15},
    {"name": "金星", "color": (255, 215, 0), "distance": 150, "size": 20},
    {"name": "地球", "color": (0, 150, 255), "distance": 200, "size": 22},
    {"name": "火星", "color": (255, 100, 50), "distance": 260, "size": 18},
    {"name": "木星", "color": (200, 180, 100), "distance": 350, "size": 40},
    {"name": "土星", "color": (255, 200, 100), "distance": 450, "size": 35},
    {"name": "天王星", "color": (100, 200, 255), "distance": 520, "size": 28},
    {"name": "海王星", "color": (50, 100, 255), "distance": 580, "size": 27}
]

class SpaceGame:
    def __init__(self):
        self.score = 0
        self.current_planet = None
        self.selected_planet = None
        self.font = pygame.font.Font(None, 40)
        self.small_font = pygame.font.Font(None, 24)
        self.next_question()

    def next_question(self):
        self.current_planet = random.choice(planets)
        self.selected_planet = None

    def draw(self):
        screen.fill(BLACK)
        
        stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(100)]
        for star in stars:
            pygame.draw.circle(screen, WHITE, star, 1)
        
        pygame.draw.circle(screen, YELLOW, (WIDTH//2, HEIGHT//2), 30)
        
        for planet in planets:
            x = WIDTH//2 + planet["distance"]
            y = HEIGHT//2 + random.randint(-50, 50)
            pygame.draw.circle(screen, planet["color"], (x, y), planet["size"])
        
        question_text = self.font.render(f"问题: 找到{self.current_planet['name']}", True, WHITE)
        screen.blit(question_text, (50, 30))
        
        score_text = self.small_font.render(f"分数: {self.score}", True, WHITE)
        screen.blit(score_text, (50, 70))

    def handle_click(self, pos):
        for planet in planets:
            x = WIDTH//2 + planet["distance"]
            y = HEIGHT//2
            distance = ((pos[0] - x)**2 + (pos[1] - y)**2)**0.5
            if distance < planet["size"] + 10:
                if planet["name"] == self.current_planet["name"]:
                    self.score += 10
                else:
                    self.score -= 5
                self.next_question()
                break

game = SpaceGame()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            game.handle_click(pygame.mouse.get_pos())
    
    game.draw()
    pygame.display.flip()

pygame.quit()