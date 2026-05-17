#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
你画我猜 - 多人聚会游戏
玩家画画，其他玩家猜词
"""

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

WIDTH, HEIGHT = 1000, 700

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 100)
RED = (255, 50, 50)
BLUE = (0, 100, 200)
YELLOW = (255, 200, 0)
PURPLE = (150, 50, 200)
ORANGE = (255, 150, 0)
GRAY = (150, 150, 150)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("你画我猜 - 多人聚会游戏")
clock = pygame.time.Clock()
font_large = get_chinese_font(50)
font_medium = get_chinese_font(36)
font_small = get_chinese_font(24)

DRAWING_AREA = (50, 120, 600, 500)
COLORS = [BLACK, RED, BLUE, GREEN, YELLOW, PURPLE, ORANGE, GRAY]
COLOR_NAMES = ["黑", "红", "蓝", "绿", "黄", "紫", "橙", "灰"]

WORDS = [
    "苹果", "香蕉", "汽车", "飞机", "房子", "大树", "小猫", "小狗",
    "太阳", "月亮", "星星", "花朵", "书本", "桌子", "椅子", "窗户",
    "鸟", "鱼", "蝴蝶", "蜜蜂", "足球", "篮球", "钢琴", "吉他",
    "雨伞", "帽子", "鞋子", "手表", "手机", "电脑", "电视", "冰箱",
    "汉堡", "披萨", "冰淇淋", "蛋糕", "咖啡", "茶杯", "筷子", "碗",
    "山", "海", "河", "湖", "云", "风", "雨", "雪",
]

class DrawGuessGame:
    def __init__(self):
        self.phase = "menu"
        self.current_word = None
        self.current_color = 0
        self.drawing_points = []
        self.guess = ""
        self.time_left = 60
        self.round = 1
        self.max_rounds = 5
        self.score = 0
        self.ai_guess = ""
        self.word_display = []
    
    def setup_round(self):
        self.current_word = random.choice(WORDS)
        self.drawing_points = []
        self.guess = ""
        self.time_left = 60
        self.ai_guess = ""
        self.word_display = ["_"] * len(self.current_word)
        self.reveal_letter()
    
    def reveal_letter(self):
        if self.current_word:
            indices = random.sample(range(len(self.current_word)), min(2, len(self.current_word)))
            for idx in indices:
                self.word_display[idx] = self.current_word[idx]

def draw_ui(game):
    pygame.draw.rect(screen, (30, 30, 50), (0, 0, WIDTH, 100))
    
    if game.current_word:
        word_text = " ".join(game.word_display)
        display = font_large.render(f"词语: {word_text}", True, YELLOW)
        screen.blit(display, (WIDTH // 2 - display.get_width() // 2, 30))
    
    time_color = GREEN if game.time_left > 20 else YELLOW if game.time_left > 10 else RED
    time_text = font_medium.render(f"时间: {game.time_left}秒", True, time_color)
    screen.blit(time_text, (WIDTH - 150, 30))
    
    score_text = font_medium.render(f"分数: {game.score}", True, WHITE)
    screen.blit(score_text, (20, 30))
    
    round_text = font_medium.render(f"回合: {game.round}/{game.max_rounds}", True, WHITE)
    screen.blit(round_text, (20, 70))
    
    pygame.draw.rect(screen, WHITE, DRAWING_AREA, 2)
    
    color_bar_y = 120
    for i, (color, name) in enumerate(zip(COLORS, COLOR_NAMES)):
        pygame.draw.rect(screen, color, (700, color_bar_y + i * 40, 50, 30))
        if i == game.current_color:
            pygame.draw.rect(screen, YELLOW, (700, color_bar_y + i * 40, 50, 30), 3)
        
        name_text = font_small.render(name, True, WHITE)
        screen.blit(name_text, (760, color_bar_y + i * 40 + 5))
    
    tools_y = color_bar_y + len(COLORS) * 40 + 20
    pygame.draw.rect(screen, BLACK if game.current_color == 0 else WHITE, 
                   (700, tools_y, 50, 30))
    clear_text = font_small.render("清除", True, WHITE)
    screen.blit(clear_text, (710, tools_y + 5))
    
    guess_y = tools_y + 60
    pygame.draw.rect(screen, (50, 50, 70), (700, guess_y, 280, 50), 2)
    guess_display = font_medium.render(game.guess, True, WHITE)
    screen.blit(guess_display, (710, guess_y + 10))
    
    ai_text = font_small.render(f"AI猜测: {game.ai_guess}", True, GRAY)
    screen.blit(ai_text, (700, guess_y + 60))

def draw_guess_game():
    game = DrawGuessGame()
    timer_event = pygame.USEREVENT + 1
    pygame.time.set_timer(timer_event, 1000)
    
    while True:
        screen.fill(BLACK)
        
        if game.phase == "menu":
            title = font_large.render("你画我猜", True, YELLOW)
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 150))
            
            instructions = [
                "游戏规则:",
                "1. 你需要画出屏幕上显示的词语",
                "2. AI会尝试猜测你画的是什么",
                "3. 如果AI猜对了，你得分",
                "4. 也可以让朋友来猜！",
                "",
                "按 空格键 开始游戏"
            ]
            
            for i, line in enumerate(instructions):
                text = font_small.render(line, True, WHITE)
                screen.blit(text, (WIDTH // 2 - 200, 250 + i * 35))
        
        elif game.phase == "playing":
            draw_ui(game)
            
            for i, point in enumerate(game.drawing_points):
                if i > 0:
                    prev = game.drawing_points[i - 1]
                    pygame.draw.line(screen, point['color'], 
                                   (prev['x'], prev['y']), 
                                   (point['x'], point['y']), 
                                   point['width'])
            
            if game.time_left <= 0:
                game.phase = "result"
        
        elif game.phase == "result":
            title = font_large.render("本回合结束!", True, YELLOW)
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 150))
            
            word_text = font_medium.render(f"词语是: {game.current_word}", True, WHITE)
            screen.blit(word_text, (WIDTH // 2 - 100, 220))
            
            ai_text = font_medium.render(f"AI猜测: {game.ai_guess}", True, GRAY)
            screen.blit(ai_text, (WIDTH // 2 - 80, 270))
            
            if game.ai_guess == game.current_word:
                result = font_large.render("🎉 AI猜对了!", True, GREEN)
                game.score += 10
            else:
                result = font_large.render("😅 AI没猜对", True, RED)
            screen.blit(result, (WIDTH // 2 - 100, 330))
            
            score_text = font_medium.render(f"当前总分: {game.score}", True, YELLOW)
            screen.blit(score_text, (WIDTH // 2 - 80, 390))
            
            if game.round >= game.max_rounds:
                final = font_large.render("游戏结束!", True, YELLOW)
                screen.blit(final, (WIDTH // 2 - 100, 450))
                
                final_score = font_medium.render(f"最终得分: {game.score}", True, GREEN)
                screen.blit(final_score, (WIDTH // 2 - 80, 510))
                
                restart = font_small.render("按 R 重新开始", True, WHITE)
                screen.blit(restart, (WIDTH // 2 - 60, 570))
            else:
                next_text = font_small.render("按 空格键 进入下一回合", True, WHITE)
                screen.blit(next_text, (WIDTH // 2 - 100, 450))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            
            elif event.type == pygame.KEYDOWN:
                if game.phase == "menu" and event.key == pygame.K_SPACE:
                    game.phase = "playing"
                    game.round = 1
                    game.score = 0
                    game.setup_round()
                
                elif game.phase == "playing":
                    if event.key == pygame.K_BACKSPACE:
                        game.guess = game.guess[:-1]
                    elif event.key == pygame.K_RETURN:
                        game.ai_guess = random.choice(WORDS)
                        if game.ai_guess == game.current_word:
                            game.score += 10
                    elif len(event.unicode) > 0 and event.unicode.isprintable():
                        game.guess += event.unicode
                    
                    if event.key == pygame.K_1:
                        game.current_color = 0
                    elif event.key in [pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8]:
                        game.current_color = event.key - 49
                
                elif game.phase == "result":
                    if event.key == pygame.K_SPACE and game.round < game.max_rounds:
                        game.round += 1
                        game.setup_round()
                        game.phase = "playing"
                    elif event.key == pygame.K_r:
                        game.phase = "menu"
                        game.round = 1
                        game.score = 0
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if game.phase == "playing":
                    mx, my = event.pos
                    
                    if DRAWING_AREA[0] < mx < DRAWING_AREA[0] + DRAWING_AREA[2] and \
                       DRAWING_AREA[1] < my < DRAWING_AREA[1] + DRAWING_AREA[3]:
                        game.drawing_points.append({
                            'x': mx, 'y': my,
                            'color': COLORS[game.current_color],
                            'width': 5
                        })
            
            elif event.type == pygame.MOUSEMOTION:
                if game.phase == "playing" and pygame.mouse.get_pressed()[0]:
                    mx, my = event.pos
                    if DRAWING_AREA[0] < mx < DRAWING_AREA[0] + DRAWING_AREA[2] and \
                       DRAWING_AREA[1] < my < DRAWING_AREA[1] + DRAWING_AREA[3]:
                        game.drawing_points.append({
                            'x': mx, 'y': my,
                            'color': COLORS[game.current_color],
                            'width': 5
                        })
            
            elif event.type == timer_event and game.phase == "playing":
                game.time_left -= 1
        
        clock.tick(60)

if __name__ == "__main__":
    draw_guess_game()
