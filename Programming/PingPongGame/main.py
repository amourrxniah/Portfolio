import math
import os
import random
import sys
import pygame

# Initialise pygame
pygame.init()
pygame.mixer.init()

# Constants
WIDTH, HEIGHT = 1000, 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
COLORS = {
    "background": (5, 10, 20),
    "paddle": (100, 200, 255),
    "ball": (255, 100, 100),
    "text": (200, 200, 200),
    "net": (50, 50, 70)
}

# Game setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ultimate Ping Pong")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
big_font = pygame.font.Font(None, 72)

# Load sounds
sound_dir = os.path.join(os.path.dirname(__file__), "sounds")
try:
    paddle_path = os.path.join(sound_dir, "paddle_hit.wav")
    wall_path = os.path.join(sound_dir, "wall_hit.wav")
    score_path = os.path.join(sound_dir, "score.mp3")  # use .wav for max compatibility

    print("Loading sounds from:", sound_dir)

    paddle_sound = pygame.mixer.Sound(paddle_path)
    wall_sound = pygame.mixer.Sound(wall_path)
    score_sound = pygame.mixer.Sound(score_path)
    sounds_loaded = True
except Exception as e:
    sounds_loaded = False
    print("Sound files not found - continuing without sound")
    print("Error:", e)

class Paddle:
    def __init__(self, x, y, width, height, speed, up_key, down_key):
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed
        self.up_key = up_key
        self.down_key = down_key
        self.score = 0

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[self.up_key] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[self.down_key] and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed

    def draw(self):
        pygame.draw.rect(screen, COLORS["paddle"], self.rect, border_radius=10)
        glow = pygame.Surface((self.rect.width + 10, self.rect.height + 10), pygame.SRCALPHA)
        pygame.draw.rect(glow, (*COLORS["paddle"], 50), (0, 0, glow.get_width(), glow.get_height()), border_radius=15)
        screen.blit(glow, (self.rect.x - 5, self.rect.y - 5))

class Ball:
    def __init__(self, x, y, size, speed):
        self.rect = pygame.Rect(x, y, size, size)
        self.speed_x = speed * random.choice((1, -1))
        self.speed_y = speed * random.choice((1, -1))
        self.max_speed = speed * 1.5
        self.size = size

    def move(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # Wall collision
        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
            self.speed_y *= -1
            if sounds_loaded:
                wall_sound.play()

        # Score conditions
        if self.rect.left <= 0:
            player2.score += 1
            self.reset()
            if sounds_loaded:
                score_sound.play()
        elif self.rect.right >= WIDTH:
            player1.score += 1
            self.reset()
            if sounds_loaded:
                score_sound.play()

    def reset(self):
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.speed_x = abs(self.speed_x) * random.choice((1, -1))
        self.speed_y = abs(self.speed_y) * random.choice((1, -1))

    def check_collision(self, paddle):
        if self.rect.colliderect(paddle.rect):
            relative_intersect_y = (paddle.rect.centery - self.rect.centery)
            normalized_relative_intersection_y = relative_intersect_y / (paddle.rect.height / 2)
            bounce_angle = normalized_relative_intersection_y * (5 * 3.14159 / 12)
            direction = -1 if paddle == player1 else 1
            self.speed_x = direction * abs(self.speed_x) * 1.05
            self.speed_y = -self.max_speed * math.sin(bounce_angle)
            if abs(self.speed_x) > self.max_speed:
                self.speed_x = self.max_speed if self.speed_x > 0 else -self.max_speed
            if sounds_loaded:
                paddle_sound.play()

    def draw(self):
        pygame.draw.ellipse(screen, COLORS["ball"], self.rect)
        glow = pygame.Surface((self.size + 10, self.size + 10), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (*COLORS["ball"], 50), (0, 0, glow.get_width(), glow.get_height()))
        screen.blit(glow, (self.rect.x - 5, self.rect.y - 5))

def ai_move(paddle, ball):
    if ball.rect.centery < paddle.rect.centery and paddle.rect.top > 0:
        paddle.rect.y -= paddle.speed
    elif ball.rect.centery > paddle.rect.centery and paddle.rect.bottom < HEIGHT:
        paddle.rect.y += paddle.speed

def draw_net():
    net_width = 4
    segment_height = 20
    gap = 10
    for y in range(0, HEIGHT, segment_height + gap):
        pygame.draw.rect(screen, COLORS["net"], (WIDTH // 2 - net_width // 2, y, net_width, segment_height))

def draw_score():
    player1_text = font.render(f"Player 1: {player1.score}", True, COLORS["text"])
    player2_text = font.render(f"AI: {player2.score}", True, COLORS["text"])
    screen.blit(player1_text, (50, 20))
    screen.blit(player2_text, (WIDTH - 150, 20))

def draw_game_over():
    if player1.score >= 5 or player2.score >= 5:
        winner = "Player 1" if player1.score >= 5 else "AI"
        game_over_text = big_font.render(f"{winner} Wins!", True, WHITE)
        restart_text = font.render("Press R to restart", True, COLORS["text"])
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 50))
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 20))
        return True
    return False

def reset_game():
    player1.score = 0
    player2.score = 0
    ball.reset()

def show_instructions():
    screen.fill(COLORS["background"])
    title = big_font.render("Ultimate Ping Pong", True, WHITE)
    inst1 = font.render("W / S to Move Paddle", True, COLORS["text"])
    inst2 = font.render("First to 5 Points Wins", True, COLORS["text"])
    inst3 = font.render("Press SPACE to Start", True, COLORS["text"])

    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 100))
    screen.blit(inst1, (WIDTH // 2 - inst1.get_width() // 2, HEIGHT // 2 - 30))
    screen.blit(inst2, (WIDTH // 2 - inst2.get_width() // 2, HEIGHT // 2 + 10))
    screen.blit(inst3, (WIDTH // 2 - inst3.get_width() // 2, HEIGHT // 2 + 50))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False

# Create game objects
player1 = Paddle(20, HEIGHT // 2 - 70, 10, 140, 8, pygame.K_w, pygame.K_s)
player2 = Paddle(WIDTH - 30, HEIGHT // 2 - 70, 10, 140, 8, None, None)  # AI-controlled
ball = Ball(WIDTH // 2, HEIGHT // 2, 20, 5)

# Show instructions before starting
show_instructions()

# Main game loop
running = True
game_over = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and game_over:
                reset_game()
                game_over = False

    if not game_over:
        player1.move()
        ai_move(player2, ball)
        ball.move()
        ball.check_collision(player1)
        ball.check_collision(player2)

    screen.fill(COLORS["background"])
    draw_net()
    player1.draw()
    player2.draw()
    ball.draw()
    draw_score()
    game_over = draw_game_over()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()