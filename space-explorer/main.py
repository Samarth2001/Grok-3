import pygame
import random
import math
import os

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Navigator: Ultimate Edition")

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (100, 100, 100)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
BLACK = (0, 0, 0)

# Load images
try:
    player_img = pygame.image.load("Starship.png").convert_alpha()
    asteroid_img = pygame.image.load("asteroid.png").convert_alpha()
    fuel_img = pygame.image.load("fuel.png").convert_alpha()
    enemy_img = pygame.image.load("enemy.png").convert_alpha()
    powerup_img = pygame.image.load("powerup.png").convert_alpha()
    bullet_img = pygame.image.load("bullet1.png").convert_alpha()
except pygame.error:
    print("Image files not found. Falling back to shapes.")
    player_img = asteroid_img = fuel_img = enemy_img = powerup_img = bullet_img = None

# Scale images
player_size = 40
player_img = pygame.transform.scale(player_img, (player_size, player_size)) if player_img else None
fuel_size = 30
fuel_img = pygame.transform.scale(fuel_img, (fuel_size, fuel_size)) if fuel_img else None
enemy_size = 50
enemy_img = pygame.transform.scale(enemy_img, (enemy_size, enemy_size)) if enemy_img else None
powerup_size = 30
powerup_img = pygame.transform.scale(powerup_img, (powerup_size, powerup_size)) if powerup_img else None
bullet_size = 25
bullet_img = pygame.transform.scale(bullet_img, (bullet_size, bullet_size)) if bullet_img else None

# Player settings
player_x = WIDTH // 2
player_y = HEIGHT - 50
player_speed = 5
fuel = 100
health = 100
score = 0
level = 1
bullets = []
enemy_bullets = []
bullet_speed = 7

# Particle system for effects
particles = []

# Game objects
class GameObject:
    def __init__(self, x, y, size, img, speed, color=None):
        self.x = x
        self.y = y
        self.size = size
        self.img = pygame.transform.scale(img, (size, size)) if img else None
        self.speed = speed
        self.color = color

    def move(self):
        self.y += self.speed
        if self.y > HEIGHT or self.y < -self.size:
            self.reset()

    def reset(self):
        self.y = random.randint(-HEIGHT, -self.size)
        self.x = random.randint(0, WIDTH - self.size)

    def draw(self):
        if self.img:
            screen.blit(self.img, (self.x, self.y))
        else:
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.size, self.size))

    def collides_with(self, other):
        return math.hypot(self.x + self.size//2 - (other.x + other.size//2),
                         self.y + self.size//2 - (other.y + other.size//2)) < (self.size + other.size) / 2

class Enemy(GameObject):
    def __init__(self, x, y, size, img, speed, color):
        super().__init__(x, y, size, img, speed, color)
        self.direction = random.choice([-1, 1])
        self.pattern = random.randint(0, 1)
        self.shoot_timer = random.randint(60, 120)  # Frames until next shot

    def move(self):
        if self.pattern == 0:
            self.x += self.direction * (2 + level * 0.5)
            if self.x <= 0 or self.x >= WIDTH - self.size:
                self.direction *= -1
        self.y += self.speed + level * 0.2
        if self.y > HEIGHT:
            self.reset()

    def shoot(self):
        self.shoot_timer -= 1
        if self.shoot_timer <= 0:
            enemy_bullets.append(GameObject(self.x + self.size//2 - bullet_size//2, self.y + self.size, bullet_size, bullet_img, 5, RED))
            self.shoot_timer = random.randint(60, 120)

class PowerUp(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, powerup_size, powerup_img, 2, BLUE)
        self.type = random.choice(["fuel", "speed", "score", "shield"])

# Particle class for effects
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 5)
        self.speed_x = random.uniform(-2, 2)
        self.speed_y = random.uniform(-2, 2)
        self.life = random.randint(20, 40)

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.life -= 1
        if self.life <= 0:
            particles.remove(self)

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)

# Initialize game objects
asteroid_sizes = [20, 30, 40, 50]
asteroids = [GameObject(random.randint(0, WIDTH), random.randint(-HEIGHT, 0), 
                        random.choice(asteroid_sizes), asteroid_img, random.uniform(2, 4), GRAY) for _ in range(6)]
fuel_cells = [GameObject(random.randint(0, WIDTH), random.randint(-HEIGHT, 0), fuel_size, fuel_img, 2, GREEN) for _ in range(3)]
enemies = [Enemy(random.randint(0, WIDTH), random.randint(-HEIGHT, 0), enemy_size, enemy_img, 3, RED) for _ in range(3)]
powerups = []

# Starry background
stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(100)]

# Font and high score
font = pygame.font.Font(None, 36)
high_score = 0
if os.path.exists("highscore.txt"):
    with open("highscore.txt", "r") as f:
        high_score = int(f.read().strip())

# Game loop
clock = pygame.time.Clock()
running = True
paused = False
distance = 0
powerup_timer = 0
powerup_active = {"speed": False, "shield": False}

while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not paused:
                bullets.append(GameObject(player_x + player_size//2 - bullet_size//2, player_y, bullet_size, bullet_img, -bullet_speed, WHITE))
            if event.key == pygame.K_p:  # Pause/unpause
                paused = not paused

    if paused:
        pause_text = font.render("Paused - Press P to Resume", True, WHITE)
        screen.blit(pause_text, (WIDTH//2 - 150, HEIGHT//2))
        pygame.display.flip()
        continue

    # Player movement
    keys = pygame.key.get_pressed()
    speed = player_speed * (1.5 if powerup_active["speed"] else 1)
    if keys[pygame.K_LEFT] and player_x > 0:
        player_x -= speed
        particles.append(Particle(player_x + player_size, player_y + player_size//2, YELLOW))  # Thruster trail
    if keys[pygame.K_RIGHT] and player_x < WIDTH - player_size:
        player_x += speed
        particles.append(Particle(player_x, player_y + player_size//2, YELLOW))
    if keys[pygame.K_UP] and player_y > 0:
        player_y -= speed
    if keys[pygame.K_DOWN] and player_y < HEIGHT - player_size:
        player_y += speed

    # Update game state
    fuel -= 0.05
    distance += 1
    if fuel <= 0 or health <= 0:
        running = False

    # Level progression
    if distance % 1000 == 0:
        level += 1
        asteroids.append(GameObject(random.randint(0, WIDTH), -50, random.choice(asteroid_sizes), asteroid_img, random.uniform(2, 4), GRAY))
        enemies.append(Enemy(random.randint(0, WIDTH), -50, enemy_size, enemy_img, 3, RED))

    # Power-up spawning and timing
    powerup_timer += 1
    if powerup_timer > 500 and random.random() < 0.02:
        powerups.append(PowerUp(random.randint(0, WIDTH), -20))
        powerup_timer = 0
    if powerup_active["speed"] and powerup_timer > 300:
        powerup_active["speed"] = False
    if powerup_active["shield"] and powerup_timer > 400:
        powerup_active["shield"] = False

    # Draw background
    screen.fill(BLACK)
    for star in stars:
        pygame.draw.circle(screen, WHITE, star, 1)

    # Update and draw particles
    for particle in particles[:]:
        particle.update()
        particle.draw()

    # Move and draw bullets
    for bullet in bullets[:]:
        bullet.move()
        bullet.draw()
        if bullet.y < 0:
            bullets.remove(bullet)

    # Move and draw enemy bullets
    for bullet in enemy_bullets[:]:
        bullet.move()
        bullet.draw()
        if bullet.collides_with(GameObject(player_x, player_y, player_size, player_img, 0)) and not powerup_active["shield"]:
            health -= 10
            enemy_bullets.remove(bullet)
            for _ in range(10):
                particles.append(Particle(player_x + player_size//2, player_y + player_size//2, RED))

    # Move and draw asteroids
    for asteroid in asteroids:
        asteroid.move()
        asteroid.draw()
        if asteroid.collides_with(GameObject(player_x, player_y, player_size, player_img, 0)) and not powerup_active["shield"]:
            health -= 20
            asteroid.reset()
            for _ in range(15):
                particles.append(Particle(player_x + player_size//2, player_y + player_size//2, GRAY))

    # Move and draw fuel cells
    for fuel_cell in fuel_cells:
        fuel_cell.move()
        fuel_cell.draw()
        if fuel_cell.collides_with(GameObject(player_x, player_y, player_size, player_img, 0)):
            fuel = min(100, fuel + 20)
            score += 100
            fuel_cell.reset()

    # Move and draw enemies
    for enemy in enemies[:]:
        enemy.move()
        enemy.shoot()
        enemy.draw()
        if enemy.collides_with(GameObject(player_x, player_y, player_size, player_img, 0)) and not powerup_active["shield"]:
            health -= 30
            enemy.reset()
            for _ in range(20):
                particles.append(Particle(enemy.x + enemy.size//2, enemy.y + enemy.size//2, RED))
        for bullet in bullets[:]:
            if enemy.collides_with(bullet):
                score += 200
                for _ in range(20):
                    particles.append(Particle(enemy.x + enemy.size//2, enemy.y + enemy.size//2, RED))
                enemy.reset()
                bullets.remove(bullet)

    # Move and draw power-ups
    for powerup in powerups[:]:
        powerup.move()
        powerup.draw()
        if powerup.collides_with(GameObject(player_x, player_y, player_size, player_img, 0)):
            if powerup.type == "fuel":
                fuel = min(100, fuel + 50)
            elif powerup.type == "speed":
                powerup_active["speed"] = True
                powerup_timer = 0
            elif powerup.type == "score":
                score += 500
            elif powerup.type == "shield":
                powerup_active["shield"] = True
                powerup_timer = 0
            powerups.remove(powerup)

    # Draw player and shield effect
    if player_img:
        screen.blit(player_img, (player_x, player_y))
    else:
        pygame.draw.rect(screen, YELLOW, (player_x, player_y, player_size, player_size))
    if powerup_active["shield"]:
        pygame.draw.circle(screen, CYAN, (int(player_x + player_size//2), int(player_y + player_size//2)), player_size, 2)

    # Update score and display
    total_score = score + distance
    score_text = font.render(f"Score: {total_score}", True, WHITE)
    fuel_text = font.render(f"Fuel: {int(fuel)}%", True, WHITE)
    health_text = font.render(f"Health: {int(health)}%", True, WHITE)
    high_score_text = font.render(f"High Score: {high_score}", True, WHITE)
    level_text = font.render(f"Level: {level}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(fuel_text, (10, 50))
    screen.blit(health_text, (10, 90))
    screen.blit(high_score_text, (10, 130))
    screen.blit(level_text, (10, 170))

    pygame.display.flip()
    clock.tick(60)

# Game over and high score handling
if total_score > high_score:
    high_score = total_score
    with open("highscore.txt", "w") as f:
        f.write(str(high_score))

game_over_text = font.render(f"Game Over! Final Score: {total_score}", True, WHITE)
screen.blit(game_over_text, (WIDTH//2 - 150, HEIGHT//2))
pygame.display.flip()
pygame.time.wait(2000)

pygame.quit()