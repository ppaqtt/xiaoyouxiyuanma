import pygame
import random
import time

pygame.init()

WIDTH, HEIGHT = 800, 600

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (200, 0, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("打字练习")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 40)
small_font = pygame.font.Font(None, 30)
big_font = pygame.font.Font(None, 80)

WORDS = [
    "apple", "banana", "cherry", "date", "elder",
    "flower", "garden", "house", "island", "juice",
    "kitchen", "lemon", "mango", "north", "orange",
    "pizza", "queen", "rain", "sun", "tiger",
    "unity", "victory", "water", "xray", "yellow",
    "zebra", "python", "coding", "game", "happy"
]

def typing_practice():
    score = 0
    time_left = 60
    start_time = time.time()
    current_word = random.choice(WORDS)
    user_input = ""
    game_over = False
    
    while not game_over:
        screen.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if user_input == current_word:
                        score += 10
                        current_word = random.choice(WORDS)
                    user_input = ""
                elif event.key == pygame.K_BACKSPACE:
                    user_input = user_input[:-1]
                else:
                    if len(user_input) < 20 and event.unicode.isalpha():
                        user_input += event.unicode
        
        elapsed = int(time.time() - start_time)
        time_left = max(0, 60 - elapsed)
        
        if time_left == 0:
            game_over = True
        
        word_text = big_font.render(current_word, True, WHITE)
        screen.blit(word_text, (WIDTH // 2 - word_text.get_width() // 2, 100))
        
        input_color = GREEN if user_input == current_word[:len(user_input)] else RED
        input_text = big_font.render(user_input, True, input_color)
        screen.blit(input_text, (WIDTH // 2 - input_text.get_width() // 2, 250))
        
        score_text = font.render(f"得分: {score}", True, WHITE)
        time_text = font.render(f"时间: {time_left}秒", True, WHITE)
        screen.blit(score_text, (50, 50))
        screen.blit(time_text, (WIDTH - 200, 50))
        
        instruction_text = small_font.render("输入单词后按回车确认", True, WHITE)
        screen.blit(instruction_text, (WIDTH // 2 - instruction_text.get_width() // 2, HEIGHT - 50))
        
        pygame.display.update()
        clock.tick(30)
    
    screen.fill(BLACK)
    result_text = big_font.render(f"最终得分: {score}", True, WHITE)
    screen.blit(result_text, (WIDTH // 2 - result_text.get_width() // 2, HEIGHT // 2 - 50))
    
    wpm = int(score * 0.5)
    wpm_text = font.render(f"约 {wpm} WPM", True, GREEN)
    screen.blit(wpm_text, (WIDTH // 2 - wpm_text.get_width() // 2, HEIGHT // 2 + 50))
    
    pygame.display.update()
    pygame.time.wait(5000)
    pygame.quit()

if __name__ == "__main__":
    typing_practice()