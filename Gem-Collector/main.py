import pygame
import sys
import random
import time

# Constants
CELL_SIZE = 40
BLACK = (0, 0, 0)      # Background
GRAY = (100, 100, 100)  # Walls
RED = (255, 0, 0)       # Red gems (10 points)
BLUE = (0, 0, 255)     # Blue gems (20 points)
YELLOW = (255, 255, 0)  # Invincibility power-up
ORANGE = (255, 165, 0)  # Speed boost power-up
GREEN = (0, 255, 0)    # Player
PURPLE = (128, 0, 128) # Monsters
WHITE = (255, 255, 255) # Text

# Maze definitions for levels
mazes = [
    # Level 1: 10x10
    [
        [1,1,1,1,1,1,1,1,1,1],
        [1,0,2,0,0,0,0,0,0,1],
        [1,0,1,0,1,0,1,1,0,1],
        [1,0,1,0,0,0,0,1,0,1],
        [1,0,1,1,1,1,0,1,0,1],
        [1,0,0,0,0,1,0,1,0,1],
        [1,0,1,1,0,1,0,1,0,1],
        [1,0,0,0,0,0,0,0,3,1],
        [1,1,1,1,1,1,1,1,1,1]
    ],
    # Level 2: 12x12, more complexity
    [
        [1,1,1,1,1,1,1,1,1,1,1,1],
        [1,0,2,0,0,1,0,0,0,0,0,1],
        [1,0,1,1,0,1,0,1,1,0,1,1],
        [1,0,0,0,0,0,0,0,1,0,0,1],
        [1,1,1,0,1,1,0,1,1,1,0,1],
        [1,0,0,0,0,1,0,0,0,0,0,1],
        [1,0,1,1,0,1,1,1,0,1,0,1],
        [1,0,1,0,0,0,0,1,0,1,0,1],
        [1,0,1,0,1,1,0,1,0,1,0,1],
        [1,0,0,0,0,1,0,0,0,0,3,1],
        [1,1,1,1,1,1,1,1,1,1,1,1]
    ]
]

# Monster definitions per level (position and initial direction)
monsters_per_level = [
    [{'pos': [1, 3], 'dir': [0, 1]}, {'pos': [5, 1], 'dir': [1, 0]}],  # Level 1
    [{'pos': [1, 4], 'dir': [0, 1]}, {'pos': [5, 1], 'dir': [1, 0]}, {'pos': [7, 3], 'dir': [0, -1]}]  # Level 2
]

# Initialize Pygame
pygame.init()
pygame.mixer.init()  # Initialize sound
screen = pygame.display.set_mode((len(mazes[0][0]) * CELL_SIZE, len(mazes[0]) * CELL_SIZE + 50))
pygame.display.set_caption("Dungeon Gem Collector")
font = pygame.font.Font(None, 36)
clock = pygame.time.Clock()

# Sound effects (replace with actual sound files if available)
try:
    gem_sound = pygame.mixer.Sound("gem.wav")  # Placeholder: add a gem sound file
    hit_sound = pygame.mixer.Sound("hit.wav")  # Placeholder: add a hit sound file
    level_sound = pygame.mixer.Sound("level.wav")  # Placeholder: add a level sound file
except:
    # Fallback: silent if sound files are missing
    gem_sound = hit_sound = level_sound = pygame.mixer.Sound(pygame.mixer.Sound(buffer=b'\0' * 1000))

# Game state
class GameState:
    def __init__(self):
        self.level = 0
        self.maze = mazes[self.level]
        self.player_pos = [CELL_SIZE, CELL_SIZE]  # Start at (1,1) in pixels
        self.monsters = [dict(m) for m in monsters_per_level[self.level]]  # Copy to avoid modifying original
        for m in self.monsters:
            m['pos'] = [m['pos'][0] * CELL_SIZE, m['pos'][1] * CELL_SIZE]  # Convert to pixels
        self.score = 0
        self.lives = 3
        self.invincible = False
        self.invincible_time = 0
        self.speed_boost = False
        self.speed_boost_time = 0
        self.gems_collected = 0
        self.initial_gems = self.total_gems()
        self.walls = self.generate_walls()
        self.gems = self.generate_gems()
        self.power_ups = self.generate_power_ups()
        self.state = "playing"  # "playing", "level_complete", "game_over", "victory"

    def total_gems(self):
        return sum(row.count(2) + row.count(3) for row in self.maze)

    def generate_walls(self):
        walls = []
        for row in range(len(self.maze)):
            for col in range(len(self.maze[0])):
                if self.maze[row][col] == 1:
                    walls.append(pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        return walls

    def generate_gems(self):
        gems = []
        for row in range(len(self.maze)):
            for col in range(len(self.maze[0])):
                if self.maze[row][col] == 2:
                    gems.append({'rect': pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE), 'value': 10, 'color': RED})
                elif self.maze[row][col] == 3:
                    gems.append({'rect': pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE), 'value': 20, 'color': BLUE})
        return gems

    def generate_power_ups(self):
        power_ups = []
        empty_cells = [(r, c) for r in range(len(self.maze)) for c in range(len(self.maze[0])) if self.maze[r][c] == 0]
        if empty_cells and random.random() < 0.5:  # 50% chance to spawn a power-up
            r, c = random.choice(empty_cells)
            type_ = random.choice(["invincibility", "speed"])
            color = YELLOW if type_ == "invincibility" else ORANGE
            power_ups.append({'rect': pygame.Rect(c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE), 'type': type_, 'color': color})
        return power_ups

game = GameState()

def move_player(dx, dy):
    """Move player with collision detection."""
    global game
    speed = 5 if game.speed_boost else 3
    new_x = game.player_pos[0] + dx * speed
    new_y = game.player_pos[1] + dy * speed
    new_rect = pygame.Rect(new_x, new_y, CELL_SIZE - 5, CELL_SIZE - 5)  # Slightly smaller for smoother movement
    if not any(new_rect.colliderect(wall) for wall in game.walls):
        game.player_pos = [new_x, new_y]

def move_monsters():
    """Move monsters with patrolling and chasing behavior."""
    player_rect = pygame.Rect(game.player_pos[0], game.player_pos[1], CELL_SIZE, CELL_SIZE)
    for monster in game.monsters:
        mx, my = monster['pos']
        px, py = game.player_pos
        dist = ((mx - px) ** 2 + (my - py) ** 2) ** 0.5
        speed = 2
        if dist < 5 * CELL_SIZE:  # Chase if within 5 cells
            dx = speed if px > mx else -speed if px < mx else 0
            dy = speed if py > my else -speed if py < my else 0
        else:  # Patrol
            dx, dy = monster['dir'][0] * speed, monster['dir'][1] * speed
        
        new_x = mx + dx
        new_y = my + dy
        new_rect = pygame.Rect(new_x, new_y, CELL_SIZE, CELL_SIZE)
        if not any(new_rect.colliderect(wall) for wall in game.walls):
            monster['pos'] = [new_x, new_y]
        else:
            monster['dir'] = [-monster['dir'][0], -monster['dir'][1]]  # Reverse direction

def check_collisions():
    """Handle gem collection, power-ups, and monster collisions."""
    global game
    player_rect = pygame.Rect(game.player_pos[0], game.player_pos[1], CELL_SIZE, CELL_SIZE)
    
    # Gems
    for gem in game.gems[:]:
        if player_rect.colliderect(gem['rect']):
            game.score += gem['value']
            game.gems_collected += 1
            game.gems.remove(gem)
            gem_sound.play()
    
    # Power-ups
    for power_up in game.power_ups[:]:
        if player_rect.colliderect(power_up['rect']):
            if power_up['type'] == "invincibility":
                game.invincible = True
                game.invincible_time = time.time() + 5  # 5 seconds
            elif power_up['type'] == "speed":
                game.speed_boost = True
                game.speed_boost_time = time.time() + 5  # 5 seconds
            game.power_ups.remove(power_up)
    
    # Monsters
    if not game.invincible:
        for monster in game.monsters:
            monster_rect = pygame.Rect(monster['pos'][0], monster['pos'][1], CELL_SIZE, CELL_SIZE)
            if player_rect.colliderect(monster_rect):
                game.lives -= 1
                hit_sound.play()
                if game.lives <= 0:
                    game.state = "game_over"
                return

    # Level completion
    if game.gems_collected == game.initial_gems:
        game.state = "level_complete"
        level_sound.play()

def update_power_ups():
    """Update power-up timers."""
    if game.invincible and time.time() > game.invincible_time:
        game.invincible = False
    if game.speed_boost and time.time() > game.speed_boost_time:
        game.speed_boost = False

def next_level():
    """Advance to the next level."""
    global game
    if game.level + 1 < len(mazes):
        game.level += 1
        game.maze = mazes[game.level]
        game.player_pos = [CELL_SIZE, CELL_SIZE]
        game.monsters = [dict(m) for m in monsters_per_level[game.level]]
        for m in game.monsters:
            m['pos'] = [m['pos'][0] * CELL_SIZE, m['pos'][1] * CELL_SIZE]
        game.walls = game.generate_walls()
        game.gems = game.generate_gems()
        game.power_ups = game.generate_power_ups()
        game.initial_gems = game.total_gems()
        game.gems_collected = 0
        game.state = "playing"
        screen = pygame.display.set_mode((len(game.maze[0]) * CELL_SIZE, len(game.maze) * CELL_SIZE + 50))
    else:
        game.state = "victory"

# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if game.state == "game_over" and event.key == pygame.K_r:
                game = GameState()  # Restart
            elif game.state == "victory" and event.key == pygame.K_r:
                game = GameState()  # Restart

    if game.state == "playing":
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            move_player(0, -1)
        if keys[pygame.K_DOWN]:
            move_player(0, 1)
        if keys[pygame.K_LEFT]:
            move_player(-1, 0)
        if keys[pygame.K_RIGHT]:
            move_player(1, 0)
        
        move_monsters()
        check_collisions()
        update_power_ups()

    # Draw
    screen.fill(BLACK)
    # Walls
    for wall in game.walls:
        pygame.draw.rect(screen, GRAY, wall)
    # Gems
    for gem in game.gems:
        pygame.draw.circle(screen, gem['color'], gem['rect'].center, CELL_SIZE // 4)
    # Power-ups
    for power_up in game.power_ups:
        pygame.draw.circle(screen, power_up['color'], power_up['rect'].center, CELL_SIZE // 4)
    # Player
    player_color = GREEN if not game.invincible else (GREEN[0], GREEN[1], GREEN[2], 128)  # Semi-transparent when invincible
    pygame.draw.circle(screen, player_color, (int(game.player_pos[0] + CELL_SIZE / 2), int(game.player_pos[1] + CELL_SIZE / 2)), CELL_SIZE // 3)
    # Monsters
    for monster in game.monsters:
        pygame.draw.rect(screen, PURPLE, (monster['pos'][0], monster['pos'][1], CELL_SIZE, CELL_SIZE))
    
    # UI
    score_text = font.render(f"Score: {game.score}", True, WHITE)
    lives_text = font.render(f"Lives: {game.lives}", True, WHITE)
    screen.blit(score_text, (10, len(game.maze) * CELL_SIZE + 10))
    screen.blit(lives_text, (len(game.maze[0]) * CELL_SIZE // 2, len(game.maze) * CELL_SIZE + 10))

    # State screens
    if game.state == "level_complete":
        text = font.render("Level Complete!", True, WHITE)
        screen.blit(text, (len(game.maze[0]) * CELL_SIZE // 2 - text.get_width() // 2, len(game.maze) * CELL_SIZE // 2))
        pygame.display.flip()
        pygame.time.wait(2000)  # Wait 2 seconds
        next_level()
    elif game.state == "game_over":
        text = font.render("Game Over! Press R to Restart", True, WHITE)
        screen.blit(text, (len(game.maze[0]) * CELL_SIZE // 2 - text.get_width() // 2, len(game.maze) * CELL_SIZE // 2))
    elif game.state == "victory":
        text = font.render("You Win! Press R to Restart", True, WHITE)
        screen.blit(text, (len(game.maze[0]) * CELL_SIZE // 2 - text.get_width() // 2, len(game.maze) * CELL_SIZE // 2))

    pygame.display.flip()
    clock.tick(60)  # 60 FPS