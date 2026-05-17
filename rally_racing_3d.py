import pygame
import os
import sys
import math
import random
import struct
import time

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

# 屏幕设置
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("拉力赛车3D")

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
GREEN = (0, 128, 0)
DARK_GREEN = (0, 80, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
BROWN = (139, 69, 19)

# 游戏状态
MENU = 0
PLAYING = 1
PAUSED = 2
GAME_OVER = 3
current_state = MENU

# 赛车参数
car_x = SCREEN_WIDTH // 2
car_y = SCREEN_HEIGHT - 100
car_angle = 0
car_speed = 0
max_speed = 15
acceleration = 0.15
deceleration = 0.08
friction = 0.02
turn_speed = 3

# 赛道参数
road_width = 400
segment_length = 10
track_length = 200
track = []
current_segment = 0

# 障碍物
obstacles = []
obstacle_types = ['rock', 'cone', 'barrier']

# 计时系统
start_time = 0
best_times = {}

# 场景
scenes = ['森林', '沙漠', '雪山']
current_scene = 0

# 车道标记
lane_marks = []

# 音效系统
audio_enabled = True
try:
    pygame.mixer.init(frequency=44100, size=-16, channels=2)
except pygame.error:
    audio_enabled = False
    print("音频设备不可用，跳过音效初始化")

def generate_sound(frequency, duration, volume=0.1):
    """生成音效"""
    if not audio_enabled:
        return None
    
    sample_rate = 44100
    samples = int(sample_rate * duration)
    sound_data = bytearray()
    
    for i in range(samples):
        t = i / sample_rate
        value = int(math.sin(2 * math.pi * frequency * t) * 32767 * volume)
        sound_data.extend(struct.pack('<h', value))
    
    sound = pygame.mixer.Sound(sound_data)
    return sound

def play_sound(sound, loops=0):
    """安全播放声音"""
    if audio_enabled and sound:
        sound.play(loops)

def stop_sound(sound):
    """安全停止声音"""
    if audio_enabled and sound:
        sound.stop()

# 生成音效
engine_sound = generate_sound(200, 0.1)
crash_sound = generate_sound(100, 0.3, 0.2)
brake_sound = generate_sound(150, 0.15, 0.15)

def generate_track(scene_index):
    """生成赛道"""
    global track, obstacles, lane_marks
    track = []
    obstacles = []
    lane_marks = []
    
    for i in range(track_length):
        # 根据场景设置不同的颜色和地形
        if scene_index == 0:  # 森林
            road_color = GRAY
            off_road_color = DARK_GREEN
            sky_color = (135, 206, 235)
        elif scene_index == 1:  # 沙漠
            road_color = (210, 180, 140)
            off_road_color = (244, 164, 96)
            sky_color = (255, 215, 0)
        else:  # 雪山
            road_color = (220, 220, 220)
            off_road_color = WHITE
            sky_color = (173, 216, 230)
        
        # 生成弯道
        curve = 0
        if i > 50 and i < 80:
            curve = 2  # 右转弯
        elif i > 100 and i < 130:
            curve = -2  # 左转弯
        elif i > 150 and i < 180:
            curve = 3  # 急右转弯
        
        # 生成障碍物
        if random.random() < 0.03 and i > 30:
            obstacle_type = random.choice(obstacle_types)
            obstacles.append({
                'type': obstacle_type,
                'segment': i,
                'offset': random.randint(-150, 150),
                'hit': False
            })
        
        track.append({
            'curve': curve,
            'road_color': road_color,
            'off_road_color': off_road_color,
            'sky_color': sky_color
        })
        
        # 车道标记
        if i % 5 == 0:
            lane_marks.append(i)

def draw_pseudo_3d():
    """绘制伪3D场景"""
    global current_segment, car_angle
    
    horizon_y = SCREEN_HEIGHT // 3
    scale = 0
    offset = 0
    
    # 绘制天空
    sky_color = track[current_segment]['sky_color'] if track else (135, 206, 235)
    screen.fill(sky_color)
    
    # 绘制远处的背景元素
    for i in range(current_segment, min(current_segment + 100, track_length)):
        segment_offset = 0
        for j in range(current_segment, i):
            segment_offset += track[j]['curve'] * 0.1
        
        perspective = 1.0 - (i - current_segment) / 100.0
        if perspective <= 0:
            continue
        
        y = horizon_y + (i - current_segment) * 4 * perspective
        if y >= SCREEN_HEIGHT:
            continue
        
        road_width_scaled = road_width * perspective
        off_road_width = (SCREEN_WIDTH - road_width_scaled) / 2
        
        # 绘制草地/路边
        pygame.draw.rect(screen, track[i]['off_road_color'], 
                        (0, y, off_road_width + segment_offset, segment_length))
        pygame.draw.rect(screen, track[i]['off_road_color'], 
                        (SCREEN_WIDTH - off_road_width + segment_offset, y, off_road_width, segment_length))
        
        # 绘制道路
        pygame.draw.rect(screen, track[i]['road_color'], 
                        (off_road_width + segment_offset, y, road_width_scaled, segment_length))
        
        # 绘制车道标记
        if i in lane_marks and perspective > 0.3:
            mark_width = 10 * perspective
            mark_height = 20 * perspective
            mark_x = SCREEN_WIDTH // 2 + segment_offset - mark_width // 2
            pygame.draw.rect(screen, WHITE, (mark_x, y, mark_width, mark_height))
        
        # 绘制障碍物
        for obs in obstacles:
            if obs['segment'] == i and not obs['hit']:
                obs_x = SCREEN_WIDTH // 2 + segment_offset + obs['offset']
                obs_y = y
                obs_size = 30 * perspective
                
                if obs['type'] == 'rock':
                    pygame.draw.circle(screen, BROWN, (int(obs_x), int(obs_y)), int(obs_size))
                elif obs['type'] == 'cone':
                    pygame.draw.polygon(screen, ORANGE, [
                        (int(obs_x), int(obs_y - obs_size)),
                        (int(obs_x - obs_size/2), int(obs_y + obs_size/2)),
                        (int(obs_x + obs_size/2), int(obs_y + obs_size/2))
                    ])
                else:
                    pygame.draw.rect(screen, RED, (int(obs_x - obs_size), int(obs_y - obs_size/2), 
                                                 int(obs_size * 2), int(obs_size)))
    
    # 绘制赛车
    draw_car()

def draw_car():
    """绘制赛车"""
    global car_x, car_y, car_angle, car_speed
    
    # 赛车主体
    car_color = RED
    body_length = 60
    body_width = 30
    
    # 根据速度改变颜色深浅
    speed_factor = car_speed / max_speed
    car_color = (int(255 * (1 - speed_factor * 0.3)), 
                 int(0 + speed_factor * 50), 
                 int(0 + speed_factor * 50))
    
    # 绘制车身
    pygame.draw.rect(screen, car_color, (car_x - body_width//2, car_y - body_length, body_width, body_length))
    
    # 绘制车窗
    pygame.draw.rect(screen, BLUE, (car_x - body_width//3, car_y - body_length + 5, body_width//1.5, body_length//3))
    
    # 绘制车轮
    pygame.draw.circle(screen, BLACK, (car_x - body_width//2 - 5, car_y - 10), 8)
    pygame.draw.circle(screen, BLACK, (car_x + body_width//2 + 5, car_y - 10), 8)
    pygame.draw.circle(screen, BLACK, (car_x - body_width//2 - 5, car_y - body_length + 10), 8)
    pygame.draw.circle(screen, BLACK, (car_x + body_width//2 + 5, car_y - body_length + 10), 8)
    
    # 绘制车头灯光（加速时）
    if car_speed > 5:
        pygame.draw.circle(screen, YELLOW, (car_x - body_width//2 + 5, car_y - body_length), 5)
        pygame.draw.circle(screen, YELLOW, (car_x + body_width//2 - 5, car_y - body_length), 5)
    
    # 绘制尾气（刹车时）
    if keys[pygame.K_DOWN] and car_speed > 0:
        for i in range(3):
            pygame.draw.circle(screen, GRAY, 
                             (car_x + random.randint(-10, 10), car_y + 10 + i*10), 
                             random.randint(3, 6))

def check_collision():
    """检测碰撞"""
    global car_speed, obstacles
    
    # 检查是否偏离赛道
    road_edge = road_width // 2 - 30
    if abs(car_x - SCREEN_WIDTH // 2) > road_edge:
        car_speed = max(0, car_speed - 0.5)
        return
    
    # 检查障碍物碰撞
    for obs in obstacles:
        if obs['segment'] == current_segment + 1 and not obs['hit']:
            obs_x = SCREEN_WIDTH // 2 + obs['offset']
            distance = abs(car_x - obs_x)
            
            if distance < 30:
                obs['hit'] = True
                car_speed = max(0, car_speed - 5)
                play_sound(crash_sound)
                return

def update_game():
    """更新游戏状态"""
    global car_x, car_y, car_angle, car_speed, current_segment, start_time
    
    # 处理输入
    global keys
    keys = pygame.key.get_pressed()
    
    # 加速
    if keys[pygame.K_UP]:
        car_speed = min(max_speed, car_speed + acceleration)
        if car_speed > 0:
            play_sound(engine_sound, -1)
        else:
            stop_sound(engine_sound)
    else:
        stop_sound(engine_sound)
    
    # 刹车
    if keys[pygame.K_DOWN]:
        car_speed = max(0, car_speed - deceleration * 2)
        if car_speed > 0:
            play_sound(brake_sound)
    
    # 自然减速
    if not keys[pygame.K_UP] and not keys[pygame.K_DOWN]:
        car_speed = max(0, car_speed - friction)
    
    # 转向
    if keys[pygame.K_LEFT] and car_speed > 0:
        car_angle += turn_speed / car_speed * 5
        car_x -= car_speed * 0.8
    
    if keys[pygame.K_RIGHT] and car_speed > 0:
        car_angle -= turn_speed / car_speed * 5
        car_x += car_speed * 0.8
    
    # 更新赛道位置
    if car_speed > 0:
        current_segment += int(car_speed / 10)
    
    # 检查是否完成赛道
    if current_segment >= track_length:
        finish_game()
    
    # 限制赛车位置
    car_x = max(50, min(SCREEN_WIDTH - 50, car_x))
    
    # 检测碰撞
    check_collision()

def finish_game():
    """完成游戏"""
    global current_state, start_time, best_times
    
    elapsed_time = time.time() - start_time
    current_state = GAME_OVER
    
    scene_name = scenes[current_scene]
    if scene_name not in best_times or elapsed_time < best_times[scene_name]:
        best_times[scene_name] = elapsed_time

def draw_menu():
    """绘制主菜单"""
    screen.fill(GREEN)
    
    # 标题
    font = get_chinese_font(72)
    title_text = font.render("拉力赛车3D", True, WHITE)
    screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, 100))
    
    # 场景选择
    font = get_chinese_font(36)
    scene_text = font.render(f"场景: {scenes[current_scene]}", True, WHITE)
    screen.blit(scene_text, (SCREEN_WIDTH//2 - scene_text.get_width()//2, 250))
    
    # 最佳成绩
    font = get_chinese_font(28)
    for i, scene in enumerate(scenes):
        if scene in best_times:
            best_time = best_times[scene]
            time_text = font.render(f"{scene}: {best_time:.2f}秒", True, YELLOW)
            screen.blit(time_text, (SCREEN_WIDTH//2 - time_text.get_width()//2, 300 + i*30))
    
    # 操作说明
    font = get_chinese_font(24)
    instructions = [
        "操作说明:",
        "↑ 加速",
        "↓ 刹车",
        "← → 转向",
        "空格键 暂停",
        "",
        "Enter 开始游戏",
        "左右箭头 切换场景"
    ]
    
    for i, text in enumerate(instructions):
        instr_text = font.render(text, True, WHITE)
        screen.blit(instr_text, (SCREEN_WIDTH//2 - instr_text.get_width()//2, 400 + i*25))

def draw_paused():
    """绘制暂停界面"""
    draw_pseudo_3d()
    
    # 半透明遮罩
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(128)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))
    
    font = get_chinese_font(64)
    paused_text = font.render("游戏暂停", True, WHITE)
    screen.blit(paused_text, (SCREEN_WIDTH//2 - paused_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
    
    font = get_chinese_font(32)
    resume_text = font.render("按空格键继续", True, YELLOW)
    screen.blit(resume_text, (SCREEN_WIDTH//2 - resume_text.get_width()//2, SCREEN_HEIGHT//2 + 20))

def draw_game_over():
    """绘制游戏结束界面"""
    screen.fill(BLACK)
    
    font = get_chinese_font(64)
    game_over_text = font.render("比赛完成!", True, GREEN)
    screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, 100))
    
    elapsed_time = time.time() - start_time
    font = get_chinese_font(48)
    time_text = font.render(f"用时: {elapsed_time:.2f}秒", True, WHITE)
    screen.blit(time_text, (SCREEN_WIDTH//2 - time_text.get_width()//2, 200))
    
    scene_name = scenes[current_scene]
    if scene_name in best_times:
        best_time = best_times[scene_name]
        font = get_chinese_font(36)
        best_text = font.render(f"最佳成绩: {best_time:.2f}秒", True, YELLOW)
        screen.blit(best_text, (SCREEN_WIDTH//2 - best_text.get_width()//2, 280))
    
    font = get_chinese_font(32)
    restart_text = font.render("按 Enter 重新开始", True, WHITE)
    screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, 380))
    
    menu_text = font.render("按 M 返回主菜单", True, WHITE)
    screen.blit(menu_text, (SCREEN_WIDTH//2 - menu_text.get_width()//2, 430))

def draw_hud():
    """绘制HUD"""
    font = get_chinese_font(24)
    
    # 速度表
    speed_text = font.render(f"速度: {int(car_speed * 10)} km/h", True, WHITE)
    screen.blit(speed_text, (20, 20))
    
    # 计时
    elapsed_time = time.time() - start_time
    time_text = font.render(f"时间: {elapsed_time:.2f}秒", True, WHITE)
    screen.blit(time_text, (20, 50))
    
    # 进度
    progress = (current_segment / track_length) * 100
    progress_text = font.render(f"进度: {int(progress)}%", True, WHITE)
    screen.blit(progress_text, (20, 80))
    
    # 场景名称
    scene_text = font.render(f"场景: {scenes[current_scene]}", True, WHITE)
    screen.blit(scene_text, (SCREEN_WIDTH - 150, 20))

def start_game():
    """开始游戏"""
    global current_state, car_x, car_y, car_angle, car_speed, current_segment, start_time, obstacles
    
    current_state = PLAYING
    car_x = SCREEN_WIDTH // 2
    car_y = SCREEN_HEIGHT - 100
    car_angle = 0
    car_speed = 0
    current_segment = 0
    start_time = time.time()
    
    # 重置障碍物状态
    for obs in obstacles:
        obs['hit'] = False
    
    generate_track(current_scene)

# 主循环
clock = pygame.time.Clock()
generate_track(current_scene)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if current_state == MENU:
                if event.key == pygame.K_RETURN:
                    start_game()
                elif event.key == pygame.K_LEFT:
                    current_scene = (current_scene - 1) % len(scenes)
                    generate_track(current_scene)
                elif event.key == pygame.K_RIGHT:
                    current_scene = (current_scene + 1) % len(scenes)
                    generate_track(current_scene)
            
            elif current_state == PLAYING:
                if event.key == pygame.K_SPACE:
                    current_state = PAUSED
            
            elif current_state == PAUSED:
                if event.key == pygame.K_SPACE:
                    current_state = PLAYING
            
            elif current_state == GAME_OVER:
                if event.key == pygame.K_RETURN:
                    start_game()
                elif event.key == pygame.K_m:
                    current_state = MENU
    
    if current_state == MENU:
        draw_menu()
    
    elif current_state == PLAYING:
        update_game()
        draw_pseudo_3d()
        draw_hud()
    
    elif current_state == PAUSED:
        draw_paused()
    
    elif current_state == GAME_OVER:
        draw_game_over()
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()