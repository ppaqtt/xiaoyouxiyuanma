import pygame
import random

pygame.init()

WIDTH, HEIGHT = 900, 700

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 200, 0)
BLUE = (0, 100, 200)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("知识问答比赛")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 32)
big_font = pygame.font.Font(None, 50)
small_font = pygame.font.Font(None, 24)

QUESTIONS = [
    {"q": "中国的首都是?", "a": ["北京", "上海", "广州", "深圳"], "c": 0, "cat": "地理"},
    {"q": "1+1等于?", "a": ["2", "3", "1", "0"], "c": 0, "cat": "数学"},
    {"q": "地球是什么形状?", "a": ["圆形", "方形", "三角形", "平形"], "c": 0, "cat": "科学"},
    {"q": "一年有多少个月?", "a": ["12", "10", "14", "11"], "c": 0, "cat": "常识"},
    {"q": "水的化学式是?", "a": ["H2O", "CO2", "O2", "H2"], "c": 0, "cat": "科学"},
    {"q": "中国的第一条河流是?", "a": ["长江", "黄河", "珠江", "淮河"], "c": 1, "cat": "地理"},
    {"q": "2乘以5等于?", "a": ["8", "10", "12", "15"], "c": 1, "cat": "数学"},
    {"q": "太阳是什么颜色?", "a": ["红色", "黄色", "蓝色", "绿色"], "c": 1, "cat": "科学"},
    {"q": "世界上最高的山是?", "a": ["珠穆朗玛峰", "乔戈里峰", "干城章嘉峰", "洛子峰"], "c": 0, "cat": "地理"},
    {"q": "5加3等于?", "a": ["7", "8", "9", "6"], "c": 1, "cat": "数学"},
    {"q": "人体最大的器官是?", "a": ["皮肤", "心脏", "肝脏", "肺"], "c": 0, "cat": "科学"},
    {"q": "中国有多少个省份?", "a": ["23", "25", "22", "24"], "c": 0, "cat": "地理"},
    {"q": "10除以2等于?", "a": ["4", "5", "6", "3"], "c": 1, "cat": "数学"},
    {"q": "月球是什么?", "a": ["地球的卫星", "行星", "恒星", "流星"], "c": 0, "cat": "科学"},
    {"q": "世界上最长的河流是?", "a": ["尼罗河", "长江", "亚马逊河", "密西西比河"], "c": 0, "cat": "地理"},
    {"q": "8乘以7等于?", "a": ["54", "56", "58", "52"], "c": 1, "cat": "数学"},
    {"q": "人体有多少块骨头?", "a": ["206", "208", "200", "210"], "c": 0, "cat": "科学"},
    {"q": "中国的最高峰是?", "a": ["珠穆朗玛峰", "乔戈里峰", "干城章嘉峰", "希夏邦马峰"], "c": 0, "cat": "地理"},
    {"q": "15减8等于?", "a": ["6", "7", "8", "5"], "c": 1, "cat": "数学"},
    {"q": "光速是多少?", "a": ["30万公里/秒", "10万公里/秒", "50万公里/秒", "20万公里/秒"], "c": 0, "cat": "科学"},
    {"q": "亚洲最大的湖是?", "a": ["里海", "贝加尔湖", "死海", "青海湖"], "c": 0, "cat": "地理"},
    {"q": "9除以3等于?", "a": ["2", "3", "4", "5"], "c": 1, "cat": "数学"},
    {"q": "人体有多少血液?", "a": ["约占体重的8%", "约占体重的5%", "约占体重的10%", "约占体重的3%"], "c": 0, "cat": "科学"},
    {"q": "中国有多少个直辖市?", "a": ["4", "5", "3", "6"], "c": 0, "cat": "地理"},
    {"q": "100减37等于?", "a": ["62", "63", "64", "61"], "c": 1, "cat": "数学"},
    {"q": "太阳系有几颗行星?", "a": ["8", "7", "9", "6"], "c": 0, "cat": "科学"},
    {"q": "世界上最小的国家是?", "a": ["梵蒂冈", "摩纳哥", "圣马力诺", "列支敦士登"], "c": 0, "cat": "地理"},
    {"q": "6乘以6等于?", "a": ["35", "36", "37", "34"], "c": 1, "cat": "数学"},
    {"q": "人体最大的肌肉是?", "a": ["臀大肌", "胸肌", "背阔肌", "股四头肌"], "c": 0, "cat": "科学"},
    {"q": "中国最长的铁路是?", "a": ["京九铁路", "京沪铁路", "哈大铁路", "陇海铁路"], "c": 0, "cat": "地理"},
]

class Player:
    def __init__(self, name, color, is_human=True):
        self.name = name
        self.color = color
        self.score = 0
        self.is_human = is_human

def trivia_contest():
    mode = "menu"
    
    screen.fill(BLACK)
    title = big_font.render("知识问答比赛", True, YELLOW)
    screen.blit(title, (WIDTH // 2 - 150, 100))
    
    inst = font.render("1. 单人模式   2. 双人对战   3. 退出", True, WHITE)
    screen.blit(inst, (WIDTH // 2 - 150, 250))
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    mode = "single"
                    waiting = False
                elif event.key == pygame.K_2:
                    mode = "multi"
                    waiting = False
                elif event.key == pygame.K_3:
                    return
    
    if mode == "single":
        players = [Player("玩家", BLUE, True)]
    else:
        players = [Player("玩家1", RED, True), Player("玩家2", GREEN, True)]
    
    current_player_idx = 0
    current_question = None
    used_questions = []
    timer = 0
    showing_result = False
    result_timer = 0
    selected_answer = -1
    
    while len(used_questions) < min(20, len(QUESTIONS)):
        screen.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN:
                current_p = players[current_player_idx]
                
                if current_p.is_human and not showing_result:
                    if event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                        selected_answer = event.key - 49
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE) and selected_answer >= 0:
                        showing_result = True
                        result_timer = 120
                        
                        if selected_answer == current_question["c"]:
                            current_p.score += 10 if timer > 5 else 20
                        selected_answer = -1
        
        if current_question is None or showing_result:
            if result_timer > 0:
                result_timer -= 1
            else:
                if len(used_questions) < len(QUESTIONS):
                    q_idx = random.choice([i for i in range(len(QUESTIONS)) if i not in used_questions])
                    used_questions.append(q_idx)
                    current_question = QUESTIONS[q_idx]
                    timer = 10 * 60
                    selected_answer = -1
                showing_result = False
        
        if not showing_result and timer > 0:
            timer -= 1
            if timer == 0:
                showing_result = True
                result_timer = 120
        
        pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, 80))
        
        for i, p in enumerate(players):
            info = f"{p.name}: {p.score}分"
            color = GREEN if p == players[current_player_idx] else WHITE
            text = font.render(info, True, color)
            screen.blit(text, (10 + i * 200, 30))
        
        if current_question:
            q_text = big_font.render(current_question["q"], True, WHITE)
            screen.blit(q_text, (WIDTH // 2 - q_text.get_width() // 2, 100))
            
            cat_text = small_font.render(f"类别: {current_question['cat']}", True, YELLOW)
            screen.blit(cat_text, (WIDTH // 2 - 50, 150))
            
            if showing_result or timer == 0:
                for i, ans in enumerate(current_question["a"]):
                    color = GREEN if i == current_question["c"] else RED if i == selected_answer else WHITE
                    pygame.draw.rect(screen, color, (WIDTH // 2 - 200, 200 + i * 80, 400, 70), 2)
                    ans_text = font.render(f"{i+1}. {ans}", True, color)
                    screen.blit(ans_text, (WIDTH // 2 - 180, 220 + i * 80))
            else:
                for i, ans in enumerate(current_question["a"]):
                    color = GREEN if i == selected_answer else WHITE
                    pygame.draw.rect(screen, color, (WIDTH // 2 - 200, 200 + i * 80, 400, 70), 2)
                    ans_text = font.render(f"{i+1}. {ans}", True, color)
                    screen.blit(ans_text, (WIDTH // 2 - 180, 220 + i * 80))
            
            timer_sec = timer // 60
            timer_color = GREEN if timer_sec > 5 else RED
            timer_text = font.render(f"时间: {timer_sec}秒", True, timer_color)
            screen.blit(timer_text, (WIDTH // 2 - 60, 550))
            
            if not showing_result:
                inst = small_font.render("按1-4选择答案，按回车确认", True, YELLOW)
                screen.blit(inst, (WIDTH // 2 - 120, 600))
        
        pygame.display.flip()
        clock.tick(60)
        
        if result_timer == 0 and showing_result:
            current_player_idx = (current_player_idx + 1) % len(players)
            current_question = None
    
    screen.fill(BLACK)
    title = big_font.render("游戏结束!", True, YELLOW)
    screen.blit(title, (WIDTH // 2 - 100, 100))
    
    winner = max(players, key=lambda p: p.score)
    
    for i, p in enumerate(players):
        result = font.render(f"{p.name}: {p.score}分", True, p.color)
        screen.blit(result, (WIDTH // 2 - 80, 200 + i * 50))
    
    winner_text = big_font.render(f"获胜者: {winner.name}!", True, winner.color)
    screen.blit(winner_text, (WIDTH // 2 - 120, 400))
    
    pygame.display.flip()
    pygame.time.wait(5000)
    pygame.quit()

if __name__ == "__main__":
    trivia_contest()
