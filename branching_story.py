"""
选择分支剧情
一个复杂的多分支剧情选择游戏
"""

import pygame
import os
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

WIDTH, HEIGHT = 900, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("选择分支剧情")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (30, 30, 30)
BLUE = (30, 100, 200)
GREEN = (0, 180, 100)
RED = (200, 50, 50)
PURPLE = (140, 50, 180)
ORANGE = (255, 140, 0)

class StoryNode:
    def __init__(self, text, choices, consequences=None):
        self.text = text
        self.choices = choices
        self.consequences = consequences if consequences else []

class BranchingStory:
    def __init__(self):
        self.current_node = 0
        self.history = []
        self.phase = "menu"
        self.font_large = get_chinese_font(64)
        self.font_medium = get_chinese_font(32)
        self.font_small = get_chinese_font(24)
        self.create_story()
    
    def create_story(self):
        self.nodes = [
            StoryNode(
                "你是一位年轻的冒险者，站在一个古老村庄的广场上。\n"
                "村民们都在议论纷纷，似乎有什么大事即将发生...",
                ["与村民交谈了解情况", "前往酒馆休息", "直接去探索附近的洞穴"]
            ),
            StoryNode(
                "村民告诉你，山上的洞穴里住着一条恶龙，\n"
                "它经常下山掠夺村庄的食物和财宝。\n"
                "村长悬赏重金招募勇士去屠龙...",
                ["接受屠龙任务", "询问是否有其他办法", "再去其他地方看看"]
            ),
            StoryNode(
                "在酒馆里，你遇到了一位神秘的旅行者。\n"
                "他低声说：'不要相信村长的话，那条龙其实...'",
                ["仔细听他说", "打断他去问老板", "直接离开去洞穴"]
            ),
            StoryNode(
                "你来到了洞穴入口，能闻到一股硫磺的气味，\n"
                "洞穴深处传来低沉的咆哮声...",
                ["勇敢地走进去", "先在入口观察", "寻找其他入口"]
            ),
            StoryNode(
                "村长交给你一把祖传的宝剑和一套盔甲，\n"
                "说：'年轻人，村庄的命运就托付给你了！'",
                ["接受装备出发", "询问关于龙的弱点", "先去找神秘旅行者"]
            ),
            StoryNode(
                "村民告诉你，其实龙是被冤枉的！\n"
                "真正作恶的是村长，他想独吞龙守护的宝藏...",
                ["去找村长对质", "先去找龙谈谈", "独自去寻找宝藏"]
            ),
            StoryNode(
                "旅行者刚要说更多，村长就带人冲了进来，\n"
                "把他抓了起来！",
                ["想办法救旅行者", "悄悄离开这里", "质问村长"]
            ),
            StoryNode(
                "你进入了洞穴，里面金光闪闪！\n"
                "一堆堆的金币和宝石，而龙正躺在宝藏堆上睡觉...",
                ["悄悄偷些宝藏", "尝试与龙交谈", "拔剑攻击"]
            ),
            StoryNode(
                "龙醒来了，但它看起来并不凶恶！\n"
                "它说：'人类，我已经很久没吃人了。\n"
                "村长一直在污蔑我，就是想独吞我的宝藏...'",
                ["相信龙的话", "还是拔剑攻击", "提出合作"]
            ),
            StoryNode(
                "你找到了龙的弱点，在激烈的战斗后，\n"
                "你成功击败了恶龙！村庄恢复了和平，\n"
                "你成为了传奇的英雄！",
                ["重新开始"]
            ),
            StoryNode(
                "你和龙一起揭露了村长的阴谋，\n"
                "村民们明白了真相，把村长赶下了台。\n"
                "龙和人类和平共处，你成了和平使者！",
                ["重新开始"]
            ),
            StoryNode(
                "你偷偷拿走了宝藏，但村长派人追了上来。\n"
                "你被当成了小偷...",
                ["重新开始"]
            ),
            StoryNode(
                "你救出了旅行者，他带你找到了龙的洞穴，\n"
                "并揭露了村长的阴谋。真相大白！",
                ["重新开始"]
            )
        ]
        
        self.choice_map = {
            0: {0: 1, 1: 2, 2: 3},
            1: {0: 4, 1: 5, 2: 3},
            2: {0: 7, 1: 2, 2: 3},
            3: {0: 7, 1: 3, 2: 3},
            4: {0: 7, 1: 4, 2: 2},
            5: {0: 5, 1: 7, 2: 11},
            6: {0: 12, 1: 1, 2: 1},
            7: {0: 11, 1: 8, 2: 9},
            8: {0: 10, 1: 9, 2: 10},
            9: {0: 0, 1: 0, 2: 0},
            10: {0: 0, 1: 0, 2: 0},
            11: {0: 0, 1: 0, 2: 0},
            12: {0: 0, 1: 0, 2: 0}
        }
    
    def draw(self):
        screen.fill(DARK_GRAY)
        
        if self.phase == "menu":
            self.draw_menu()
        elif self.phase == "game":
            self.draw_game()
        
        pygame.display.flip()
    
    def draw_menu(self):
        title = self.font_large.render("选择分支剧情", True, PURPLE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        
        subtitle = self.font_medium.render("每个选择都将影响故事的结局", True, WHITE)
        screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, 180))
        
        instructions = [
            "点击选项来做出你的选择",
            "探索不同的剧情分支",
            "发现所有可能的结局！",
            "",
            "按 空格键 开始冒险"
        ]
        
        y = 250
        for line in instructions:
            text = self.font_small.render(line, True, GRAY)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, y))
            y += 35
        
        endings = self.font_small.render(f"已探索结局: {len(set(self.history))} / 3", True, ORANGE)
        screen.blit(endings, (WIDTH//2 - endings.get_width()//2, y + 30))
    
    def draw_game(self):
        # 历史记录
        pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, 40))
        hist_text = f"历史: {' → '.join([str(h) for h in self.history[-5:]])}"
        text = self.font_small.render(hist_text, True, GRAY)
        screen.blit(text, (20, 10))
        
        # 当前剧情
        node = self.nodes[self.current_node]
        
        text_y = 80
        lines = node.text.split('\n')
        for line in lines:
            text = self.font_medium.render(line, True, WHITE)
            screen.blit(text, (50, text_y))
            text_y += 35
        
        # 选择按钮
        button_y = text_y + 40
        for i, choice in enumerate(node.choices):
            btn_rect = pygame.Rect(50, button_y, WIDTH - 100, 60)
            colors = [BLUE, GREEN, ORANGE, RED]
            pygame.draw.rect(screen, colors[i % len(colors)], btn_rect, border_radius=10)
            
            text = self.font_medium.render(choice, True, WHITE)
            screen.blit(text, (70, button_y + 15))
            button_y += 75
    
    def handle_click(self, pos):
        if self.phase != "game":
            return
        
        node = self.nodes[self.current_node]
        
        text_y = 80 + len(node.text.split('\n')) * 35 + 40
        for i, _ in enumerate(node.choices):
            btn_rect = pygame.Rect(50, text_y, WIDTH - 100, 60)
            if btn_rect.collidepoint(pos):
                self.make_choice(i)
            text_y += 75
    
    def make_choice(self, choice_index):
        self.history.append(self.current_node)
        
        if self.current_node in self.choice_map:
            next_node = self.choice_map[self.current_node].get(choice_index, 0)
            self.current_node = next_node
            
            if next_node in [9, 10, 11, 12]:
                if next_node == 9:
                    self.history.append("结局1：英雄结局")
                elif next_node == 10:
                    self.history.append("结局2：和平结局")
                elif next_node == 11:
                    self.history.append("结局3：贪婪结局")
                elif next_node == 12:
                    self.history.append("结局4：真相结局")
        
        if len(self.nodes[self.current_node].choices) == 1 and \
           self.nodes[self.current_node].choices[0] == "重新开始":
            pygame.time.delay(3000)
            self.current_node = 0
            self.history.append("重新开始")
    
    def handle_key(self, key):
        if key == pygame.K_SPACE and self.phase == "menu":
            self.phase = "game"
        elif key == pygame.K_r:
            self.current_node = 0
            self.history = []
            self.phase = "menu"
        elif key == pygame.K_h:
            if self.history:
                self.current_node = self.history.pop()

def main():
    game = BranchingStory()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    game.handle_click(event.pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                else:
                    game.handle_key(event.key)
        
        game.draw()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
