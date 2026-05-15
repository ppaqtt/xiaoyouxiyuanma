import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("文字冒险故事")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 255)
GRAY = (100, 100, 100)

class TextAdventure:
    def __init__(self):
        self.font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 24)
        self.story_index = 0
        
        self.stories = [
            {
                "text": "你醒来发现自己躺在一片神秘的森林中。四周漆黑一片，只有远处有微弱的光芒。",
                "choices": ["朝着光芒走去", "在原地等待", "尝试返回"]
            },
            {
                "text": "你朝着光芒走去，发现了一座古老的城堡。城堡的大门半开着，里面传来奇怪的声音。",
                "choices": ["进入城堡", "在门外呼喊", "转身离开"]
            },
            {
                "text": "你进入城堡，发现里面布满了蜘蛛网和灰尘。突然，你听到了脚步声...",
                "choices": ["躲在柱子后面", "继续前进", "快速逃跑"]
            },
            {
                "text": "你躲在柱子后面，看到一个神秘的身影走过。他似乎在寻找什么东西。",
                "choices": ["跟随他", "趁他不注意溜走", "主动打招呼"]
            },
            {
                "text": "恭喜你！你发现了城堡的秘密，成为了新的守护者。",
                "choices": ["重新开始"]
            }
        ]

    def draw(self):
        screen.fill(BLACK)
        
        story = self.stories[self.story_index]
        
        title_text = self.font.render("神秘森林冒险", True, BLUE)
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 30))
        
        text_lines = self.wrap_text(story["text"], 700)
        y = 100
        for line in text_lines:
            text = self.small_font.render(line, True, WHITE)
            screen.blit(text, (50, y))
            y += 30
        
        y += 30
        for i, choice in enumerate(story["choices"]):
            choice_text = self.small_font.render(f"{i+1}. {choice}", True, BLUE)
            pygame.draw.rect(screen, GRAY, (50, y, 700, 40))
            screen.blit(choice_text, (60, y + 8))
            y += 50

    def wrap_text(self, text, max_width):
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + word + " "
            test_surface = self.small_font.render(test_line, True, WHITE)
            if test_surface.get_width() <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "
        
        lines.append(current_line)
        return lines

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_1, pygame.K_KP1]:
                self.make_choice(0)
            elif event.key in [pygame.K_2, pygame.K_KP2]:
                self.make_choice(1)
            elif event.key in [pygame.K_3, pygame.K_KP3]:
                self.make_choice(2)

    def make_choice(self, choice):
        if self.story_index < len(self.stories) - 1:
            self.story_index += 1
        else:
            self.story_index = 0

game = TextAdventure()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        game.handle_input(event)
    
    game.draw()
    pygame.display.flip()

pygame.quit()