import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Constants
TILE_SIZE = 16  # Increased for larger window
WIDTH, HEIGHT = 28 * TILE_SIZE, 36 * TILE_SIZE  # 448x576 (portrait)
FPS = 30

# Colors (exact matches to original Pac-Man)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
PINK = (255, 184, 255)
CYAN = (0, 255, 255)
ORANGE = (255, 184, 81)
BLUE = (0, 0, 255)
DARK_BLUE = (33, 33, 255)

# Original maze layout
original_maze = [
    "############################",
    "#............##............#",
    "#.####.#####.##.#####.####.#",
    "#P#  #.#   #.##.#   #.#  #P#",
    "#.####.#####.##.#####.####.#",
    "#..........................#",
    "#.####.##.########.##.####.#",
    "#......##....##....##......#",
    "######.##### ## #####.######",
    "     #.#     G      #.#     ",
    "######.# ##### ######.# #####",
    "      .  #          #  .     ",
    "######.# ##### ######.# #####",
    "#............##............#",
    "#.####.#####.##.#####.####.#",
    "#P..##.......  .......##..P#",
    "#.####.#####.##.#####.####.#",
    "#..........................#",
    "############################",
]


# Player class
class Player:
    def __init__(self, x, y):
        self.grid_x = x  # Grid-based position
        self.grid_y = y
        self.direction = (1, 0)  # Start facing right
        self.next_direction = (1, 0)
        self.speed = 1  # Move one tile at a time
        self.score = 0
        self.lives = 3
        self.frame = 0

    def move(self, maze):
        # Check if next direction is valid
        next_x = self.grid_x + self.next_direction[0]
        next_y = self.grid_y + self.next_direction[1]
        if 0 <= next_x < 28 and 0 <= next_y < len(maze) and maze[next_y][next_x] != "#":
            self.direction = self.next_direction
            self.grid_x = next_x
            self.grid_y = next_y

        # Wrap-around tunnels
        if self.grid_x < 0:
            self.grid_x = 27
        elif self.grid_x >= 28:
            self.grid_x = 0

        # Eat dots or power pellets
        if maze[self.grid_y][self.grid_x] in (".", "P"):
            if maze[self.grid_y][self.grid_x] == ".":
                self.score += 10
            elif maze[self.grid_y][self.grid_x] == "P":
                self.score += 50
                for ghost in ghosts:
                    ghost.frightened = True
                    ghost.frightened_timer = 240
            maze[self.grid_y][self.grid_x] = " "
            global dot_count
            dot_count -= 1

    def draw(self, screen):
        self.frame = (self.frame + 1) % 10
        center = (
            self.grid_x * TILE_SIZE + TILE_SIZE // 2,
            self.grid_y * TILE_SIZE + TILE_SIZE // 2,
        )
        if self.frame < 5 or self.direction == (0, 0):
            pygame.draw.circle(screen, YELLOW, center, TILE_SIZE // 2)
        else:
            direction_angles = {(-1, 0): 0.5, (1, 0): 2.5, (0, -1): 1, (0, 1): 4}
            start_angle = direction_angles[self.direction]
            pygame.draw.arc(
                screen,
                YELLOW,
                (
                    center[0] - TILE_SIZE // 2,
                    center[1] - TILE_SIZE // 2,
                    TILE_SIZE,
                    TILE_SIZE,
                ),
                start_angle,
                start_angle + 1,
                TILE_SIZE,
            )


# Ghost class
class Ghost:
    def __init__(self, x, y, color, name):
        self.grid_x = x
        self.grid_y = y
        self.color = color
        self.name = name
        self.direction = (0, -1)  # Start moving up
        self.speed = 1
        self.frightened = False
        self.frightened_timer = 0

    def move(self, target_x, target_y):
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        valid_directions = []
        for d in directions:
            new_x = self.grid_x + d[0]
            new_y = self.grid_y + d[1]
            if 0 <= new_x < 28 and 0 <= new_y < len(maze) and maze[new_y][new_x] != "#":
                valid_directions.append(d)

        if not valid_directions:  # Avoid getting stuck
            return

        if self.frightened and self.frightened_timer > 0:
            self.frightened_timer -= 1
            if self.frightened_timer == 0:
                self.frightened = False
            self.direction = random.choice(valid_directions)
        else:
            # Simplified ghost AI
            if self.name == "Blinky":
                dx, dy = target_x - self.grid_x, target_y - self.grid_y
            elif self.name == "Pinky":
                dx, dy = (target_x + 4 * pacman.direction[0]) - self.grid_x, (
                    target_y + 4 * pacman.direction[1]
                ) - self.grid_y
            elif self.name == "Inky":
                dx, dy = (target_x + 2 * pacman.direction[0]) - self.grid_x, (
                    target_y + 2 * pacman.direction[1]
                ) - self.grid_y
            else:  # Clyde
                dist = abs(target_x - self.grid_x) + abs(target_y - self.grid_y)
                dx, dy = (
                    (27 - self.grid_x, 17 - self.grid_y)
                    if dist < 8
                    else (target_x - self.grid_x, target_y - self.grid_y)
                )

            best_direction = self.direction
            min_dist = float("inf")
            for d in valid_directions:
                new_x = self.grid_x + d[0]
                new_y = self.grid_y + d[1]
                dist = abs(new_x - (self.grid_x + dx)) + abs(new_y - (self.grid_y + dy))
                if dist < min_dist and d != (
                    -self.direction[0],
                    -self.direction[1],
                ):  # No U-turns
                    min_dist = dist
                    best_direction = d
            self.direction = best_direction

        self.grid_x += self.direction[0]
        self.grid_y += self.direction[1]

        # Wrap-around tunnels
        if self.grid_x < 0:
            self.grid_x = 27
        elif self.grid_x >= 28:
            self.grid_x = 0

    def draw(self, screen):
        color = BLUE if self.frightened else self.color
        body = pygame.Rect(
            self.grid_x * TILE_SIZE, self.grid_y * TILE_SIZE, TILE_SIZE, TILE_SIZE
        )
        pygame.draw.rect(screen, color, body)
        pygame.draw.polygon(
            screen,
            color,
            [
                (body.left, body.bottom),
                (body.left + TILE_SIZE // 4, body.bottom - TILE_SIZE // 4),
                (body.left + TILE_SIZE // 2, body.bottom),
                (body.left + 3 * TILE_SIZE // 4, body.bottom - TILE_SIZE // 4),
                (body.right, body.bottom),
            ],
        )
        eye_color = WHITE if not self.frightened else BLACK
        pupil_color = BLACK if not self.frightened else BLUE
        eye_x_offset = (
            TILE_SIZE * 0.3
            if self.direction[0] > 0
            else -TILE_SIZE * 0.3 if self.direction[0] < 0 else 0
        )
        eye_y_offset = (
            TILE_SIZE * 0.3
            if self.direction[1] > 0
            else -TILE_SIZE * 0.3 if self.direction[1] < 0 else 0
        )
        pygame.draw.circle(
            screen,
            eye_color,
            (
                int(body.left + TILE_SIZE * 0.5 - eye_x_offset),
                int(body.top + TILE_SIZE * 0.3 - eye_y_offset),
            ),
            4,
        )
        pygame.draw.circle(
            screen,
            eye_color,
            (
                int(body.right - TILE_SIZE * 0.5 - eye_x_offset),
                int(body.top + TILE_SIZE * 0.3 - eye_y_offset),
            ),
            4,
        )
        pygame.draw.circle(
            screen,
            pupil_color,
            (
                int(body.left + TILE_SIZE * 0.5 - eye_x_offset),
                int(body.top + TILE_SIZE * 0.3 - eye_y_offset),
            ),
            2,
        )
        pygame.draw.circle(
            screen,
            pupil_color,
            (
                int(body.right - TILE_SIZE * 0.5 - eye_x_offset),
                int(body.top + TILE_SIZE * 0.3 - eye_y_offset),
            ),
            2,
        )


# Initialize game
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pac-Man")
clock = pygame.time.Clock()


# Setup game state
def reset_game():
    global maze, pacman, ghosts, dot_count
    maze = [list(row) for row in original_maze]
    pacman_start = (13, 13)  # Center-ish starting position
    ghost_starts = [(13, 9), (14, 9), (13, 10), (14, 10)]  # Spread out ghosts
    dot_count = sum(row.count(".") + row.count("P") for row in maze)
    pacman = Player(pacman_start[0], pacman_start[1])
    ghosts = [
        Ghost(ghost_starts[0][0], ghost_starts[0][1], RED, "Blinky"),
        Ghost(ghost_starts[1][0], ghost_starts[1][1], PINK, "Pinky"),
        Ghost(ghost_starts[2][0], ghost_starts[2][1], CYAN, "Inky"),
        Ghost(ghost_starts[3][0], ghost_starts[3][1], ORANGE, "Clyde"),
    ]
    return False  # game_over = False


# Initial game setup
game_over = reset_game()
font = pygame.font.SysFont(None, 36)

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                pacman.next_direction = (0, -1)
            elif event.key == pygame.K_DOWN:
                pacman.next_direction = (0, 1)
            elif event.key == pygame.K_LEFT:
                pacman.next_direction = (-1, 0)
            elif event.key == pygame.K_RIGHT:
                pacman.next_direction = (1, 0)
            elif event.key == pygame.K_r and game_over:
                game_over = reset_game()

    if not game_over:
        # Update game state (once every 3 frames for smoother pacing)
        if pygame.time.get_ticks() % 3 == 0:
            pacman.move(maze)
            for ghost in ghosts:
                ghost.move(pacman.grid_x, pacman.grid_y)

            # Collision with ghosts
            for ghost in ghosts:
                if (ghost.grid_x, ghost.grid_y) == (pacman.grid_x, pacman.grid_y):
                    if ghost.frightened:
                        ghost.grid_x, ghost.grid_y = ghost_starts[0]
                        pacman.score += 200
                    else:
                        pacman.lives -= 1
                        pacman.grid_x, pacman.grid_y = pacman_start
                        if pacman.lives <= 0:
                            game_over = True

            # Level completion
            if dot_count == 0:
                game_over = True

    # Draw everything
    screen.fill(BLACK)
    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            if cell == "#":
                pygame.draw.rect(
                    screen,
                    DARK_BLUE,
                    (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE),
                )
            elif cell == ".":
                pygame.draw.circle(
                    screen,
                    WHITE,
                    (x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE // 2),
                    2,
                )
            elif cell == "P":
                pygame.draw.circle(
                    screen,
                    WHITE,
                    (x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE // 2),
                    5,
                )

    pacman.draw(screen)
    for ghost in ghosts:
        ghost.draw(screen)

    score_text = font.render(f"Score: {pacman.score}", True, WHITE)
    lives_text = font.render(f"Lives: {pacman.lives}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(lives_text, (WIDTH - 120, 10))

    if game_over:
        win_text = "You Win!" if dot_count == 0 else "Game Over!"
        game_over_text = font.render(f"{win_text} Press R to Restart", True, WHITE)
        screen.blit(game_over_text, (WIDTH // 2 - 150, HEIGHT // 2))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
