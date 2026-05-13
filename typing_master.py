"""
打字大师 - 高级打字练习游戏
操作说明：
- 输入屏幕上掉落的单词来消除它们
- 单词掉到底部会失去一条生命
- 连续正确输入可积累连击加分
- 难度会随时间递增（掉落速度加快，单词更长）
- 按ESC返回主菜单
"""

import pygame
import random
import sys
import time
import math

# 初始化pygame
pygame.init()

# 窗口设置
WIDTH, HEIGHT = 900, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("打字大师 - Typing Master")

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
DARK_GRAY = (80, 80, 80)
BG_COLOR = (20, 20, 40)
RED = (255, 80, 80)
GREEN = (80, 255, 120)
YELLOW = (255, 220, 60)
BLUE = (80, 160, 255)
CYAN = (80, 220, 255)
ORANGE = (255, 160, 60)
PURPLE = (180, 100, 255)

# 单词库（按难度分级）
WORDS_EASY = [
    "the", "and", "for", "are", "but", "not", "you", "all", "can", "her",
    "was", "one", "our", "out", "day", "get", "has", "him", "his", "how",
    "its", "may", "new", "now", "old", "see", "way", "who", "boy", "did",
    "cat", "dog", "run", "big", "red", "top", "fun", "sun", "map", "cup"
]

WORDS_MEDIUM = [
    "about", "after", "again", "begin", "being", "below", "cause", "could",
    "every", "first", "found", "great", "house", "large", "learn", "never",
    "other", "place", "plant", "point", "right", "small", "sound", "spell",
    "still", "study", "their", "there", "these", "thing", "think", "three",
    "water", "where", "which", "world", "would", "write", "young", "after",
    "apple", "brave", "cloud", "dream", "eagle", "flame", "grape", "heart"
]

WORDS_HARD = [
    "another", "because", "between", "country", "develop", "example",
    "feature", "general", "history", "however", "imagine", "include",
    "kitchen", "library", "machine", "natural", "obvious", "picture",
    "quality", "realize", "science", "thought", "through", "understand",
    "village", "weather", "without", "problem", "program", "provide",
    "service", "special", "balance", "chapter", "culture", "display",
    "element", "freedom", "gateway", "harvest", "improve", "journey"
]

# 字体
try:
    font_large = pygame.font.SysFont("simhei", 48)
    font_medium = pygame.font.SysFont("simhei", 28)
    font_small = pygame.font.SysFont("simhei", 20)
    font_word = pygame.font.SysFont("consolas", 26, bold=True)
    font_input = pygame.font.SysFont("consolas", 30, bold=True)
except:
    font_large = pygame.font.Font(None, 48)
    font_medium = pygame.font.Font(None, 28)
    font_small = pygame.font.Font(None, 20)
    font_word = pygame.font.Font(None, 26)
    font_input = pygame.font.Font(None, 30)


class FallingWord:
    """掉落的单词类"""
    def __init__(self, word, x, speed):
        self.word = word
        self.x = x
        self.y = -20
        self.speed = speed
        self.matched = 0  # 已匹配的字符数
        self.active = True
        self.color = random.choice([WHITE, CYAN, YELLOW, GREEN, ORANGE, PURPLE])
        # 消除动画
        self.exploding = False
        self.explode_timer = 0

    def update(self, dt):
        if self.exploding:
            self.explode_timer += dt
            if self.explode_timer > 500:
                self.active = False
            return
        self.y += self.speed * dt / 1000.0

    def draw(self, surface):
        if self.exploding:
            # 消除动画：放大并淡出
            alpha = max(0, 255 - int(self.explode_timer / 500 * 255))
            scale = 1.0 + self.explode_timer / 500 * 0.5
            text = font_word.render(self.word, True, GREEN)
            scaled = pygame.transform.scale(text,
                (int(text.get_width() * scale), int(text.get_height() * scale)))
            scaled.set_alpha(alpha)
            surface.blit(scaled, (self.x - scaled.get_width() // 2, self.y))
            return

        # 绘制单词
        for i, ch in enumerate(self.word):
            if i < self.matched:
                color = GREEN  # 已匹配的字符显示绿色
            else:
                color = self.color
            char_surf = font_word.render(ch, True, color)
            surface.blit(char_surf, (self.x + i * 18 - len(self.word) * 9, self.y))

        # 绘制下划线指示当前单词
        if self.matched > 0:
            line_w = len(self.word) * 18
            pygame.draw.line(surface, GREEN,
                (self.x - len(self.word) * 9, self.y + 28),
                (self.x - len(self.word) * 9 + line_w, self.y + 28), 2)


class Particle:
    """粒子效果"""
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(50, 200)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = random.uniform(0.3, 0.8)
        self.max_life = self.life
        self.size = random.randint(2, 5)

    def update(self, dt):
        self.x += self.vx * dt / 1000.0
        self.y += self.vy * dt / 1000.0
        self.vy += 200 * dt / 1000.0  # 粒子重力
        self.life -= dt / 1000.0

    def draw(self, surface):
        alpha = max(0, self.life / self.max_life)
        size = max(1, int(self.size * alpha))
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), size)


class Game:
    """游戏主类"""
    def __init__(self):
        self.state = "menu"  # menu, playing, gameover
        self.reset()

    def reset(self):
        self.words = []
        self.particles = []
        self.input_text = ""
        self.lives = 5
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.words_typed = 0
        self.start_time = 0
        self.game_time = 0
        self.spawn_timer = 0
        self.spawn_interval = 2000  # 毫秒
        self.difficulty = 1
        self.difficulty_timer = 0
        self.wpm = 0
        self.total_chars = 0
        self.current_target = None  # 当前锁定的单词

    def get_word_list(self):
        """根据难度获取单词列表"""
        if self.difficulty <= 3:
            return WORDS_EASY
        elif self.difficulty <= 6:
            return WORDS_MEDIUM + WORDS_EASY
        else:
            return WORDS_HARD + WORDS_MEDIUM

    def spawn_word(self):
        """生成新的掉落单词"""
        word_list = self.get_word_list()
        word = random.choice(word_list)
        # 避免重复
        existing = [w.word for w in self.words if not w.exploding]
        while word in existing and len(existing) < len(word_list):
            word = random.choice(word_list)

        # 随机x位置，确保不超出屏幕
        text_w = len(word) * 18
        x = random.randint(text_w // 2 + 20, WIDTH - text_w // 2 - 20)
        speed = 30 + self.difficulty * 5 + random.uniform(-5, 10)
        self.words.append(FallingWord(word, x, speed))

    def find_matching_word(self, text):
        """查找匹配输入的单词（优先选择y最大的，即最接近底部的）"""
        best = None
        best_y = -1
        for w in self.words:
            if w.exploding:
                continue
            if w.word.startswith(text) and len(text) > 0:
                if w.y > best_y:
                    best = w
                    best_y = w.y
        return best

    def update(self, dt):
        """更新游戏状态"""
        if self.state != "playing":
            return

        self.game_time += dt
        self.difficulty_timer += dt

        # 每15秒增加难度
        if self.difficulty_timer > 15000:
            self.difficulty += 1
            self.difficulty_timer = 0
            self.spawn_interval = max(600, self.spawn_interval - 150)

        # 生成新单词
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_word()
            self.spawn_timer = 0

        # 更新单词位置
        for word in self.words:
            word.update(dt)
            # 检查是否掉到底部
            if not word.exploding and word.y > HEIGHT - 60:
                word.active = False
                self.lives -= 1
                self.combo = 0
                # 如果当前锁定的是这个单词，取消锁定
                if self.current_target == word:
                    self.current_target = None
                    self.input_text = ""

        # 移除不活跃的单词
        self.words = [w for w in self.words if w.active]

        # 更新粒子
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.life > 0]

        # 更新匹配状态
        if self.input_text:
            target = self.find_matching_word(self.input_text)
            if target:
                self.current_target = target
                target.matched = len(self.input_text)
                # 检查是否完全匹配
                if self.input_text == target.word:
                    self.complete_word(target)
            else:
                # 没有匹配的单词，重置
                if self.current_target:
                    self.current_target.matched = 0
                self.current_target = None
        else:
            if self.current_target:
                self.current_target.matched = 0
            self.current_target = None

        # 计算WPM
        minutes = self.game_time / 60000.0
        if minutes > 0:
            self.wpm = int(self.words_typed / minutes)

        # 检查游戏结束
        if self.lives <= 0:
            self.state = "gameover"

    def complete_word(self, word):
        """完成一个单词"""
        word.exploding = True
        word.explode_timer = 0
        self.combo += 1
        self.max_combo = max(self.max_combo, self.combo)
        self.words_typed += 1
        self.total_chars += len(word.word)

        # 计算分数（连击加成）
        base_score = len(word.word) * 10
        combo_bonus = min(self.combo, 10)
        self.score += base_score * combo_bonus

        # 生成粒子效果
        for _ in range(15):
            self.particles.append(Particle(word.x, word.y, GREEN))

        self.input_text = ""
        self.current_target = None

    def draw(self):
        """绘制游戏画面"""
        screen.fill(BG_COLOR)

        if self.state == "menu":
            self.draw_menu()
        elif self.state == "playing":
            self.draw_game()
        elif self.state == "gameover":
            self.draw_gameover()

        pygame.display.flip()

    def draw_menu(self):
        """绘制主菜单"""
        # 标题
        title = font_large.render("打字大师", True, CYAN)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 150))

        subtitle = font_medium.render("Typing Master", True, GRAY)
        screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, 210))

        # 操作说明
        instructions = [
            "游戏规则：",
            "单词从屏幕上方掉落",
            "输入正确的单词来消除它们",
            "单词掉到底部会失去生命",
            "连续正确输入获得连击加分",
            "难度会随时间递增",
            "",
            "按 ENTER 开始游戏",
            "按 ESC 退出"
        ]
        for i, text in enumerate(instructions):
            color = YELLOW if i == 0 else WHITE
            surf = font_small.render(text, True, color)
            screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, 300 + i * 35))

    def draw_game(self):
        """绘制游戏画面"""
        # 绘制底部危险线
        pygame.draw.line(screen, RED, (0, HEIGHT - 60), (WIDTH, HEIGHT - 60), 2)
        danger_text = font_small.render("DANGER ZONE", True, (100, 30, 30))
        screen.blit(danger_text, (WIDTH // 2 - danger_text.get_width() // 2, HEIGHT - 50))

        # 绘制掉落的单词
        for word in self.words:
            word.draw(screen)

        # 绘制粒子
        for p in self.particles:
            p.draw(screen)

        # 绘制输入框
        input_rect = pygame.Rect(WIDTH // 2 - 200, HEIGHT - 110, 400, 40)
        pygame.draw.rect(screen, (40, 40, 60), input_rect, border_radius=5)
        pygame.draw.rect(screen, CYAN, input_rect, 2, border_radius=5)

        input_surf = font_input.render(self.input_text + "|", True, WHITE)
        screen.blit(input_surf, (input_rect.x + 10, input_rect.y + 5))

        # 绘制HUD
        self.draw_hud()

    def draw_hud(self):
        """绘制游戏信息"""
        # 分数
        score_text = font_medium.render(f"分数: {self.score}", True, WHITE)
        screen.blit(score_text, (20, 10))

        # WPM
        wpm_text = font_small.render(f"WPM: {self.wpm}", True, YELLOW)
        screen.blit(wpm_text, (20, 45))

        # 连击
        if self.combo > 1:
            combo_text = font_medium.render(f"连击 x{self.combo}", True, ORANGE)
            screen.blit(combo_text, (WIDTH // 2 - combo_text.get_width() // 2, 10))

        # 生命值
        lives_text = font_medium.render("生命: ", True, WHITE)
        screen.blit(lives_text, (WIDTH - 250, 10))
        for i in range(self.lives):
            pygame.draw.circle(screen, RED, (WIDTH - 250 + 80 + i * 30, 25), 10)
            pygame.draw.circle(screen, (255, 150, 150), (WIDTH - 250 + 78 + i * 30, 22), 4)

        # 难度等级
        diff_text = font_small.render(f"难度: {self.difficulty}", True, PURPLE)
        screen.blit(diff_text, (WIDTH - 120, 45))

        # 已输入单词数
        typed_text = font_small.render(f"已消除: {self.words_typed}", True, GREEN)
        screen.blit(typed_text, (20, 70))

    def draw_gameover(self):
        """绘制游戏结束画面"""
        # 半透明背景
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(180)
        screen.blit(overlay, (0, 0))

        # 游戏结束标题
        title = font_large.render("游戏结束", True, RED)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 120))

        # 统计信息
        stats = [
            f"最终分数: {self.score}",
            f"打字速度: {self.wpm} WPM",
            f"消除单词: {self.words_typed}",
            f"最大连击: {self.max_combo}",
            f"最终难度: {self.difficulty}",
        ]
        for i, text in enumerate(stats):
            surf = font_medium.render(text, True, WHITE)
            screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, 220 + i * 45))

        # 重新开始提示
        restart = font_medium.render("按 ENTER 重新开始", True, YELLOW)
        screen.blit(restart, (WIDTH // 2 - restart.get_width() // 2, 500))

        back = font_small.render("按 ESC 返回菜单", True, GRAY)
        screen.blit(back, (WIDTH // 2 - back.get_width() // 2, 550))


def main():
    game = Game()
    clock = pygame.time.Clock()

    while True:
        dt = clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game.state == "playing":
                        game.state = "menu"
                        game.reset()
                    elif game.state == "gameover":
                        game.state = "menu"
                        game.reset()
                    else:
                        pygame.quit()
                        sys.exit()

                elif event.key == pygame.K_RETURN:
                    if game.state == "menu":
                        game.reset()
                        game.state = "playing"
                        game.start_time = time.time()
                    elif game.state == "gameover":
                        game.reset()
                        game.state = "playing"
                        game.start_time = time.time()

                elif game.state == "playing":
                    if event.key == pygame.K_BACKSPACE:
                        if game.input_text:
                            game.input_text = game.input_text[:-1]
                    elif event.unicode.isalpha():
                        game.input_text += event.unicode.lower()

        game.update(dt)
        game.draw()


if __name__ == "__main__":
    main()
