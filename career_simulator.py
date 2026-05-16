import pygame
import random
import sys
import math

# 初始化 pygame
pygame.init()

# 尝试初始化音效，失败则跳过
try:
    pygame.mixer.init()
    sound_enabled = True
except pygame.error:
    sound_enabled = False

# 屏幕设置
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("职业模拟器 - Career Simulator")

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
BLUE = (50, 100, 200)
GREEN = (50, 150, 50)
RED = (150, 50, 50)
YELLOW = (200, 180, 50)
ORANGE = (200, 100, 50)
PURPLE = (120, 50, 150)

# 字体设置
font_small = pygame.font.Font(None, 24)
font_medium = pygame.font.Font(None, 32)
font_large = pygame.font.Font(None, 48)

# 游戏状态
game_state = "start"  # start, main, job, event, result
current_year = 1
current_age = 22
career_path = ""  # tech, management, startup

# 属性系统
attributes = {
    "能力": 20,
    "人脉": 10,
    "资金": 5000,
    "健康": 80
}

# 职业道路数据
career_paths = {
    "tech": {
        "name": "技术路线",
        "title": ["实习生", "初级工程师", "中级工程师", "高级工程师", "技术主管", "架构师", "CTO"],
        "salary": [3000, 6000, 10000, 15000, 22000, 35000, 50000],
        "required_ability": [0, 20, 40, 60, 80, 90, 100]
    },
    "management": {
        "name": "管理路线",
        "title": ["实习生", "专员", "主管", "经理", "高级经理", "总监", "CEO"],
        "salary": [3000, 5000, 8000, 12000, 18000, 30000, 50000],
        "required_ability": [0, 20, 40, 60, 75, 90, 100],
        "required_network": [0, 15, 30, 50, 70, 85, 100]
    },
    "startup": {
        "name": "创业路线",
        "title": ["创业者", "小老板", "企业家", "CEO"],
        "salary": [-5000, 2000, 10000, 50000],
        "required_ability": [0, 30, 60, 90],
        "required_funds": [50000, 100000, 500000, 1000000]
    }
}

current_title_index = 0
current_salary = 0

# 工作任务
work_tasks = {
    "tech": [
        {"name": "修复bug", "ability_gain": 2, "health_cost": 5, "success_rate": 0.8},
        {"name": "开发新功能", "ability_gain": 5, "health_cost": 10, "success_rate": 0.6},
        {"name": "技术分享", "ability_gain": 3, "network_gain": 2, "health_cost": 3, "success_rate": 0.9},
        {"name": "参与开源项目", "ability_gain": 4, "network_gain": 3, "health_cost": 8, "success_rate": 0.7}
    ],
    "management": [
        {"name": "团队会议", "network_gain": 3, "health_cost": 3, "success_rate": 0.9},
        {"name": "项目管理", "ability_gain": 2, "network_gain": 2, "health_cost": 8, "success_rate": 0.75},
        {"name": "商务谈判", "network_gain": 5, "ability_gain": 3, "health_cost": 10, "success_rate": 0.6},
        {"name": "员工培训", "ability_gain": 2, "network_gain": 4, "health_cost": 5, "success_rate": 0.85}
    ],
    "startup": [
        {"name": "寻找投资人", "network_gain": 5, "funds_gain": 10000, "health_cost": 10, "success_rate": 0.4},
        {"name": "产品开发", "ability_gain": 4, "health_cost": 12, "success_rate": 0.7},
        {"name": "市场营销", "network_gain": 3, "funds_gain": 5000, "health_cost": 8, "success_rate": 0.6},
        {"name": "团队组建", "network_gain": 4, "ability_gain": 2, "health_cost": 6, "success_rate": 0.8}
    ]
}

# 随机事件
random_events = [
    {"text": "你在咖啡馆遇到了一位行业大佬，相谈甚欢！", "network_gain": 10, "probability": 0.1},
    {"text": "你帮助了一位同事解决难题，获得了感谢。", "network_gain": 5, "probability": 0.15},
    {"text": "加班太多，身体有些吃不消了。", "health_cost": 15, "probability": 0.1},
    {"text": "投资的股票涨了！", "funds_gain": 5000, "probability": 0.08},
    {"text": "参加了一场行业峰会，收获颇丰。", "ability_gain": 5, "network_gain": 5, "probability": 0.12},
    {"text": "感冒了，需要休息几天。", "health_cost": 20, "probability": 0.08},
    {"text": "收到了猎头的电话，有更好的机会！", "salary_bonus": 2000, "probability": 0.05},
    {"text": "朋友介绍了一个大客户。", "network_gain": 8, "funds_gain": 8000, "probability": 0.07},
    {"text": "自学了一门新技能。", "ability_gain": 8, "probability": 0.1},
    {"text": "周末去爬山放松了一下。", "health_gain": 10, "probability": 0.15}
]

# 音效系统 - 使用 bytearray 生成音效
def generate_sound(frequency, duration, volume=0.1):
    if not sound_enabled:
        return None
    sample_rate = 44100
    samples = int(sample_rate * duration)
    arr = bytearray()
    for i in range(samples):
        t = i / sample_rate
        value = int((math.sin(2 * math.pi * frequency * t) + 1) * 127 * volume)
        arr.extend([value, value])  # 立体声
    return pygame.mixer.Sound(arr)

# 音效缓存
sounds = {}
if sound_enabled:
    sounds = {
        "click": generate_sound(800, 0.1),
        "success": generate_sound(523, 0.2) + generate_sound(659, 0.2),
        "fail": generate_sound(330, 0.3),
        "levelup": generate_sound(440, 0.15) + generate_sound(554, 0.15) + generate_sound(659, 0.2)
    }

# 绘制按钮
def play_sound(sound_name):
    if sound_enabled and sound_name in sounds:
        sounds[sound_name].play()

def draw_button(text, x, y, width, height, color, hover_color, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    
    if x + width > mouse[0] > x and y + height > mouse[1] > y:
        pygame.draw.rect(screen, hover_color, (x, y, width, height))
        if click[0] == 1 and action:
            play_sound("click")
            return action()
    else:
        pygame.draw.rect(screen, color, (x, y, width, height))
    
    text_surf = font_medium.render(text, True, WHITE)
    text_rect = text_surf.get_rect(center=(x + width/2, y + height/2))
    screen.blit(text_surf, text_rect)
    return False

# 绘制属性条
def draw_attribute_bar(name, value, max_value, x, y, color):
    bar_width = 200
    bar_height = 20
    percentage = value / max_value
    fill_width = bar_width * percentage
    
    pygame.draw.rect(screen, LIGHT_GRAY, (x, y, bar_width, bar_height))
    pygame.draw.rect(screen, color, (x, y, fill_width, bar_height))
    
    text = font_small.render(f"{name}: {value}", True, BLACK)
    screen.blit(text, (x, y - 25))

# 开始界面
def draw_start_screen():
    screen.fill(WHITE)
    
    title_text = font_large.render("职业模拟器", True, BLUE)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH/2, 100))
    screen.blit(title_text, title_rect)
    
    subtitle_text = font_medium.render("从实习生到CEO的职业发展之旅", True, GRAY)
    subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH/2, 160))
    screen.blit(subtitle_text, subtitle_rect)
    
    pygame.draw.rect(screen, LIGHT_GRAY, (SCREEN_WIDTH/2 - 300, 220, 600, 300))
    
    # 职业道路选择
    path_text = font_medium.render("选择你的职业道路:", True, BLACK)
    screen.blit(path_text, (SCREEN_WIDTH/2 - 120, 250))
    
    draw_button("技术路线", SCREEN_WIDTH/2 - 250, 310, 150, 50, BLUE, (70, 120, 220), lambda: select_career("tech"))
    draw_button("管理路线", SCREEN_WIDTH/2 - 50, 310, 150, 50, GREEN, (70, 170, 70), lambda: select_career("management"))
    draw_button("创业路线", SCREEN_WIDTH/2 + 150, 310, 150, 50, ORANGE, (220, 120, 70), lambda: select_career("startup"))
    
    tips_text = font_small.render("提示：技术路线注重能力提升，管理路线注重人脉，创业路线需要资金", True, GRAY)
    tips_rect = tips_text.get_rect(center=(SCREEN_WIDTH/2, 420))
    screen.blit(tips_text, tips_rect)

# 选择职业道路
def select_career(path):
    global career_path, game_state, current_title_index, current_salary
    career_path = path
    current_title_index = 0
    current_salary = career_paths[path]["salary"][0]
    game_state = "main"
    play_sound("success")

# 主游戏界面
def draw_main_screen():
    screen.fill(WHITE)
    
    # 顶部信息栏
    pygame.draw.rect(screen, BLUE, (0, 0, SCREEN_WIDTH, 80))
    year_text = font_medium.render(f"第 {current_year} 年 | 年龄: {current_age}岁", True, WHITE)
    screen.blit(year_text, (30, 20))
    
    path_name = career_paths[career_path]["name"]
    title = career_paths[career_path]["title"][current_title_index]
    title_text = font_medium.render(f"{path_name} - {title}", True, WHITE)
    screen.blit(title_text, (SCREEN_WIDTH/2 - 100, 20))
    
    salary_text = font_medium.render(f"月薪: ¥{current_salary}", True, WHITE)
    screen.blit(salary_text, (SCREEN_WIDTH - 150, 20))
    
    # 属性面板
    pygame.draw.rect(screen, LIGHT_GRAY, (30, 100, 250, 220))
    attr_title = font_medium.render("属性", True, BLACK)
    screen.blit(attr_title, (30, 100))
    
    draw_attribute_bar("能力", attributes["能力"], 100, 50, 140, BLUE)
    draw_attribute_bar("人脉", attributes["人脉"], 100, 50, 185, GREEN)
    draw_attribute_bar("资金", attributes["资金"], 1000000, 50, 230, YELLOW)
    draw_attribute_bar("健康", attributes["健康"], 100, 50, 275, RED)
    
    # 工作任务面板
    pygame.draw.rect(screen, LIGHT_GRAY, (300, 100, 470, 350))
    task_title = font_medium.render("今日工作任务", True, BLACK)
    screen.blit(task_title, (300, 100))
    
    tasks = work_tasks[career_path]
    for i, task in enumerate(tasks):
        y = 140 + i * 80
        pygame.draw.rect(screen, WHITE, (320, y, 430, 60))
        
        task_name = font_small.render(task["name"], True, BLACK)
        screen.blit(task_name, (335, y + 10))
        
        effects = []
        if "ability_gain" in task:
            effects.append(f"能力 +{task['ability_gain']}")
        if "network_gain" in task:
            effects.append(f"人脉 +{task['network_gain']}")
        if "funds_gain" in task:
            effects.append(f"资金 +{task['funds_gain']}")
        if "health_cost" in task:
            effects.append(f"健康 -{task['health_cost']}")
        
        effects_text = font_small.render(", ".join(effects), True, GRAY)
        screen.blit(effects_text, (335, y + 35))
        
        success_text = font_small.render(f"成功率: {int(task['success_rate'] * 100)}%", True, BLUE)
        screen.blit(success_text, (680, y + 35))
        
        # 执行任务按钮
        if draw_button("执行", 680, y + 5, 70, 25, GREEN, (70, 170, 70), lambda t=task: do_task(t)):
            return
    
    # 休息按钮
    if draw_button("休息一天", SCREEN_WIDTH/2 - 80, 480, 160, 50, YELLOW, (220, 200, 70), rest):
        return
    
    # 检查升级
    check_promotion()

# 执行任务
def do_task(task):
    global attributes
    
    # 检查健康
    if attributes["健康"] <= 0:
        show_event("你的健康值过低，需要休息！")
        return
    
    # 随机决定是否成功
    if random.random() < task["success_rate"]:
        # 成功
        if "ability_gain" in task:
            attributes["能力"] = min(100, attributes["能力"] + task["ability_gain"])
        if "network_gain" in task:
            attributes["人脉"] = min(100, attributes["人脉"] + task["network_gain"])
        if "funds_gain" in task:
            attributes["资金"] += task["funds_gain"]
        
        if "health_cost" in task:
            attributes["健康"] = max(0, attributes["健康"] - task["health_cost"])
        
        play_sound("success")
        show_event(f"任务完成！{task['name']} 成功！")
    else:
        # 失败
        if "health_cost" in task:
            attributes["健康"] = max(0, attributes["健康"] - int(task["health_cost"] * 0.5))
        
        play_sound("fail")
        show_event(f"任务失败了...{task['name']} 没有成功")
    
    # 随机事件
    check_random_event()
    
    # 增加资金（工资）
    attributes["资金"] += current_salary // 30  # 日薪

# 休息
def rest():
    global attributes
    attributes["健康"] = min(100, attributes["健康"] + 15)
    play_sound("success")
    show_event("你休息了一天，精神焕发！")
    check_random_event()

# 检查随机事件
def check_random_event():
    for event in random_events:
        if random.random() < event["probability"]:
            if "network_gain" in event:
                attributes["人脉"] = min(100, attributes["人脉"] + event["network_gain"])
            if "health_cost" in event:
                attributes["健康"] = max(0, attributes["健康"] - event["health_cost"])
            if "funds_gain" in event:
                attributes["资金"] += event["funds_gain"]
            if "ability_gain" in event:
                attributes["能力"] = min(100, attributes["能力"] + event["ability_gain"])
            if "salary_bonus" in event:
                global current_salary
                current_salary += event["salary_bonus"]
            
            show_event(event["text"])
            break

# 检查升级
def check_promotion():
    global current_title_index, current_salary
    
    path = career_paths[career_path]
    if current_title_index < len(path["title"]) - 1:
        next_index = current_title_index + 1
        requirements = []
        
        if path["required_ability"][next_index] <= attributes["能力"]:
            requirements.append("能力")
        
        if "required_network" in path and path["required_network"][next_index] <= attributes["人脉"]:
            requirements.append("人脉")
        
        if "required_funds" in path and path["required_funds"][next_index] <= attributes["资金"]:
            requirements.append("资金")
        
        # 检查是否满足晋升条件
        needs_ability = path["required_ability"][next_index]
        needs_network = path["required_network"][next_index] if "required_network" in path else 0
        needs_funds = path["required_funds"][next_index] if "required_funds" in path else 0
        
        if (attributes["能力"] >= needs_ability and 
            (not "required_network" in path or attributes["人脉"] >= needs_network) and
            (not "required_funds" in path or attributes["资金"] >= needs_funds)):
            
            current_title_index = next_index
            current_salary = path["salary"][next_index]
            play_sound("levelup")
            show_event(f"恭喜！你晋升为 {path['title'][current_title_index]}！")
            
            # 检查是否达到最终目标
            if current_title_index == len(path["title"]) - 1:
                game_state = "result"

# 事件弹窗
event_text = ""
show_event_flag = False

def show_event(text):
    global event_text, show_event_flag
    event_text = text
    show_event_flag = True

def draw_event_popup():
    global show_event_flag
    
    if show_event_flag:
        pygame.draw.rect(screen, BLACK, (SCREEN_WIDTH/2 - 200, SCREEN_HEIGHT/2 - 80, 400, 160))
        pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH/2 - 195, SCREEN_HEIGHT/2 - 75, 390, 150))
        
        event_surf = font_small.render(event_text, True, BLACK)
        event_rect = event_surf.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 20))
        screen.blit(event_surf, event_rect)
        
        if draw_button("确定", SCREEN_WIDTH/2 - 60, SCREEN_HEIGHT/2 + 30, 120, 40, BLUE, (70, 120, 220), lambda: close_event()):
            return

def close_event():
    global show_event_flag, current_year, current_age
    show_event_flag = False
    
    # 增加年份和年龄
    current_year += 1
    current_age += 1
    
    # 每年健康自然下降
    attributes["健康"] = max(0, attributes["健康"] - 2)
    
    # 检查游戏结束条件
    if attributes["健康"] <= 0:
        global game_state
        game_state = "result"

# 结果界面
def draw_result_screen():
    screen.fill(WHITE)
    
    path = career_paths[career_path]
    final_title = path["title"][current_title_index]
    
    if current_title_index == len(path["title"]) - 1:
        # 成功结局
        title_text = font_large.render("🎉 恭喜！", True, GREEN)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH/2, 150))
        screen.blit(title_text, title_rect)
        
        result_text = font_medium.render(f"你成功成为了 {final_title}！", True, BLACK)
        result_rect = result_text.get_rect(center=(SCREEN_WIDTH/2, 220))
        screen.blit(result_text, result_rect)
        
        stats_text = font_small.render(f"用时: {current_year} 年 | 最终资金: ¥{attributes['资金']}", True, GRAY)
        stats_rect = stats_text.get_rect(center=(SCREEN_WIDTH/2, 280))
        screen.blit(stats_text, stats_rect)
    else:
        # 失败结局
        title_text = font_large.render("💔 游戏结束", True, RED)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH/2, 150))
        screen.blit(title_text, title_rect)
        
        result_text = font_medium.render("你的健康透支了，需要好好休息...", True, BLACK)
        result_rect = result_text.get_rect(center=(SCREEN_WIDTH/2, 220))
        screen.blit(result_text, result_rect)
        
        stats_text = font_small.render(f"最终职位: {final_title} | 用时: {current_year} 年", True, GRAY)
        stats_rect = stats_text.get_rect(center=(SCREEN_WIDTH/2, 280))
        screen.blit(stats_text, stats_rect)
    
    # 重新开始按钮
    draw_button("重新开始", SCREEN_WIDTH/2 - 100, 350, 200, 50, BLUE, (70, 120, 220), restart_game)

# 重新开始游戏
def restart_game():
    global game_state, current_year, current_age, career_path
    global current_title_index, current_salary, attributes
    
    game_state = "start"
    current_year = 1
    current_age = 22
    career_path = ""
    current_title_index = 0
    current_salary = 0
    attributes = {
        "能力": 20,
        "人脉": 10,
        "资金": 5000,
        "健康": 80
    }
    play_sound("click")

# 主游戏循环
running = True
clock = pygame.time.Clock()

while running:
    screen.fill(WHITE)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    if game_state == "start":
        draw_start_screen()
    elif game_state == "main":
        draw_main_screen()
        if show_event_flag:
            draw_event_popup()
    elif game_state == "result":
        draw_result_screen()
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()