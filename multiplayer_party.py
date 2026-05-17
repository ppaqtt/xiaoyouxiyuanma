import pygame
import os
import random
import math

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

WIDTH, HEIGHT = 900, 700

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 200, 0)
BLUE = (0, 100, 200)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("多人派对对战")
clock = pygame.time.Clock()
font = get_chinese_font(40)
big_font = get_chinese_font(60)

class Player:
    def __init__(self, num, color, controls):
        self.num = num
        self.color = color
        self.controls = controls
        self.score = 0
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.radius = 20
        self.active = True
    
    def move(self, keys):
        speed = 5
        if keys[self.controls['up']] and self.y > self.radius:
            self.y -= speed
        if keys[self.controls['down']] and self.y < HEIGHT - self.radius:
            self.y += speed
        if keys[self.controls['left']] and self.x > self.radius:
            self.x -= speed
        if keys[self.controls['right']] and self.x < WIDTH - self.radius:
            self.x += speed
    
    def draw(self):
        if self.active:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius, 2)
            num_text = font.render(str(self.num), True, WHITE)
            screen.blit(num_text, (int(self.x) - 8, int(self.y) - 15))

class MiniGame:
    def __init__(self, name, desc):
        self.name = name
        self.desc = desc

def musical_chairs(players):
    running = True
    chairs = [(WIDTH // 4, HEIGHT // 2), (WIDTH // 2, HEIGHT // 2), 
              (WIDTH * 3 // 4, HEIGHT // 2)]
    active_chairs = len(chairs)
    music_on = True
    music_timer = random.randint(180, 360)
    eliminated = []
    round_num = 1
    
    while active_chairs > 1 and len(players) - len(eliminated) > 1:
        for p in players:
            if p not in eliminated:
                p.x = WIDTH // 2
                p.y = HEIGHT // 2
        
        music_on = True
        music_timer = random.randint(180, 360)
        
        while music_on:
            screen.fill(BLACK)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
            
            keys = pygame.key.get_pressed()
            for p in players:
                if p not in eliminated:
                    p.move(keys)
                    p.draw()
            
            for i, chair in enumerate(chairs[:active_chairs]):
                pygame.draw.circle(screen, GREEN if i < active_chairs else GRAY, chair, 30)
            
            music_timer -= 1
            if music_timer <= 0:
                music_on = False
            
            title = big_font.render("抢椅子!", True, YELLOW)
            screen.blit(title, (WIDTH // 2 - 100, 50))
            
            music_text = font.render("音乐播放中..." if music_on else "停!", 
                                  True, GREEN if music_on else RED)
            screen.blit(music_text, (WIDTH // 2 - 80, 100))
            
            pygame.display.flip()
            clock.tick(60)
        
        closest_player = None
        closest_dist = float('inf')
        for p in players:
            if p not in eliminated:
                for i, chair in enumerate(chairs[:active_chairs]):
                    dist = math.sqrt((p.x - chair[0])**2 + (p.y - chair[1])**2)
                    if dist < closest_dist:
                        closest_dist = dist
                        closest_player = p
        
        if closest_player:
            eliminated.append(closest_player)
        
        active_chairs -= 1
        round_num += 1
        pygame.time.wait(1000)
    
    winner = [p for p in players if p not in eliminated][0]
    return winner

def star_collector(players):
    stars = []
    for _ in range(10):
        stars.append({
            'x': random.randint(50, WIDTH - 50),
            'y': random.randint(100, HEIGHT - 100),
            'collected': [False] * len(players)
        })
    
    timer = 300
    running = True
    
    while timer > 0 and not all(all(s['collected']) for s in stars):
        screen.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
        
        keys = pygame.key.get_pressed()
        for i, p in enumerate(players):
            p.move(keys)
            for star in stars:
                if not star['collected'][i]:
                    dist = math.sqrt((p.x - star['x'])**2 + (p.y - star['y'])**2)
                    if dist < 30:
                        star['collected'][i] = True
                        p.score += 10
        
        for i, p in enumerate(players):
            p.draw()
        
        for star in stars:
            collected_count = sum(star['collected'])
            color = [WHITE, GREEN, YELLOW, ORANGE][min(collected_count, 3)]
            if collected_count < len(players):
                pygame.draw.circle(screen, color, (star['x'], star['y']), 15)
                pygame.draw.circle(screen, WHITE, (star['x'], star['y']), 15, 2)
        
        timer -= 1
        timer_text = font.render(f"时间: {timer // 60}", True, WHITE)
        screen.blit(timer_text, (10, 10))
        
        for i, p in enumerate(players):
            score_text = font.render(f"玩家{i+1}: {p.score}", True, p.color)
            screen.blit(score_text, (10, 50 + i * 30))
        
        title = big_font.render("抢星星!", True, YELLOW)
        screen.blit(title, (WIDTH // 2 - 100, 50))
        
        pygame.display.flip()
        clock.tick(60)
    
    best = max(players, key=lambda p: p.score)
    return best

def tug_of_war(players):
    rope_pos = WIDTH // 2
    rope_vel = 0
    left_team = [players[0]] if len(players) > 0 else []
    right_team = [players[1]] if len(players) > 1 else []
    timer = 600
    
    while timer > 0 and abs(rope_pos - WIDTH // 2) < 300:
        screen.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
        
        keys = pygame.key.get_pressed()
        left_press = sum(keys[left_team[0].controls[k]] if left_team else 0 
                        for k in ['left', 'right'])
        right_press = sum(keys[right_team[0].controls[k]] if right_team else 0 
                         for k in ['left', 'right'])
        
        rope_vel += (right_press - left_press) * 0.1
        rope_vel *= 0.98
        rope_pos += rope_vel
        
        pygame.draw.line(screen, BROWN, (50, HEIGHT // 2), (WIDTH - 50, HEIGHT // 2), 10)
        pygame.draw.circle(screen, RED, (int(rope_pos), HEIGHT // 2), 20)
        
        pygame.draw.rect(screen, GREEN, (0, HEIGHT // 2 - 50, 50, 100))
        pygame.draw.rect(screen, BLUE, (WIDTH - 50, HEIGHT // 2 - 50, 50, 100))
        
        title = big_font.render("拔河!", True, YELLOW)
        screen.blit(title, (WIDTH // 2 - 100, 50))
        
        timer -= 1
        timer_text = font.render(f"时间: {timer // 60}", True, WHITE)
        screen.blit(timer_text, (10, 10))
        
        pygame.display.flip()
        clock.tick(60)
    
    winner = left_team[0] if rope_pos < WIDTH // 2 else right_team[0] if rope_pos > WIDTH // 2 else None
    if winner:
        winner.score += 50
    return winner

def reaction_test(players):
    running = True
    round_num = 0
    max_rounds = len(players) * 2
    
    while round_num < max_rounds:
        screen.fill(BLACK)
        
        colors = [GREEN, RED, YELLOW, BLUE]
        show_color = random.choice(colors)
        target = colors[0]
        wait_time = random.randint(60, 180)
        
        while wait_time > 0:
            screen.fill(show_color)
            text = big_font.render("等待...", True, WHITE)
            screen.blit(text, (WIDTH // 2 - 100, HEIGHT // 2 - 50))
            wait_time -= 1
            
            pygame.display.flip()
            clock.tick(60)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
        
        screen.fill(target)
        text = big_font.render("按空格!", True, WHITE)
        screen.blit(text, (WIDTH // 2 - 100, HEIGHT // 2 - 50))
        pygame.display.flip()
        
        start = pygame.time.get_ticks()
        responded = [False] * len(players)
        
        while not all(responded):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                elif event.type == pygame.KEYDOWN:
                    key_map = {pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2, pygame.K_4: 3}
                    if event.key in key_map:
                        idx = key_map[event.key]
                        if not responded[idx] and idx < len(players):
                            reaction = pygame.time.get_ticks() - start
                            if reaction < 1000:
                                players[idx].score += max(0, 1000 - reaction)
                            responded[idx] = True
            
            for i, p in enumerate(players):
                status = "已响应!" if responded[i] else "等待中..."
                color = GREEN if responded[i] else WHITE
                info = font.render(f"玩家{i+1}: {status}", True, color)
                screen.blit(info, (WIDTH // 2 - 100, HEIGHT // 2 + 50 + i * 40))
            
            pygame.display.flip()
            clock.tick(60)
        
        round_num += 1
        pygame.time.wait(1000)
    
    winner = max(players, key=lambda p: p.score)
    return winner

def multiplayer_party():
    controls_list = [
        {'up': pygame.K_w, 'down': pygame.K_s, 'left': pygame.K_a, 'right': pygame.K_d},
        {'up': pygame.K_UP, 'down': pygame.K_DOWN, 'left': pygame.K_LEFT, 'right': pygame.K_RIGHT},
        {'up': pygame.K_i, 'down': pygame.K_k, 'left': pygame.K_j, 'right': pygame.K_l},
    ]
    
    colors = [RED, GREEN, BLUE, YELLOW]
    player_count = 2
    
    screen.fill(BLACK)
    title = big_font.render("多人派对对战", True, YELLOW)
    screen.blit(title, (WIDTH // 2 - 150, 100))
    inst = font.render("选择玩家数量 (2-4)", True, WHITE)
    screen.blit(inst, (WIDTH // 2 - 100, 200))
    
    for i in range(1, 5):
        num_text = font.render(f"{i}名玩家 - 按{i}", True, WHITE)
        screen.blit(num_text, (WIDTH // 2 - 80, 250 + i * 40))
    
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_2, pygame.K_3, pygame.K_4):
                    player_count = event.key - 48
                    waiting = False
    
    players = [Player(i+1, colors[i], controls_list[i]) for i in range(player_count)]
    
    games = [
        MiniGame("抢椅子", "音乐停止时抢椅子"),
        MiniGame("抢星星", "收集星星得分"),
        MiniGame("拔河", "拉扯绳子"),
        MiniGame("反应力", "看到绿色按键"),
    ]
    
    game_results = []
    
    for i, game in enumerate(games):
        screen.fill(BLACK)
        title = big_font.render(f"第{i+1}轮: {game.name}", True, YELLOW)
        screen.blit(title, (WIDTH // 2 - 150, 100))
        desc = font.render(game.desc, True, WHITE)
        screen.blit(desc, (WIDTH // 2 - 100, 180))
        start = font.render("按空格开始", True, GREEN)
        screen.blit(start, (WIDTH // 2 - 80, 300))
        pygame.display.flip()
        
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    waiting = False
        
        if game.name == "抢椅子":
            winner = musical_chairs(players)
        elif game.name == "抢星星":
            winner = star_collector(players)
        elif game.name == "拔河":
            winner = tug_of_war(players)
        else:
            winner = reaction_test(players)
        
        if winner:
            winner.score += 30
            game_results.append((game.name, winner))
        
        screen.fill(BLACK)
        result = font.render(f"{game.name}获胜: 玩家{winner.num}", True, winner.color)
        screen.blit(result, (WIDTH // 2 - 150, 100))
        
        for p in players:
            score = font.render(f"玩家{p.num}: {p.score}分", True, p.color)
            screen.blit(score, (WIDTH // 2 - 100, 200 + p.num * 40))
        
        pygame.display.flip()
        pygame.time.wait(3000)
    
    overall_winner = max(players, key=lambda p: p.score)
    
    screen.fill(BLACK)
    title = big_font.render("最终胜利!", True, YELLOW)
    screen.blit(title, (WIDTH // 2 - 150, 100))
    winner_text = big_font.render(f"玩家{overall_winner.num}", True, overall_winner.color)
    screen.blit(winner_text, (WIDTH // 2 - 100, 200))
    
    for p in players:
        score = font.render(f"玩家{p.num}: {p.score}分", True, p.color)
        screen.blit(score, (WIDTH // 2 - 100, 300 + p.num * 40))
    
    pygame.display.flip()
    pygame.time.wait(5000)
    pygame.quit()

if __name__ == "__main__":
    multiplayer_party()
