import pygame
import random
from itertools import permutations

pygame.init()

WIDTH, HEIGHT = 600, 700

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLUE = (0, 100, 200)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("24点游戏")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 40)
big_font = pygame.font.Font(None, 80)
small_font = pygame.font.Font(None, 25)

NUMBERS = []

def generate_numbers():
    return [random.randint(1, 13) for _ in range(4)]

def solve_24(numbers):
    for perm in permutations(numbers):
        for ops in permutations(['+', '-', '*', '/'], 3):
            for p in range(5):
                try:
                    if p == 0:
                        result = eval(f"({perm[0]}{ops[0]}{perm[1]}){ops[1]}{perm[2]}{ops[2]}{perm[3]}")
                    elif p == 1:
                        result = eval(f"(({perm[0]}{ops[0]}{perm[1]}){ops[1]}{perm[2]}){ops[2]}{perm[3]}")
                    elif p == 2:
                        result = eval(f"({perm[0]}{ops[0]}({perm[1]}{ops[1]}{perm[2]})){ops[2]}{perm[3]}")
                    elif p == 3:
                        result = eval(f"{perm[0]}{ops[0]}(({perm[1]}{ops[1]}{perm[2]}){ops[2]}{perm[3]})")
                    else:
                        result = eval(f"{perm[0]}{ops[0]}({perm[1]}{ops[1]}({perm[2]}{ops[2]}{perm[3]}))")
                    
                    if abs(result - 24) < 0.0001:
                        return True
                except:
                    pass
    return False

def twenty_four():
    global NUMBERS
    NUMBERS = generate_numbers()
    
    score = 0
    rounds = 5
    current_round = 0
    time_left = 60
    game_over = False
    start_ticks = pygame.time.get_ticks()
    user_input = ""
    
    while not game_over:
        screen.fill(BLACK)
        
        seconds = max(0, time_left - (pygame.time.get_ticks() - start_ticks) // 1000)
        if seconds == 0 and not game_over:
            game_over = True
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    try:
                        result = eval(user_input)
                        if abs(result - 24) < 0.0001:
                            score += 100
                            current_round += 1
                            if current_round < rounds:
                                NUMBERS = generate_numbers()
                            else:
                                game_over = True
                        else:
                            score = max(0, score - 20)
                    except:
                        score = max(0, score - 10)
                    user_input = ""
                elif event.key == pygame.K_BACKSPACE:
                    user_input = user_input[:-1]
                elif event.key == pygame.K_SPACE:
                    user_input += " "
                elif event.unicode in ['+', '-', '*', '/', '(', ')']:
                    user_input += event.unicode
                elif event.unicode.isdigit():
                    user_input += event.unicode
        
        round_text = font.render(f"回合: {current_round + 1}/{rounds}", True, WHITE)
        screen.blit(round_text, (10, 10))
        
        score_text = font.render(f"得分: {score}", True, WHITE)
        screen.blit(score_text, (WIDTH - 150, 10))
        
        time_text = font.render(f"时间: {seconds}秒", True, WHITE)
        screen.blit(time_text, (WIDTH//2 - 50, 10))
        
        numbers_text = big_font.render(" ".join(map(str, NUMBERS)), True, GREEN)
        screen.blit(numbers_text, (WIDTH//2 - numbers_text.get_width()//2, 100))
        
        instruction_text = small_font.render("用这四个数字计算24点 (按回车确认)", True, WHITE)
        screen.blit(instruction_text, (WIDTH//2 - instruction_text.get_width()//2, 180))
        
        input_text = font.render(user_input + "|", True, BLUE)
        screen.blit(input_text, (WIDTH//2 - 100, 300))
        
        hint_text = small_font.render("提示: " + ("有解!" if solve_24(NUMBERS) else "无解"), 
                                     True, GREEN if solve_24(NUMBERS) else RED)
        screen.blit(hint_text, (WIDTH//2 - 50, 400))
        
        operators_text = small_font.render("运算符: + - * / ( )", True, WHITE)
        screen.blit(operators_text, (WIDTH//2 - operators_text.get_width()//2, 500))
        
        pygame.display.update()
        clock.tick(30)
    
    screen.fill(BLACK)
    result_text = big_font.render(f"最终得分: {score}", True, WHITE)
    screen.blit(result_text, (WIDTH//2 - result_text.get_width()//2, HEIGHT//2))
    pygame.display.update()
    pygame.time.wait(3000)
    pygame.quit()

if __name__ == "__main__":
    twenty_four()