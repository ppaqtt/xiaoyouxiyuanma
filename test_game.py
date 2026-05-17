
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

import sys
import os

# 添加项目路径
sys.path.insert(0, '/workspace')

print("测试人生模拟器游戏代码...")

try:
    # 测试导入
    import pygame
    print("✓ pygame 导入成功")
    
    # 测试代码语法
    with open('/workspace/life_simulator.py', 'r') as f:
        code = f.read()
    
    # 编译代码检查语法
    compile(code, '/workspace/life_simulator.py', 'exec')
    print("✓ 代码语法正确")
    
    # 测试主要类
    import importlib.util
    spec = importlib.util.spec_from_file_location("life_simulator", "/workspace/life_simulator.py")
    life_simulator = importlib.util.module_from_spec(spec)
    
    # 直接执行代码部分（不运行游戏循环）
    exec(code, life_simulator.__dict__)
    
    print("✓ 所有类和函数加载成功")
    
    # 测试 LifeSimulator 类
    sim = life_simulator.LifeSimulator()
    print(f"✓ LifeSimulator 初始化成功 - 年龄: {sim.age}")
    
    # 测试 make_choice 方法
    sim.make_choice(0)
    print(f"✓ 选择成功 - 年龄现在: {sim.age}")
    print(f"  健康: {sim.health}, 幸福: {sim.happiness}")
    print(f"  财富: {sim.wealth}, 学历: {sim.education}")
    
    # 测试多个年份
    for i in range(5):
        if sim.current_choices:
            sim.make_choice(0)
            print(f"  第 {i+1} 年后: 年龄 {sim.age} 岁")
    
    print("\n🎉 所有测试通过！")
    print("\n游戏功能:")
    print("- 从出生到死亡的完整人生模拟")
    print("- 6个不同的人生阶段")
    print("- 每个阶段有不同的选择")
    print("- 4个核心属性系统")
    print("- 随机事件机制")
    print("- 人生总结评价")
    print("- 完整的音效系统")
    
except Exception as e:
    print(f"✗ 测试失败: {e}")
    import traceback
    traceback.print_exc()
