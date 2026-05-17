import pygame
import os
import random
import math
import sys

# 初始化pygame
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

# 音效生成函数
def generate_sound(frequency, duration, sample_rate=44100):
    samples = int(sample_rate * duration)
    arr = bytearray()
    for i in range(samples):
        t = i / sample_rate
        value = int(math.sin(2 * math.pi * frequency * t) * 127 + 128)
        arr.append(value)
    return pygame.mixer.Sound(arr)

# 生成音效
try:
    pygame.mixer.init(frequency=44100, size=-8, channels=1)
    click_sound = generate_sound(800, 0.1)
    success_sound = generate_sound(523, 0.2)
    fail_sound = generate_sound(200, 0.3)
    level_up_sound = generate_sound(659, 0.15)
    
    def play_sound(sound):
        sound.play()
except pygame.error:
    # 没有音频设备时的静音模式
    class DummySound:
        def play(self):
            pass
    
    click_sound = DummySound()
    success_sound = DummySound()
    fail_sound = DummySound()
    level_up_sound = DummySound()

# 游戏常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (50, 100, 200)
GREEN = (50, 200, 100)
RED = (200, 50, 50)
YELLOW = (255, 200, 50)

# 设置屏幕
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("校园生活模拟器")

# 字体设置
font = get_chinese_font(36)
small_font = get_chinese_font(24)
large_font = get_chinese_font(48)

# 游戏阶段
STAGES = ["小学", "初中", "高中", "大学"]
STAGE_YEARS = [6, 3, 3, 4]

# 事件列表
EVENTS = [
    {"text": "你在图书馆遇到了一位有趣的同学", "choices": [
        {"text": "主动打招呼", "effects": {"学习": -5, "社交": 15, "心情": 10}},
        {"text": "专注学习不理会", "effects": {"学习": 5, "社交": -5}}
    ]},
    {"text": "学校组织了一场运动会", "choices": [
        {"text": "积极参加比赛", "effects": {"体力": -15, "社交": 10, "心情": 15}},
        {"text": "当啦啦队", "effects": {"社交": 5, "心情": 10}},
        {"text": "待在教室学习", "effects": {"学习": 10, "体力": 5}}
    ]},
    {"text": "期末考试临近", "choices": [
        {"text": "熬夜复习", "effects": {"学习": 20, "体力": -20, "心情": -10}},
        {"text": "正常复习", "effects": {"学习": 10, "体力": -5}},
        {"text": "放松心态", "effects": {"心情": 10}}
    ]},
    {"text": "同学邀请你参加生日派对", "choices": [
        {"text": "参加派对", "effects": {"社交": 15, "心情": 15, "体力": -10}},
        {"text": "拒绝并学习", "effects": {"学习": 10, "社交": -5, "心情": -5}}
    ]},
    {"text": "你感到很累", "choices": [
        {"text": "睡个好觉", "effects": {"体力": 25, "心情": 10}},
        {"text": "喝咖啡继续学习", "effects": {"学习": 5, "体力": -10, "心情": -5}}
    ]},
    {"text": "发现一本好书", "choices": [
        {"text": "认真阅读", "effects": {"学习": 15, "心情": 5}},
        {"text": "借回去以后看", "effects": {"学习": 5}}
    ]},
    {"text": "老师布置了很多作业", "choices": [
        {"text": "认真完成", "effects": {"学习": 15, "体力": -10}},
        {"text": "抄同学的", "effects": {"学习": 0, "社交": -10, "心情": -5}}
    ]},
    {"text": "周末到了", "choices": [
        {"text": "去图书馆学习", "effects": {"学习": 10, "体力": -5}},
        {"text": "和朋友出去玩", "effects": {"社交": 15, "心情": 15, "体力": -10}},
        {"text": "在家休息", "effects": {"体力": 20, "心情": 5}}
    ]}
]

class Game:
    def __init__(self):
        self.reset_game()
    
    def reset_game(self):
        self.stage = 0
        self.year = 1
        self.attributes = {"学习": 20, "社交": 20, "体力": 100, "心情": 70}
        self.scores = []
        self.current_event = None
        self.event_choices = None
        self.game_over = False
        self.final_evaluation = ""
        self.game_state = "menu"  # menu, playing, event, exam, result
    
    def update_attributes(self, effects):
        for attr, value in effects.items():
            if attr in self.attributes:
                self.attributes[attr] = max(0, min(100, self.attributes[attr] + value))
    
    def get_random_event(self):
        return random.choice(EVENTS)
    
    def calculate_exam_score(self):
        base_score = self.attributes["学习"]
        mood_bonus = self.attributes["心情"] // 10
        energy_bonus = self.attributes["体力"] // 20
        random_factor = random.randint(-10, 10)
        score = min(100, max(0, base_score + mood_bonus + energy_bonus + random_factor))
        return score
    
    def get_evaluation(self):
        avg_score = sum(self.scores) / len(self.scores) if self.scores else 0
        total_attr = sum(self.attributes.values())
        
        if avg_score >= 90 and total_attr >= 300:
            return "🌟 优秀毕业生！你的校园生活非常成功！"
        elif avg_score >= 80 and total_attr >= 250:
            return "🎉 良好毕业生！你的校园生活丰富多彩！"
        elif avg_score >= 60 and total_attr >= 200:
            return "👍 合格毕业生！继续加油！"
        else:
            return "💪 还有进步空间！未来可期！"

def draw_menu():
    screen.fill(WHITE)
    
    title = large_font.render("校园生活模拟器", True, BLUE)
    title_rect = title.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 80))
    screen.blit(title, title_rect)
    
    start_button = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2, 200, 50)
    pygame.draw.rect(screen, GREEN, start_button)
    start_text = font.render("开始游戏", True, WHITE)
    start_text_rect = start_text.get_rect(center=start_button.center)
    screen.blit(start_text, start_text_rect)
    
    return start_button

def draw_game_hud(game):
    # 阶段和年份
    stage_text = font.render(f"{STAGES[game.stage]} - 第 {game.year} 年", True, BLACK)
    screen.blit(stage_text, (20, 20))
    
    # 属性条
    y = 60
    for attr, value in game.attributes.items():
        label = small_font.render(attr, True, BLACK)
        screen.blit(label, (20, y))
        
        bar_bg = pygame.Rect(80, y + 5, 200, 20)
        pygame.draw.rect(screen, GRAY, bar_bg)
        
        bar_fg = pygame.Rect(80, y + 5, int(value * 2), 20)
        color = BLUE if attr == "学习" else GREEN if attr == "社交" else YELLOW if attr == "体力" else RED
        pygame.draw.rect(screen, color, bar_fg)
        
        value_text = small_font.render(f"{value}", True, BLACK)
        screen.blit(value_text, (290, y))
        
        y += 35

def draw_actions():
    actions = [
        {"text": "📚 学习", "effects": {"学习": 15, "社交": -5, "体力": -10, "心情": -5}},
        {"text": "👥 社交", "effects": {"社交": 15, "学习": -5, "心情": 10}},
        {"text": "⚽ 运动", "effects": {"体力": 20, "学习": -5, "心情": 10}},
        {"text": "😴 休息", "effects": {"体力": 30, "心情": 15}}
    ]
    
    buttons = []
    for i, action in enumerate(actions):
        button = pygame.Rect(SCREEN_WIDTH//2 - 150 + (i % 2) * 160, 400 + (i // 2) * 60, 140, 50)
        pygame.draw.rect(screen, BLUE, button)
        text = font.render(action["text"], True, WHITE)
        text_rect = text.get_rect(center=button.center)
        screen.blit(text, text_rect)
        buttons.append((button, action["effects"]))
    
    return buttons

def draw_event(game):
    if game.current_event:
        # 事件背景
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        # 事件文本
        event_box = pygame.Rect(SCREEN_WIDTH//2 - 300, SCREEN_HEIGHT//2 - 150, 600, 300)
        pygame.draw.rect(screen, WHITE, event_box)
        
        event_text = font.render(game.current_event["text"], True, BLACK)
        event_text_rect = event_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 80))
        screen.blit(event_text, event_text_rect)
        
        # 选项按钮
        buttons = []
        choices = game.current_event["choices"]
        for i, choice in enumerate(choices):
            button = pygame.Rect(SCREEN_WIDTH//2 - 250, SCREEN_HEIGHT//2 - 30 + i * 70, 500, 50)
            pygame.draw.rect(screen, BLUE, button)
            text = font.render(choice["text"], True, WHITE)
            text_rect = text.get_rect(center=button.center)
            screen.blit(text, text_rect)
            buttons.append((button, choice["effects"]))
        
        return buttons
    return []

def draw_exam_result(score):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(200)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))
    
    result_box = pygame.Rect(SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 - 100, 400, 200)
    pygame.draw.rect(screen, WHITE, result_box)
    
    exam_text = font.render("期末考试成绩", True, BLACK)
    exam_text_rect = exam_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
    screen.blit(exam_text, exam_text_rect)
    
    score_text = large_font.render(f"{score}分", True, BLUE if score >= 60 else RED)
    score_text_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
    screen.blit(score_text, score_text_rect)
    
    if score >= 90:
        grade_text = font.render("优秀！🎉", True, GREEN)
    elif score >= 80:
        grade_text = font.render("良好！👍", True, BLUE)
    elif score >= 60:
        grade_text = font.render("及格！😊", True, YELLOW)
    else:
        grade_text = font.render("不及格...😢", True, RED)
    
    grade_text_rect = grade_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 70))
    screen.blit(grade_text, grade_text_rect)
    
    continue_button = pygame.Rect(SCREEN_WIDTH//2 - 80, SCREEN_HEIGHT//2 + 100, 160, 40)
    pygame.draw.rect(screen, GREEN, continue_button)
    continue_text = font.render("继续", True, WHITE)
    continue_text_rect = continue_text.get_rect(center=continue_button.center)
    screen.blit(continue_text, continue_text_rect)
    
    return continue_button

def draw_game_over(game):
    screen.fill(WHITE)
    
    title = large_font.render("🎓 毕业啦！", True, BLUE)
    title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 100))
    screen.blit(title, title_rect)
    
    evaluation = font.render(game.final_evaluation, True, BLACK)
    evaluation_rect = evaluation.get_rect(center=(SCREEN_WIDTH//2, 200))
    screen.blit(evaluation, evaluation_rect)
    
    # 统计信息
    stats_y = 280
    
    avg_score = sum(game.scores) / len(game.scores) if game.scores else 0
    avg_text = font.render(f"平均成绩: {avg_score:.1f}分", True, BLACK)
    screen.blit(avg_text, (SCREEN_WIDTH//2 - 150, stats_y))
    
    for attr, value in game.attributes.items():
        attr_text = font.render(f"{attr}: {value}", True, BLACK)
        screen.blit(attr_text, (SCREEN_WIDTH//2 - 150, stats_y + 40))
        stats_y += 40
    
    restart_button = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 100, 200, 50)
    pygame.draw.rect(screen, GREEN, restart_button)
    restart_text = font.render("重新开始", True, WHITE)
    restart_text_rect = restart_text.get_rect(center=restart_button.center)
    screen.blit(restart_text, restart_text_rect)
    
    return restart_button

def main():
    game = Game()
    clock = pygame.time.Clock()
    
    while True:
        screen.fill(WHITE)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                
                if game.game_state == "menu":
                    start_button = draw_menu()
                    if start_button.collidepoint(pos):
                        click_sound.play()
                        game.game_state = "playing"
                
                elif game.game_state == "playing":
                    buttons = draw_actions()
                    for button, effects in buttons:
                        if button.collidepoint(pos):
                            click_sound.play()
                            game.update_attributes(effects)
                            
                            # 随机事件
                            if random.random() < 0.5:
                                game.current_event = game.get_random_event()
                                game.game_state = "event"
                            else:
                                # 检查是否该考试
                                game.year += 1
                                if game.year > STAGE_YEARS[game.stage]:
                                    # 阶段结束，考试
                                    game.game_state = "exam"
                                elif game.year % STAGE_YEARS[game.stage] == 0 or random.random() < 0.3:
                                    # 随机考试
                                    game.game_state = "exam"
                
                elif game.game_state == "event":
                    buttons = draw_event(game)
                    for button, effects in buttons:
                        if button.collidepoint(pos):
                            click_sound.play()
                            game.update_attributes(effects)
                            game.current_event = None
                            game.year += 1
                            
                            if game.year > STAGE_YEARS[game.stage]:
                                game.game_state = "exam"
                            else:
                                game.game_state = "playing"
                
                elif game.game_state == "exam":
                    continue_button = draw_exam_result(0)  # 占位
                    if continue_button.collidepoint(pos):
                        game.stage += 1
                        if game.stage >= len(STAGES):
                            game.final_evaluation = game.get_evaluation()
                            game.game_over = True
                            game.game_state = "result"
                        else:
                            game.year = 1
                            game.game_state = "playing"
                
                elif game.game_state == "result":
                    restart_button = draw_game_over(game)
                    if restart_button.collidepoint(pos):
                        click_sound.play()
                        game.reset_game()
        
        # 绘制画面
        if game.game_state == "menu":
            draw_menu()
        
        elif game.game_state == "playing":
            draw_game_hud(game)
            draw_actions()
            
            # 阶段进度条
            total_years = sum(STAGE_YEARS)
            current_total = sum(STAGE_YEARS[:game.stage]) + game.year - 1
            progress = current_total / total_years
            progress_bar = pygame.Rect(20, SCREEN_HEIGHT - 30, SCREEN_WIDTH - 40, 20)
            pygame.draw.rect(screen, GRAY, progress_bar)
            pygame.draw.rect(screen, BLUE, (20, SCREEN_HEIGHT - 30, (SCREEN_WIDTH - 40) * progress, 20))
        
        elif game.game_state == "event":
            draw_game_hud(game)
            draw_event(game)
        
        elif game.game_state == "exam":
            draw_game_hud(game)
            score = game.calculate_exam_score()
            game.scores.append(score)
            if score >= 60:
                success_sound.play()
            else:
                fail_sound.play()
            continue_button = draw_exam_result(score)
        
        elif game.game_state == "result":
            draw_game_over(game)
        
        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()