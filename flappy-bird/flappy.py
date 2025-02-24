import pygame
import random
import os

pygame.init()

# Constants
WIDTH = 400
HEIGHT = 600
FPS = 60
GRAVITY = 1000
FLAP_POWER = -300
PIPE_SPEED = 200
PIPE_SPACING = 300
PIPE_GAP = 150
PIPE_WIDTH = 80
BIRD_SIZE = 30
GAP_BUFFER = 50

# Colors
BACKGROUND_COLOR = (139, 69, 19)  # Brown for cave theme
GROUND_COLOR = (34, 139, 34)  # Green for ground
BIRD_COLOR = (255, 215, 0)  # Yellow for bird
PIPE_COLOR = (107, 142, 35)  # Olive green for pipes
TEXT_COLOR = (245, 245, 245)  # Off-white for text

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird - Retro Cave Theme")
clock = pygame.time.Clock()


class Bird:
    def __init__(self):
        self.reset()
        self.flapping = False

    def reset(self):
        self.x = 100
        self.y = 300
        self.velocity = 0
        self.flapping = False

    def flap(self):
        self.velocity = FLAP_POWER
        self.flapping = True

    def update(self, dt):
        self.velocity += GRAVITY * dt
        self.y += self.velocity * dt
        if self.y < 0:
            self.y = 0
            self.velocity = 0
        if self.flapping:
            self.flapping = False  # Reset after one frame

    def draw(self, screen):
        # Draw bird: circle for body, triangles for wings and beak
        wing_offset = 5 if self.flapping else 0
        # Left wing
        pygame.draw.polygon(
            screen,
            BIRD_COLOR,
            [
                (self.x, self.y + BIRD_SIZE // 2),
                (self.x - 10, self.y + BIRD_SIZE // 2 - wing_offset),
                (self.x - 10, self.y + BIRD_SIZE // 2 + wing_offset),
            ],
        )
        # Right wing
        pygame.draw.polygon(
            screen,
            BIRD_COLOR,
            [
                (self.x + BIRD_SIZE, self.y + BIRD_SIZE // 2),
                (self.x + BIRD_SIZE + 10, self.y + BIRD_SIZE // 2 - wing_offset),
                (self.x + BIRD_SIZE + 10, self.y + BIRD_SIZE // 2 + wing_offset),
            ],
        )
        # Body
        pygame.draw.circle(
            screen,
            BIRD_COLOR,
            (int(self.x + BIRD_SIZE / 2), int(self.y + BIRD_SIZE / 2)),
            BIRD_SIZE // 2,
        )
        # Beak
        beak_points = [
            (self.x + BIRD_SIZE, self.y + BIRD_SIZE // 2),
            (self.x + BIRD_SIZE + 10, self.y + BIRD_SIZE // 2 - 5),
            (self.x + BIRD_SIZE + 10, self.y + BIRD_SIZE // 2 + 5),
        ]
        pygame.draw.polygon(screen, (255, 165, 0), beak_points)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, BIRD_SIZE, BIRD_SIZE)


class Pipe:
    def __init__(self, x):
        self.x = x
        min_gap_y = GAP_BUFFER + PIPE_GAP / 2
        max_gap_y = HEIGHT - GAP_BUFFER - PIPE_GAP / 2
        self.gap_y = random.randint(int(min_gap_y), int(max_gap_y))
        self.scored = False

    def update(self, dt):
        self.x -= PIPE_SPEED * dt

    def draw(self, screen):
        top_height = self.gap_y - PIPE_GAP / 2
        bottom_y = self.gap_y + PIPE_GAP / 2
        pygame.draw.polygon(
            screen,
            PIPE_COLOR,
            [
                (self.x, 0),
                (self.x + PIPE_WIDTH, 0),
                (self.x + PIPE_WIDTH / 2, top_height),
            ],
        )
        pygame.draw.polygon(
            screen,
            PIPE_COLOR,
            [
                (self.x, HEIGHT),
                (self.x + PIPE_WIDTH, HEIGHT),
                (self.x + PIPE_WIDTH / 2, bottom_y),
            ],
        )

    def get_rects(self):
        top_rect = pygame.Rect(self.x, 0, PIPE_WIDTH, self.gap_y - PIPE_GAP / 2)
        bottom_rect = pygame.Rect(
            self.x,
            self.gap_y + PIPE_GAP / 2,
            PIPE_WIDTH,
            HEIGHT - (self.gap_y + PIPE_GAP / 2),
        )
        return top_rect, bottom_rect


def draw_background(ground_x1, ground_x2, dt=None):
    screen.fill(BACKGROUND_COLOR)
    ground_height = 50
    pygame.draw.rect(
        screen, GROUND_COLOR, (ground_x1, HEIGHT - ground_height, WIDTH, ground_height)
    )
    pygame.draw.rect(
        screen, GROUND_COLOR, (ground_x2, HEIGHT - ground_height, WIDTH, ground_height)
    )
    if dt is not None:
        ground_x1 -= PIPE_SPEED * dt
        ground_x2 -= PIPE_SPEED * dt
        if ground_x1 <= -WIDTH:
            ground_x1 = ground_x2 + WIDTH
        if ground_x2 <= -WIDTH:
            ground_x2 = ground_x1 + WIDTH
    return ground_x1, ground_x2


def draw_title_screen(font):
    title_text = font.render("Flappy Bird - Retro Cave", True, TEXT_COLOR)
    start_text = font.render("Press any key to start", True, TEXT_COLOR)
    screen.blit(
        title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 50)
    )
    screen.blit(
        start_text, (WIDTH // 2 - start_text.get_width() // 2, HEIGHT // 2 + 10)
    )


def draw_start_screen(font):
    text1 = font.render("Press SPACE to Start", True, TEXT_COLOR)
    text2 = font.render("Flap: SPACE", True, TEXT_COLOR)
    screen.blit(text1, (WIDTH // 2 - text1.get_width() // 2, HEIGHT // 2 - 50))
    screen.blit(text2, (WIDTH // 2 - text2.get_width() // 2, HEIGHT // 2 + 10))


def draw_game_over_screen(font, score, high_score):
    game_over_text = font.render("Game Over", True, TEXT_COLOR)
    score_text = font.render(f"Score: {score}", True, TEXT_COLOR)
    high_score_text = font.render(f"High Score: {high_score}", True, TEXT_COLOR)
    restart_text = font.render("Press R to Restart", True, TEXT_COLOR)
    screen.blit(
        game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 75)
    )
    screen.blit(
        score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 - 25)
    )
    screen.blit(
        high_score_text,
        (WIDTH // 2 - high_score_text.get_width() // 2, HEIGHT // 2 + 25),
    )
    screen.blit(
        restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 75)
    )


def load_high_score():
    if os.path.exists("high_score.txt"):
        with open("high_score.txt", "r") as f:
            return int(f.read().strip())
    return 0


def save_high_score(score):
    with open("high_score.txt", "w") as f:
        f.write(str(score))


def main():
    bird = Bird()
    pipes = []
    score = 0
    high_score = load_high_score()
    game_state = "title"  # Start with title screen
    font = pygame.font.SysFont("comicsans", 30)
    time_between_pipes = (PIPE_SPACING / PIPE_SPEED) * 1000
    last_pipe_time = pygame.time.get_ticks() - time_between_pipes
    ground_x1, ground_x2 = 0, WIDTH
    score_scale = 1.0
    score_timer = 0

    while True:
        dt = clock.tick(FPS) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if game_state == "title":
                    game_state = "start"
                elif game_state == "start" and event.key == pygame.K_SPACE:
                    game_state = "playing"
                elif game_state == "playing" and event.key == pygame.K_SPACE:
                    bird.flap()
                elif game_state == "game_over" and event.key == pygame.K_r:
                    bird.reset()
                    pipes.clear()
                    score = 0
                    game_state = "start"
                    last_pipe_time = pygame.time.get_ticks() - time_between_pipes

        if game_state == "playing":
            bird.update(dt)
            for pipe in pipes:
                pipe.update(dt)
            current_time = pygame.time.get_ticks()
            if current_time - last_pipe_time > time_between_pipes:
                pipes.append(Pipe(WIDTH))
                last_pipe_time = current_time
            pipes = [pipe for pipe in pipes if pipe.x + PIPE_WIDTH > 0]
            for pipe in pipes:
                if not pipe.scored and pipe.x < bird.x:
                    score += 1
                    pipe.scored = True
                    score_scale = 1.5
                    score_timer = 0.2
            if bird.y + BIRD_SIZE > HEIGHT:
                game_state = "game_over"
            for pipe in pipes:
                top_rect, bottom_rect = pipe.get_rects()
                if bird.get_rect().colliderect(top_rect) or bird.get_rect().colliderect(
                    bottom_rect
                ):
                    game_state = "game_over"
            ground_x1, ground_x2 = draw_background(ground_x1, ground_x2, dt)
            score_timer -= dt
            if score_timer <= 0:
                score_scale = 1.0
        else:
            draw_background(ground_x1, ground_x2)

        if game_state == "title":
            draw_title_screen(font)
        elif game_state == "start":
            draw_start_screen(font)
        elif game_state == "playing":
            for pipe in pipes:
                pipe.draw(screen)
            bird.draw(screen)
            score_text = font.render(f"Score: {score}", True, TEXT_COLOR)
            scaled_text = pygame.transform.scale(
                score_text,
                (
                    int(score_text.get_width() * score_scale),
                    int(score_text.get_height() * score_scale),
                ),
            )
            screen.blit(scaled_text, (10, 10))
        elif game_state == "game_over":
            if score > high_score:
                high_score = score
                save_high_score(high_score)
            draw_game_over_screen(font, score, high_score)
        pygame.display.update()


if __name__ == "__main__":
    main()
