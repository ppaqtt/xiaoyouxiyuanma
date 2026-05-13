import pygame
import random
import math

pygame.init()

WIDTH, HEIGHT = 600, 700

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

COLORS = [RED, GREEN, BLUE, YELLOW, PURPLE]

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("泡泡龙")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 30)

class Bubble:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.radius = 20
        self.vx = 0
        self.vy = 0
        self.placed = True
        self.connected = False
    
    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius, 2)
    
    def update(self):
        if not self.placed:
            self.x += self.vx
            self.y += self.vy
            
            if self.x <= self.radius or self.x >= WIDTH - self.radius:
                self.vx *= -1
            
            if self.y <= self.radius:
                self.placed = True
                self.y = self.radius
    
    def check_collision(self, other):
        dx = self.x - other.x
        dy = self.y - other.y
        distance = math.sqrt(dx**2 + dy**2)
        return distance < self.radius + other.radius

def bubble_shooter():
    grid = []
    bubble_radius = 20
    rows = 10
    cols = 15
    
    for row in range(rows):
        grid_row = []
        offset = 0 if row % 2 == 0 else bubble_radius
        for col in range(cols):
            x = 30 + col * (bubble_radius * 2) + offset
            y = 40 + row * (bubble_radius * 1.7)
            if row < 5:
                color = random.choice(COLORS)
                bubble = Bubble(x, y, color)
                grid_row.append(bubble)
            else:
                grid_row.append(None)
        grid.append(grid_row)
    
    current_color = random.choice(COLORS)
    next_color = random.choice(COLORS)
    player_bubble = Bubble(WIDTH // 2, HEIGHT - 60, current_color)
    player_bubble.placed = False
    
    score = 0
    game_over = False
    aiming = True
    shoot_angle = 0
    
    def drop_disconnected_bubbles():
        nonlocal score
        for row in grid:
            for bubble in row:
                if bubble:
                    bubble.connected = False
        
        for bubble in grid[0]:
            if bubble:
                flood_fill(0, grid[0].index(bubble))
        
        for row in range(len(grid)):
            for col in range(len(grid[row])):
                if grid[row][col] and not grid[row][col].connected:
                    score += 10
                    grid[row][col] = None
    
    def flood_fill(row, col):
        if row < 0 or row >= len(grid) or col < 0 or col >= len(grid[row]):
            return
        if not grid[row][col] or grid[row][col].connected:
            return
        grid[row][col].connected = True
        
        directions = [(-1, -1), (-1, 0), (0, -1), (0, 1), (1, -1), (1, 0)]
        if row % 2 == 1:
            directions = [(-1, 0), (-1, 1), (0, -1), (0, 1), (1, 0), (1, 1)]
        
        for dr, dc in directions:
            flood_fill(row + dr, col + dc)
    
    while not game_over:
        screen.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEMOTION and aiming:
                mouse_x, mouse_y = event.pos
                dx = mouse_x - player_bubble.x
                dy = mouse_y - player_bubble.y
                shoot_angle = math.atan2(dy, dx)
            elif event.type == pygame.MOUSEBUTTONDOWN and aiming:
                if event.button == 1:
                    player_bubble.vx = math.cos(shoot_angle) * 10
                    player_bubble.vy = math.sin(shoot_angle) * 10
                    aiming = False
        
        if not aiming:
            player_bubble.update()
            
            for row in range(len(grid)):
                for col in range(len(grid[row])):
                    bubble = grid[row][col]
                    if bubble and player_bubble.check_collision(bubble):
                        placed = False
                        for new_row in range(len(grid)):
                            for new_col in range(len(grid[new_row])):
                                if not grid[new_row][new_col]:
                                    grid[new_row][new_col] = player_bubble
                                    player_bubble.placed = True
                                    placed = True
                                    
                                    remove_connected(new_row, new_col, player_bubble.color)
                                    drop_disconnected_bubbles()
                                    
                                    current_color = next_color
                                    next_color = random.choice(COLORS)
                                    player_bubble = Bubble(WIDTH // 2, HEIGHT - 60, current_color)
                                    player_bubble.placed = False
                                    aiming = True
                                    break
                            if placed:
                                break
                        break
            
            if player_bubble.y <= player_bubble.radius:
                for col in range(len(grid[0])):
                    if not grid[0][col]:
                        grid[0][col] = player_bubble
                        player_bubble.placed = True
                        remove_connected(0, col, player_bubble.color)
                        drop_disconnected_bubbles()
                        
                        current_color = next_color
                        next_color = random.choice(COLORS)
                        player_bubble = Bubble(WIDTH // 2, HEIGHT - 60, current_color)
                        player_bubble.placed = False
                        aiming = True
                        break
        
        def remove_connected(row, col, color):
            nonlocal score
            if row < 0 or row >= len(grid) or col < 0 or col >= len(grid[row]):
                return
            if not grid[row][col] or grid[row][col].color != color:
                return
            
            grid[row][col] = None
            score += 10
            
            directions = [(-1, -1), (-1, 0), (0, -1), (0, 1), (1, -1), (1, 0)]
            if row % 2 == 1:
                directions = [(-1, 0), (-1, 1), (0, -1), (0, 1), (1, 0), (1, 1)]
            
            for dr, dc in directions:
                remove_connected(row + dr, col + dc)
        
        for row in grid:
            for bubble in row:
                if bubble:
                    bubble.draw()
        
        player_bubble.draw()
        
        pygame.draw.circle(screen, next_color, (WIDTH - 60, HEIGHT - 60), 25)
        pygame.draw.circle(screen, WHITE, (WIDTH - 60, HEIGHT - 60), 25, 2)
        
        if aiming:
            end_x = player_bubble.x + math.cos(shoot_angle) * 150
            end_y = player_bubble.y + math.sin(shoot_angle) * 150
            pygame.draw.line(screen, WHITE, (player_bubble.x, player_bubble.y), (end_x, end_y), 2)
        
        score_text = font.render(f"得分: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    bubble_shooter()