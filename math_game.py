import pygame
import random

pygame.init()

WIDTH, HEIGHT = 800, 600

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLUE = (0, 100, 200)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("数学计算挑战")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 50)
big_font = pygame.font.Font(None, 80)
small_font = pygame.font.Font(None, 30)

def generate_problem():
    operators = ['+', '-', '*']
    op = random.choice(operators)
    
    if op == '+':
        a = random.randint(0, 50)
        b = random.randint(0, 50)
        answer = a + b
    elif op == '-':
        a = random.randint(20, 100)
        b = random.randint(0, a)
        answer = a - b
    else:
        a = random.randint(0, 12)
        b = random.randint(0, 12)
        answer = a * b
    
    return f"{a} {op} {b} = ?", answer

def math_game():
    score = 0
    problems_solved = 0
    current_problem, current_answer = generate_problem()
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
                    try:
                        if int(user_input) == current_answer:
                            score += 10
                        else:
                            score = max(0, score - 5)
                        problems_solved += 1
                        current_problem, current_answer = generate_problem()
                        user_input = ""
                    except:
                        pass
                elif event.key == pygame.K_BACKSPACE:
                    user_input = user_input[:-1]
                elif event.key == pygame.K_ESCAPE:
                    game_over = True
                elif event.unicode.isdigit() or (event.unicode == '-' and len(user_input) == 0):
                    user_input += event.unicode
        
        problem_text = big_font.render(current_problem, True, WHITE)
        screen.blit(problem_text, (WIDTH // 2 - problem_text.get_width() // 2, 100))
        
        input_text = big_font.render(user_input, True, GREEN)
        screen.blit(input_text, (WIDTH // 2 - input_text.get_width() // 2, 250))
        
        score_text = font.render(f"得分: {score}", True, WHITE)
        problem_count = font.render(f"题目: {problems_solved}", True, WHITE)
        screen.blit(score_text, (50, 50))
        screen.blit(problem_count, (WIDTH - 200, 50))
        
        instruction_text = small_font.render("输入答案后按回车 | ESC结束", True, WHITE)
        screen.blit(instruction_text, (WIDTH // 2 - instruction_text.get_width() // 2, HEIGHT - 50))
        
        pygame.display.update()
        clock.tick(30)
    
    screen.fill(BLACK)
    result_text = big_font.render(f"最终得分: {score}", True, WHITE)
    screen.blit(result_text, (WIDTH // 2 - result_text.get_width() // 2, HEIGHT // 2 - 50))
    
    accuracy_text = font.render(f"完成 {problems_solved} 道题", True, BLUE)
    screen.blit(accuracy_text, (WIDTH // 2 - accuracy_text.get_width() // 2, HEIGHT // 2 + 50))
    
    pygame.display.update()
    pygame.time.wait(3000)
    pygame.quit()

if __name__ == "__main__":
    math_game()