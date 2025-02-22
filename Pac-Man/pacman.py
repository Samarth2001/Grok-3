import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Constants
TILE_SIZE = 20
MAZE_WIDTH, MAZE_HEIGHT = 19, 31  # Adjusted for portrait, matching classic layout
WINDOW_WIDTH, WINDOW_HEIGHT = MAZE_WIDTH * TILE_SIZE, (
    MAZE_HEIGHT * TILE_SIZE + 50
)  # 380x670, with 50px for UI
FPS = 30

# Colors (strong, vibrant palette like original Pac-Man)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
PINK = (255, 105, 180)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
BLUE = (0, 0, 255)
NAVY_BLUE = (0, 0, 139)  # Strong blue for walls

# Classic Pac-Man maze layout (19x31, portrait-oriented, adjusted for open paths)
original_maze = [
    "###################",
    "#............##...#",
    "#.####.#####.##.##.#",
    "#P#  #.#   #.##.# #P#",
    "#.####.#####.##.####.#",
    "#........................#",
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
    "###################",
]

# Global starting positions (adjusted for new maze)
pacman_start = (9, 15)  # Center-ish in the maze
ghost_starts = [(9, 9), (10, 9), (9, 10), (10, 10)]


# Player class
class Player:
    def __init__(self, x, y):
        self.grid_x = x
        self.grid_y = y
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.score = 0
        self.lives = 3
        self.frame = 0
        self.move_timer = 0

    def move(self, maze):
        self.move_timer += 1
        if self.move_timer < 6:
            return
        self.move_timer = 0

        # Try next direction
        next_x = self.grid_x + self.next_direction[0]
        next_y = self.grid_y + self.next_direction[1]
        if (
            0 <= next_x < MAZE_WIDTH
            and 0 <= next_y < len(maze)
            and maze[next_y][next_x] != "#"
        ):
            self.direction = self.next_direction
            self.grid_x = next_x
            self.grid_y = next_y
        else:
            # Continue in current direction
            next_x = self.grid_x + self.direction[0]
            next_y = self.grid_y + self.direction[1]
            if (
                0 <= next_x < MAZE_WIDTH
                and 0 <= next_y < len(maze)
                and maze[next_y][next_x] != "#"
            ):
                self.grid_x = next_x
                self.grid_y = next_y

        # Wrap-around tunnels
        if self.grid_x < 0:
            self.grid_x = MAZE_WIDTH - 1
        elif self.grid_x >= MAZE_WIDTH:
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

    def draw(self, screen, offset_y=50):
        self.frame = (self.frame + 1) % 10
        center = (
            self.grid_x * TILE_SIZE + TILE_SIZE // 2,
            self.grid_y * TILE_SIZE + TILE_SIZE // 2 + offset_y,
        )
        if self.frame < 5 or self.direction == (0, 0):
            pygame.draw.circle(screen, YELLOW, center, TILE_SIZE // 2 - 2)
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
                TILE_SIZE - 4,
            )


# Ghost class
class Ghost:
    def __init__(self, x, y, color, name):
        self.grid_x = x
        self.grid_y = y
        self.color = color
        self.name = name
        self.direction = (0, -1)
        self.frightened = False
        self.frightened_timer = 0
        self.move_timer = 0
        self.mode = "chase"
        self.mode_timer = 0

    def move(self, target_x, target_y):
        self.move_timer += 1
        if self.move_timer < 6:
            return
        self.move_timer = 0

        self.mode_timer += 1
        if self.mode_timer >= 300:
            self.mode = "scatter" if self.mode == "chase" else "chase"
            self.mode_timer = 0

        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        valid_directions = []
        for d in directions:
            new_x = self.grid_x + d[0]
            new_y = self.grid_y + d[1]
            if (
                0 <= new_x < MAZE_WIDTH
                and 0 <= new_y < len(maze)
                and maze[new_y][new_x] != "#"
            ):
                valid_directions.append(d)

        if not valid_directions:
            return

        if self.frightened and self.frightened_timer > 0:
            self.frightened_timer -= 1
            if self.frightened_timer == 0:
                self.frightened = False
            self.direction = random.choice(valid_directions)
        else:
            if self.mode == "scatter":
                scatter_targets = {
                    "Blinky": (18, 0),
                    "Pinky": (0, 0),
                    "Inky": (18, 30),
                    "Clyde": (0, 30),
                }
                tx, ty = scatter_targets[self.name]
            else:
                if self.name == "Blinky":
                    tx, ty = target_x, target_y
                elif self.name == "Pinky":
                    tx = min(max(target_x + 4 * pacman.direction[0], 0), MAZE_WIDTH - 1)
                    ty = min(max(target_y + 4 * pacman.direction[1], 0), len(maze) - 1)
                elif self.name == "Inky":
                    tx = min(max(target_x + 2 * pacman.direction[0], 0), MAZE_WIDTH - 1)
                    ty = min(max(target_y + 2 * pacman.direction[1], 0), len(maze) - 1)
                else:  # Clyde
                    dist = abs(target_x - self.grid_x) + abs(target_y - self.grid_y)
                    tx, ty = (0, 30) if dist < 8 else (target_x, target_y)

            best_direction = self.direction
            min_dist = float("inf")
            for d in valid_directions:
                new_x = self.grid_x + d[0]
                new_y = self.grid_y + d[1]
                dist = abs(new_x - tx) + abs(new_y - ty)
                if dist < min_dist and d != (-self.direction[0], -self.direction[1]):
                    min_dist = dist
                    best_direction = d
            self.direction = best_direction

        # Update position with bounds check
        new_x = self.grid_x + self.direction[0]
        new_y = self.grid_y + self.direction[1]
        if (
            0 <= new_x < MAZE_WIDTH
            and 0 <= new_y < len(maze)
            and maze[new_y][new_x] != "#"
        ):
            self.grid_x = new_x
            self.grid_y = new_y

        # Wrap-around tunnels
        if self.grid_x < 0:
            self.grid_x = MAZE_WIDTH - 1
        elif self.grid_x >= MAZE_WIDTH:
            self.grid_x = 0

    def draw(self, screen, offset_y=50):
        color = BLUE if self.frightened else self.color
        center = (
            self.grid_x * TILE_SIZE + TILE_SIZE // 2,
            self.grid_y * TILE_SIZE + TILE_SIZE // 2 + offset_y,
        )
        pygame.draw.circle(screen, color, center, TILE_SIZE // 2 - 2)
        eye_x_offset = (
            TILE_SIZE * 0.2
            if self.direction[0] > 0
            else -TILE_SIZE * 0.2 if self.direction[0] < 0 else 0
        )
        eye_y_offset = (
            TILE_SIZE * 0.2
            if self.direction[1] > 0
            else -TILE_SIZE * 0.2 if self.direction[1] < 0 else 0
        )
        pygame.draw.circle(
            screen,
            WHITE,
            (
                int(center[0] - TILE_SIZE * 0.2 - eye_x_offset),
                int(center[1] - eye_y_offset),
            ),
            4,
        )
        pygame.draw.circle(
            screen,
            WHITE,
            (
                int(center[0] + TILE_SIZE * 0.2 - eye_x_offset),
                int(center[1] - eye_y_offset),
            ),
            4,
        )
        pygame.draw.circle(
            screen,
            BLACK,
            (
                int(center[0] - TILE_SIZE * 0.2 - eye_x_offset),
                int(center[1] - eye_y_offset),
            ),
            2,
        )
        pygame.draw.circle(
            screen,
            BLACK,
            (
                int(center[0] + TILE_SIZE * 0.2 - eye_x_offset),
                int(center[1] - eye_y_offset),
            ),
            2,
        )


# Initialize game
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Pac-Man")
clock = pygame.time.Clock()


# Setup game state
def reset_game():
    global maze, pacman, ghosts, dot_count
    maze = [list(row) for row in original_maze]
    dot_count = sum(row.count(".") + row.count("P") for row in maze)
    pacman = Player(pacman_start[0], pacman_start[1])
    ghosts = [
        Ghost(ghost_starts[0][0], ghost_starts[0][1], RED, "Blinky"),
        Ghost(ghost_starts[1][0], ghost_starts[1][1], PINK, "Pinky"),
        Ghost(ghost_starts[2][0], ghost_starts[2][1], CYAN, "Inky"),
        Ghost(ghost_starts[3][0], ghost_starts[3][1], ORANGE, "Clyde"),
    ]
    return False


# Initial setup
game_over = reset_game()
font = pygame.font.SysFont(None, 28)

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
        pacman.move(maze)
        for ghost in ghosts:
            ghost.move(pacman.grid_x, pacman.grid_y)

        # Collision with ghosts
        for ghost in ghosts:
            if (ghost.grid_x, ghost.grid_y) == (pacman.grid_x, pacman.grid_y):
                if ghost.frightened:
                    ghost.grid_x, ghost.grid_y = ghost_starts[ghosts.index(ghost)]
                    ghost.frightened = False
                    ghost.frightened_timer = 0
                    pacman.score += 200
                else:
                    pacman.lives -= 1
                    pacman.grid_x, pacman.grid_y = pacman_start
                    if pacman.lives <= 0:
                        game_over = True

        if dot_count == 0:
            game_over = True

    # Draw everything
    screen.fill(BLACK)
    MAZE_OFFSET_Y = (
        WINDOW_HEIGHT - MAZE_HEIGHT * TILE_SIZE
    ) // 2  # Center maze vertically
    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            if cell == "#":
                pygame.draw.rect(
                    screen,
                    NAVY_BLUE,
                    (
                        x * TILE_SIZE,
                        y * TILE_SIZE + MAZE_OFFSET_Y,
                        TILE_SIZE,
                        TILE_SIZE,
                    ),
                    border_radius=4,
                )
            elif cell == ".":
                pygame.draw.circle(
                    screen,
                    WHITE,
                    (
                        x * TILE_SIZE + TILE_SIZE // 2,
                        y * TILE_SIZE + TILE_SIZE // 2 + MAZE_OFFSET_Y,
                    ),
                    3,
                )
            elif cell == "P":
                pygame.draw.circle(
                    screen,
                    WHITE,
                    (
                        x * TILE_SIZE + TILE_SIZE // 2,
                        y * TILE_SIZE + TILE_SIZE // 2 + MAZE_OFFSET_Y,
                    ),
                    6,
                )

    pacman.draw(screen, MAZE_OFFSET_Y)
    for ghost in ghosts:
        ghost.draw(screen, MAZE_OFFSET_Y)

    score_text = font.render(f"Score: {pacman.score}", True, WHITE)
    lives_text = font.render(f"Lives: {pacman.lives}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(lives_text, (WINDOW_WIDTH - 100, 10))

    if game_over:
        win_text = "You Win!" if dot_count == 0 else "Game Over!"
        game_over_text = font.render(f"{win_text} Press R to Restart", True, WHITE)
        screen.blit(game_over_text, (WINDOW_WIDTH // 2 - 120, WINDOW_HEIGHT // 2))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
