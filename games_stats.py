#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Python 小游戏合集 - 完整统计
# 共 138 个游戏

import os

# 游戏数据整理
games_data = {
    "📝 经典文字": [
        ("猜数字", "guess_number.py", "猜1-100的随机数"),
        ("井字棋", "tic_tac_toe.py", "经典双人对战"),
        ("绞刑架", "hangman.py", "猜单词游戏"),
        ("石头剪刀布", "rock_paper_scissors.py", "人机对战"),
    ],
    "🕹️ 街机复刻": [
        ("贪吃蛇", "snake_game.py", "经典街机"),
        ("贪吃蛇3D", "snake_3d.py", "伪3D透视"),
        ("贪吃蛇双人", "snake_2p.py", "双人对战"),
        ("贪吃蛇变种", "snake_variants.py", "多种模式"),
        ("2048", "game_2048.py", "数字合并"),
        ("俄罗斯方块", "tetris.py", "经典方块"),
        ("打砖块", "breakout.py", "弹球打砖"),
        ("扫雷", "minesweeper.py", "经典扫雷"),
        ("吃豆人", "pac_man.py", "经典迷宫"),
        ("大金刚", "donkey_kong.py", "平台跳跃"),
        ("太空侵略者", "space_invaders_classic.py", "经典射击"),
        ("炸弹人专业版", "bomberman_pro.py", "炸弹爆炸"),
        ("Pong乒乓球", "pong.py", "经典双人"),
        ("打地鼠", "whack_a_mole.py", "反应速度"),
        ("打靶游戏", "shooting_range.py", "射击打靶"),
        ("桌球", "billiards.py", "简化台球"),
        ("推箱子", "sokoban_variants.py", "推箱子变种"),
    ],
    "🏰 策略塔防": [
        ("塔防", "tower_defense.py", "经典塔防"),
        ("塔防豪华版", "tower_defense_deluxe.py", "6种塔类型"),
        ("即时战略简化版", "mini_rts.py", "采集建造"),
        ("即时战略对战", "rts_battle.py", "实时战斗"),
        ("回合制战术", "tactical_warfare.py", "战棋游戏"),
        ("国际象棋", "chess_simple.py", "简化象棋"),
        ("大富翁", "monopoly_style.py", "买地收租"),
        ("五子棋", "gomoku.py", "双人对战"),
        ("坦克大战", "tank_battle.py", "坦克射击"),
        ("卡牌构建", "card_builder_dbg.py", "DBG卡牌"),
    ],
    "⚔️ RPG冒险": [
        ("简单RPG", "simple_rpg.py", "基础RPG"),
        ("回合制RPG", "turn_based_rpg.py", "完整剧情"),
        ("俯视角ARPG", "top_down_arpg.py", "刷怪升级"),
        ("文字RPG", "text_rpg.py", "文字冒险"),
        ("像素冒险RPG", "pixel_quest_rpg.py", "像素冒险"),
        ("类银河恶魔城", "metroidvania_simple.py", "探索解锁"),
        ("平台跳跃", "platformer.py", "超级玛丽风格"),
        ("横版射击", "horizontal_shooter.py", "弹幕射击"),
        ("Roguelike地牢", "roguelike_dungeon.py", "随机地牢"),
        ("Roguelike战术", "roguelike_tactical.py", "回合制"),
        ("卡牌Roguelike", "card_roguelike.py", "杀戮尖塔风格"),
        ("动作Roguelike", "action_roguelike.py", "动作风格"),
    ],
    "🏪 模拟经营": [
        ("餐厅模拟器", "restaurant_sim.py", "经营餐厅"),
        ("城市建造", "city_builder.py", "建城市"),
        ("商店经营", "shop_keeper.py", "开商店"),
        ("农场模拟器", "farm_simulator.py", "种庄稼"),
        ("沙盒建造者", "sandbox_builder.py", "自由建造"),
    ],
    "🧩 益智解谜": [
        ("记忆配对", "memory_game.py", "翻牌配对"),
        ("数字拼图", "puzzle.py", "数字滑块"),
        ("拼图块", "puzzle_blocks.py", "块拼图"),
        ("华容道", "huarong_dao.py", "经典滑块"),
        ("一笔画", "one_stroke.py", "一笔画完"),
        ("数独", "sudoku.py", "数字数独"),
        ("连连看", "lianliankan.py", "连连看"),
        ("连连看麻将版", "mahjong_link.py", "麻将配对"),
        ("消消乐", "match_three.py", "三消游戏"),
        ("找不同", "spot_difference.py", "找不同"),
        ("管道连接", "pipe_builder.py", "接管道"),
        ("逻辑解谜", "logic_puzzle.py", "电路连接"),
        ("重力反转", "gravity_puzzle.py", "重力切换"),
        ("时间控制", "time_manipulation.py", "时间控制"),
        ("时间循环", "time_loop_puzzle.py", "时间循环"),
        ("24点", "twenty_four.py", "算24点"),
    ],
    "🎵 音乐创意": [
        ("音乐节奏大师", "rhythm_master.py", "节奏游戏"),
        ("音乐生成器", "music_generator.py", "创作音乐"),
        ("像素艺术", "pixel_art.py", "像素绘画"),
        ("像素动画师", "pixel_animator.py", "做动画"),
        ("画画猜词", "draw_something.py", "猜词游戏"),
        ("物理沙盒", "physics_sandbox.py", "物理实验"),
        ("物理弹珠球", "physics_balls.py", "弹球物理"),
    ],
    "🎯 休闲街机": [
        ("水果忍者", "fruit_ninja.py", "切水果"),
        ("接水果", "catch_fruit.py", "接水果"),
        ("接金币", "collect_coins.py", "接金币"),
        ("跳一跳", "jump_game.py", "跳跃游戏"),
        ("叠杯子", "stacking.py", "叠杯子"),
        ("跑酷", "parkour_runner.py", "自动跑酷"),
        ("泡泡射击", "bubble_shooter.py", "泡泡龙"),
        ("躲避球", "dodge_game.py", "躲避障碍"),
        ("简单弹球", "pinball.py", "弹球机"),
        ("弹球物理版", "pinball_physics.py", "物理弹球"),
    ],
    "📚 文字学习": [
        ("打字练习", "typing_practice.py", "练打字"),
        ("打字大师", "typing_master.py", "打字游戏"),
        ("数学游戏", "math_game.py", "学数学"),
        ("快速心算", "quick_math.py", "心算挑战"),
        ("Simon说", "simon_says.py", "记忆游戏"),
        ("颜色记忆", "color_memory.py", "记颜色"),
        ("文字接龙", "word_snake.py", "单词接龙"),
        ("字母重组", "anagram.py", "拼单词"),
        ("单词拼写", "word_scramble.py", "拼单词"),
        ("数字赛马", "number_race.py", "数字比赛"),
    ],
    "♠️ 卡牌桌游": [
        ("21点", "blackjack.py", "21点"),
        ("接龙", "solitaire.py", "接龙纸牌"),
        ("UNO", "uno_game.py", "UNO"),
        ("卡牌对战", "card_battle.py", "对战"),
        ("骰子游戏", "dice_games.py", "骰子"),
        ("多米诺骨牌", "dominoes.py", "多米诺"),
        ("沙狐球", "shuffleboard.py", "沙狐球"),
    ],
    "🎉 多人派对": [
        ("多人派对对战", "multiplayer_party.py", "多人同屏"),
        ("派对游戏合集", "party_games.py", "多个小游戏"),
        ("知识问答比赛", "trivia_contest.py", "问答比赛"),
    ],
    "🔫 生存射击": [
        ("太空射击", "space_shooter.py", "射击游戏"),
        ("僵尸生存", "zombie_survival.py", "打僵尸"),
        ("飞行模拟", "flight_sim.py", "开飞机"),
        ("推理游戏", "deduction_game.py", "推理"),
        ("迷宫", "maze.py", "走迷宫"),
        ("迷宫逃生", "maze_escape.py", "逃迷宫"),
        ("密室逃脱", "escape_room.py", "找线索"),
    ],
    "🤖 放置自动": [
        ("自动点击器", "auto_clicker.py", "自动点击"),
        ("放置挂机游戏", "idle_incremental.py", "挂机"),
    ],
    "🚗 赛车驾驶": [
        ("赛车", "racing.py", "赛车"),
        ("双人赛车", "racing_2p.py", "双人赛车"),
        ("飞行模拟", "flight_sim.py", "飞行"),
    ],
    "🎬 视觉叙事": [
        ("视觉小说", "visual_novel.py", "剧情"),
        ("密室逃脱", "escape_room.py", "逃脱"),
    ],
}

# 统计总数
total_games = 0
for category, games in games_data.items():
    total_games += len(games)

# 打印统计报告
print("=" * 80)
print("🎮 Python 小游戏合集 - 完整统计报告")
print("=" * 80)
print()
print(f"总游戏数: {total_games} 个")
print(f"分类数: {len(games_data)} 个")
print()

print("-" * 80)
print("📊 游戏分类详细统计")
print("-" * 80)
print()

for category, games in games_data.items():
    print(f"{category} - {len(games)}个游戏")
    for i, (name, file, desc) in enumerate(games, 1):
        print(f"  {i:2d}. {name}")
    print()

print("-" * 80)
print("💡 推荐添加的新游戏类型")
print("-" * 80)
print()

# 推荐添加的游戏
recommendations = {
    "🌍 多人在线游戏": [
        "在线多人五子棋",
        "在线多人对战贪吃蛇",
        "在线坦克大战",
        "在线答题比赛",
    ],
    "👑 MOBA/战斗": [
        "简化版MOBA类游戏",
        "回合制战斗模拟",
        "英雄养成系统",
        "技能树系统",
    ],
    "🌐 3D基础游戏": [
        "3D迷宫探索",
        "3D飞行模拟器",
        "3D方块建造",
        "简单3D赛车",
    ],
    "🎯 射击游戏": [
        "第一人称射击（简化版）",
        "横版射击 - 魂斗罗风格",
        "狙击精英 - 射击模拟",
        "双摇杆射击",
    ],
    "💹 模拟经营更多": [
        "医院模拟器",
        "学校模拟器",
        "机场管理",
        "火车/地铁管理",
        "动物园/水族馆",
    ],
    "🔬 科学教育": [
        "元素周期表小游戏",
        "物理定律模拟",
        "化学实验模拟器",
        "编程入门小游戏",
    ],
    "🎪 聚会游戏更多": [
        "谁是卧底",
        "你画我猜",
        "成语接龙",
        "快速反应比赛",
        "疯狂猜词",
    ],
    "🚀 创意/实验": [
        "AI对战 - 训练AI玩家",
        "神经演化演示",
        "分形艺术生成",
        "音乐可视化",
        "粒子物理沙盒",
    ],
    "🗺️ 策略更多": [
        "文明/帝国简化版",
        "战棋中国象棋",
        "战棋国际象棋高级版",
        "高级卡牌游戏",
        "资源管理游戏",
    ],
    "🧠 益智更多": [
        "数织（Nonogram）",
        "扫雷高级版",
        "数独杀手版",
        "七巧板拼图",
        "拼图华容道",
    ],
}

print("推荐添加的游戏分类:")
for category, games in recommendations.items():
    print(f"\n{category} - {len(games)}个推荐")
    for game in games:
        print(f"  • {game}")

print()
print("-" * 80)
print("📈 统计图表")
print("-" * 80)
print()

# ASCII统计图
max_count = max(len(games) for games in games_data.values())
print("游戏数量统计图:")
for category, games in games_data.items():
    count = len(games)
    bar = "█" * int(count / max_count * 20)
    print(f"{category:12} | {count:2d} | {bar}")

print()
print("=" * 80)
print("✅ 统计完成！")
print("=" * 80)

# 保存到文件
with open("/workspace/GAMES_STATS.txt", "w", encoding="utf-8") as f:
    f.write("=" * 80 + "\n")
    f.write("🎮 Python 小游戏合集 - 完整统计报告\n")
    f.write("=" * 80 + "\n\n")
    f.write(f"总游戏数: {total_games} 个\n")
    f.write(f"分类数: {len(games_data)} 个\n\n")
    
    f.write("-" * 80 + "\n")
    f.write("📊 游戏分类详细统计\n")
    f.write("-" * 80 + "\n\n")
    
    for category, games in games_data.items():
        f.write(f"{category} - {len(games)}个游戏\n")
        for i, (name, file, desc) in enumerate(games, 1):
            f.write(f"  {i:2d}. {name} - {file} - {desc}\n")
        f.write("\n")

print("\n✅ 统计报告已保存到: /workspace/GAMES_STATS.txt")
print("🎮 游戏合集很丰富！")
print("📌 提示: 想要添加新游戏？告诉我具体类型！")

