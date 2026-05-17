import pygame
import os
import sys
import math
import random
from pygame.locals import *

# 初始化 pygame
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

# 初始化音效系统
try:
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
    sound_enabled = True
except pygame.error:
    sound_enabled = False

# 屏幕设置
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("生命科学学习工具")

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (50, 100, 200)
GREEN = (50, 200, 100)
RED = (200, 50, 50)
YELLOW = (255, 200, 50)
PURPLE = (150, 50, 200)
PINK = (255, 100, 150)
ORANGE = (255, 150, 50)
CYAN = (50, 200, 200)
BROWN = (139, 69, 19)

# 字体设置
font_large = get_chinese_font(48)
font_medium = get_chinese_font(32)
font_small = get_chinese_font(24)

# 音效生成器
def generate_sound(frequency, duration, volume=0.1):
    """使用 bytearray 生成音效"""
    if not sound_enabled:
        return None
    
    sample_rate = 44100
    num_samples = int(sample_rate * duration)
    sound_data = bytearray()
    
    for i in range(num_samples):
        t = float(i) / sample_rate
        value = int(128 + 127 * math.sin(2 * math.pi * frequency * t))
        sound_data.append(value)
    
    sound = pygame.mixer.Sound(sound_data)
    sound.set_volume(volume)
    return sound

# 空音效函数（用于无声环境）
class DummySound:
    def play(self):
        pass

# 预生成音效
click_sound = generate_sound(800, 0.1) if sound_enabled else DummySound()
success_sound = generate_sound(523, 0.15) if sound_enabled else DummySound()
error_sound = generate_sound(200, 0.2) if sound_enabled else DummySound()
hover_sound = generate_sound(600, 0.05) if sound_enabled else DummySound()

# 当前页面
current_page = "menu"

# 游戏状态
dna_angle = 0
cell_parts = []
selected_part = None
genetics_score = 0
genetics_question = 0

# 细胞结构部件
cell_structure = [
    {"name": "细胞膜", "color": BLUE, "x": 600, "y": 400, "radius": 250, "info": "细胞膜是细胞的外层边界，控制物质进出细胞。"},
    {"name": "细胞质", "color": CYAN, "x": 600, "y": 400, "radius": 200, "info": "细胞质是细胞内的胶状物质，包含各种细胞器。"},
    {"name": "细胞核", "color": PURPLE, "x": 600, "y": 400, "radius": 80, "info": "细胞核是细胞的控制中心，包含DNA。"},
    {"name": "线粒体", "color": ORANGE, "x": 450, "y": 300, "radius": 30, "info": "线粒体是细胞的能量工厂，产生ATP。"},
    {"name": "叶绿体", "color": GREEN, "x": 750, "y": 500, "radius": 35, "info": "叶绿体是植物细胞特有的，进行光合作用。"},
    {"name": "内质网", "color": PINK, "x": 500, "y": 450, "radius": 25, "info": "内质网参与蛋白质和脂质的合成。"},
    {"name": "高尔基体", "color": YELLOW, "x": 700, "y": 350, "radius": 28, "info": "高尔基体负责蛋白质的加工和运输。"},
    {"name": "核糖体", "color": BROWN, "x": 550, "y": 380, "radius": 15, "info": "核糖体是蛋白质合成的场所。"},
]

# DNA碱基对
dna_bases = [
    {"base1": "A", "base2": "T", "color1": RED, "color2": YELLOW},
    {"base1": "T", "base2": "A", "color1": YELLOW, "color2": RED},
    {"base1": "C", "base2": "G", "color1": BLUE, "color2": GREEN},
    {"base1": "G", "base2": "C", "color1": GREEN, "color2": BLUE},
]

# 遗传学问题
genetics_questions = [
    {
        "question": "人类有多少条染色体？",
        "options": ["23条", "46条", "44条", "48条"],
        "answer": 1,
        "explanation": "人类正常细胞含有46条染色体（23对），其中22对是常染色体，1对是性染色体。"
    },
    {
        "question": "DNA的全称是什么？",
        "options": ["脱氧核糖核酸", "核糖核酸", "腺嘌呤核苷酸", "三磷酸腺苷"],
        "answer": 0,
        "explanation": "DNA的全称是脱氧核糖核酸（Deoxyribonucleic Acid），是携带遗传信息的分子。"
    },
    {
        "question": "以下哪个不是DNA碱基？",
        "options": ["A（腺嘌呤）", "T（胸腺嘧啶）", "U（尿嘧啶）", "G（鸟嘌呤）"],
        "answer": 2,
        "explanation": "U（尿嘧啶）是RNA特有的碱基，DNA中的碱基是A、T、C、G。"
    },
    {
        "question": "在DNA复制中，A与哪个碱基配对？",
        "options": ["G", "C", "T", "U"],
        "answer": 2,
        "explanation": "在DNA中，腺嘌呤（A）与胸腺嘧啶（T）配对，胞嘧啶（C）与鸟嘌呤（G）配对。"
    },
    {
        "question": "什么是显性遗传？",
        "options": [
            "需要两个隐性基因才表现",
            "只要有一个显性基因就表现",
            "只在男性身上表现",
            "只在女性身上表现"
        ],
        "answer": 1,
        "explanation": "显性遗传是指只要有一个显性等位基因就能表现出相应的性状。"
    },
]

# 绘制按钮
def draw_button(text, x, y, width, height, color, hover_color, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    
    if x + width > mouse[0] > x and y + height > mouse[1] > y:
        pygame.draw.rect(screen, hover_color, (x, y, width, height), border_radius=10)
        if click[0] == 1 and action:
            pygame.time.delay(200)
            click_sound.play()
            action()
    else:
        pygame.draw.rect(screen, color, (x, y, width, height), border_radius=10)
    
    text_surface = font_medium.render(text, True, BLACK)
    text_rect = text_surface.get_rect(center=(x + width/2, y + height/2))
    screen.blit(text_surface, text_rect)

# 绘制标题页面
def draw_menu():
    screen.fill(BLACK)
    
    # 背景装饰 - DNA螺旋
    global dna_angle
    dna_angle += 0.02
    
    for i in range(20):
        z = i * 20
        angle = dna_angle + z * 0.1
        x1 = 100 + 50 * math.cos(angle)
        y1 = SCREEN_HEIGHT // 2 + 50 * math.sin(angle) + z - 200
        x2 = 100 + 50 * math.cos(angle + math.pi)
        y2 = SCREEN_HEIGHT // 2 + 50 * math.sin(angle + math.pi) + z - 200
        
        if 0 < y1 < SCREEN_HEIGHT and 0 < y2 < SCREEN_HEIGHT:
            pygame.draw.circle(screen, RED, (int(x1), int(y1)), 5)
            pygame.draw.circle(screen, BLUE, (int(x2), int(y2)), 5)
            pygame.draw.line(screen, WHITE, (x1, y1), (x2, y2), 2)
    
    # 主标题
    title_text = font_large.render("生命科学学习工具", True, WHITE)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 200))
    screen.blit(title_text, title_rect)
    
    subtitle_text = font_medium.render("探索细胞与DNA的奥秘", True, CYAN)
    subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH//2, 280))
    screen.blit(subtitle_text, subtitle_rect)
    
    # 按钮
    draw_button("细胞结构", SCREEN_WIDTH//2 - 150, 400, 300, 60, BLUE, CYAN, show_cell)
    draw_button("DNA双螺旋", SCREEN_WIDTH//2 - 150, 480, 300, 60, PURPLE, PINK, show_dna)
    draw_button("遗传学知识", SCREEN_WIDTH//2 - 150, 560, 300, 60, GREEN, CYAN, show_genetics)
    draw_button("退出游戏", SCREEN_WIDTH//2 - 150, 640, 300, 60, RED, ORANGE, quit_game)

# 细胞结构页面
def show_cell():
    global current_page, selected_part
    current_page = "cell"
    selected_part = None

def draw_cell():
    screen.fill(BLACK)
    
    # 返回按钮
    draw_button("返回", 50, 50, 100, 40, GRAY, LIGHT_GRAY, back_to_menu)
    
    title_text = font_large.render("细胞结构探索", True, WHITE)
    screen.blit(title_text, (SCREEN_WIDTH//2 - 200, 50))
    
    # 绘制细胞结构
    for part in cell_structure:
        pygame.draw.circle(screen, part["color"], (part["x"], part["y"]), part["radius"], 2)
    
    # 细胞膜
    pygame.draw.circle(screen, BLUE, (600, 400), 250, 3)
    # 细胞质（填充）
    pygame.draw.circle(screen, (0, 150, 150), (600, 400), 200)
    # 细胞核
    pygame.draw.circle(screen, PURPLE, (600, 400), 80)
    pygame.draw.circle(screen, (100, 0, 150), (600, 400), 80, 2)
    
    # 检查鼠标点击
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    
    for part in cell_structure:
        distance = math.sqrt((mouse[0] - part["x"])**2 + (mouse[1] - part["y"])**2)
        if distance <= part["radius"]:
            if click[0] == 1:
                global selected_part
                selected_part = part
                click_sound.play()
    
    # 显示选中部分的信息
    if selected_part:
        info_box = pygame.Surface((400, 200))
        info_box.fill((30, 30, 30))
        info_box.set_alpha(200)
        screen.blit(info_box, (SCREEN_WIDTH//2 - 200, 650))
        
        name_text = font_medium.render(selected_part["name"], True, selected_part["color"])
        screen.blit(name_text, (SCREEN_WIDTH//2 - 180, 670))
        
        text_lines = []
        info = selected_part["info"]
        current_line = ""
        for char in info:
            if font_small.size(current_line + char)[0] < 360:
                current_line += char
            else:
                text_lines.append(current_line)
                current_line = char
        text_lines.append(current_line)
        
        for i, line in enumerate(text_lines):
            line_surface = font_small.render(line, True, WHITE)
            screen.blit(line_surface, (SCREEN_WIDTH//2 - 180, 710 + i*25))
    
    # 提示文字
    hint_text = font_small.render("点击细胞各部分了解其功能", True, CYAN)
    screen.blit(hint_text, (SCREEN_WIDTH//2 - 150, 75))

# DNA双螺旋页面
def show_dna():
    global current_page
    current_page = "dna"

def draw_dna():
    screen.fill(BLACK)
    
    draw_button("返回", 50, 50, 100, 40, GRAY, LIGHT_GRAY, back_to_menu)
    
    title_text = font_large.render("DNA双螺旋结构", True, WHITE)
    screen.blit(title_text, (SCREEN_WIDTH//2 - 200, 50))
    
    global dna_angle
    dna_angle += 0.03
    
    # 绘制DNA双螺旋
    center_x = SCREEN_WIDTH // 2
    center_y = SCREEN_HEIGHT // 2
    
    for i in range(30):
        z = i * 15
        angle = dna_angle + z * 0.15
        
        # 两条螺旋链
        x1 = center_x + 150 * math.cos(angle)
        y1 = center_y + z - 225 + 50 * math.sin(angle * 2)
        x2 = center_x + 150 * math.cos(angle + math.pi)
        y2 = center_y + z - 225 + 50 * math.sin(angle * 2 + math.pi)
        
        # 绘制链
        pygame.draw.circle(screen, WHITE, (int(x1), int(y1)), 3)
        pygame.draw.circle(screen, WHITE, (int(x2), int(y2)), 3)
        
        if i > 0:
            prev_angle = dna_angle + (i-1) * 0.15
            prev_x1 = center_x + 150 * math.cos(prev_angle)
            prev_y1 = center_y + (i-1)*15 - 225 + 50 * math.sin(prev_angle * 2)
            prev_x2 = center_x + 150 * math.cos(prev_angle + math.pi)
            prev_y2 = center_y + (i-1)*15 - 225 + 50 * math.sin(prev_angle * 2 + math.pi)
            
            pygame.draw.line(screen, WHITE, (int(x1), int(y1)), (int(prev_x1), int(prev_y1)), 2)
            pygame.draw.line(screen, WHITE, (int(x2), int(y2)), (int(prev_x2), int(prev_y2)), 2)
        
        # 绘制碱基对
        base_pair = dna_bases[i % 4]
        pygame.draw.line(screen, base_pair["color1"], (int(x1), int(y1)), (int(x2), int(y2)), 3)
        
        # 显示碱基字母
        base1_text = font_small.render(base_pair["base1"], True, base_pair["color1"])
        base2_text = font_small.render(base_pair["base2"], True, base_pair["color2"])
        screen.blit(base1_text, (x1 + 5, y1 - 10))
        screen.blit(base2_text, (x2 + 5, y2 - 10))
    
    # 信息面板
    info_box = pygame.Surface((500, 150))
    info_box.fill((30, 30, 30))
    info_box.set_alpha(200)
    screen.blit(info_box, (SCREEN_WIDTH//2 - 250, 680))
    
    info_texts = [
        "DNA是双螺旋结构，由两条互补的核苷酸链组成",
        "碱基配对规则：A与T配对，C与G配对",
        "DNA携带遗传信息，决定生物体的性状"
    ]
    
    for i, text in enumerate(info_texts):
        line_surface = font_small.render(text, True, CYAN)
        screen.blit(line_surface, (SCREEN_WIDTH//2 - 230, 700 + i*30))

# 遗传学知识页面
def show_genetics():
    global current_page, genetics_score, genetics_question
    current_page = "genetics"
    genetics_score = 0
    genetics_question = 0

def draw_genetics():
    screen.fill(BLACK)
    
    draw_button("返回", 50, 50, 100, 40, GRAY, LIGHT_GRAY, back_to_menu)
    
    title_text = font_large.render("遗传学知识问答", True, WHITE)
    screen.blit(title_text, (SCREEN_WIDTH//2 - 200, 50))
    
    # 显示分数
    score_text = font_medium.render(f"得分: {genetics_score}/{len(genetics_questions)}", True, YELLOW)
    screen.blit(score_text, (SCREEN_WIDTH//2 - 80, 120))
    
    if genetics_question < len(genetics_questions):
        question = genetics_questions[genetics_question]
        
        # 问题
        question_text = font_medium.render(question["question"], True, WHITE)
        screen.blit(question_text, (SCREEN_WIDTH//2 - 300, 200))
        
        # 选项
        for i, option in enumerate(question["options"]):
            y_pos = 280 + i * 70
            color = BLUE if i == question["answer"] else GREEN
            
            # 检查点击
            mouse = pygame.mouse.get_pos()
            click = pygame.mouse.get_pressed()
            
            if SCREEN_WIDTH//2 - 300 < mouse[0] < SCREEN_WIDTH//2 + 300 and y_pos < mouse[1] < y_pos + 50:
                color = CYAN
                if click[0] == 1:
                    pygame.time.delay(200)
                    if i == question["answer"]:
                        genetics_score += 1
                        success_sound.play()
                    else:
                        error_sound.play()
                    
                    # 显示解释
                    explanation_box = pygame.Surface((600, 100))
                    explanation_box.fill((30, 30, 30))
                    explanation_box.set_alpha(200)
                    screen.blit(explanation_box, (SCREEN_WIDTH//2 - 300, 600))
                    
                    explanation_text = font_small.render(question["explanation"], True, CYAN)
                    screen.blit(explanation_text, (SCREEN_WIDTH//2 - 280, 620))
                    
                    pygame.display.flip()
                    pygame.time.delay(2000)
                    
                    genetics_question += 1
    
    else:
        # 显示结果
        result_text = font_large.render("测试完成！", True, WHITE)
        screen.blit(result_text, (SCREEN_WIDTH//2 - 150, 300))
        
        score_text = font_large.render(f"最终得分: {genetics_score}/{len(genetics_questions)}", True, YELLOW)
        screen.blit(score_text, (SCREEN_WIDTH//2 - 200, 400))
        
        if genetics_score == len(genetics_questions):
            grade_text = font_medium.render("完美！你是遗传学专家！", True, GREEN)
        elif genetics_score >= len(genetics_questions) * 0.7:
            grade_text = font_medium.render("优秀！继续努力！", True, CYAN)
        elif genetics_score >= len(genetics_questions) * 0.5:
            grade_text = font_medium.render("不错！还有进步空间！", True, ORANGE)
        else:
            grade_text = font_medium.render("需要多加学习哦！", True, RED)
        
        screen.blit(grade_text, (SCREEN_WIDTH//2 - 200, 500))
        
        draw_button("重新开始", SCREEN_WIDTH//2 - 150, 580, 300, 60, BLUE, CYAN, show_genetics)
    
    # 绘制选项按钮
    if genetics_question < len(genetics_questions):
        question = genetics_questions[genetics_question]
        for i, option in enumerate(question["options"]):
            y_pos = 280 + i * 70
            pygame.draw.rect(screen, BLUE, (SCREEN_WIDTH//2 - 300, y_pos, 600, 50), border_radius=10)
            option_text = font_medium.render(f"{i+1}. {option}", True, WHITE)
            screen.blit(option_text, (SCREEN_WIDTH//2 - 280, y_pos + 12))

def back_to_menu():
    global current_page
    current_page = "menu"

def quit_game():
    pygame.quit()
    sys.exit()

# 灰色系颜色（用于按钮）
GRAY = (100, 100, 100)
LIGHT_GRAY = (150, 150, 150)

# 主循环
def main():
    clock = pygame.time.Clock()
    
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        
        if current_page == "menu":
            draw_menu()
        elif current_page == "cell":
            draw_cell()
        elif current_page == "dna":
            draw_dna()
        elif current_page == "genetics":
            draw_genetics()
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()