import pygame
import os
import random
import math
import sys

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

try:
    pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
    audio_available = True
except Exception:
    audio_available = False

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("人生模拟器")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (240, 240, 240)
DARK_GRAY = (100, 100, 100)
RED = (220, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 100, 200)
YELLOW = (255, 200, 50)
PURPLE = (150, 50, 200)
ORANGE = (255, 150, 50)
PINK = (255, 150, 200)
BROWN = (139, 69, 19)

font_large = get_chinese_font(48)
font_medium = get_chinese_font(36)
font_small = get_chinese_font(24)

class SoundManager:
    def __init__(self):
        self.sounds = {}
        if audio_available:
            self.generate_sounds()
    
    def generate_tone(self, frequency, duration, volume=0.5):
        sample_rate = 22050
        n_samples = int(sample_rate * duration)
        sound_buffer = bytearray()
        for i in range(n_samples):
            t = i / sample_rate
            value = int(32767 * volume * math.sin(2 * math.pi * frequency * t))
            sound_buffer.append(value & 0xff)
            sound_buffer.append((value >> 8) & 0xff)
        return pygame.mixer.Sound(sound_buffer)
    
    def generate_sounds(self):
        self.sounds['click'] = self.generate_tone(800, 0.1, 0.3)
        self.sounds['success'] = self.generate_tone(1000, 0.15, 0.4)
        self.sounds['fail'] = self.generate_tone(300, 0.2, 0.3)
        self.sounds['birthday'] = self.generate_tone(600, 0.1, 0.3)
        self.sounds['death'] = self.generate_tone(200, 0.5, 0.4)
    
    def play(self, sound_name):
        if audio_available and sound_name in self.sounds:
            self.sounds[sound_name].play()

sound_manager = SoundManager()

class LifeStage:
    INFANT = "婴儿"
    CHILD = "儿童"
    TEEN = "青少年"
    ADULT = "成年"
    MIDDLE = "中年"
    ELDERLY = "老年"

class LifeSimulator:
    def __init__(self):
        self.age = 0
        self.stage = LifeStage.INFANT
        self.health = 80
        self.happiness = 70
        self.wealth = 0
        self.education = 0
        self.is_alive = True
        self.life_events = []
        self.year = 0
        self.current_choices = []
        self.show_result = False
        self.result_text = ""
        self.game_over = False
        self.generate_choices()
    
    def get_stage(self):
        if self.age < 3:
            return LifeStage.INFANT
        elif self.age < 12:
            return LifeStage.CHILD
        elif self.age < 18:
            return LifeStage.TEEN
        elif self.age < 40:
            return LifeStage.ADULT
        elif self.age < 60:
            return LifeStage.MIDDLE
        else:
            return LifeStage.ELDERLY
    
    def generate_choices(self):
        stage = self.get_stage()
        self.current_choices = []
        
        if stage == LifeStage.INFANT:
            self.current_choices = [
                {"text": "乖乖睡觉", "effects": {"health": 5, "happiness": 3, "wealth": 0, "education": 0}},
                {"text": "哭闹不止", "effects": {"health": -2, "happiness": -5, "wealth": 0, "education": 0}},
                {"text": "探索世界", "effects": {"health": 2, "happiness": 5, "wealth": 0, "education": 2}}
            ]
        elif stage == LifeStage.CHILD:
            self.current_choices = [
                {"text": "努力学习", "effects": {"health": -1, "happiness": -2, "wealth": 0, "education": 8}},
                {"text": "尽情玩耍", "effects": {"health": 3, "happiness": 8, "wealth": 0, "education": 1}},
                {"text": "帮做家务", "effects": {"health": 2, "happiness": 2, "wealth": 2, "education": 2}}
            ]
        elif stage == LifeStage.TEEN:
            self.current_choices = [
                {"text": "认真读书备考", "effects": {"health": -3, "happiness": -5, "wealth": 0, "education": 12}},
                {"text": "谈恋爱", "effects": {"health": 1, "happiness": 10, "wealth": -5, "education": -3}},
                {"text": "打工赚钱", "effects": {"health": -2, "happiness": -3, "wealth": 15, "education": 2}},
                {"text": "发展兴趣", "effects": {"health": 2, "happiness": 8, "wealth": -2, "education": 5}}
            ]
        elif stage == LifeStage.ADULT:
            self.current_choices = [
                {"text": "努力工作", "effects": {"health": -5, "happiness": -3, "wealth": 25, "education": 3}},
                {"text": "创业冒险", "effects": {"health": -8, "happiness": -5, "wealth": 50, "education": 5}},
                {"text": "结婚生子", "effects": {"health": -3, "happiness": 12, "wealth": -15, "education": 2}},
                {"text": "继续深造", "effects": {"health": 2, "happiness": 3, "wealth": -10, "education": 15}}
            ]
        elif stage == LifeStage.MIDDLE:
            self.current_choices = [
                {"text": "事业冲刺", "effects": {"health": -6, "happiness": -4, "wealth": 30, "education": 2}},
                {"text": "照顾家庭", "effects": {"health": 3, "happiness": 10, "wealth": -5, "education": 1}},
                {"text": "投资理财", "effects": {"health": -2, "happiness": 2, "wealth": 20, "education": 3}},
                {"text": "锻炼身体", "effects": {"health": 8, "happiness": 5, "wealth": -3, "education": 0}}
            ]
        elif stage == LifeStage.ELDERLY:
            self.current_choices = [
                {"text": "安享晚年", "effects": {"health": 5, "happiness": 8, "wealth": -8, "education": 0}},
                {"text": "含饴弄孙", "effects": {"health": 3, "happiness": 12, "wealth": -5, "education": 0}},
                {"text": "继续工作", "effects": {"health": -5, "happiness": -3, "wealth": 15, "education": 1}}
            ]
        
        if random.random() < 0.3:
            self.add_random_event()
    
    def add_random_event(self):
        events = [
            {"text": "意外收获意外之财！", "effects": {"health": 0, "happiness": 5, "wealth": 20, "education": 0}},
            {"text": "生病住院", "effects": {"health": -15, "happiness": -10, "wealth": -10, "education": 0}},
            {"text": "遇到贵人", "effects": {"health": 0, "happiness": 8, "wealth": 10, "education": 5}},
            {"text": "中了小奖", "effects": {"health": 0, "happiness": 15, "wealth": 30, "education": 0}},
            {"text": "失去亲人", "effects": {"health": -5, "happiness": -15, "wealth": 0, "education": 0}},
            {"text": "学到新技能", "effects": {"health": 0, "happiness": 5, "wealth": 0, "education": 8}}
        ]
        event = random.choice(events)
        self.result_text = event["text"]
        self.health += event["effects"]["health"]
        self.happiness += event["effects"]["happiness"]
        self.wealth += event["effects"]["wealth"]
        self.education += event["effects"]["education"]
        self.show_result = True
    
    def make_choice(self, choice_index):
        if 0 <= choice_index < len(self.current_choices):
            choice = self.current_choices[choice_index]
            self.health += choice["effects"]["health"]
            self.happiness += choice["effects"]["happiness"]
            self.wealth += choice["effects"]["wealth"]
            self.education += choice["effects"]["education"]
            
            self.life_events.append(f"{self.age}岁: {choice['text']}")
            
            if choice["effects"]["health"] > 0 or choice["effects"]["happiness"] > 0 or choice["effects"]["wealth"] > 0 or choice["effects"]["education"] > 0:
                sound_manager.play('success')
            else:
                sound_manager.play('fail')
            
            self.next_year()
    
    def next_year(self):
        self.age += 1
        self.year += 1
        
        sound_manager.play('birthday')
        
        self.health = max(0, min(100, self.health))
        self.happiness = max(0, min(100, self.happiness))
        self.wealth = max(-100, min(200, self.wealth))
        self.education = max(0, min(100, self.education))
        
        if self.health <= 0:
            self.is_alive = False
            self.game_over = True
            sound_manager.play('death')
            return
        
        if self.get_stage() != self.stage:
            self.stage = self.get_stage()
        
        self.generate_choices()
    
    def get_life_summary(self):
        summary = []
        summary.append(f"你活到了 {self.age} 岁")
        summary.append(f"最终健康: {self.health}")
        summary.append(f"最终幸福: {self.happiness}")
        summary.append(f"最终财富: {self.wealth}")
        summary.append(f"最终学历: {self.education}")
        
        score = (self.health + self.happiness + self.wealth + self.education)
        
        if score >= 300:
            summary.append("人生评价: 完美人生！")
        elif score >= 200:
            summary.append("人生评价: 成功人生！")
        elif score >= 100:
            summary.append("人生评价: 普通人生")
        else:
            summary.append("人生评价: 悲惨人生")
        
        return summary

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.hovered = False
    
    def draw(self, surface):
        color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=10)
        
        text_surface = font_small.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.hovered:
                return True
        return False

class Game:
    def __init__(self):
        self.simulator = LifeSimulator()
        self.buttons = []
        self.restart_button = Button(300, 500, 200, 50, "重新开始", GREEN, (100, 255, 100))
        self.state = "playing"
    
    def update_buttons(self):
        self.buttons = []
        button_width = 300
        button_height = 60
        start_y = 250
        spacing = 10
        
        for i, choice in enumerate(self.simulator.current_choices):
            x = (SCREEN_WIDTH - button_width) // 2
            y = start_y + i * (button_height + spacing)
            button = Button(x, y, button_width, button_height, choice["text"], LIGHT_GRAY, GRAY)
            self.buttons.append(button)
    
    def draw_attribute_bar(self, surface, x, y, width, height, value, max_value, color, label):
        pygame.draw.rect(surface, GRAY, (x, y, width, height), border_radius=5)
        fill_width = int((value / max_value) * width)
        fill_width = max(0, min(width, fill_width))
        pygame.draw.rect(surface, color, (x, y, fill_width, height), border_radius=5)
        pygame.draw.rect(surface, BLACK, (x, y, width, height), 2, border_radius=5)
        
        label_surface = font_small.render(f"{label}: {value}", True, BLACK)
        surface.blit(label_surface, (x, y - 20))
    
    def draw(self):
        screen.fill(WHITE)
        
        if self.state == "playing":
            self.draw_playing()
        elif self.state == "game_over":
            self.draw_game_over()
        
        pygame.display.flip()
    
    def draw_playing(self):
        title_text = font_large.render("人生模拟器", True, BLACK)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
        screen.blit(title_text, title_rect)
        
        age_text = font_medium.render(f"年龄: {self.simulator.age} 岁", True, BLACK)
        age_rect = age_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        screen.blit(age_text, age_rect)
        
        stage_text = font_medium.render(f"阶段: {self.simulator.get_stage()}", True, PURPLE)
        stage_rect = stage_text.get_rect(center=(SCREEN_WIDTH // 2, 140))
        screen.blit(stage_text, stage_rect)
        
        bar_width = 150
        bar_height = 20
        start_x = 50
        start_y = 180
        spacing = 60
        
        self.draw_attribute_bar(screen, start_x, start_y, bar_width, bar_height, self.simulator.health, 100, GREEN, "健康")
        self.draw_attribute_bar(screen, start_x + bar_width + 50, start_y, bar_width, bar_height, self.simulator.happiness, 100, YELLOW, "幸福")
        self.draw_attribute_bar(screen, start_x, start_y + spacing, bar_width, bar_height, self.simulator.wealth, 200, BLUE, "财富")
        self.draw_attribute_bar(screen, start_x + bar_width + 50, start_y + spacing, bar_width, bar_height, self.simulator.education, 100, ORANGE, "学历")
        
        if self.simulator.show_result:
            result_text = font_medium.render(self.simulator.result_text, True, RED)
            result_rect = result_text.get_rect(center=(SCREEN_WIDTH // 2, 300))
            screen.blit(result_text, result_rect)
        
        self.update_buttons()
        for button in self.buttons:
            button.draw(screen)
    
    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        title_text = font_large.render("人生结束", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 80))
        screen.blit(title_text, title_rect)
        
        summary = self.simulator.get_life_summary()
        for i, line in enumerate(summary):
            text = font_medium.render(line, True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 150 + i * 50))
            screen.blit(text, text_rect)
        
        self.restart_button.draw(screen)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if self.state == "playing":
                for i, button in enumerate(self.buttons):
                    if button.handle_event(event):
                        sound_manager.play('click')
                        self.simulator.make_choice(i)
                        if self.simulator.game_over:
                            self.state = "game_over"
            
            elif self.state == "game_over":
                if self.restart_button.handle_event(event):
                    sound_manager.play('click')
                    self.simulator = LifeSimulator()
                    self.state = "playing"
    
    def run(self):
        while True:
            self.handle_events()
            self.draw()
            clock.tick(60)

if __name__ == "__main__":
    game = Game()
    game.run()
