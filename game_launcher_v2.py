import pygame
import sys
import os
import subprocess

pygame.init()

WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🎮 Python 小游戏合集 - 游戏启动器 v1.0")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
GREEN = (0, 200, 100)
BLUE = (0, 100, 200)
RED = (200, 50, 50)
YELLOW = (255, 200, 0)
PURPLE = (150, 50, 200)
ORANGE = (255, 150, 0)
CYAN = (0, 200, 200)
BROWN = (139, 69, 19)

font_large = pygame.font.Font(None, 48)
font_medium = pygame.font.Font(None, 32)
font_small = pygame.font.Font(None, 24)
font_tiny = pygame.font.Font(None, 20)

categories = [
    {"name": "🏠 全部游戏", "color": PURPLE},
    {"name": "📝 经典文字", "color": GRAY},
    {"name": "🕹️ 街机复刻", "color": BLUE},
    {"name": "🏰 策略塔防", "color": GREEN},
    {"name": "⚔️ RPG冒险", "color": ORANGE},
    {"name": "🏪 模拟经营", "color": YELLOW},
    {"name": "🧩 益智解谜", "color": RED},
    {"name": "🎵 音乐创意", "color": PURPLE},
    {"name": "🎯 休闲街机", "color": CYAN},
    {"name": "📚 文字学习", "color": GRAY},
    {"name": "♠️ 卡牌桌游", "color": GREEN},
    {"name": "🎉 多人派对", "color": RED},
    {"name": "🔫 生存射击", "color": ORANGE},
    {"name": "🤖 放置自动", "color": YELLOW},
    {"name": "🚗 赛车驾驶", "color": PURPLE},
    {"name": "🎬 视觉叙事", "color": BLUE},
    {"name": "🔬 科学教育", "color": GREEN},
]

games_data = {
    "📝 经典文字": [
        {"name": "猜数字", "file": "guess_number.py", "desc": "猜1-100的随机数"},
        {"name": "井字棋", "file": "tic_tac_toe.py", "desc": "经典双人对战"},
        {"name": "绞刑架", "file": "hangman.py", "desc": "猜单词游戏"},
        {"name": "石头剪刀布", "file": "rock_paper_scissors.py", "desc": "人机对战"},
        {"name": "文字德州扑克", "file": "text_poker.py", "desc": "德州扑克"},
        {"name": "文字21点", "file": "text_blackjack.py", "desc": "21点纸牌"},
        {"name": "聊天机器人", "file": "chat_bot.py", "desc": "AI聊天"},
    ],
    "🕹️ 街机复刻": [
        {"name": "贪吃蛇", "file": "snake_game.py", "desc": "经典街机"},
        {"name": "贪吃蛇3D", "file": "snake_3d.py", "desc": "伪3D透视"},
        {"name": "贪吃蛇双人", "file": "snake_2p.py", "desc": "双人对战"},
        {"name": "贪吃蛇变种", "file": "snake_variants.py", "desc": "多种模式"},
        {"name": "2048", "file": "game_2048.py", "desc": "数字合并"},
        {"name": "俄罗斯方块", "file": "tetris.py", "desc": "经典方块"},
        {"name": "打砖块", "file": "breakout.py", "desc": "弹球打砖"},
        {"name": "扫雷", "file": "minesweeper.py", "desc": "经典扫雷"},
        {"name": "扫雷高级版", "file": "minesweeper_advanced.py", "desc": "高级扫雷"},
        {"name": "吃豆人", "file": "pac_man.py", "desc": "经典迷宫"},
        {"name": "大金刚", "file": "donkey_kong.py", "desc": "平台跳跃"},
        {"name": "太空侵略者", "file": "space_invaders_classic.py", "desc": "经典射击"},
        {"name": "炸弹人专业版", "file": "bomberman_pro.py", "desc": "炸弹爆炸"},
        {"name": "Pong乒乓球", "file": "pong.py", "desc": "经典双人"},
        {"name": "打地鼠", "file": "whack_a_mole.py", "desc": "反应速度"},
        {"name": "打靶游戏", "file": "shooting_range.py", "desc": "射击打靶"},
        {"name": "桌球", "file": "billiards.py", "desc": "简化台球"},
        {"name": "推箱子", "file": "sokoban_variants.py", "desc": "推箱子变种"},
        {"name": "魂斗罗射击", "file": "contra_shooter.py", "desc": "经典射击"},
    ],
    "🏰 策略塔防": [
        {"name": "塔防", "file": "tower_defense.py", "desc": "经典塔防"},
        {"name": "塔防豪华版", "file": "tower_defense_deluxe.py", "desc": "6种塔类型"},
        {"name": "即时战略简化版", "file": "mini_rts.py", "desc": "采集建造"},
        {"name": "即时战略对战", "file": "rts_battle.py", "desc": "实时战斗"},
        {"name": "回合制战术", "file": "tactical_warfare.py", "desc": "战棋游戏"},
        {"name": "国际象棋", "file": "chess_simple.py", "desc": "简化象棋"},
        {"name": "大富翁", "file": "monopoly_style.py", "desc": "买地收租"},
        {"name": "五子棋", "file": "gomoku.py", "desc": "双人对战"},
        {"name": "在线五子棋", "file": "online_gomoku.py", "desc": "AI对战"},
        {"name": "坦克大战", "file": "tank_battle.py", "desc": "坦克射击"},
        {"name": "卡牌构建", "file": "card_builder_dbg.py", "desc": "DBG卡牌"},
    ],
    "⚔️ RPG冒险": [
        {"name": "简单RPG", "file": "simple_rpg.py", "desc": "基础RPG"},
        {"name": "回合制RPG", "file": "turn_based_rpg.py", "desc": "完整剧情"},
        {"name": "俯视角ARPG", "file": "top_down_arpg.py", "desc": "刷怪升级"},
        {"name": "文字RPG", "file": "text_rpg.py", "desc": "文字冒险"},
        {"name": "像素冒险RPG", "file": "pixel_quest_rpg.py", "desc": "像素冒险"},
        {"name": "类银河恶魔城", "file": "metroidvania_simple.py", "desc": "探索解锁"},
        {"name": "平台跳跃", "file": "platformer.py", "desc": "超级玛丽"},
        {"name": "横版射击", "file": "horizontal_shooter.py", "desc": "弹幕射击"},
        {"name": "Roguelike地牢", "file": "roguelike_dungeon.py", "desc": "随机地牢"},
        {"name": "Roguelike战术", "file": "roguelike_tactical.py", "desc": "回合制"},
        {"name": "卡牌Roguelike", "file": "card_roguelike.py", "desc": "杀戮尖塔"},
        {"name": "动作Roguelike", "file": "action_roguelike.py", "desc": "动作风格"},
    ],
    "🏪 模拟经营": [
        {"name": "餐厅模拟器", "file": "restaurant_sim.py", "desc": "经营餐厅"},
        {"name": "城市建造", "file": "city_builder.py", "desc": "建城市"},
        {"name": "商店经营", "file": "shop_keeper.py", "desc": "开商店"},
        {"name": "农场模拟器", "file": "farm_simulator.py", "desc": "种庄稼"},
        {"name": "沙盒建造者", "file": "sandbox_builder.py", "desc": "自由建造"},
        {"name": "医院模拟器", "file": "hospital_sim.py", "desc": "医院经营"},
        {"name": "学校模拟器", "file": "school_sim.py", "desc": "学校管理"},
        {"name": "动物园模拟器", "file": "zoo_sim.py", "desc": "动物园管理"},
    ],
    "🧩 益智解谜": [
        {"name": "记忆配对", "file": "memory_game.py", "desc": "翻牌配对"},
        {"name": "数字拼图", "file": "puzzle.py", "desc": "数字滑块"},
        {"name": "拼图块", "file": "puzzle_blocks.py", "desc": "块拼图"},
        {"name": "华容道", "file": "huarong_dao.py", "desc": "经典滑块"},
        {"name": "一笔画", "file": "one_stroke.py", "desc": "一笔画完"},
        {"name": "数独", "file": "sudoku.py", "desc": "数字数独"},
        {"name": "连连看", "file": "lianliankan.py", "desc": "连连看"},
        {"name": "连连看麻将版", "file": "mahjong_link.py", "desc": "麻将配对"},
        {"name": "消消乐", "file": "match_three.py", "desc": "三消"},
        {"name": "找不同", "file": "spot_difference.py", "desc": "找不同"},
        {"name": "管道连接", "file": "pipe_builder.py", "desc": "接管道"},
        {"name": "逻辑解谜", "file": "logic_puzzle.py", "desc": "电路连接"},
        {"name": "重力反转", "file": "gravity_puzzle.py", "desc": "重力切换"},
        {"name": "时间控制", "file": "time_manipulation.py", "desc": "时间控制"},
        {"name": "时间循环", "file": "time_loop_puzzle.py", "desc": "时间循环"},
        {"name": "24点", "file": "twenty_four.py", "desc": "算24点"},
        {"name": "数织", "file": "nonogram.py", "desc": "逻辑填空"},
        {"name": "成语接龙", "file": "idiom_game.py", "desc": "成语接龙"},
        {"name": "七巧板", "file": "tangram.py", "desc": "拼图游戏"},
    ],
    "🎵 音乐创意": [
        {"name": "音乐节奏大师", "file": "rhythm_master.py", "desc": "节奏游戏"},
        {"name": "音乐生成器", "file": "music_generator.py", "desc": "创作音乐"},
        {"name": "像素艺术", "file": "pixel_art.py", "desc": "像素绘画"},
        {"name": "像素动画师", "file": "pixel_animator.py", "desc": "做动画"},
        {"name": "画画猜词", "file": "draw_something.py", "desc": "猜词游戏"},
        {"name": "物理沙盒", "file": "physics_sandbox.py", "desc": "物理实验"},
        {"name": "物理弹珠球", "file": "physics_balls.py", "desc": "弹球物理"},
    ],
    "🎯 休闲街机": [
        {"name": "水果忍者", "file": "fruit_ninja.py", "desc": "切水果"},
        {"name": "接水果", "file": "catch_fruit.py", "desc": "接水果"},
        {"name": "接金币", "file": "collect_coins.py", "desc": "接金币"},
        {"name": "跳一跳", "file": "jump_game.py", "desc": "跳跃游戏"},
        {"name": "叠杯子", "file": "stacking.py", "desc": "叠杯子"},
        {"name": "跑酷", "file": "parkour_runner.py", "desc": "自动跑酷"},
        {"name": "泡泡射击", "file": "bubble_shooter.py", "desc": "泡泡龙"},
        {"name": "躲避球", "file": "dodge_game.py", "desc": "躲避障碍"},
        {"name": "简单弹球", "file": "pinball.py", "desc": "弹球机"},
        {"name": "弹球物理版", "file": "pinball_physics.py", "desc": "物理弹球"},
        {"name": "彩虹岛冒险", "file": "rainbow_island.py", "desc": "彩虹跑酷"},
    ],
    "📚 文字学习": [
        {"name": "打字练习", "file": "typing_practice.py", "desc": "练打字"},
        {"name": "打字大师", "file": "typing_master.py", "desc": "打字游戏"},
        {"name": "数学游戏", "file": "math_game.py", "desc": "学数学"},
        {"name": "快速心算", "file": "quick_math.py", "desc": "心算挑战"},
        {"name": "Simon说", "file": "simon_says.py", "desc": "记忆游戏"},
        {"name": "颜色记忆", "file": "color_memory.py", "desc": "记颜色"},
        {"name": "文字接龙", "file": "word_snake.py", "desc": "单词接龙"},
        {"name": "字母重组", "file": "anagram.py", "desc": "拼单词"},
        {"name": "单词拼写", "file": "word_scramble.py", "desc": "拼单词"},
        {"name": "数字赛马", "file": "number_race.py", "desc": "数字比赛"},
    ],
    "♠️ 卡牌桌游": [
        {"name": "21点", "file": "blackjack.py", "desc": "21点"},
        {"name": "接龙", "file": "solitaire.py", "desc": "接龙纸牌"},
        {"name": "UNO", "file": "uno_game.py", "desc": "UNO"},
        {"name": "卡牌对战", "file": "card_battle.py", "desc": "对战"},
        {"name": "骰子游戏", "file": "dice_games.py", "desc": "骰子"},
        {"name": "多米诺骨牌", "file": "dominoes.py", "desc": "多米诺"},
        {"name": "沙狐球", "file": "shuffleboard.py", "desc": "沙狐球"},
    ],
    "🎉 多人派对": [
        {"name": "多人派对对战", "file": "multiplayer_party.py", "desc": "多人同屏"},
        {"name": "派对游戏合集", "file": "party_games.py", "desc": "多个小游戏"},
        {"name": "知识问答比赛", "file": "trivia_contest.py", "desc": "问答比赛"},
        {"name": "谁是卧底", "file": "spy_game.py", "desc": "卧底猜测"},
        {"name": "疯狂猜词", "file": "crazy_word_game.py", "desc": "猜词对战"},
        {"name": "你画我猜", "file": "draw_and_guess.py", "desc": "画画猜词"},
    ],
    "🔫 生存射击": [
        {"name": "太空射击", "file": "space_shooter.py", "desc": "射击游戏"},
        {"name": "僵尸生存", "file": "zombie_survival.py", "desc": "打僵尸"},
        {"name": "飞行模拟", "file": "flight_sim.py", "desc": "开飞机"},
        {"name": "推理游戏", "file": "deduction_game.py", "desc": "推理"},
        {"name": "迷宫", "file": "maze.py", "desc": "走迷宫"},
        {"name": "迷宫逃生", "file": "maze_escape.py", "desc": "逃迷宫"},
        {"name": "密室逃脱", "file": "escape_room.py", "desc": "找线索"},
    ],
    "🤖 放置自动": [
        {"name": "自动点击器", "file": "auto_clicker.py", "desc": "自动点击"},
        {"name": "放置挂机游戏", "file": "idle_incremental.py", "desc": "挂机"},
        {"name": "点击英雄", "file": "clicker_hero.py", "desc": "点击游戏"},
        {"name": "农场自动种植", "file": "farm_auto.py", "desc": "农场经营"},
        {"name": "工厂生产线", "file": "factory_sim.py", "desc": "工厂模拟"},
    ],
    "🚗 赛车驾驶": [
        {"name": "赛车", "file": "racing.py", "desc": "赛车"},
        {"name": "双人赛车", "file": "racing_2p.py", "desc": "双人赛车"},
        {"name": "飞行模拟", "file": "flight_sim.py", "desc": "飞行"},
        {"name": "2D赛车竞速", "file": "racing_2d.py", "desc": "竞速赛车"},
        {"name": "卡丁车赛道", "file": "kart_racing.py", "desc": "卡丁车"},
        {"name": "摩托车狂飙", "file": "motorcycle_racing.py", "desc": "摩托竞速"},
    ],
    "🎬 视觉叙事": [
        {"name": "视觉小说", "file": "visual_novel.py", "desc": "剧情"},
        {"name": "密室逃脱", "file": "escape_room.py", "desc": "逃脱"},
        {"name": "互动故事冒险", "file": "interactive_story.py", "desc": "互动剧情"},
        {"name": "侦探推理小说", "file": "detective_game.py", "desc": "侦探推理"},
        {"name": "选择分支剧情", "file": "branching_story.py", "desc": "剧情选择"},
    ],
    "🔬 科学教育": [
        {"name": "元素周期表", "file": "element_game.py", "desc": "化学元素"},
        {"name": "物理实验室", "file": "physics_lab.py", "desc": "物理模拟"},
    ],
    "🔫 生存射击": [
        {"name": "太空射击", "file": "space_shooter.py", "desc": "射击游戏"},
        {"name": "僵尸生存", "file": "zombie_survival.py", "desc": "打僵尸"},
        {"name": "飞行模拟", "file": "flight_sim.py", "desc": "开飞机"},
        {"name": "推理游戏", "file": "deduction_game.py", "desc": "推理"},
        {"name": "迷宫", "file": "maze.py", "desc": "走迷宫"},
        {"name": "迷宫逃生", "file": "maze_escape.py", "desc": "逃迷宫"},
        {"name": "密室逃脱", "file": "escape_room.py", "desc": "找线索"},
        {"name": "狙击精英", "file": "sniper_game.py", "desc": "狙击游戏"},
        {"name": "双摇杆射击", "file": "twin_stick_shooter.py", "desc": "射击"},
    ],
}

all_games = []
for category, games in games_data.items():
    for game in games:
        game["category"] = category
        all_games.append(game)

current_category = 0
scroll_offset = 0
selected_game = None
search_query = ""

def draw_gradient():
    for y in range(HEIGHT):
        r = int(20 + y / HEIGHT * 40)
        g = int(20 + y / HEIGHT * 40)
        b = int(40 + y / HEIGHT * 60)
        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))

def draw_categories():
    category_y = 30
    for i, category in enumerate(categories):
        x = 10 + (i % 8) * 148
        y = category_y + (i // 8) * 50
        
        if i == current_category:
            pygame.draw.rect(screen, category["color"], (x, y, 143, 40), border_radius=5)
            pygame.draw.rect(screen, WHITE, (x, y, 143, 40), 3, border_radius=5)
        else:
            pygame.draw.rect(screen, DARK_GRAY, (x, y, 143, 40), border_radius=5)
        
        text = font_small.render(category["name"], True, WHITE)
        text_rect = text.get_rect(center=(x + 71, y + 20))
        screen.blit(text, text_rect)

def draw_games():
    games_to_show = []
    if current_category == 0:
        games_to_show = all_games
    else:
        category_name = categories[current_category]["name"]
        if category_name in games_data:
            games_to_show = games_data[category_name]
    
    if search_query:
        games_to_show = [g for g in games_to_show if search_query.lower() in g["name"].lower()]
    
    start_idx = scroll_offset
    visible_count = min(12, len(games_to_show) - start_idx)
    
    for i in range(visible_count):
        game_idx = start_idx + i
        if game_idx >= len(games_to_show):
            break
        
        game = games_to_show[game_idx]
        row = i // 4
        col = i % 4
        x = 10 + col * 295
        y = 150 + row * 160
        
        is_selected = selected_game == game
        
        if is_selected:
            pygame.draw.rect(screen, YELLOW, (x - 5, y - 5, 285, 150), 3, border_radius=10)
        
        pygame.draw.rect(screen, (60, 60, 80), (x, y, 275, 140), border_radius=10)
        
        name_text = font_medium.render(game["name"], True, WHITE)
        screen.blit(name_text, (x + 20, y + 15))
        
        desc_text = font_tiny.render(game["desc"], True, GRAY)
        screen.blit(desc_text, (x + 20, y + 50))
        
        category_text = font_tiny.render(game["category"], True, PURPLE)
        screen.blit(category_text, (x + 20, y + 75))
        
        play_text = font_small.render("▶ 开始游戏", True, GREEN)
        screen.blit(play_text, (x + 20, y + 100))

def draw_search():
    pygame.draw.rect(screen, (40, 40, 60), (10, HEIGHT - 70, WIDTH - 20, 50), border_radius=8)
    search_text = font_medium.render(f"搜索: {search_query}", True, WHITE)
    screen.blit(search_text, (30, HEIGHT - 55))

def draw_scrollbar():
    games_to_show = all_games if current_category == 0 else games_data.get(categories[current_category]["name"], [])
    total_games = len(games_to_show)
    if search_query:
        total_games = len([g for g in games_to_show if search_query.lower() in g["name"].lower()])
    
    if total_games > 12:
        scroll_height = HEIGHT - 190
        thumb_height = max(40, (12 / total_games) * scroll_height)
        thumb_y = 150 + (scroll_offset / total_games) * scroll_height
        
        pygame.draw.rect(screen, DARK_GRAY, (WIDTH - 25, 150, 15, scroll_height))
        pygame.draw.rect(screen, (150, 150, 180), (WIDTH - 25, thumb_y, 15, thumb_height))

def launch_game(game):
    file_path = os.path.join(os.getcwd(), game["file"])
    if os.path.exists(file_path):
        try:
            subprocess.Popen([sys.executable, file_path])
        except Exception as e:
            print(f"启动游戏失败: {e}")
    else:
        print(f"游戏文件不存在: {file_path}")

running = True
while running:
    screen.fill(BLACK)
    draw_gradient()
    
    title_text = font_large.render("🎮 Python 小游戏合集 - 游戏启动器 v1.0", True, YELLOW)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 5))
    
    count_text = font_small.render(f"共 {len(all_games)} 个游戏 | 按ESC退出 | 方向键翻页/分类 | 鼠标点击启动", True, WHITE)
    screen.blit(count_text, (20, HEIGHT - 100))
    
    draw_categories()
    draw_games()
    draw_scrollbar()
    draw_search()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            
            for i, category in enumerate(categories):
                x = 10 + (i % 8) * 148
                y = 30 + (i // 8) * 50
                if x <= mx <= x + 143 and y <= my <= y + 40:
                    current_category = i
                    scroll_offset = 0
                    selected_game = None
            
            games_to_show = all_games if current_category == 0 else games_data.get(categories[current_category]["name"], [])
            if search_query:
                games_to_show = [g for g in games_to_show if search_query.lower() in g["name"].lower()]
            
            for i in range(len(games_to_show)):
                if i < scroll_offset or i >= scroll_offset + 12:
                    continue
                row = (i - scroll_offset) // 4
                col = (i - scroll_offset) % 4
                x = 10 + col * 295
                y = 150 + row * 160
                
                if x <= mx <= x + 275 and y <= my <= y + 140:
                    selected_game = games_to_show[i]
                    launch_game(games_to_show[i])
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_UP:
                scroll_offset = max(0, scroll_offset - 4)
            elif event.key == pygame.K_DOWN:
                scroll_offset += 4
            elif event.key == pygame.K_LEFT:
                current_category = max(0, current_category - 1)
                scroll_offset = 0
            elif event.key == pygame.K_RIGHT:
                current_category = min(len(categories) - 1, current_category + 1)
                scroll_offset = 0
            elif event.key == pygame.K_BACKSPACE:
                search_query = search_query[:-1]
            elif event.key == pygame.K_SPACE:
                search_query += " "
            elif event.key != pygame.K_RETURN:
                if len(event.unicode) > 0 and event.unicode.isprintable():
                    search_query += event.unicode
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
