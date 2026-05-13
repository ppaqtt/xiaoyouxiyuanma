import pygame
import random
import math

pygame.init()

WIDTH, HEIGHT = 800, 600

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
COLORS = [
    (255, 0, 0), (0, 255, 0), (0, 0, 255), 
    (255, 255, 0), (255, 0, 255), (0, 255, 255),
    (255, 165, 0), (128, 0, 128)
]

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("物理弹珠球")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 30)

class Ball:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-5, 5)
        self.vy = random.uniform(-5, 5)
        self.radius = random.randint(15, 30)
        self.color = random.choice(COLORS)
        self.mass = self.radius ** 2
    
    def update(self, gravity, friction):
        self.vy += gravity
        self.vx *= friction
        self.vy *= friction
        
        self.x += self.vx
        self.y += self.vy
        
        if self.x - self.radius < 0:
            self.x = self.radius
            self.vx *= -0.8
        elif self.x + self.radius > WIDTH:
            self.x = WIDTH - self.radius
            self.vx *= -0.8
        
        if self.y - self.radius < 0:
            self.y = self.radius
            self.vy *= -0.8
        elif self.y + self.radius > HEIGHT:
            self.y = HEIGHT - self.radius
            self.vy *= -0.8
    
    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, WHITE, (int(self.x - self.radius // 3), int(self.y - self.radius // 3)), self.radius // 4)

def physics_balls():
    balls = []
    gravity = 0.3
    friction = 0.995
    
    for _ in range(8):
        ball = Ball(random.randint(100, WIDTH - 100), random.randint(100, HEIGHT - 200))
        balls.append(ball)
    
    dragging = False
    dragged_ball = None
    drag_offset_x = 0
    drag_offset_y = 0
    
    while True:
        screen.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    x, y = event.pos
                    for ball in balls:
                        distance = math.sqrt((x - ball.x)**2 + (y - ball.y)**2)
                        if distance < ball.radius:
                            dragging = True
                            dragged_ball = ball
                            drag_offset_x = ball.x - x
                            drag_offset_y = ball.y - y
                            ball.vx = 0
                            ball.vy = 0
                            break
                elif event.button == 3:
                    x, y = event.pos
                    balls.append(Ball(x, y))
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if dragging and dragged_ball:
                        dragged_ball.vx = (event.pos[0] - (dragged_ball.x - drag_offset_x)) * 0.3
                        dragged_ball.vy = (event.pos[1] - (dragged_ball.y - drag_offset_y)) * 0.3
                    dragging = False
                    dragged_ball = None
            elif event.type == pygame.MOUSEMOTION:
                if dragging and dragged_ball:
                    x, y = event.pos
                    dragged_ball.x = x + drag_offset_x
                    dragged_ball.y = y + drag_offset_y
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    balls = []
                elif event.key == pygame.K_g:
                    gravity = gravity * -1 if gravity != 0 else 0.3
        
        for ball in balls:
            if ball is not dragged_ball:
                ball.update(gravity, friction)
        
        for i in range(len(balls)):
            for j in range(i + 1, len(balls)):
                ball1, ball2 = balls[i], balls[j]
                distance = math.sqrt((ball1.x - ball2.x)**2 + (ball1.y - ball2.y)**2)
                
                if distance < ball1.radius + ball2.radius:
                    nx = (ball2.x - ball1.x) / distance
                    ny = (ball2.y - ball1.y) / distance
                    
                    rel_vx = ball1.vx - ball2.vx
                    rel_vy = ball1.vy - ball2.vy
                    
                    rel_vel_normal = rel_vx * nx + rel_vy * ny
                    
                    if rel_vel_normal > 0:
                        impulse = -(1 + 0.5) * rel_vel_normal / (1/ball1.mass + 1/ball2.mass)
                        
                        ball1.vx += impulse * nx / ball1.mass
                        ball1.vy += impulse * ny / ball1.mass
                        ball2.vx -= impulse * nx / ball2.mass
                        ball2.vy -= impulse * ny / ball2.mass
                    
                    overlap = ball1.radius + ball2.radius - distance
                    separation_x = overlap / 2 * nx
                    separation_y = overlap / 2 * ny
                    ball1.x -= separation_x
                    ball1.y -= separation_y
                    ball2.x += separation_x
                    ball2.y += separation_y
        
        for ball in balls:
            ball.draw()
        
        count_text = font.render(f"球数: {len(balls)}", True, WHITE)
        screen.blit(count_text, (10, 10))
        
        gravity_text = font.render(f"重力: {gravity:.2f} (G切换)", True, WHITE)
        screen.blit(gravity_text, (10, 50))
        
        instruction_text = font.render("点击拖动球 | 右键添加 | C清空 | G重力反向", True, WHITE)
        screen.blit(instruction_text, (WIDTH//2 - instruction_text.get_width()//2, HEIGHT - 30))
        
        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    physics_balls()