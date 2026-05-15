import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("侦探推理故事")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 255)
RED = (200, 50, 50)
GREEN = (50, 200, 50)

class DetectiveStory:
    def __init__(self):
        self.font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 24)
        self.clue_index = 0
        self.solved = False
        
        self.clues = [
            {
                "text": "案发现场：一家珠宝店被盗。店主声称昨晚关门时一切正常，但今早发现保险柜被打开，珠宝不翼而飞。",
                "question": "你首先想调查什么？",
                "options": ["保险柜的锁", "监控录像", "现场脚印"]
            },
            {
                "text": "你检查了保险柜的锁，发现没有被撬动的痕迹。锁是电子密码锁，需要指纹和密码双重验证。",
                "question": "下一步调查什么？",
                "options": ["询问店员", "检查后门", "查看库存记录"]
            },
            {
                "text": "你询问了店员，发现只有店主和两名店员有密码和指纹权限。昨晚值班的是小王。",
                "question": "你认为谁最可疑？",
                "options": ["店主", "小王", "另一名店员小李"]
            },
            {
                "text": "你发现小王最近有赌博欠债的记录，而且他的银行账户昨天收到了一笔大额转账。",
                "question": "你决定？",
                "options": ["逮捕小王", "继续调查", "询问转账来源"]
            },
            {
                "text": "真相大白！小王确实是盗窃犯。他利用值班机会盗取了珠宝，并通过黑市卖掉。你成功破案！",
                "question": "",
                "options": ["重新开始"]
            }
        ]

    def draw(self):
        screen.fill(BLACK)
        
        clue = self.clues[self.clue_index]
        
        title_text = self.font.render("侦探推理故事", True, BLUE)
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 30))
        
        text_lines = self.wrap_text(clue["text"], 700)
        y = 100
        for line in text_lines:
            text = self.small_font.render(line, True, WHITE)
            screen.blit(text, (50, y))
            y += 30
        
        if clue["question"]:
            y += 20
            question_text = self.font.render(clue["question"], True, GREEN)
            screen.blit(question_text, (50, y))
            
            y += 30
            for i, option in enumerate(clue["options"]):
                option_text = self.small_font.render(f"{i+1}. {option}", True, BLUE)
                pygame.draw.rect(screen, (50, 50, 50), (50, y, 700, 40))
                screen.blit(option_text, (60, y + 8))
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
        if self.clue_index < len(self.clues) - 1:
            self.clue_index += 1
        else:
            self.clue_index = 0

game = DetectiveStory()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        game.handle_input(event)
    
    game.draw()
    pygame.display.flip()

pygame.quit()