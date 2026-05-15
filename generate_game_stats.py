#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re

WORKSPACE_DIR = "/workspace"

# 工具/启动器文件（不算游戏）
UTIL_FILES = [
    "game_launcher.py",
    "game_launcher_v2.py",
    "games_stats.py",
    "final_summary.py",
    "recommend_new_games.py",
    "verify_uniqueness.py",
    "summarize_new_games.py",
]

def count_games():
    """统计工作区中的游戏文件"""
    all_files = [f for f in os.listdir(WORKSPACE_DIR) if f.endswith(".py")]
    game_files = [f for f in all_files if f not in UTIL_FILES]
    
    print("=" * 80)
    print("📊 游戏文件统计")
    print("=" * 80)
    print(f"总Python文件数：{len(all_files)}")
    print(f"工具/启动器文件：{len(UTIL_FILES)}")
    print(f"实际游戏文件：{len(game_files)}")
    print()
    
    # 分类统计（基于README的分类）
    categories = {
        "📝 经典文字游戏": [
            "guess_number.py", "tic_tac_toe.py", "hangman.py",
            "rock_paper_scissors.py", "text_poker.py", "text_blackjack.py",
            "chat_bot.py", "adventure_text.py", "code_breaker.py", "couplet_master.py"
        ],
        "🕹️ 街机复刻": [
            "snake_game.py", "snake_3d.py", "snake_2p.py", "snake_variants.py",
            "game_2048.py", "tetris.py", "breakout.py", "minesweeper.py",
            "minesweeper_advanced.py", "pac_man.py", "donkey_kong.py",
            "space_invaders_classic.py", "bomberman_pro.py", "pong.py",
            "whack_a_mole.py", "shooting_range.py", "billiards.py", "sokoban_variants.py",
            "contra_shooter.py", "bomberman.py", "sokoban.py"
        ],
        "🏰 策略塔防": [
            "tower_defense.py", "tower_defense_deluxe.py", "mini_rts.py",
            "rts_battle.py", "tactical_warfare.py", "chess_simple.py",
            "chinese_chess.py", "monopoly_style.py", "gomoku.py", "online_gomoku.py",
            "tank_battle.py", "card_builder_dbg.py", "tictactoe_ai.py"
        ],
        "⚔️ RPG冒险": [
            "simple_rpg.py", "turn_based_rpg.py", "top_down_arpg.py",
            "text_rpg.py", "pixel_quest_rpg.py", "metroidvania_simple.py",
            "platformer.py", "horizontal_shooter.py", "roguelike_dungeon.py",
            "roguelike_tactical.py", "card_roguelike.py", "action_roguelike.py"
        ],
        "🏪 模拟经营": [
            "restaurant_sim.py", "city_builder.py", "shop_keeper.py",
            "farm_simulator.py", "sandbox_builder.py", "hospital_sim.py",
            "school_sim.py", "zoo_sim.py", "simple_stardew_valley.py"
        ],
        "🧩 益智解谜": [
            "memory_game.py", "puzzle.py", "puzzle_blocks.py", "huarong_dao.py",
            "one_stroke.py", "sudoku.py", "lianliankan.py", "mahjong_link.py",
            "match_three.py", "spot_difference.py", "pipe_builder.py", "logic_puzzle.py",
            "gravity_puzzle.py", "time_manipulation.py", "time_loop_puzzle.py",
            "twenty_four.py", "nonogram.py", "idiom_game.py", "tangram.py",
            "paint_by_number.py"
        ],
        "🎵 音乐创意": [
            "rhythm_master.py", "music_generator.py", "pixel_art.py",
            "pixel_animator.py", "draw_something.py", "physics_sandbox.py",
            "physics_balls.py", "fractal_art.py", "music_visualizer.py",
            "guitar_hero.py", "pixel_art_editor.py"
        ],
        "🎯 休闲街机": [
            "fruit_ninja.py", "catch_fruit.py", "collect_coins.py", "jump_game.py",
            "stacking.py", "parkour_runner.py", "bubble_shooter.py", "dodge_game.py",
            "pinball.py", "pinball_physics.py", "rainbow_island.py"
        ],
        "📚 文字学习": [
            "typing_practice.py", "typing_master.py", "math_game.py",
            "quick_math.py", "simon_says.py", "color_memory.py", "word_snake.py",
            "anagram.py", "word_scramble.py", "number_race.py"
        ],
        "♠️ 卡牌桌游": [
            "blackjack.py", "solitaire.py", "uno_game.py", "card_battle.py",
            "dice_games.py", "dominoes.py", "shuffleboard.py", "stud_poker.py",
            "landlord.py", "bridge.py"
        ],
        "🎉 多人派对": [
            "multiplayer_party.py", "party_games.py", "trivia_contest.py",
            "spy_game.py", "crazy_word_game.py", "draw_and_guess.py",
            "multiplayer_quiz.py", "multiplayer_memory.py", "multiplayer_spot_diff.py",
            "multiplayer_bomberman.py"
        ],
        "🔫 生存射击": [
            "space_shooter.py", "zombie_survival.py", "flight_sim.py",
            "deduction_game.py", "maze.py", "maze_escape.py", "escape_room.py",
            "sniper_game.py", "twin_stick_shooter.py", "island_survival.py"
        ],
        "🤖 放置自动": [
            "auto_clicker.py", "idle_incremental.py", "clicker_hero.py",
            "farm_auto.py", "factory_sim.py", "idle_evolution.py",
            "idle_mining.py", "idle_tower_defense.py"
        ],
        "🚗 赛车驾驶": [
            "racing.py", "racing_2p.py", "flight_sim.py", "racing_2d.py",
            "kart_racing.py", "motorcycle_racing.py"
        ],
        "🎬 视觉叙事": [
            "visual_novel.py", "escape_room.py", "interactive_story.py",
            "detective_game.py", "branching_story.py", "text_adventure.py",
            "time_travel.py", "mystery_novel.py"
        ],
        "🔬 科学教育": [
            "element_game.py", "physics_lab.py", "chemistry_lab.py",
            "programming_tutor.py", "geometry_lab.py", "evolution_sim.py",
            "geography_quiz.py"
        ],
        "🏃 竞速运动": [
            "athletics.py", "swimming.py", "cycling.py"
        ],
        "🏋️ 体育竞技": [
            "table_tennis.py", "tennis.py", "badminton.py"
        ],
        "🎭 角色扮演模拟": [
            "life_simulator.py", "pet_simulator.py", "space_colony.py"
        ],
        "🎲 创意工具": [
            "pixel_art_editor.py", "paint_by_number.py"
        ]
    }
    
    print("=" * 80)
    print("📂 各分类游戏统计")
    print("=" * 80)
    print()
    
    total_count = 0
    category_counts = []
    
    for category, files in categories.items():
        existing_files = [f for f in files if f in game_files]
        count = len(existing_files)
        total_count += count
        category_counts.append((category, count, len(files)))
        
        # 打印分类
        bar = "█" * (count // 2)
        print(f"{category}")
        print(f"  数量: {count} / {len(files)}")
        if count > 0:
            print(f"  进度: {bar}")
        print()
    
    print("=" * 80)
    print("📉 游戏较少的分类")
    print("=" * 80)
    print()
    
    # 找出数量较少的分类
    for category, count, _ in sorted(category_counts, key=lambda x: x[1]):
        if count <= 6:
            print(f"{category} - {count} 个游戏")
            # 显示该分类已有的游戏
            for f in categories[category]:
                if f in game_files:
                    print(f"  ✓ {f}")
            print()
    
    print("=" * 80)
    print("✨ 推荐可添加的新游戏")
    print("=" * 80)
    print()
    
    recommendations = [
        {
            "category": "🎲 创意工具",
            "games": [
                {
                    "name": "像素动画编辑器",
                    "desc": "像素画逐帧动画创作工具",
                    "type": "创作工具"
                },
                {
                    "name": "简笔画助手",
                    "desc": "儿童简笔画教学和创作工具",
                    "type": "创作工具"
                }
            ]
        },
        {
            "category": "🏋️ 体育竞技",
            "games": [
                {
                    "name": "足球射门",
                    "desc": "点球大战小游戏",
                    "type": "体育游戏"
                },
                {
                    "name": "篮球三分",
                    "desc": "三分球投篮挑战",
                    "type": "体育游戏"
                }
            ]
        },
        {
            "category": "🏃 竞速运动",
            "games": [
                {
                    "name": "跳绳挑战",
                    "desc": "快速反应的跳绳游戏",
                    "type": "休闲体育"
                },
                {
                    "name": "跳房子",
                    "desc": "经典儿童跳房子游戏",
                    "type": "休闲体育"
                }
            ]
        },
        {
            "category": "🔬 科学教育",
            "games": [
                {
                    "name": "天文太阳系",
                    "desc": "太阳系行星科普互动演示",
                    "type": "科普教育"
                },
                {
                    "name": "生命科学",
                    "desc": "细胞和DNA基础科普",
                    "type": "科普教育"
                }
            ]
        },
        {
            "category": "🚗 赛车驾驶",
            "games": [
                {
                    "name": "3D拉力赛",
                    "desc": "简化版3D拉力赛车游戏",
                    "type": "竞速游戏"
                },
                {
                    "name": "卡丁车大作战",
                    "desc": "道具赛模式的卡丁车游戏",
                    "type": "竞速游戏"
                }
            ]
        },
        {
            "category": "🤖 放置自动",
            "games": [
                {
                    "name": "放置餐厅",
                    "desc": "点击升级餐厅的放置游戏",
                    "type": "放置游戏"
                },
                {
                    "name": "矿场大亨",
                    "desc": "自动采矿的放置经营游戏",
                    "type": "放置游戏"
                }
            ]
        }
    ]
    
    for rec in recommendations:
        print(f"{rec['category']}")
        for game in rec['games']:
            print(f"  🎮 {game['name']}")
            print(f"     {game['desc']}")
            print(f"     类型: {game['type']}")
        print()
    
    # 保存统计报告
    with open(os.path.join(WORKSPACE_DIR, "GAME_STATS_REPORT.txt"), "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("📊 游戏文件统计报告\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"总Python文件数：{len(all_files)}\n")
        f.write(f"工具/启动器文件：{len(UTIL_FILES)}\n")
        f.write(f"实际游戏文件：{len(game_files)}\n\n")
        f.write("=" * 80 + "\n")
        f.write("📂 各分类游戏统计\n")
        f.write("=" * 80 + "\n\n")
        for category, count, _ in category_counts:
            f.write(f"{category} - {count} 个游戏\n")
    
    print(f"\n✅ 详细报告已保存到: GAME_STATS_REPORT.txt")

if __name__ == "__main__":
    count_games()
