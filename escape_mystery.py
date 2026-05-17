import pygame
import os
import sys
import random

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

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("神秘逃脱")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 255)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
BROWN = (139, 90, 43)
GRAY = (100, 100, 100)

class EscapeRoom:
    def __init__(self):
        self.room = 0
        self.inventory = set()
        self.puzzles_solved = set()
        self.font = get_chinese_font(32)
        self.large_font = get_chinese_font(48)
        self.message = "欢迎来到神秘房间！探索四周，找到逃脱的方法。"
        self.room_descriptions = [
            "昏暗的书房，墙上挂着一幅奇怪的画，书架上的书似乎少了几本。桌子上有一本日记。",
            "复古风格的客厅，角落里有一个老式的保险柜，需要密码才能打开。沙发底下好像有东西...",
            "整洁的厨房，冰箱里有一些食物，炉灶上有一把钥匙，水池里放着一个花瓶，里面有一束枯萎的花。"
        ]

    def draw(self):
        screen.fill((50, 50, 60))
        
        if self.room == 0:
            self.draw_study()
        elif self.room == 1:
            self.draw_living_room()
        elif self.room == 2:
            self.draw_kitchen()
        
        pygame.draw.rect(screen, (40, 40, 50), (0, 500, 800, 100))
        pygame.draw.rect(screen, BLACK, (0, 500, 800, 100), 2)
        
        msg_lines = self.wrap_text(self.message, 750)
        y = 510
        for line in msg_lines:
            screen.blit(line, (25, y))
            y += 25
        
        inv_text = self.font.render(f"物品: {', '.join(self.inventory) if self.inventory else '空'}", True, WHITE)
        screen.blit(inv_text, (25, 460))

    def wrap_text(self, text, max_width):
        words = text.split()
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + word + " "
            test_surface = self.font.render(test_line, True, WHITE)
            if test_surface.get_width() <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "
        if current_line:
            lines.append(current_line)
        return lines

    def draw_study(self):
        pygame.draw.rect(screen, (80, 60, 40), (100, 100, 200, 350))  # 书架
        pygame.draw.rect(screen, BROWN, (400, 150, 250, 120))  # 桌子
        pygame.draw.rect(screen, (120, 80, 50), (350, 80, 200, 140))  # 画框
        pygame.draw.rect(screen, (180, 100, 100), (360, 90, 180, 120))  # 画
        
        title = self.large_font.render("书房", True, WHITE)
        screen.blit(title, (350, 20))
        
        if "diary_key" not in self.puzzles_solved:
            self.draw_button(50, 200, 150, 50, "查看日记")
        self.draw_button(400, 300, 200, 50, "查看挂画")
        self.draw_button(250, 420, 150, 50, "去客厅")
        
        if "secret" in self.inventory:
            self.draw_button(550, 420, 150, 50, "检查秘密")

    def draw_living_room(self):
        pygame.draw.rect(screen, (200, 150, 100), (250, 350, 300, 100))  # 沙发
        pygame.draw.rect(screen, (150, 150, 180), (100, 200, 150, 180))  # 保险柜
        pygame.draw.rect(screen, (180, 160, 120), (500, 150, 200, 250))  # 窗户
        
        title = self.large_font.render("客厅", True, WHITE)
        screen.blit(title, (350, 20))
        
        self.draw_button(200, 300, 150, 50, "沙发底下")
        self.draw_button(100, 400, 150, 50, "保险柜")
        self.draw_button(500, 400, 150, 50, "回书房")
        self.draw_button(650, 400, 130, 50, "去厨房")

    def draw_kitchen(self):
        pygame.draw.rect(screen, (200, 200, 220), (300, 150, 200, 150))  # 冰箱
        pygame.draw.rect(screen, (150, 150, 150), (100, 200, 150, 120))  # 炉灶
        pygame.draw.rect(screen, (100, 150, 200), (550, 220, 180, 100))  # 水池
        
        title = self.large_font.render("厨房", True, WHITE)
        screen.blit(title, (350, 20))
        
        self.draw_button(300, 320, 150, 50, "打开冰箱")
        self.draw_button(100, 350, 150, 50, "检查炉灶")
        self.draw_button(550, 350, 180, 50, "查看花瓶")
        self.draw_button(250, 420, 150, 50, "回客厅")
        
        if "kitchen_key" in self.inventory and "safe_open" in self.puzzles_solved and "secret" in self.inventory:
            self.draw_button(450, 420, 150, 50, "逃脱！")

    def draw_button(self, x, y, w, h, text):
        pygame.draw.rect(screen, (60, 80, 100), (x, y, w, h), border_radius=5)
        pygame.draw.rect(screen, BLUE, (x, y, w, h), 2, border_radius=5)
        text_surf = self.font.render(text, True, WHITE)
        screen.blit(text_surf, (x + (w - text_surf.get_width()) // 2, y + 10))

    def handle_click(self, pos):
        if self.room == 0:
            if self.button_clicked(pos, 50, 200, 150, 50):
                self.message = "日记最后一页写着：'真相藏在画中，数字是3-1-4'。"
                self.puzzles_solved.add("diary_key")
            elif self.button_clicked(pos, 400, 300, 200, 50):
                if "diary_key" in self.puzzles_solved:
                    self.message = "你在画框背面发现了一个暗格，里面有一张纸条写着'保险柜密码是314'，还有一把神秘的钥匙！"
                    self.inventory.add("secret")
                    self.inventory.add("code_314")
                else:
                    self.message = "一幅奇怪的风景画，但似乎没有什么特别的。"
            elif self.button_clicked(pos, 250, 420, 150, 50):
                self.room = 1
                self.message = "你来到了客厅。"
            elif self.button_clicked(pos, 550, 420, 150, 50) and "secret" in self.inventory:
                self.message = "这把钥匙很特别，似乎能打开某个重要的东西..."
        elif self.room == 1:
            if self.button_clicked(pos, 200, 300, 150, 50):
                if "sofa_checked" not in self.puzzles_solved:
                    self.message = "你在沙发底下发现了一把小钥匙！"
                    self.inventory.add("sofa_key")
                    self.puzzles_solved.add("sofa_checked")
                else:
                    self.message = "这里已经没有其他东西了。"
            elif self.button_clicked(pos, 100, 400, 150, 50):
                if "safe_open" not in self.puzzles_solved:
                    if "code_314" in self.inventory:
                        self.message = "你输入密码314，保险柜打开了！里面是厨房的钥匙！"
                        self.inventory.add("kitchen_key")
                        self.puzzles_solved.add("safe_open")
                    else:
                        self.message = "保险柜需要密码才能打开。也许线索在其他地方？"
                else:
                    self.message = "保险柜已经空了。"
            elif self.button_clicked(pos, 500, 400, 150, 50):
                self.room = 0
                self.message = "你回到了书房。"
            elif self.button_clicked(pos, 650, 400, 130, 50):
                if "kitchen_key" in self.inventory:
                    self.room = 2
                    self.message = "你用厨房钥匙打开了门，进入了厨房。"
                else:
                    self.message = "门被锁住了。"
        elif self.room == 2:
            if self.button_clicked(pos, 300, 320, 150, 50):
                if "fridge_checked" not in self.puzzles_solved:
                    self.message = "冰箱里有一张纸条：'花瓶中藏着最后的真相'。"
                    self.puzzles_solved.add("fridge_checked")
                else:
                    self.message = "冰箱里只有一些过期食物。"
            elif self.button_clicked(pos, 100, 350, 150, 50):
                if "stove_checked" not in self.puzzles_solved:
                    self.message = "炉灶上有一把精致的钥匙，上面刻着'EXIT'字样。"
                    self.inventory.add("exit_key")
                    self.puzzles_solved.add("stove_checked")
                else:
                    self.message = "这里已经没什么可看的了。"
            elif self.button_clicked(pos, 550, 350, 180, 50):
                if "vase_checked" not in self.puzzles_solved:
                    self.message = "你在花瓶里发现了一个按钮，按下去后，一扇隐藏的门出现了！"
                    self.puzzles_solved.add("vase_checked")
                else:
                    self.message = "花瓶里只剩下枯萎的花了。"
            elif self.button_clicked(pos, 250, 420, 150, 50):
                self.room = 1
                self.message = "你回到了客厅。"
            elif self.button_clicked(pos, 450, 420, 150, 50):
                self.message = "恭喜！你成功逃出了神秘房间！"
                pygame.time.wait(2000)
                self.__init__()

    def button_clicked(self, pos, x, y, w, h):
        return x <= pos[0] <= x + w and y <= pos[1] <= y + h

game = EscapeRoom()
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            game.handle_click(pygame.mouse.get_pos())
    
    game.draw()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
