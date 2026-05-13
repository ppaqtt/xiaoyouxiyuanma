import pygame
import random

pygame.init()

WIDTH, HEIGHT = 600, 600

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLUE = (0, 100, 200)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("快速心算")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 50)
big_font = pygame.font.Font(None, 80)

def generate_problem():
    operators = ['+', '-', '*']
    op = random.choice(operators)
    
    if op == '+':
        a = random.randint(10, 99)
        b = random.randint(10, 99)
        answer = a + b
    elif op == '-':
        a = random.randint(50, 99)
        b = random.randint(10, 49)
        answer = a - b
    else:
        a = random.randint(5, 15)
        b = random.randint(5, 15)
        answer = a * b
    
    choices = [answer]
    while len(choices) < 4:
        wrong = answer + random.choice([-15, -10, -5, 5, 10, 15])
        if wrong not in choices and wrong > 0:
            choices.append(wrong)
    
    random.shuffle(choices)
    
    return f"{a} {op} {b}", answer, choices

def quick_math():
    problem, answer, choices = generate_problem()
    
    buttons = []
    button_width = 250
    button_height = 80
    margin = 20
    
    for i, choice in enumerate(choices):
        row = i // 2
        col = i % 2
        x = WIDTH//4 - button_width//2 + col * (button_width + margin)
        y = 300 + row * (button_height + margin)
        buttons.append({'rect': pygame.Rect(x, y, button_width, button_height), 'value': choice})
    
    score = 0
    correct = 0
    time_left = 60
    game_over = False
    start_ticks = pygame.time.get_ticks()
    feedback = None
    feedback_timer = 0
    
    while not game_over:
        screen.fill(BLACK)
        
        seconds = max(0, 60 - (pygame.time.get_ticks() - start_ticks) // 1000)
        if seconds == 0:
            game_over = True
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN and not feedback:
                mouse_pos = event.pos
                for btn in buttons:
                    if btn['rect'].collidepoint(mouse_pos):
                        if btn['value'] == answer:
                            score += 100
                            correct += 1
                            feedback = "正确!"
                            feedback_color = GREEN
                        else:
                            score = max(0, score - 50)
                            feedback = "错误!"
                            feedback_color = RED
                        feedback_timer = 30
                        problem, answer, choices = generate_problem()
                        
                        for i, choice in enumerate(choices):
                            row = i // 2
                            col = i % 2
                            x = WIDTH//4 - button_width//2 + col * (button_width + margin)
                            y = 300 + row * (button_height + margin)
                            buttons[i] = {'rect': pygame.Rect(x, y, button_width, button_height), 'value': choice}
                        break
        
        if feedback_timer > 0:
            feedback_timer -= 1
            if feedback_timer == 0:
                feedback = None
        
        problem_text = big_font.render(problem, True, WHITE)
        screen.blit(problem_text, (WIDTH//2 - problem_text.get_width()//2, 100))
        
        question_text = font.render("= ?", True, WHITE)
        screen.blit(question_text, (WIDTH//2 + 50, 150))
        
        for btn in buttons:
            color = GREEN if feedback and btn['value'] == answer else BLUE
            pygame.draw.rect(screen, color, btn['rect'], border_radius=10)
            text = font.render(str(btn['value']), True, WHITE)
            screen.blit(text, (btn['rect'].x + 80, btn['rect'].y + 20))
        
        if feedback:
            feedback_text = big_font.render(feedback, True, feedback_color)
            screen.blit(feedback_text, (WIDTH//2 - feedback_text.get_width()//2, 50))
        
        score_text = font.render(f"得分: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        time_text = font.render(f"时间: {seconds}秒", True, WHITE)
        screen.blit(time_text, (WIDTH - 120, 10))
        
        correct_text = font.render(f"正确: {correct}", True, WHITE)
        screen.blit(correct_text, (10, 50))
        
        pygame.display.update()
        clock.tick(30)
    
    screen.fill(BLACK)
    result_text = big_font.render(f"最终得分: {score}", True, WHITE)
    screen.blit(result_text, (WIDTH//2 - result_text.get_width()//2, HEIGHT//2 - 50))
    
    accuracy = int((correct / max(1, correct + (score // 50))) * 100) if score > 0 else 0
    accuracy_text = font.render(f"正确率: {accuracy}%", True, GREEN)
    screen.blit(accuracy_text, (WIDTH//2 - accuracy_text.get_width()//2, HEIGHT//2 + 50))
    
    pygame.display.update()
    pygame.time.wait(3000)
    pygame.quit()

if __name__ == "__main__":
    quick_math()