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
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLUE = (0, 100, 200)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("单词拼写")

clock = pygame.time.Clock()
font = get_chinese_font(40)
big_font = get_chinese_font(80)

WORDS = [
    "PYTHON", "GAME", "CODE", "PLAY", "FUN", "WIN",
    "JUMP", "SHOOT", "MOVE", "FAST", "SKILL",
    "LEVEL", "SCORE", "POWER", "MUSIC", "SOUND",
    "START", "FINISH", "PLAYER", "COMPUTER"
]

def word_scramble():
    word = random.choice(WORDS)
    scrambled = ''.join(random.sample(word, len(word)))
    
    user_input = ""
    score = 0
    words_solved = 0
    time_left = 120
    game_over = False
    start_ticks = pygame.time.get_ticks()
    feedback = ""
    feedback_color = WHITE
    
    while not game_over:
        screen.fill(BLACK)
        
        elapsed = int((pygame.time.get_ticks() - start_ticks) / 1000)
        time_left = max(0, 120 - elapsed)
        
        if time_left == 0:
            game_over = True
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if user_input.upper() == word:
                        score += 100 + len(word) * 10
                        words_solved += 1
                        feedback = "正确!"
                        feedback_color = GREEN
                        word = random.choice(WORDS)
                        scrambled = ''.join(random.sample(word, len(word)))
                    else:
                        feedback = "错误!"
                        feedback_color = RED
                    user_input = ""
                elif event.key == pygame.K_BACKSPACE:
                    user_input = user_input[:-1]
                elif event.unicode.isalpha():
                    user_input += event.unicode
        
        scrambled_text = big_font.render(scrambled, True, BLUE)
        screen.blit(scrambled_text, (WIDTH // 2 - scrambled_text.get_width() // 2, 100))
        
        instruction = font.render("重新排列单词拼写正确答案", True, WHITE)
        screen.blit(instruction, (WIDTH // 2 - instruction.get_width() // 2, 180))
        
        input_text = big_font.render(user_input, True, WHITE)
        screen.blit(input_text, (WIDTH // 2 - input_text.get_width() // 2, 300))
        
        if feedback:
            feedback_text = font.render(feedback, True, feedback_color)
            screen.blit(feedback_text, (WIDTH // 2 - feedback_text.get_width() // 2, 400))
        
        score_text = font.render(f"得分: {score}", True, WHITE)
        time_text = font.render(f"时间: {time_left}秒", True, WHITE)
        solved_text = font.render(f"已解: {words_solved}", True, WHITE)
        
        screen.blit(score_text, (50, 30))
        screen.blit(time_text, (WIDTH - 150, 30))
        screen.blit(solved_text, (WIDTH // 2 - 60, 30))
        
        pygame.display.update()
        clock.tick(30)
    
    screen.fill(BLACK)
    result_text = big_font.render(f"最终得分: {score}", True, WHITE)
    screen.blit(result_text, (WIDTH // 2 - result_text.get_width() // 2, HEIGHT // 2 - 50))
    
    stats_text = font.render(f"解决单词: {words_solved}", True, GREEN)
    screen.blit(stats_text, (WIDTH // 2 - stats_text.get_width() // 2, HEIGHT // 2 + 50))
    
    pygame.display.update()
    pygame.time.wait(5000)
    pygame.quit()

if __name__ == "__main__":
    word_scramble()