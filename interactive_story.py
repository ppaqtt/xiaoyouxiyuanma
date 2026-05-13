"""
互动故事冒险
一个带有选择分支的互动叙事游戏
"""

import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 900, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("互动故事冒险")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (50, 50, 50)
BLUE = (0, 100, 200)
GREEN = (0, 180, 100)
RED = (200, 50, 50)
PURPLE = (150, 50, 200)

class Scene:
    def __init__(self, title, description, choices):
        self.title = title
        self.description = description
        self.choices = choices

class Game:
    def __init__(self):
        self.current_scene = 0
        self.player_name = "探险家"
        self.game_started = False
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 28)
        
        self.scenes = [
            Scene(
                "序章：神秘的邀请函",
                f"{self.player_name}，你收到了一封神秘的邀请函...\n\n"
                "信中写道：'我们需要你，一位真正的探险家。在古老的森林深处，\n"
                "隐藏着失落已久的宝藏。只有你能找到它！'\n\n"
                "你决定...",
                ["前往森林探险", "忽略这封信", "先去调查一下"]
            ),
            Scene(
                "森林入口",
                "你来到了古老森林的入口。茂密的树木遮天蔽日，\n"
                "前方有两条小径：一条明亮但看起来很普通，\n"
                "另一条幽暗但似乎有神秘的光芒...",
                ["走明亮的小路", "走幽暗的小径", "在入口先休息一下"]
            ),
            Scene(
                "发现了一座桥",
                "你沿着明亮的小路前进，发现了一座古老的石桥。\n"
                "桥看起来有些破旧，但似乎还能走...",
                ["小心过桥", "寻找其他路线", "检查桥的牢固度"]
            ),
            Scene(
                "神秘洞穴",
                "你选择了幽暗的小径，来到了一个发着蓝光的洞穴。\n"
                "洞穴深处似乎有什么东西在闪闪发光...",
                ["进入洞穴", "在外面观察", "大声呼喊"]
            ),
            Scene(
                "遇到了老者",
                "在调查的路上，你遇到了一位神秘的老者。\n"
                "他微笑着看着你，说：'年轻人，我可以帮助你，\n"
                "但需要一些东西作为交换...'",
                ["接受老者的帮助", "礼貌拒绝", "询问交换条件"]
            ),
            Scene(
                "宝藏！",
                "恭喜你，{self.player_name}！\n\n"
                "你找到了传说中的宝藏！\n\n"
                "这是一次伟大的冒险！",
                ["重新开始"]
            ),
            Scene(
                "冒险结束",
                "你选择了平凡的生活，\n"
                "也许宝藏并不适合你...\n\n"
                "但永远不要忘记你心中的冒险精神！",
                ["重新开始"]
            ),
            Scene(
                "遇到了危险",
                "哎呀！你遇到了一些危险...\n\n"
                "但不要担心，每一次失败都是新的开始！",
                ["重新开始"]
            )
        ]
    
    def draw(self):
        screen.fill(BLACK)
        
        if not self.game_started:
            self.draw_title()
        else:
            self.draw_story()
        
        pygame.display.flip()
    
    def draw_title(self):
        title = self.font_large.render("互动故事冒险", True, PURPLE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        
        subtitle = self.font_medium.render("做出选择，决定你的命运！", True, WHITE)
        screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, 200))
        
        instructions = [
            "使用鼠标点击选择你想要的选项",
            "每一个选择都会影响故事的走向",
            "",
            "按 空格键 开始游戏"
        ]
        
        y = 300
        for line in instructions:
            text = self.font_small.render(line, True, GRAY)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, y))
            y += 40
    
    def draw_story(self):
        scene = self.scenes[self.current_scene]
        
        title = self.font_large.render(scene.title, True, BLUE)
        screen.blit(title, (50, 30))
        
        desc_lines = scene.description.split('\n')
        y = 130
        for line in desc_lines:
            text = self.font_medium.render(line, True, WHITE)
            screen.blit(text, (50, y))
            y += 35
        
        # 绘制选择按钮
        button_height = 60
        start_y = y + 50
        
        for i, choice in enumerate(scene.choices):
            button_y = start_y + i * (button_height + 15)
            
            button_rect = pygame.Rect(50, button_y, WIDTH - 100, button_height)
            pygame.draw.rect(screen, DARK_GRAY, button_rect, border_radius=10)
            pygame.draw.rect(screen, BLUE, button_rect, 3, border_radius=10)
            
            text = self.font_medium.render(choice, True, WHITE)
            screen.blit(text, (70, button_y + (button_height - 30) // 2))
    
    def handle_click(self, pos):
        if not self.game_started:
            self.game_started = True
            return
        
        scene = self.scenes[self.current_scene]
        
        button_height = 60
        start_y = 280 + (len(scene.description.split('\n')) * 35) + 50
        
        for i, _ in enumerate(scene.choices):
            button_y = start_y + i * (button_height + 15)
            button_rect = pygame.Rect(50, button_y, WIDTH - 100, button_height)
            
            if button_rect.collidepoint(pos):
                self.make_choice(i)
    
    def make_choice(self, choice_index):
        scene = self.scenes[self.current_scene]
        
        if scene.title == "序章：神秘的邀请函":
            if choice_index == 0:
                self.current_scene = 1
            elif choice_index == 1:
                self.current_scene = 6
            else:
                self.current_scene = 4
        elif scene.title == "森林入口":
            if choice_index == 0:
                self.current_scene = 2
            elif choice_index == 1:
                self.current_scene = 3
            else:
                self.current_scene = 1
        elif scene.title == "发现了一座桥":
            if choice_index == 0:
                self.current_scene = 5
            elif choice_index == 1:
                self.current_scene = 1
            else:
                self.current_scene = 7
        elif scene.title == "神秘洞穴":
            if choice_index == 0:
                self.current_scene = 5
            elif choice_index == 1:
                self.current_scene = 3
            else:
                self.current_scene = 7
        elif scene.title == "遇到了老者":
            if choice_index == 0:
                self.current_scene = 5
            elif choice_index == 1:
                self.current_scene = 1
            else:
                self.current_scene = 5
        elif scene.title in ["宝藏！", "冒险结束", "遇到了危险"]:
            self.current_scene = 0
            self.game_started = False

def main():
    game = Game()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    game.handle_click(event.pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game.game_started:
                    game.game_started = True
                elif event.key == pygame.K_ESCAPE:
                    running = False
        
        game.draw()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
