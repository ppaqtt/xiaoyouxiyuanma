import pygame
import os
import random
import math
import time

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
RED = (200, 0, 0)
GREEN = (0, 200, 0)
BLUE = (0, 100, 200)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GRAY = (150, 150, 150)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("派对游戏合集")

clock = pygame.time.Clock()
font = get_chinese_font(36)
big_font = get_chinese_font(60)
small_font = get_chinese_font(24)

class Menu:
    def __init__(self):
        self.games = [
            {'name': '快速反应', 'desc': '看到绿色点击!'},
            {'name': '记忆数字', 'desc': '记住闪现的数字'},
            {'name': '节奏拍手', 'desc': '按节奏按键!'},
            {'name': '颜色干扰', 'desc': '说出文字颜色!'},
            {'name': '弹球对决', 'desc': '先到5分!'},
        ]
        self.selected = 0
    
    def draw(self):
        screen.fill((20, 20, 60))
        title = big_font.render("派对游戏合集", True, YELLOW)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 30))
        
        for i, game in enumerate(self.games):
            y = 120 + i * 80
            color = YELLOW if i == self.selected else WHITE
            pygame.draw.rect(screen, (40, 40, 80), (200, y, 400, 60), border_radius=10)
            if i == self.selected:
                pygame.draw.rect(screen, YELLOW, (200, y, 400, 60), 3, border_radius=10)
            
            name_text = font.render(game['name'], True, color)
            desc_text = small_font.render(game['desc'], True, GRAY)
            screen.blit(name_text, (220, y + 5))
            screen.blit(desc_text, (220, y + 35))
        
        inst = small_font.render("↑↓选择 | 回车开始 | ESC退出", True, WHITE)
        screen.blit(inst, (WIDTH // 2 - inst.get_width() // 2, HEIGHT - 40))

def quick_reaction():
    screen.fill(BLACK)
    score = 0
    round_num = 0
    max_rounds = 10
    state = 'wait'  # wait, ready, go, result
    wait_time = 0
    reaction_start = 0
    reaction_time = 0
    
    while round_num < max_rounds:
        screen.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                if event.key == pygame.K_SPACE:
                    if state == 'wait':
                        state = 'ready'
                        wait_time = random.randint(60, 180)
                    elif state == 'ready':
                        state = 'result'
                        reaction_time = -1  # 太早了
                    elif state == 'go':
                        reaction_time = time.time() - reaction_start
                        score += max(0, int(1000 - reaction_time * 1000))
                        state = 'result'
                    elif state == 'result':
                        round_num += 1
                        state = 'wait'
        
        if state == 'wait':
            text = big_font.render("按空格开始", True, WHITE)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))
        elif state == 'ready':
            wait_time -= 1
            text = big_font.render("等待绿色...", True, RED)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))
            if wait_time <= 0:
                state = 'go'
                reaction_start = time.time()
        elif state == 'go':
            screen.fill(GREEN)
            text = big_font.render("点击!", True, WHITE)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))
        elif state == 'result':
            if reaction_time < 0:
                text = big_font.render("太早了!", True, RED)
            else:
                text = big_font.render(f"{reaction_time:.3f}秒", True, YELLOW)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 30))
            cont = font.render("按空格继续", True, WHITE)
            screen.blit(cont, (WIDTH // 2 - cont.get_width() // 2, HEIGHT // 2 + 40))
        
        score_text = font.render(f"得分: {score}  回合: {round_num}/{max_rounds}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        pygame.display.flip()
        clock.tick(60)

def memory_numbers():
    screen.fill(BLACK)
    level = 1
    score = 0
    
    while True:
        num_length = level + 2
        numbers = [str(random.randint(0, 9)) for _ in range(num_length)]
        sequence = ''.join(numbers)
        
        # 显示数字
        screen.fill(BLACK)
        text = big_font.render(f"记住: {sequence}", True, YELLOW)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 30))
        level_text = font.render(f"关卡: {level}", True, WHITE)
        screen.blit(level_text, (10, 10))
        pygame.display.flip()
        pygame.time.wait(1500 + level * 200)
        
        # 输入
        user_input = ""
        while len(user_input) < num_length:
            screen.fill(BLACK)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return
                    elif event.key == pygame.K_BACKSPACE:
                        user_input = user_input[:-1]
                    elif event.unicode.isdigit():
                        user_input += event.unicode
            
            input_text = big_font.render(user_input + "_", True, WHITE)
            screen.blit(input_text, (WIDTH // 2 - input_text.get_width() // 2, HEIGHT // 2))
            hint = font.render(f"输入{num_length}位数字", True, GRAY)
            screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT // 2 + 50))
            pygame.display.flip()
            clock.tick(30)
        
        if user_input == sequence:
            score += level * 10
            level += 1
        else:
            screen.fill(BLACK)
            fail = big_font.render(f"错误! 正确: {sequence}", True, RED)
            score_text = font.render(f"最终得分: {score}  到达关卡: {level}", True, WHITE)
            screen.blit(fail, (WIDTH // 2 - fail.get_width() // 2, HEIGHT // 2 - 30))
            screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 + 40))
            pygame.display.flip()
            pygame.time.wait(3000)
            return

def rhythm_clap():
    screen.fill(BLACK)
    score = 0
    combo = 0
    bpm = 120
    beat_interval = 60000 / bpm
    last_beat = pygame.time.get_ticks()
    total_beats = 30
    beat_count = 0
    
    while beat_count < total_beats:
        now = pygame.time.get_ticks()
        screen.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                if event.key == pygame.K_SPACE:
                    time_since_beat = now - last_beat
                    next_beat_in = beat_interval - time_since_beat
                    
                    if time_since_beat < 200:
                        score += 10 + combo * 2
                        combo += 1
                        feedback = "完美!" if time_since_beat < 100 else "好!"
                    elif next_beat_in < 200:
                        score += 5
                        combo = 0
                        feedback = "早了一点"
                    else:
                        combo = 0
                        feedback = "不在节拍上"
        
        # 节拍指示器
        time_since_beat = now - last_beat
        if time_since_beat >= beat_interval:
            last_beat = now
            beat_count += 1
        
        # 节拍可视化
        progress = time_since_beat / beat_interval
        circle_radius = int(50 + 30 * math.sin(progress * math.pi))
        color = GREEN if progress < 0.3 else (YELLOW if progress < 0.6 else RED)
        pygame.draw.circle(screen, color, (WIDTH // 2, HEIGHT // 2), circle_radius)
        
        score_text = font.render(f"得分: {score}  连击: {combo}  节拍: {beat_count}/{total_beats}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        pygame.display.flip()
        clock.tick(60)
    
    screen.fill(BLACK)
    result = big_font.render(f"最终得分: {score}", True, YELLOW)
    screen.blit(result, (WIDTH // 2 - result.get_width() // 2, HEIGHT // 2))
    pygame.display.flip()
    pygame.time.wait(3000)

def color_interference():
    screen.fill(BLACK)
    score = 0
    round_num = 0
    max_rounds = 15
    
    color_names = ['RED', 'GREEN', 'BLUE', 'YELLOW', 'PURPLE']
    color_values = [RED, GREEN, BLUE, YELLOW, PURPLE]
    
    while round_num < max_rounds:
        screen.fill(BLACK)
        
        word_idx = random.randint(0, len(color_names) - 1)
        display_color_idx = random.randint(0, len(color_values) - 1)
        
        word = color_names[word_idx]
        display_color = color_values[display_color_idx]
        
        text = big_font.render(word, True, display_color)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 50))
        
        inst = font.render("按对应颜色的数字键! (1红 2绿 3蓝 4黄 5紫)", True, WHITE)
        screen.blit(inst, (WIDTH // 2 - inst.get_width() // 2, HEIGHT // 2 + 40))
        
        score_text = font.render(f"得分: {score}  回合: {round_num}/{max_rounds}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        pygame.display.flip()
        
        start = pygame.time.get_ticks()
        answered = False
        
        while pygame.time.get_ticks() - start < 3000 and not answered:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return
                    key_map = {pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2, pygame.K_4: 3, pygame.K_5: 4}
                    if event.key in key_map:
                        if key_map[event.key] == display_color_idx:
                            score += 10
                        else:
                            score = max(0, score - 5)
                        answered = True
                        round_num += 1
        
        if not answered:
            round_num += 1
    
    screen.fill(BLACK)
    result = big_font.render(f"最终得分: {score}", True, YELLOW)
    screen.blit(result, (WIDTH // 2 - result.get_width() // 2, HEIGHT // 2))
    pygame.display.flip()
    pygame.time.wait(3000)

def mini_pong():
    paddle1_y = HEIGHT // 2 - 50
    paddle2_y = HEIGHT // 2 - 50
    ball_x, ball_y = WIDTH // 2, HEIGHT // 2
    ball_dx, ball_dy = 4, 3
    score1, score2 = 0, 0
    paddle_speed = 6
    
    while score1 < 5 and score2 < 5:
        screen.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and paddle1_y > 0:
            paddle1_y -= paddle_speed
        if keys[pygame.K_s] and paddle1_y < HEIGHT - 100:
            paddle1_y += paddle_speed
        if keys[pygame.K_UP] and paddle2_y > 0:
            paddle2_y -= paddle_speed
        if keys[pygame.K_DOWN] and paddle2_y < HEIGHT - 100:
            paddle2_y += paddle_speed
        
        ball_x += ball_dx
        ball_y += ball_dy
        
        if ball_y <= 0 or ball_y >= HEIGHT - 10:
            ball_dy *= -1
        
        if ball_x <= 30 and paddle1_y <= ball_y <= paddle1_y + 100:
            ball_dx *= -1
        if ball_x >= WIDTH - 40 and paddle2_y <= ball_y <= paddle2_y + 100:
            ball_dx *= -1
        
        if ball_x < 0:
            score2 += 1
            ball_x, ball_y = WIDTH // 2, HEIGHT // 2
            ball_dx = 4
        if ball_x > WIDTH:
            score1 += 1
            ball_x, ball_y = WIDTH // 2, HEIGHT // 2
            ball_dx = -4
        
        pygame.draw.rect(screen, WHITE, (10, paddle1_y, 15, 100))
        pygame.draw.rect(screen, WHITE, (WIDTH - 25, paddle2_y, 15, 100))
        pygame.draw.circle(screen, YELLOW, (int(ball_x), int(ball_y)), 8)
        pygame.draw.line(screen, GRAY, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT), 2)
        
        s1 = font.render(str(score1), True, WHITE)
        s2 = font.render(str(score2), True, WHITE)
        screen.blit(s1, (WIDTH // 4, 10))
        screen.blit(s2, (WIDTH * 3 // 4, 10))
        
        pygame.display.flip()
        clock.tick(60)

def party_games():
    game_funcs = [quick_reaction, memory_numbers, rhythm_clap, color_interference, mini_pong]
    menu = Menu()
    running = True
    
    while running:
        menu.draw()
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_UP:
                    menu.selected = (menu.selected - 1) % len(menu.games)
                elif event.key == pygame.K_DOWN:
                    menu.selected = (menu.selected + 1) % len(menu.games)
                elif event.key == pygame.K_RETURN:
                    game_funcs[menu.selected]()
        
        clock.tick(30)
    
    pygame.quit()

if __name__ == "__main__":
    party_games()
