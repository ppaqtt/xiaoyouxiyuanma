import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("侦探事务所")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 255)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
GRAY = (100, 100, 100)
BROWN = (139, 90, 43)

class DetectiveGame:
    def __init__(self):
        self.clues = set()
        self.accused = None
        self.current_scene = "office"
        self.day = 1
        self.game_over = False
        self.victory = False
        self.font = pygame.font.Font(None, 32)
        self.large_font = pygame.font.Font(None, 48)
        self.message = "欢迎来到侦探事务所！有人报案称珠宝店被盗，请前往现场调查。"
        
        self.suspects = {
            "owner": "珠宝店老板 - 声称昨晚锁好店门后就回家了，有不在场证明。",
            "clerk": "店员小王 - 赌博欠了很多钱，最后一个离开店铺。",
            "guard": "保安 - 当班时声称一直在岗位，但监控有15分钟空白。"
        }
        
        self.clue_locations = {
            "scene": {
                "safe": {"name": "保险柜", "found": False, "text": "保险柜没有被撬动的痕迹，是正常打开的。"},
                "window": {"name": "窗户", "found": False, "text": "窗户完好，没有闯入迹象。"},
                "floor": {"name": "地板", "found": False, "text": "地板上有一组奇怪的脚印，似乎是高跟鞋。"}
            },
            "owner": {
                "desk": {"name": "办公桌", "found": False, "text": "办公桌上有一份保险单，保额很高。"},
                "safe": {"name": "家庭保险柜", "found": False, "text": "保险柜里有一些现金，但远不够偿还债务。"}
            },
            "clerk": {
                "room": {"name": "房间", "found": False, "text": "房间里有很多催债单，还有一张当票。"},
                "safe": {"name": "柜子", "found": False, "text": "柜子里藏着一些珠宝，与被盗物品描述一致！"}
            },
            "guard": {
                "lounge": {"name": "休息室", "found": False, "text": "休息室有咖啡杯，里面有安眠药残留。"},
                "log": {"name": "值班记录", "found": False, "text": "值班记录完整，但签名似乎是伪造的。"}
            }
        }

    def draw(self):
        screen.fill((40, 40, 50))
        
        if self.game_over:
            self.draw_ending()
            return
        
        self.draw_header()
        
        if self.current_scene == "office":
            self.draw_office()
        elif self.current_scene == "scene":
            self.draw_scene()
        elif self.current_scene in ["owner", "clerk", "guard"]:
            self.draw_interrogation()
        
        self.draw_footer()

    def draw_header(self):
        pygame.draw.rect(screen, (30, 30, 40), (0, 0, 800, 80))
        pygame.draw.rect(screen, BLACK, (0, 0, 800, 80), 2)
        
        title = self.large_font.render("侦探事务所", True, (200, 180, 120))
        screen.blit(title, (300, 20))
        
        day_text = self.font.render(f"第 {self.day} 天", True, WHITE)
        screen.blit(day_text, (50, 25))
        
        clue_count = len(self.clues)
        clue_text = self.font.render(f"线索: {clue_count}/10", True, WHITE)
        screen.blit(clue_text, (650, 25))

    def draw_office(self):
        pygame.draw.rect(screen, (80, 60, 40), (200, 300, 400, 200))
        
        self.draw_button(100, 200, 200, 50, "去现场调查")
        self.draw_button(350, 200, 200, 50, "询问嫌疑人")
        
        if self.day > 1:
            self.draw_button(200, 280, 400, 50, "推理真相")

    def draw_scene(self):
        pygame.draw.rect(screen, (120, 100, 80), (100, 200, 600, 250))
        
        self.draw_clue_button(150, 220, 150, 40, "scene", "safe")
        self.draw_clue_button(350, 220, 150, 40, "scene", "window")
        self.draw_clue_button(500, 220, 150, 40, "scene", "floor")
        
        self.draw_button(300, 400, 200, 50, "回办公室")

    def draw_interrogation(self):
        pygame.draw.rect(screen, (150, 130, 110), (100, 150, 600, 300))
        
        self.draw_button(150, 170, 500, 40, f"询问 {self.suspect_name()}")
        
        suspect_desc = self.suspects[self.current_scene]
        desc_lines = self.wrap_text(suspect_desc, 500)
        y = 230
        for line in desc_lines:
            screen.blit(line, (150, y))
            y += 25
        
        locations = self.clue_locations[self.current_scene]
        y = 320
        for key, clue in locations.items():
            self.draw_clue_button(150, y, 500, 35, self.current_scene, key)
            y += 45
        
        self.draw_button(300, 400, 200, 50, "回办公室")

    def draw_clue_button(self, x, y, w, h, scene, key):
        clue = self.clue_locations[scene][key]
        color = GREEN if f"{scene}_{key}" in self.clues else (80, 80, 100)
        pygame.draw.rect(screen, color, (x, y, w, h), border_radius=5)
        pygame.draw.rect(screen, BLACK, (x, y, w, h), 2, border_radius=5)
        text = self.font.render(clue["name"] + (" ✓" if f"{scene}_{key}" in self.clues else ""), True, WHITE)
        screen.blit(text, (x + 10, y + 5))

    def draw_footer(self):
        pygame.draw.rect(screen, (50, 50, 60), (0, 500, 800, 100))
        pygame.draw.rect(screen, BLACK, (0, 500, 800, 100), 2)
        
        msg_lines = self.wrap_text(self.message, 750)
        y = 510
        for line in msg_lines:
            screen.blit(line, (25, y))
            y += 25

    def draw_ending(self):
        screen.fill(BLACK if not self.victory else (0, 50, 0))
        if self.victory:
            title = self.large_font.render("案件告破！", True, GREEN)
            desc = self.font.render("你成功找到了真正的窃贼 - 店员小王！", True, WHITE)
        else:
            title = self.large_font.render("错了！", True, RED)
            desc = self.font.render("你指认错了嫌疑人，真凶逍遥法外。", True, WHITE)
        
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 200))
        screen.blit(desc, (WIDTH//2 - desc.get_width()//2, 280))
        
        self.draw_button(300, 400, 200, 50, "重新开始")

    def draw_button(self, x, y, w, h, text):
        pygame.draw.rect(screen, (60, 80, 120), (x, y, w, h), border_radius=5)
        pygame.draw.rect(screen, BLUE, (x, y, w, h), 2, border_radius=5)
        text_surf = self.font.render(text, True, WHITE)
        screen.blit(text_surf, (x + (w - text_surf.get_width()) // 2, y + 10))

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

    def suspect_name(self):
        return {"owner": "店老板", "clerk": "店员小王", "guard": "保安"}[self.current_scene]

    def handle_click(self, pos):
        if self.game_over:
            if self.button_clicked(pos, 300, 400, 200, 50):
                self.__init__()
            return
        
        if self.current_scene == "office":
            if self.button_clicked(pos, 100, 200, 200, 50):
                self.current_scene = "scene"
                self.message = "你来到了珠宝店现场，仔细调查每一个角落！"
            elif self.button_clicked(pos, 350, 200, 200, 50):
                self.choose_suspect()
            elif self.day > 1 and self.button_clicked(pos, 200, 280, 400, 50):
                self.accuse()
        elif self.current_scene == "scene":
            for key in self.clue_locations["scene"]:
                if self.button_clicked(pos, 150, 220 + list(self.clue_locations["scene"].keys()).index(key) * 60, 150, 40):
                    self.find_clue("scene", key)
            if self.button_clicked(pos, 300, 400, 200, 50):
                self.current_scene = "office"
        elif self.current_scene in ["owner", "clerk", "guard"]:
            locations = self.clue_locations[self.current_scene]
            for key in locations:
                if self.button_clicked(pos, 150, 320 + list(locations.keys()).index(key) * 45, 500, 35):
                    self.find_clue(self.current_scene, key)
            if self.button_clicked(pos, 300, 400, 200, 50):
                self.current_scene = "office"

    def button_clicked(self, pos, x, y, w, h):
        return x <= pos[0] <= x + w and y <= pos[1] <= y + h

    def find_clue(self, scene, key):
        clue_id = f"{scene}_{key}"
        if clue_id not in self.clues:
            self.clues.add(clue_id)
            self.message = self.clue_locations[scene][key]["text"]
            if len(self.clues) in [3, 6, 9]:
                self.day += 1
                self.message += f" 第 {self.day} 天开始了。"

    def choose_suspect(self):
        self.message = "请选择要询问的嫌疑人，或者先去办公室。"
        pygame.draw.rect(screen, (50, 50, 70), (150, 150, 500, 300), border_radius=10)
        pygame.draw.rect(screen, BLACK, (150, 150, 500, 300), 2, border_radius=10)
        
        self.draw_button(250, 180, 300, 50, "询问店老板")
        self.draw_button(250, 260, 300, 50, "询问店员小王")
        self.draw_button(250, 340, 300, 50, "询问保安")
        self.draw_button(250, 420, 300, 50, "返回")
        
        pygame.display.flip()
        
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if self.button_clicked(pos, 250, 180, 300, 50):
                        self.current_scene = "owner"
                        self.message = "你现在在询问珠宝店老板。"
                        waiting = False
                    elif self.button_clicked(pos, 250, 260, 300, 50):
                        self.current_scene = "clerk"
                        self.message = "你现在在询问店员小王。"
                        waiting = False
                    elif self.button_clicked(pos, 250, 340, 300, 50):
                        self.current_scene = "guard"
                        self.message = "你现在在询问保安。"
                        waiting = False
                    elif self.button_clicked(pos, 250, 420, 300, 50):
                        waiting = False

    def accuse(self):
        self.message = "根据收集到的线索，你认为谁是罪犯？"
        pygame.draw.rect(screen, (50, 50, 70), (150, 150, 500, 300), border_radius=10)
        pygame.draw.rect(screen, BLACK, (150, 150, 500, 300), 2, border_radius=10)
        
        self.draw_button(250, 180, 300, 50, "店老板")
        self.draw_button(250, 260, 300, 50, "店员小王")
        self.draw_button(250, 340, 300, 50, "保安")
        self.draw_button(250, 420, 300, 50, "取消")
        
        pygame.display.flip()
        
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if self.button_clicked(pos, 250, 260, 300, 50):
                        self.victory = True
                        self.game_over = True
                        waiting = False
                    elif self.button_clicked(pos, 250, 180, 300, 50) or self.button_clicked(pos, 250, 340, 300, 50):
                        self.victory = False
                        self.game_over = True
                        waiting = False
                    elif self.button_clicked(pos, 250, 420, 300, 50):
                        waiting = False

game = DetectiveGame()
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
