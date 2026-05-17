"""
聊天机器人
与AI聊天机器人对话
"""

import pygame
import os
import sys
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

WIDTH, HEIGHT = 850, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("聊天机器人")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (50, 50, 50)
LIGHT_GRAY = (230, 230, 230)
BLUE = (0, 120, 200)
GREEN = (0, 180, 100)
PURPLE = (150, 50, 200)

responses = {
    "hello": ["你好!", "嗨!", "你好啊!"],
    "你好": ["你好!", "嗨!", "你好啊!"],
    "hi": ["Hi!", "Hello!", "你好!"],
    "名字": ["我叫小智!", "你可以叫我AI助手", "我是聊天机器人!"],
    "你是谁": ["我叫小智!", "你可以叫我AI助手", "我是聊天机器人!"],
    "你好吗": ["我很好，谢谢!", "我很棒!", "挺好的!"],
    "好": ["好的!", "没问题!", "了解!"],
    "再见": ["再见!", "拜拜!", "下次见!"],
    "bye": ["Bye!", "Goodbye!", "再见!"],
    "喜欢": ["我喜欢和你聊天!", "那很棒!", "听起来不错!"],
    "爱": ["谢谢! 我也喜欢和你聊天!", "你真好!", "❤️"],
    "游戏": ["你喜欢玩什么游戏?", "我知道很多游戏!", "我们来玩个游戏吧!"],
    "学习": ["学习很重要!", "加油!", "你可以的!"],
    "天气": ["今天天气怎样?", "我希望是个好天气!"],
    "吃": ["我喜欢吃披萨!", "你想吃什么?", "美食万岁!"],
    "default": ["有意思!", "继续说!", "嗯嗯", "我明白了!", "真的吗?", "好有趣!"]
}

class ChatMessage:
    def __init__(self, text, is_user):
        self.text = text
        self.is_user = is_user
        self.time = 0

class ChatBot:
    def __init__(self):
        self.messages = []
        self.input_text = ""
        self.font_large = get_chinese_font(48)
        self.font_medium = get_chinese_font(32)
        self.font_small = get_chinese_font(26)
        self.add_message("你好！我是小智，很高兴和你聊天！", False)
    
    def add_message(self, text, is_user):
        self.messages.append(ChatMessage(text, is_user))
        if len(self.messages) > 15:
            self.messages.pop(0)
    
    def get_response(self, text):
        text = text.lower()
        
        for key, resp in responses.items():
            if key in text:
                return random.choice(resp)
        
        return random.choice(responses["default"])
    
    def send_message(self):
        if self.input_text.strip():
            self.add_message(self.input_text, True)
            self.input_text = ""
            
            pygame.time.wait(300)
            response = self.get_response(self.messages[-1].text)
            self.add_message(response, False)
    
    def draw(self):
        screen.fill(LIGHT_GRAY)
        
        # 标题
        pygame.draw.rect(screen, BLUE, (0, 0, WIDTH, 60))
        title = self.font_large.render("🤖 聊天机器人", True, WHITE)
        screen.blit(title, (20, 10))
        
        # 聊天区域
        y = 80
        for msg in self.messages:
            bg = GREEN if msg.is_user else (200, 200, 200)
            text_color = WHITE if msg.is_user else BLACK
            
            text_surface = self.font_small.render(msg.text, True, text_color)
            
            if msg.is_user:
                x = WIDTH - text_surface.get_width() - 30
            else:
                x = 30
            
            pygame.draw.rect(screen, bg, (x - 10, y - 5, 
                                          text_surface.get_width() + 20, 35), border_radius=10)
            screen.blit(text_surface, (x, y))
            y += 45
        
        # 输入区域
        pygame.draw.rect(screen, WHITE, (20, HEIGHT - 70, WIDTH - 140, 45), border_radius=8)
        pygame.draw.rect(screen, GRAY, (20, HEIGHT - 70, WIDTH - 140, 45), 2, border_radius=8)
        
        input_surface = self.font_medium.render(self.input_text, True, BLACK)
        screen.blit(input_surface, (30, HEIGHT - 60))
        
        # 发送按钮
        send_btn = pygame.Rect(WIDTH - 110, HEIGHT - 70, 90, 45)
        pygame.draw.rect(screen, BLUE, send_btn, border_radius=8)
        send_text = self.font_medium.render("发送", True, WHITE)
        screen.blit(send_text, (WIDTH - 98, HEIGHT - 60))
        
        pygame.display.flip()
    
    def handle_click(self, pos):
        send_btn = pygame.Rect(WIDTH - 110, HEIGHT - 70, 90, 45)
        if send_btn.collidepoint(pos):
            self.send_message()
    
    def handle_key(self, key):
        if key == pygame.K_RETURN:
            self.send_message()
        elif key == pygame.K_BACKSPACE:
            self.input_text = self.input_text[:-1]
        elif key == pygame.K_ESCAPE:
            pass
        else:
            if len(self.input_text) < 50 and hasattr(event, 'unicode') and event.unicode.isprintable():
                self.input_text += event.unicode

def main():
    bot = ChatBot()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    bot.handle_click(event.pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                else:
                    if event.key == pygame.K_RETURN:
                        bot.send_message()
                    elif event.key == pygame.K_BACKSPACE:
                        bot.input_text = bot.input_text[:-1]
                    elif len(bot.input_text) < 50 and event.unicode and event.unicode.isprintable():
                        bot.input_text += event.unicode
        
        bot.draw()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
