#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
成语接龙 - 文字游戏
根据成语的最后一个字接新的成语
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

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("成语接龙 - 文字游戏")
clock = pygame.time.Clock()
font_large = get_chinese_font(50)
font_medium = get_chinese_font(36)
font_small = get_chinese_font(24)

IDIOMS = [
    "一帆风顺", "顺藤摸瓜", "瓜田李下", "下里巴人",
    "人山人海", "海阔天空", "空穴来风", "风平浪静",
    "静观其变", "变本加厉", "厉兵秣马", "马到成功",
    "功德圆满", "善始善终", "始终如一", "一见钟情",
    "情投意合", "合二为一", "一往无前", "前车之鉴",
    "鉴往知来", "来者不善", "善罢甘休", "休养生息",
    "息息相关", "关门大吉", "吉人天相", "相得益彰",
    "彰善瘅恶", "恶贯满盈", "盈千累万", "万无一失",
    "失而复得", "得意忘形", "形影不离", "离经叛道",
    "道听途说", "说三道四", "四通八达", "达官贵人",
    "人多势众", "众志成城", "城狐社鼠", "鼠目寸光",
    "光怪陆离", "离乡背井", "井底之蛙", "蛙鸣蝉噪",
    "噪杂囔囔", "囊空如洗", "洗手奉公", "公而忘私",
    "私心杂念", "念兹在兹", "兹事体大", "大材小用",
    "用心良苦", "苦尽甘来", "来日方长", "长驱直入",
    "入木三分", "分秒必争", "争先恐后", "后会有期",
    "期期艾艾", "艾发衰容", "容光焕发", "发人深省",
    "省吃俭用", "用其所长", "长年累月", "月明星稀",
    "稀奇古怪", "怪声怪气", "气壮山河", "河山带砺",
    "砺山带河", "河清海晏", "晏子使楚", "楚楚动人",
    "人心不古", "古往今来", "来者不善", "善善从长",
]

class IdiomGame:
    def __init__(self):
        self.current_idiom = None
        self.history = []
        self.player_score = 0
        self.ai_score = 0
        self.round = 1
        self.max_rounds = 10
        self.time_left = 30
        self.phase = "start"
    
    def start_game(self):
        self.current_idiom = random.choice(IDIOMS)
        self.history = [self.current_idiom]
        self.round = 1
        self.player_score = 0
        self.ai_score = 0
        self.phase = "playing"
        self.time_left = 30
    
    def check_idiom(self, idiom):
        if idiom in self.history:
            return False, "成语已使用过"
        
        if len(idiom) < 4:
            return False, "成语长度不够"
        
        last_char = self.current_idiom[-1]
        if idiom[0] != last_char:
            return False, f"需要以'{last_char}'开头"
        
        if idiom not in IDIOMS:
            return False, "这不是有效成语"
        
        return True, "正确"
    
    def ai_respond(self):
        last_char = self.current_idiom[-1]
        candidates = [i for i in IDIOMS if i[0] == last_char and i not in self.history]
        
        if candidates:
            ai_choice = random.choice(candidates)
            self.history.append(ai_choice)
            self.current_idiom = ai_choice
            self.ai_score += 10
            return ai_choice
        return None
    
    def get_hint(self):
        last_char = self.current_idiom[-1]
        candidates = [i for i in IDIOMS if i[0] == last_char and i not in self.history]
        if candidates:
            return f"提示: 以'{last_char}'开头的成语还有{len(candidates)}个"
        return "无法找到合适的成语"

def idiom_game():
    game = IdiomGame()
    user_input = ""
    timer_event = pygame.USEREVENT + 1
    pygame.time.set_timer(timer_event, 1000)
    
    while True:
        screen.fill(BLACK)
        
        if game.phase == "start":
            title = font_large.render("成语接龙", True, YELLOW)
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))
            
            instructions = [
                "游戏规则:",
                "1. 系统会显示一个成语",
                "2. 你需要说出以该成语最后一个字开头的成语",
                "3. 如果30秒内没有回答，AI自动接龙",
                "4. 正确接龙得10分",
                "5. 总共进行10回合",
                "",
                "按 空格键 开始游戏"
            ]
            
            for i, line in enumerate(instructions):
                text = font_small.render(line, True, WHITE)
                screen.blit(text, (WIDTH // 2 - 200, 200 + i * 35))
        
        elif game.phase == "playing":
            pygame.draw.rect(screen, (30, 30, 50), (0, 0, WIDTH, 100))
            
            round_text = font_medium.render(f"回合: {game.round}/{game.max_rounds}", True, WHITE)
            screen.blit(round_text, (20, 30))
            
            player_score = font_medium.render(f"你: {game.player_score}分", True, GREEN)
            screen.blit(player_score, (200, 30))
            
            ai_score = font_medium.render(f"AI: {game.ai_score}分", True, RED)
            screen.blit(ai_score, (200, 60))
            
            time_color = GREEN if game.time_left > 20 else YELLOW if game.time_left > 10 else RED
            time_text = font_large.render(f"时间: {game.time_left}", True, time_color)
            screen.blit(time_text, (WIDTH - 150, 20))
            
            current_display = font_large.render(f"当前成语: {game.current_idiom}", True, YELLOW)
            screen.blit(current_display, (WIDTH // 2 - current_display.get_width() // 2, 130))
            
            next_char = game.current_idiom[-1]
            next_text = font_medium.render(f"下一个成语需要以 '{next_char}' 开头", True, WHITE)
            screen.blit(next_text, (WIDTH // 2 - next_text.get_width() // 2, 190))
            
            pygame.draw.rect(screen, (50, 50, 70), (WIDTH // 2 - 200, 250, 400, 60), 3)
            input_display = font_large.render(user_input, True, WHITE)
            screen.blit(input_display, (WIDTH // 2 - 200, 255))
            
            prompt = font_small.render("输入成语后按回车确认", True, GRAY)
            screen.blit(prompt, (WIDTH // 2 - 80, 320))
            
            prompt2 = font_small.render("按 H 获取提示", True, GRAY)
            screen.blit(prompt2, (WIDTH // 2 - 50, 350))
            
            history_y = 400
            history_title = font_medium.render("接龙历史:", True, WHITE)
            screen.blit(history_title, (50, history_y))
            
            for i, idiom in enumerate(game.history[-8:]):
                color = GREEN if i == len(game.history) - 1 else GRAY
                text = font_small.render(idiom, True, color)
                screen.blit(text, (50 + (i % 2) * 200, history_y + 30 + (i // 2) * 30))
        
        elif game.phase == "result":
            title = font_large.render("游戏结束!", True, YELLOW)
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 150))
            
            if game.player_score > game.ai_score:
                result = font_large.render("🎉 你赢了!", True, GREEN)
            elif game.player_score < game.ai_score:
                result = font_large.render("😅 AI赢了", True, RED)
            else:
                result = font_large.render("🤝 平局!", True, YELLOW)
            screen.blit(result, (WIDTH // 2 - 80, 220))
            
            scores = [
                f"你的得分: {game.player_score}",
                f"AI得分: {game.ai_score}",
                f"总共接龙: {len(game.history) - 1}个成语"
            ]
            
            for i, line in enumerate(scores):
                text = font_medium.render(line, True, WHITE)
                screen.blit(text, (WIDTH // 2 - 100, 300 + i * 50))
            
            restart = font_small.render("按 R 重新开始", True, WHITE)
            screen.blit(restart, (WIDTH // 2 - 60, 500))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            
            elif event.type == pygame.KEYDOWN:
                if game.phase == "start" and event.key == pygame.K_SPACE:
                    game.start_game()
                
                elif game.phase == "playing":
                    if event.key == pygame.K_BACKSPACE:
                        user_input = user_input[:-1]
                    elif event.key == pygame.K_RETURN and user_input:
                        valid, msg = game.check_idiom(user_input)
                        if valid:
                            game.history.append(user_input)
                            game.current_idiom = user_input
                            game.player_score += 10
                            user_input = ""
                            
                            ai_response = game.ai_respond()
                            if not ai_response:
                                game.phase = "result"
                            else:
                                game.round += 1
                                if game.round > game.max_rounds:
                                    game.phase = "result"
                                else:
                                    game.time_left = 30
                        else:
                            time_color = RED
                    elif event.key == pygame.K_h:
                        hint = game.get_hint()
                        hint_text = font_small.render(hint, True, YELLOW)
                        screen.blit(hint_text, (WIDTH // 2 - 150, 380))
                
                elif game.phase == "result" and event.key == pygame.K_r:
                    game.phase = "start"
            
            elif event.type == timer_event and game.phase == "playing":
                game.time_left -= 1
                if game.time_left <= 0:
                    ai_response = game.ai_respond()
                    if not ai_response:
                        game.phase = "result"
                    else:
                        game.round += 1
                        if game.round > game.max_rounds:
                            game.phase = "result"
                        else:
                            game.time_left = 30
        
        clock.tick(60)

if __name__ == "__main__":
    idiom_game()
