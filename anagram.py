import pygame
import random
import string

pygame.init()

WIDTH, HEIGHT = 800, 600

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLUE = (0, 100, 200)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("字母重组")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 50)
big_font = pygame.font.Font(None, 80)
small_font = pygame.font.Font(None, 30)

WORDS = [
    "PYTHON", "GAME", "CODE", "PLAY", "FUN", "WIN", "JUMP", "SHOOT",
    "MOVE", "FAST", "SKILL", "LEVEL", "SCORE", "POWER", "MUSIC", "SOUND",
    "START", "FINISH", "PLAYER", "COMPUTER", "KEYBOARD", "MONITOR", "MOUSE"
]

def shuffle_word(word):
    while True:
        shuffled = ''.join(random.sample(word, len(word)))
        if shuffled != word:
            return shuffled

def anagram():
    word = random.choice(WORDS)
    scrambled = shuffle_word(word)
    
    user_input = ""
    score = 0
    time_left = 60
    game_over = False
    start_ticks = pygame.time.get_ticks()
    streak = 0
    
    while not game_over:
        screen.fill(BLACK)
        
        elapsed = int((pygame.time.get_ticks() - start_ticks) / 1000)
        time_left = max(0, 60 - elapsed)
        
        if time_left == 0:
            game_over = True
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if user_input.upper() == word:
                        score += 100 + streak * 10
                        streak += 1
                        word = random.choice(WORDS)
                        scrambled = shuffle_word(word)
                    else:
                        score = max(0, score - 20)
                        streak = 0
                    user_input = ""
                elif event.key == pygame.K_BACKSPACE:
                    user_input = user_input[:-1]
                elif event.unicode.isalpha():
                    user_input += event.unicode.upper()
        
        scrambled_text = big_font.render(scrambled, True, BLUE)
        screen.blit(scrambled_text, (WIDTH//2 - scrambled_text.get_width()//2, 100))
        
        instruction = small_font.render("重组字母成正确的单词 (按回车确认)", True, WHITE)
        screen.blit(instruction, (WIDTH//2 - instruction.get_width()//2, 180))
        
        input_color = GREEN if user_input.upper() == word else WHITE
        input_text = big_font.render(user_input + "|", True, input_color)
        screen.blit(input_text, (WIDTH//2 - 150, 300))
        
        score_text = font.render(f"得分: {score}", True, WHITE)
        screen.blit(score_text, (50, 30))
        
        time_text = font.render(f"时间: {time_left}秒", True, WHITE)
        screen.blit(time_text, (WIDTH - 150, 30))
        
        streak_text = font.render(f"连续: {streak}", True, GREEN)
        screen.blit(streak_text, (WIDTH//2 - 50, 30))
        
        pygame.display.update()
        clock.tick(30)
    
    screen.fill(BLACK)
    result_text = big_font.render(f"最终得分: {score}", True, WHITE)
    screen.blit(result_text, (WIDTH//2 - result_text.get_width()//2, HEIGHT//2 - 50))
    
    wpm = int(score / 10)
    wpm_text = font.render(f"效率评分: {wpm}", True, GREEN)
    screen.blit(wpm_text, (WIDTH//2 - wpm_text.get_width()//2, HEIGHT//2 + 50))
    
    pygame.display.update()
    pygame.time.wait(5000)
    pygame.quit()

if __name__ == "__main__":
    anagram()