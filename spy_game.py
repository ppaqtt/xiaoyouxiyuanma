#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
谁是卧底 - 多人聚会游戏
玩家和AI轮流描述词语，找出卧底
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

WIDTH, HEIGHT = 900, 700

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
pygame.display.set_caption("谁是卧底 - 多人聚会游戏")
clock = pygame.time.Clock()
font_large = get_chinese_font(50)
font_medium = get_chinese_font(36)
font_small = get_chinese_font(28)

# 词库
WORD_PAIRS = [
    ("苹果", "梨子"),
    ("狗", "猫"),
    ("汽车", "火车"),
    ("米饭", "面条"),
    ("电脑", "手机"),
    ("医生", "护士"),
    ("飞机", "火车"),
    ("书本", "报纸"),
    ("咖啡", "茶水"),
    ("足球", "篮球"),
    ("大海", "河流"),
    ("森林", "草原"),
    ("春天", "夏天"),
    ("老人", "中年人"),
    ("北京", "上海"),
    ("火车", "地铁"),
    ("电影", "电视剧"),
    ("音乐", "歌曲"),
    ("画画", "书法"),
    ("跑步", "游泳"),
]

class Player:
    def __init__(self, name, is_ai=False):
        self.name = name
        self.is_ai = is_ai
        self.is_spy = False
        self.votes = 0
        self.described = False
    
    def describe(self, word, is_spy_word):
        if self.is_ai:
            if is_spy_word:
                return "这个...不太确定呢"
            return self.generate_description(word)
        return None
    
    def generate_description(self, word):
        descriptions = {
            "苹果": ["红色的水果", "可以榨汁", "牛顿也喜欢", "手机品牌", "圆圆的"],
            "梨子": ["黄绿色的水果", "水分很多", "润肺止咳", "形状像葫芦"],
            "狗": ["人类的朋友", "会看家", "忠诚的", "有尾巴", "四条腿"],
            "猫": ["会抓老鼠", "很独立", "喜欢睡觉", "有胡须", "九条命"],
        }
        return random.choice(descriptions.get(word, ["好吃的", "常见的", "很有用的"]))

class SpyGame:
    def __init__(self):
        self.players = []
        self.current_word = None
        self.spy_word = None
        self.normal_word = None
        self.current_player_idx = 0
        self.phase = "setup"
        self.descriptions = []
        self.round = 1
        self.winner = None
        self.game_over = False
    
    def setup_game(self, num_players=4):
        self.players = []
        for i in range(num_players):
            if i == 0:
                self.players.append(Player("你", is_ai=False))
            else:
                self.players.append(Player(f"玩家{i}", is_ai=True))
        
        spy_idx = random.randint(0, len(self.players) - 1)
        self.players[spy_idx].is_spy = True
        
        pair = random.choice(WORD_PAIRS)
        if random.random() < 0.5:
            self.normal_word, self.spy_word = pair
        else:
            self.spy_word, self.normal_word = pair
        
        self.phase = "describe"
        self.current_player_idx = 0
    
    def get_current_word(self, player):
        if player.is_spy:
            return self.spy_word
        return self.normal_word
    
    def vote_player(self, player_idx):
        self.players[player_idx].votes += 1
    
    def check_votes(self):
        max_votes = max(p.votes for p in self.players)
        candidates = [p for p in self.players if p.votes == max_votes]
        
        if len(candidates) == 1:
            if candidates[0].is_spy:
                self.winner = "好人"
            else:
                self.winner = "卧底"
            self.game_over = True
            return candidates[0]
        return None

def spy_game():
    game = SpyGame()
    
    screen.fill(BLACK)
    title = font_large.render("谁是卧底", True, YELLOW)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))
    
    instructions = [
        "游戏规则:",
        "1. 所有人会得到一个词语",
        "2. 除了卧底，其他人的词语相同",
        "3. 轮流描述，但不能说出词语",
        "4. 描述结束后投票找出卧底",
        "5. 如果找出卧底，好人获胜",
        "6. 如果卧底存活到最后，卧底获胜",
        "",
        "选择玩家数量:",
        "按 4 选择4人 | 按 5 选择5人 | 按 6 选择6人"
    ]
    
    for i, line in enumerate(instructions):
        text = font_small.render(line, True, WHITE)
        screen.blit(text, (WIDTH // 2 - 200, 200 + i * 35))
    
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_4, pygame.K_5, pygame.K_6):
                    num = event.key - 48
                    game.setup_game(num)
                    waiting = False
    
    while not game.game_over:
        screen.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        
        pygame.draw.rect(screen, (30, 30, 50), (0, 0, WIDTH, 80))
        
        round_text = font_medium.render(f"第 {game.round} 轮 - 描述阶段", True, YELLOW)
        screen.blit(round_text, (WIDTH // 2 - round_text.get_width() // 2, 20))
        
        current_player = game.players[game.current_player_idx]
        word = game.get_current_word(current_player)
        
        if current_player.is_ai:
            pygame.time.wait(1000)
            desc = current_player.describe(word, current_player.is_spy)
            game.descriptions.append((current_player.name, desc, current_player.is_spy))
            game.current_player_idx += 1
            
            if game.current_player_idx >= len(game.players):
                game.phase = "vote"
                game.current_player_idx = 0
        else:
            role = "【卧底】" if current_player.is_spy else "【好人】"
            role_color = RED if current_player.is_spy else GREEN
            
            player_text = font_large.render(f"你是: {role}", True, role_color)
            screen.blit(player_text, (WIDTH // 2 - player_text.get_width() // 2, 120))
            
            word_text = font_large.render(f"你的词语是: {word}", True, WHITE)
            screen.blit(word_text, (WIDTH // 2 - word_text.get_width() // 2, 180))
            
            desc_prompt = font_medium.render("请在下方输入你的描述:", True, YELLOW)
            screen.blit(desc_prompt, (WIDTH // 2 - 150, 250))
            
            pygame.draw.rect(screen, (50, 50, 70), (WIDTH // 2 - 250, 300, 500, 100), 3)
            
            for i, (name, desc, is_spy) in enumerate(game.descriptions):
                spy_marker = "(卧底?)" if is_spy else ""
                desc_text = font_small.render(f"{name}{spy_marker}: {desc}", True, GRAY)
                screen.blit(desc_text, (WIDTH // 2 - 200, 420 + i * 30))
            
            inst = font_small.render("按回车确认描述", True, GREEN)
            screen.blit(inst, (WIDTH // 2 - 80, 480))
        
        pygame.display.flip()
        clock.tick(60)
        
        if game.phase == "vote" and game.current_player_idx == 0 and not game.players[0].described:
            game.players[0].described = True
    
    screen.fill(BLACK)
    if game.winner == "好人":
        result = font_large.render("🎉 好人获胜！卧底被找出来了！", True, GREEN)
    else:
        result = font_large.render("😈 卧底获胜！成功隐藏了自己！", True, RED)
    screen.blit(result, (WIDTH // 2 - 200, HEIGHT // 2 - 50))
    
    for player in game.players:
        status = f"{player.name}: {'卧底' if player.is_spy else '好人'} - {player.votes}票"
        color = RED if player.is_spy else GREEN
        text = font_medium.render(status, True, color)
        screen.blit(text, (WIDTH // 2 - 100, HEIGHT // 2 + 50 + game.players.index(player) * 40))
    
    pygame.display.flip()
    pygame.time.wait(5000)
    pygame.quit()

if __name__ == "__main__":
    spy_game()
