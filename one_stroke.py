import pygame
import random
from collections import deque

pygame.init()

WIDTH, HEIGHT = 600, 700
GRID_SIZE = 50
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (255, 0, 0)
BLUE = (0, 100, 200)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
GRAY = (100, 100, 100)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("一笔画解谜")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 32)
big_font = pygame.font.Font(None, 50)
small_font = pygame.font.Font(None, 24)

LEVELS = [
    {
        "nodes": [(2, 2), (4, 2), (6, 2), (4, 4), (2, 6), (6, 6)],
        "edges": [((2,2),(4,2)), ((4,2),(6,2)), ((4,2),(4,4)), ((2,6),(4,4)), ((4,4),(6,6))],
        "start": (2, 2),
        "name": "第一关"
    },
    {
        "nodes": [(1, 1), (5, 1), (3, 3), (1, 5), (5, 5), (3, 7)],
        "edges": [((1,1),(3,3)), ((5,1),(3,3)), ((1,5),(3,3)), ((5,5),(3,3)), ((3,3),(3,7))],
        "start": (3, 3),
        "name": "第二关"
    },
    {
        "nodes": [(1, 1), (5, 1), (3, 3), (1, 5), (5, 5)],
        "edges": [((1,1),(3,3)), ((5,1),(3,3)), ((1,5),(3,3)), ((5,5),(3,3))],
        "start": (3, 3),
        "name": "第三关"
    },
    {
        "nodes": [(2, 2), (4, 2), (6, 2), (2, 4), (4, 4), (6, 4), (2, 6), (4, 6), (6, 6)],
        "edges": [((2,2),(4,2)), ((4,2),(6,2)), ((2,2),(2,4)), ((2,4),(2,6)), 
                  ((4,4),(2,4)), ((4,4),(4,6)), ((4,2),(4,4)), ((6,2),(6,4)), ((6,4),(6,6)), ((4,6),(6,6))],
        "start": (2, 2),
        "name": "第四关"
    },
]

class OneStroke:
    def __init__(self, level_data):
        self.nodes = set(level_data["nodes"])
        self.edges = level_data["edges"]
        self.start = level_data["start"]
        self.path = [self.start]
        self.visited_edges = set()
        self.current = self.start
        self.visited_count = {node: 0 for node in self.nodes}
        self.visited_count[self.start] = 1
    
    def get_connected_nodes(self, node):
        connected = []
        for edge in self.edges:
            if node in edge:
                other = edge[0] if edge[1] == node else edge[1]
                if edge not in self.visited_edges:
                    connected.append(other)
        return connected
    
    def move_to(self, node):
        if node not in self.nodes:
            return False
        
        edge = tuple(sorted([self.current, node]))
        if edge in self.visited_edges:
            return False
        
        self.visited_edges.add(edge)
        self.visited_count[node] += 1
        self.path.append(node)
        self.current = node
        return True
    
    def undo(self):
        if len(self.path) > 1:
            prev = self.path[-2]
            edge = tuple(sorted([self.current, prev]))
            if edge in self.visited_edges:
                self.visited_edges.remove(edge)
            self.visited_count[self.current] -= 1
            self.path.pop()
            self.current = prev
    
    def check_win(self):
        return all(self.visited_count[node] >= 1 for node in self.nodes)
    
    def can_move_to(self, node):
        if node not in self.nodes:
            return False
        edge = tuple(sorted([self.current, node]))
        return edge not in self.visited_edges
    
    def draw(self, level_data):
        screen.fill(BLACK)
        
        for edge in self.edges:
            x1 = edge[0][0] * GRID_SIZE + GRID_SIZE // 2
            y1 = edge[0][1] * GRID_SIZE + GRID_SIZE // 2
            x2 = edge[1][0] * GRID_SIZE + GRID_SIZE // 2
            y2 = edge[1][1] * GRID_SIZE + GRID_SIZE // 2
            
            edge_key = tuple(sorted([edge[0], edge[1]]))
            if edge_key in self.visited_edges:
                pygame.draw.line(screen, GREEN, (x1, y1), (x2, y2), 5)
            else:
                pygame.draw.line(screen, GRAY, (x1, y1), (x2, y2), 2)
        
        for i in range(len(self.path) - 1):
            node1 = self.path[i]
            node2 = self.path[i + 1]
            x1 = node1[0] * GRID_SIZE + GRID_SIZE // 2
            y1 = node1[1] * GRID_SIZE + GRID_SIZE // 2
            x2 = node2[0] * GRID_SIZE + GRID_SIZE // 2
            y2 = node2[1] * GRID_SIZE + GRID_SIZE // 2
            pygame.draw.line(screen, YELLOW, (x1, y1), (x2, y2), 8)
        
        for node in self.nodes:
            x = node[0] * GRID_SIZE + GRID_SIZE // 2
            y = node[1] * GRID_SIZE + GRID_SIZE // 2
            
            if node == self.current:
                pygame.draw.circle(screen, RED, (x, y), 20)
            elif self.visited_count[node] > 0:
                pygame.draw.circle(screen, GREEN, (x, y), 15)
                pygame.draw.circle(screen, WHITE, (x, y), 15, 2)
            else:
                pygame.draw.circle(screen, WHITE, (x, y), 15)
                pygame.draw.circle(screen, WHITE, (x, y), 15, 2)

def one_stroke_game():
    current_level = 0
    levels_completed = 0
    
    while current_level < len(LEVELS):
        level = LEVELS[current_level]
        game = OneStroke(level)
        
        running = True
        won = False
        hint_shown = False
        
        while running:
            screen.fill(BLACK)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        game = OneStroke(level)
                        hint_shown = False
                    elif event.key == pygame.K_u:
                        game.undo()
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                        current_level = len(LEVELS)
                        break
                    elif event.key == pygame.K_h:
                        hint_shown = not hint_shown
                    elif not won:
                        if event.key in (pygame.K_UP, pygame.K_w):
                            dx, dy = 0, -1
                        elif event.key in (pygame.K_DOWN, pygame.K_s):
                            dx, dy = 0, 1
                        elif event.key in (pygame.K_LEFT, pygame.K_a):
                            dx, dy = -1, 0
                        elif event.key in (pygame.K_RIGHT, pygame.K_d):
                            dx, dy = 1, 0
                        else:
                            continue
                        
                        target = (game.current[0] + dx, game.current[1] + dy)
                        
                        for node in game.nodes:
                            if abs(node[0] - target[0]) <= 1 and abs(node[1] - target[1]) <= 1:
                                if node != game.current and game.can_move_to(node):
                                    game.move_to(node)
                                    break
            
            if game.check_win() and not won:
                won = True
                levels_completed += 1
                
                screen.fill(GREEN)
                win_text = big_font.render("过关!", True, WHITE)
                screen.blit(win_text, (WIDTH // 2 - 80, HEIGHT // 2 - 50))
                
                next_text = font.render("按空格进入下一关", True, BLACK)
                screen.blit(next_text, (WIDTH // 2 - 100, HEIGHT // 2 + 20))
                
                pygame.display.flip()
                
                waiting = True
                while waiting:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            return
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_SPACE:
                                current_level += 1
                                waiting = False
                                running = False
                            elif event.key == pygame.K_r:
                                waiting = False
            else:
                game.draw(level)
                
                pygame.draw.rect(screen, BLACK, (0, HEIGHT - 80, WIDTH, 80))
                
                title = font.render(f"{level['name']}", True, YELLOW)
                screen.blit(title, (10, HEIGHT - 70))
                
                nodes_visited = sum(1 for n in game.nodes if game.visited_count[n] > 0)
                progress = font.render(f"节点: {nodes_visited}/{len(game.nodes)}", True, GREEN)
                screen.blit(progress, (200, HEIGHT - 70))
                
                edges_visited = len(game.visited_edges)
                total_edges = len(game.edges)
                edges_text = font.render(f"边: {edges_visited}/{total_edges}", True, BLUE)
                screen.blit(edges_text, (200, HEIGHT - 40))
                
                inst = small_font.render("WASD移动到相邻节点 | U撤销 | H提示 | R重试", True, WHITE)
                screen.blit(inst, (10, HEIGHT - 30))
                
                if hint_shown:
                    hint_text = small_font.render(f"提示: 从{level['start']}开始", True, YELLOW)
                    screen.blit(hint_text, (400, HEIGHT - 55))
                
                pygame.display.flip()
                clock.tick(60)
    
    screen.fill(BLACK)
    result = big_font.render("恭喜全部通关!", True, YELLOW)
    screen.blit(result, (WIDTH // 2 - 150, HEIGHT // 2 - 50))
    
    complete = font.render(f"完成 {levels_completed} 个关卡!", True, GREEN)
    screen.blit(complete, (WIDTH // 2 - 100, HEIGHT // 2 + 20))
    
    pygame.display.flip()
    pygame.time.wait(5000)
    pygame.quit()

if __name__ == "__main__":
    one_stroke_game()
