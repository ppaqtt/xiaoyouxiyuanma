import pygame
import random

pygame.init()

WIDTH, HEIGHT = 800, 600

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
BLUE = (0, 100, 200)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
PURPLE = (128, 0, 128)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("自动点击器大师")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
big_font = pygame.font.Font(None, 60)
small_font = pygame.font.Font(None, 24)

class AutoClicker:
    def __init__(self):
        self.gold = 0
        self.total_gold = 0
        self.click_power = 1
        self.gold_per_second = 0
        self.upgrades = {
            'click_power': {'cost': 10, 'bonus': 1, 'name': '点击力', 'owned': 0},
            'auto_clicker': {'cost': 50, 'bonus': 1, 'name': '自动点击器', 'owned': 0},
            'click_multiplier': {'cost': 200, 'bonus': 2, 'name': '点击倍率', 'owned': 0},
            'golden_touch': {'cost': 500, 'bonus': 5, 'name': '黄金之触', 'owned': 0},
            'money_printer': {'cost': 1000, 'bonus': 10, 'name': '印钞机', 'owned': 0},
        }
        self.achievements = []
        self.unlocked_achievements = []
        
        self.click_count = 0
        self.total_clicks = 0
        
        self.milestones = [100, 500, 1000, 5000, 10000, 50000, 100000, 500000, 1000000]
        self.milestone_idx = 0
    
    def click(self):
        gold_earned = self.click_power * (1 + self.upgrades['click_multiplier']['owned'])
        self.gold += gold_earned
        self.total_gold += gold_earned
        self.click_count += 1
        self.total_clicks += 1
        
        self.check_achievements()
    
    def buy_upgrade(self, upgrade_type):
        upgrade = self.upgrades[upgrade_type]
        cost = int(upgrade['cost'] * (1.15 ** upgrade['owned']))
        
        if self.gold >= cost:
            self.gold -= cost
            upgrade['owned'] += 1
            
            if upgrade_type == 'click_power':
                self.click_power += upgrade['bonus']
            elif upgrade_type == 'auto_clicker':
                self.gold_per_second += upgrade['bonus']
            elif upgrade_type == 'golden_touch':
                self.click_power += upgrade['bonus']
            
            return True
        return False
    
    def check_achievements(self):
        new_achievements = []
        
        if self.total_clicks >= 100 and "点击100次" not in self.unlocked_achievements:
            new_achievements.append("点击100次")
        if self.total_clicks >= 1000 and "点击1000次" not in self.unlocked_achievements:
            new_achievements.append("点击1000次")
        if self.total_gold >= 10000 and "累积10000金币" not in self.unlocked_achievements:
            new_achievements.append("累积10000金币")
        if self.total_gold >= 100000 and "累积100000金币" not in self.unlocked_achievements:
            new_achievements.append("累积100000金币")
        
        for ach in new_achievements:
            if ach not in self.unlocked_achievements:
                self.unlocked_achievements.append(ach)
                self.achievements.append(ach)
        
        while self.milestone_idx < len(self.milestones):
            if self.total_gold >= self.milestones[self.milestone_idx]:
                self.milestone_idx += 1
            else:
                break
    
    def update(self):
        self.gold += self.gold_per_second / 60
        self.total_gold += self.gold_per_second / 60
        self.check_achievements()

def format_number(num):
    if num >= 1000000:
        return f"{num/1000000:.2f}M"
    elif num >= 1000:
        return f"{num/1000:.2f}K"
    return f"{int(num)}"

def auto_clicker_game():
    game = AutoClicker()
    
    click_x, click_y = WIDTH // 4, HEIGHT // 2
    button_radius = 80
    click_effects = []
    
    while True:
        screen.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                dist = ((mx - click_x)**2 + (my - click_y)**2)**0.5
                if dist < button_radius:
                    game.click()
                    click_effects.append({'x': mx, 'y': my, 'life': 30, 'text': f"+{format_number(game.click_power * (1 + game.upgrades['click_multiplier']['owned']))}"})
        
        game.update()
        
        for effect in click_effects[:]:
            effect['life'] -= 1
            if effect['life'] <= 0:
                click_effects.remove(effect)
        
        pygame.draw.circle(screen, YELLOW, (click_x, click_y), button_radius)
        pygame.draw.circle(screen, WHITE, (click_x, click_y), button_radius, 4)
        
        click_text = big_font.render("点击!", True, BLACK)
        screen.blit(click_text, (click_x - click_text.get_width() // 2, 
                                 click_y - click_text.get_height() // 2))
        
        for effect in click_effects:
            alpha = effect['life'] / 30
            text = font.render(effect['text'], True, (int(255 * alpha), int(255 * alpha), 0))
            screen.blit(text, (effect['x'], effect['y'] - (30 - effect['life'])))
        
        pygame.draw.rect(screen, (20, 20, 40), (0, 0, WIDTH, 80))
        
        gold_text = big_font.render(f"💰 {format_number(game.gold)}", True, YELLOW)
        screen.blit(gold_text, (10, 20))
        
        gps_text = font.render(f"+{format_number(game.gold_per_second)}/秒", True, GREEN)
        screen.blit(gps_text, (10, 65))
        
        total_text = font.render(f"总金币: {format_number(game.total_gold)}", True, WHITE)
        screen.blit(total_text, (250, 20))
        
        clicks_text = font.render(f"点击次数: {game.total_clicks}", True, WHITE)
        screen.blit(clicks_text, (250, 50))
        
        milestone_text = font.render(f"里程碑: {game.milestone_idx}/{len(game.milestones)}", True, PURPLE)
        screen.blit(milestone_text, (500, 35))
        
        pygame.draw.rect(screen, (20, 20, 40), (WIDTH - 320, 0, 320, HEIGHT))
        
        upgrade_title = font.render("升级:", True, WHITE)
        screen.blit(upgrade_title, (WIDTH - 310, 10))
        
        y_offset = 50
        for upgrade_type, upgrade in game.upgrades.items():
            cost = int(upgrade['cost'] * (1.15 ** upgrade['owned']))
            can_afford = game.gold >= cost
            
            color = GREEN if can_afford else RED
            text = f"{upgrade['name']} Lv.{upgrade['owned']}"
            cost_text = f"({format_number(cost)})"
            
            t = small_font.render(text, True, color)
            screen.blit(t, (WIDTH - 310, y_offset))
            
            c = small_font.render(cost_text, True, color)
            screen.blit(c, (WIDTH - 310, y_offset + 20))
            
            hint = small_font.render(f"按{list(game.upgrades.keys()).index(upgrade_type) + 1}", True, YELLOW)
            screen.blit(hint, (WIDTH - 100, y_offset + 5))
            
            y_offset += 55
        
        if game.achievements:
            ach = game.achievements[0]
            pygame.draw.rect(screen, PURPLE, (WIDTH // 4, HEIGHT - 100, WIDTH // 2, 60), border_radius=10)
            ach_text = big_font.render(f"🏆 成就解锁: {ach}!", True, YELLOW)
            screen.blit(ach_text, (WIDTH // 4 + 20, HEIGHT - 80))
        
        inst = small_font.render("1-5升级 | 点击按钮获得金币", True, WHITE)
        screen.blit(inst, (10, HEIGHT - 30))
        
        pygame.display.flip()
        clock.tick(60)
        
        if game.achievements and random.random() < 0.01:
            game.achievements.pop(0)

if __name__ == "__main__":
    auto_clicker_game()
