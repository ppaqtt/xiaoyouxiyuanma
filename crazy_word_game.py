"""
疯狂猜词游戏
玩家需要根据提示猜测词语，支持双人模式
"""

import pygame
import random
import sys

pygame.init()

WIDTH, HEIGHT = 900, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("疯狂猜词 🎭")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
DARK_GRAY = (60, 60, 60)
GREEN = (76, 175, 80)
RED = (244, 67, 54)
BLUE = (33, 150, 243)
ORANGE = (255, 152, 0)
PURPLE = (156, 39, 176)
YELLOW = (255, 235, 59)

CATEGORIES = {
    "水果": ["苹果", "香蕉", "橙子", "葡萄", "西瓜", "草莓", "芒果", "猕猴桃", "桃子", "梨", "菠萝", "樱桃", "蓝莓", "柚子", "火龙果"],
    "动物": ["老虎", "狮子", "大象", "熊猫", "猴子", "兔子", "狐狸", "狼", "熊", "豹子", "长颈鹿", "斑马", "犀牛", "河马", "鳄鱼"],
    "职业": ["医生", "教师", "警察", "厨师", "护士", "司机", "飞行员", "律师", "建筑师", "工程师", "画家", "歌手", "作家", "运动员", "科学家"],
    "运动": ["足球", "篮球", "网球", "乒乓球", "羽毛球", "游泳", "跑步", "跳远", "滑雪", "滑冰", "拳击", "摔跤", "射箭", "帆船", "攀岩"],
    "食物": ["面条", "饺子", "包子", "披萨", "汉堡", "寿司", "牛排", "烤鸭", "火锅", "烧烤", "沙拉", "汤圆", "粽子", "月饼", "冰淇淋"],
    "交通工具": ["汽车", "火车", "飞机", "轮船", "地铁", "公交", "摩托", "单车", "卡车", "救护车", "消防车", "出租车", "直升机", "潜艇", "热气球"],
    "国家": ["中国", "美国", "日本", "韩国", "英国", "法国", "德国", "俄罗斯", "印度", "巴西", "澳大利亚", "加拿大", "意大利", "西班牙", "墨西哥"],
    "电影": ["喜剧", "动作", "爱情", "恐怖", "科幻", "动画", "悬疑", "战争", "纪录", "奇幻", "冒险", "家庭", "音乐", "历史", "西部"],
    "自然": ["太阳", "月亮", "星星", "云", "雨", "雪", "风", "雷", "彩虹", "火山", "海洋", "河流", "森林", "沙漠", "草原"],
    "颜色": ["红色", "蓝色", "绿色", "黄色", "紫色", "橙色", "粉色", "黑色", "白色", "棕色", "灰色", "金色", "银色", "青色", "玫红"]
}

class Game:
    def __init__(self):
        self.round = 1
        self.max_rounds = 5
        self.current_team = 1
        self.team1_score = 0
        self.team2_score = 0
        self.current_word = ""
        self.current_category = ""
        self.used_words = set()
        self.time_left = 60
        self.last_tick = 0
        self.phase = "menu"
        self.guessed_words = []
        self.wrong_guesses = 0
        self.round_over = False
        self.round_result = ""
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 36)
        self.font_tiny = pygame.font.Font(None, 28)
        
    def get_new_word(self):
        available_cats = list(CATEGORIES.keys())
        while True:
            cat = random.choice(available_cats)
            words = CATEGORIES[cat]
            word = random.choice(words)
            if word not in self.used_words:
                self.used_words.add(word)
                return word, cat
    
    def start_round(self):
        self.current_word, self.current_category = self.get_new_word()
        self.time_left = 60
        self.last_tick = pygame.time.get_ticks()
        self.guessed_words = []
        self.wrong_guesses = 0
        self.round_over = False
        self.phase = "playing"
    
    def update(self):
        if self.phase == "playing":
            current_tick = pygame.time.get_ticks()
            if current_tick - self.last_tick >= 1000:
                self.time_left -= 1
                self.last_tick = current_tick
                if self.time_left <= 0:
                    self.end_round()
        
        if self.phase == "round_result":
            if pygame.time.get_ticks() - self.result_time >= 3000:
                if self.round >= self.max_rounds:
                    self.phase = "game_over"
                else:
                    self.round += 1
                    self.current_team = 2 if self.current_team == 1 else 1
                    self.start_round()
    
    def guess_word(self, correct):
        if correct:
            self.guessed_words.append(self.current_word)
            self.current_word, self.current_category = self.get_new_word()
        else:
            self.wrong_guesses += 1
            if self.wrong_guesses >= 3:
                self.end_round()
    
    def end_round(self):
        self.round_result = f"本轮猜中: {len(self.guessed_words)}个词"
        if self.current_team == 1:
            self.team1_score += len(self.guessed_words)
        else:
            self.team2_score += len(self.guessed_words)
        self.phase = "round_result"
        self.result_time = pygame.time.get_ticks()
    
    def draw(self):
        screen.fill(WHITE)
        
        if self.phase == "menu":
            self.draw_menu()
        elif self.phase == "setup":
            self.draw_setup()
        elif self.phase == "playing":
            self.draw_playing()
        elif self.phase == "round_result":
            self.draw_round_result()
        elif self.phase == "game_over":
            self.draw_game_over()
        
        pygame.display.flip()
    
    def draw_menu(self):
        title = self.font_large.render("🎭 疯狂猜词 🎭", True, PURPLE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        
        instructions = [
            "游戏规则:",
            "• 两人轮流进行",
            "• 描述者说出词语，其他队员猜",
            "• 60秒内猜对越多得分越高",
            "• 错误3次自动结束本轮",
            "",
            "按 空格键 开始游戏"
        ]
        
        y = 220
        for line in instructions:
            text = self.font_small.render(line, True, DARK_GRAY)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, y))
            y += 40
    
    def draw_setup(self):
        title = self.font_large.render("游戏设置", True, PURPLE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))
        
        info = [
            f"回合数: {self.max_rounds}",
            "",
            "↑/↓ 调整回合数",
            "",
            "按 空格键 开始游戏"
        ]
        
        y = 200
        for line in info:
            text = self.font_small.render(line, True, DARK_GRAY)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, y))
            y += 50
        
        team1 = self.font_medium.render(f"队伍1得分: {self.team1_score}", True, BLUE)
        team2 = self.font_medium.render(f"队伍2得分: {self.team2_score}", True, ORANGE)
        screen.blit(team1, (WIDTH//2 - 150, 450))
        screen.blit(team2, (WIDTH//2 - 150, 500))
    
    def draw_playing(self):
        header = f"第 {self.round}/{self.max_rounds} 回合 - 队伍 {self.current_team}"
        title = self.font_large.render(header, True, DARK_GRAY)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 30))
        
        timer_color = GREEN if self.time_left > 15 else (ORANGE if self.time_left > 5 else RED)
        timer = self.font_large.render(f"⏱ {self.time_left}", True, timer_color)
        screen.blit(timer, (WIDTH//2 - timer.get_width()//2, 80))
        
        cat_text = self.font_medium.render(f"类别: {self.current_category}", True, BLUE)
        screen.blit(cat_text, (WIDTH//2 - cat_text.get_width()//2, 160))
        
        word_box = pygame.Rect(WIDTH//2 - 200, 230, 400, 100)
        pygame.draw.rect(screen, PURPLE, word_box, border_radius=15)
        word_text = self.font_large.render(self.current_word, True, WHITE)
        screen.blit(word_text, (WIDTH//2 - word_text.get_width()//2, 255))
        
        guesses = self.font_small.render(f"已猜中: {len(self.guessed_words)} 个", True, GREEN)
        screen.blit(guesses, (WIDTH//2 - guesses.get_width()//2, 350))
        
        wrong = self.font_small.render(f"错误次数: {self.wrong_guesses}/3", True, RED)
        screen.blit(wrong, (WIDTH//2 - wrong.get_width()//2, 390))
        
        if self.guessed_words:
            guessed_text = self.font_tiny.render("已猜词语: " + " ".join(self.guessed_words), True, GRAY)
            screen.blit(guessed_text, (WIDTH//2 - guessed_text.get_width()//2, 430))
        
        instructions = self.font_small.render("←猜对 | →猜错 | 空格-结束本轮", True, DARK_GRAY)
        screen.blit(instructions, (WIDTH//2 - instructions.get_width()//2, 580))
    
    def draw_round_result(self):
        title = self.font_large.render("本轮结束!", True, GREEN)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 200))
        
        result = self.font_medium.render(self.round_result, True, DARK_GRAY)
        screen.blit(result, (WIDTH//2 - result.get_width()//2, 300))
        
        team1 = self.font_medium.render(f"队伍1: {self.team1_score}分", True, BLUE)
        team2 = self.font_medium.render(f"队伍2: {self.team2_score}分", True, ORANGE)
        screen.blit(team1, (WIDTH//2 - 100, 380))
        screen.blit(team2, (WIDTH//2 - 100, 440))
        
        next_text = self.font_small.render("下一轮准备中...", True, GRAY)
        screen.blit(next_text, (WIDTH//2 - next_text.get_width()//2, 520))
    
    def draw_game_over(self):
        title = self.font_large.render("🏆 游戏结束! 🏆", True, YELLOW)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 150))
        
        if self.team1_score > self.team2_score:
            winner = "队伍1 获胜!"
            winner_color = BLUE
        elif self.team2_score > self.team1_score:
            winner = "队伍2 获胜!"
            winner_color = ORANGE
        else:
            winner = "平局!"
            winner_color = PURPLE
        
        winner_text = self.font_large.render(winner, True, winner_color)
        screen.blit(winner_text, (WIDTH//2 - winner_text.get_width()//2, 280))
        
        team1 = self.font_medium.render(f"队伍1: {self.team1_score}分", True, BLUE)
        team2 = self.font_medium.render(f"队伍2: {self.team2_score}分", True, ORANGE)
        screen.blit(team1, (WIDTH//2 - 100, 370))
        screen.blit(team2, (WIDTH//2 - 100, 430))
        
        restart = self.font_small.render("按 R 重新开始 | ESC 返回主菜单", True, DARK_GRAY)
        screen.blit(restart, (WIDTH//2 - restart.get_width()//2, 550))
    
    def handle_key(self, key):
        if self.phase == "menu":
            if key == pygame.K_SPACE:
                self.phase = "setup"
        
        elif self.phase == "setup":
            if key in (pygame.K_UP, pygame.K_DOWN):
                self.max_rounds = max(1, min(10, self.max_rounds + (1 if key == pygame.K_UP else -1)))
            elif key == pygame.K_SPACE:
                self.start_round()
        
        elif self.phase == "playing":
            if key == pygame.K_LEFT:
                self.guess_word(True)
            elif key == pygame.K_RIGHT:
                self.guess_word(False)
            elif key == pygame.K_SPACE:
                self.end_round()
        
        elif self.phase == "game_over":
            if key == pygame.K_r:
                self.__init__()
                self.phase = "menu"
            elif key == pygame.K_ESCAPE:
                self.__init__()

def main():
    game = Game()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game.phase in ("playing", "round_result"):
                        game.__init__()
                        game.phase = "menu"
                    else:
                        running = False
                else:
                    game.handle_key(event.key)
        
        game.update()
        game.draw()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
