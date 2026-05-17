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
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 100, 200)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("贪吃蛇单词版")

clock = pygame.time.Clock()
font = get_chinese_font(30)

WORDS = [
    "APPLE", "BREAD", "CAKE", "DOOR", "EGGS",
    "FISH", "GRAPE", "HOUSE", "ICECREAM", "JUICE",
    "KING", "LAMP", "MILK", "NUTS", "OLIVE",
    "PIZZA", "QUEEN", "RICE", "SALT", "TEA",
    "UMbrella", "VANILLA", "WATER", "XRAY", "YOGURT",
    "ZEBRA", "PYTHON", "GAME", "PLAY", "SCORE"
]

class WordSnake:
    def __init__(self):
        self.body = [(WIDTH // 40, HEIGHT // 40 // 2)]
        self.direction = (1, 0)
        self.grow_word = True
        self.current_word = random.choice(WORDS)
        self.display_word = self.current_word
        self.word_index = 0
    
    def move(self):
        head = self.body[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
        
        if (new_head[0] < 0 or new_head[0] >= WIDTH // 40 or
            new_head[1] < 0 or new_head[1] >= HEIGHT // 40 or
            new_head in self.body):
            return False
        
        self.body.insert(0, new_head)
        
        if self.grow_word and self.word_index < len(self.current_word):
            self.display_word = self.current_word[:self.word_index + 1]
            self.word_index += 1
            if self.word_index >= len(self.current_word):
                self.grow_word = False
        else:
            self.body.pop()
        
        return True
    
    def draw(self):
        for segment in self.body:
            pygame.draw.rect(screen, GREEN,
                           (segment[0]*40, segment[1]*40, 38, 38), border_radius=5)

def get_letter_position(word_snake):
    if len(word_snake.body) > word_snake.word_index:
        return word_snake.body[word_snake.word_index]
    return None

def word_snake_game():
    snake = WordSnake()
    score = 0
    letters_collected = 0
    game_over = False
    
    while not game_over:
        screen.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and snake.direction != (0, 1):
                    snake.direction = (0, -1)
                elif event.key == pygame.K_DOWN and snake.direction != (0, -1):
                    snake.direction = (0, 1)
                elif event.key == pygame.K_LEFT and snake.direction != (1, 0):
                    snake.direction = (-1, 0)
                elif event.key == pygame.K_RIGHT and snake.direction != (-1, 0):
                    snake.direction = (1, 0)
        
        if not snake.move():
            game_over = True
        
        if len(snake.body) == 1 or snake.word_index >= len(snake.current_word):
            score += len(snake.current_word) * 10
            letters_collected += len(snake.current_word)
            snake.current_word = random.choice(WORDS)
            snake.word_index = 0
            snake.grow_word = True
            snake.display_word = ""
        
        snake.draw()
        
        letter_pos = get_letter_position(snake)
        if letter_pos:
            display_text = snake.display_word + snake.current_word[snake.word_index:]
            text = font.render(display_text, True, BLUE)
            x = letter_pos[0] * 40 + 40
            y = letter_pos[1] * 40 + 20
            screen.blit(text, (x, y))
        
        word_hint = font.render(f"单词: {snake.current_word}", True, WHITE)
        screen.blit(word_hint, (10, 10))
        
        progress = font.render(f"进度: {snake.word_index}/{len(snake.current_word)}", True, GREEN)
        screen.blit(progress, (10, 50))
        
        score_text = font.render(f"得分: {score}", True, WHITE)
        screen.blit(score_text, (WIDTH - 150, 10))
        
        collected_text = font.render(f"收集: {letters_collected}", True, WHITE)
        screen.blit(collected_text, (WIDTH - 150, 50))
        
        instruction_text = font.render("方向键移动 | 收集字母组成单词", True, WHITE)
        screen.blit(instruction_text, (WIDTH//2 - instruction_text.get_width()//2, HEIGHT - 30))
        
        pygame.display.update()
        clock.tick(10)
    
    screen.fill(BLACK)
    result_text = font.render(f"游戏结束! 得分: {score} 收集字母: {letters_collected}", True, WHITE)
    screen.blit(result_text, (WIDTH//2 - result_text.get_width()//2, HEIGHT//2))
    pygame.display.update()
    pygame.time.wait(3000)
    pygame.quit()

if __name__ == "__main__":
    word_snake_game()