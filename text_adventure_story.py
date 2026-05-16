import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("命运抉择")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 255)
GREEN = (50, 200, 50)
RED = (200, 50, 50)
GRAY = (100, 100, 100)

class StoryNode:
    def __init__(self, text, choices=None):
        self.text = text
        self.choices = choices if choices else []

story_tree = {
    "start": StoryNode(
        "你在一个陌生的森林中醒来，阳光透过树叶洒下斑驳的光影。远处传来流水声，左边是茂密的灌木丛，右边有一条蜿蜒的小路。",
        [("向左探索", "bush"), ("沿小路前进", "path"), ("原地等待", "wait")]
    ),
    "bush": StoryNode(
        "你拨开灌木丛，发现了一个隐藏的宝箱！箱子上有一把古老的锁，似乎需要钥匙才能打开。",
        [("尝试撬开箱子", "pry"), ("寻找钥匙", "search_key"), ("回到起点", "start")]
    ),
    "pry": StoryNode(
        "你找到一块石头，用力砸向锁。锁开了！箱子里有一把闪闪发光的宝剑，你感觉自己变强了！",
        [("拿着宝剑继续探索", "path_with_sword")]
    ),
    "path": StoryNode(
        "你沿着小路前进，来到了一个古老的村庄。村口有一个神秘的老人向你招手。",
        [("和老人对话", "talk_old"), ("直接穿过村庄", "through_village")]
    ),
    "path_with_sword": StoryNode(
        "你沿着小路前进，来到了一个古老的村庄。村口有一个神秘的老人向你招手，他看到你的宝剑，眼睛一亮！",
        [("和老人对话", "talk_old_sword"), ("直接穿过村庄", "through_village")]
    ),
    "search_key": StoryNode(
        "你仔细搜索周围，在一块石头下面找到了一把生锈的钥匙。",
        [("用钥匙打开箱子", "open_box"), ("回到起点", "start")]
    ),
    "open_box": StoryNode(
        "你用钥匙打开了箱子，里面是一本古老的魔法书！你能感觉到书中蕴含的神秘力量。",
        [("带着魔法书继续探索", "path_with_book")]
    ),
    "talk_old": StoryNode(
        "老人说：'年轻人，我等你很久了。这座村庄附近的山洞里有一件宝物，但那里住着一条恶龙...'",
        [("询问更多信息", "more_info"), ("勇敢地去山洞", "cave"), ("委婉拒绝", "decline")]
    ),
    "talk_old_sword": StoryNode(
        "老人看到宝剑，兴奋地说：'这就是传说中的勇者之剑！拿着它，你一定能战胜恶龙！'",
        [("询问更多信息", "more_info"), ("勇敢地去山洞", "cave_hero"), ("委婉拒绝", "decline")]
    ),
    "talk_old_book": StoryNode(
        "老人看到魔法书，恭敬地说：'这是上古法师留下的遗物！有了它，恶龙不是你的对手！'",
        [("询问更多信息", "more_info"), ("勇敢地去山洞", "cave_mage"), ("委婉拒绝", "decline")]
    ),
    "wait": StoryNode(
        "你坐在原地等待，希望有人经过。不久，你听到了脚步声...是一群强盗！",
        [("尝试逃跑", "run"), ("和他们战斗", "fight"), ("交出身上值钱的东西", "surrender")]
    ),
    "cave": StoryNode(
        "你来到山洞，一股热浪扑面而来。恶龙出现了！没有武器的你根本无法抗衡，只能落荒而逃...",
        [("重新开始", "start")]
    ),
    "cave_hero": StoryNode(
        "你来到山洞，一股热浪扑面而来。恶龙出现了！勇者之剑发出耀眼的光芒，你轻松击败了恶龙！",
        [("查看战利品", "treasure")]
    ),
    "cave_mage": StoryNode(
        "你来到山洞，一股热浪扑面而来。恶龙出现了！你翻开魔法书，一道强大的魔法将恶龙制服！",
        [("查看战利品", "treasure")]
    ),
    "treasure": StoryNode(
        "龙穴里堆满了金银财宝！你成为了传奇英雄！恭喜你完成了冒险！",
        [("重新开始", "start")]
    ),
    "path_with_book": StoryNode(
        "你带着魔法书来到村庄，神秘老人一眼就认出了它，眼中充满了敬意。",
        [("和老人对话", "talk_old_book"), ("直接穿过村庄", "through_village")]
    ),
    "through_village": StoryNode(
        "你穿过了村庄，继续前进。前面是一望无际的平原，你开始了新的旅程...",
        [("重新开始", "start")]
    ),
    "more_info": StoryNode(
        "老人告诉你：恶龙虽然凶猛，但它害怕一件东西——古老的勇者之剑或魔法书。可惜这些都失传已久了...",
        [("去山洞碰碰运气", "cave"), ("感谢老人后离开", "through_village")]
    ),
    "decline": StoryNode(
        "你婉拒了老人的请求，继续自己的旅程。也许下次你会更勇敢...",
        [("重新开始", "start")]
    ),
    "run": StoryNode(
        "你拼命逃跑，总算摆脱了强盗。虽然安全了，但你也迷失了方向，只能原路返回...",
        [("重新开始", "start")]
    ),
    "fight": StoryNode(
        "你勇敢地战斗，但寡不敌众，最终被强盗制服。不过，他们只抢了你的钱就走了...",
        [("重新开始", "start")]
    ),
    "surrender": StoryNode(
        "你交出了身上的钱，强盗满意地离开了。虽然破财，但至少保住了性命。",
        [("重新开始", "start")]
    )
}

class TextAdventure:
    def __init__(self):
        self.current_node = "start"
        self.font = pygame.font.Font(None, 32)
        self.large_font = pygame.font.Font(None, 48)

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

    def draw(self):
        screen.fill(BLACK)
        
        title_text = self.large_font.render("命运抉择", True, BLUE)
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 20))
        
        node = story_tree[self.current_node]
        
        text_lines = self.wrap_text(node.text, 700)
        y = 100
        for line in text_lines:
            screen.blit(line, (50, y))
            y += 35
        
        y += 20
        for i, (choice_text, _) in enumerate(node.choices):
            button_y = y + i * 60
            pygame.draw.rect(screen, (40, 40, 80), (50, button_y, 700, 50), border_radius=5)
            pygame.draw.rect(screen, BLUE, (50, button_y, 700, 50), 2, border_radius=5)
            
            choice_surface = self.font.render(f"{i+1}. {choice_text}", True, WHITE)
            screen.blit(choice_surface, (70, button_y + 12))

    def handle_click(self, pos):
        node = story_tree[self.current_node]
        for i, (_, target_node) in enumerate(node.choices):
            button_y = 220 + i * 60
            if 50 <= pos[0] <= 750 and button_y <= pos[1] <= button_y + 50:
                self.current_node = target_node
                break

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            node = story_tree[self.current_node]
            if pygame.K_1 <= event.key <= pygame.K_9:
                idx = event.key - pygame.K_1
                if 0 <= idx < len(node.choices):
                    self.current_node = node.choices[idx][1]

game = TextAdventure()
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            game.handle_click(pygame.mouse.get_pos())
        game.handle_input(event)
    
    game.draw()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
