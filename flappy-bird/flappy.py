import pygame
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH = 400
HEIGHT = 600
FPS = 60
GRAVITY = 1000  # pixels per second squared
FLAP_POWER = -300  # pixels per second
PIPE_SPEED = 200  # pixels per second
PIPE_SPACING = 300  # pixels between pipes
PIPE_GAP = 150  # pixels
PIPE_WIDTH = 80
BIRD_SIZE = 30
GAP_BUFFER = 50  # pixels to keep gap away from top and bottom

# Colors (Natural and soft for eyes)
BACKGROUND_COLOR = (139, 69, 19)  # Saddle Brown
GROUND_COLOR = (34, 139, 34)  # Forest Green
BIRD_COLOR = (255, 215, 0)  # Gold
PIPE_COLOR = (107, 142, 35)  # Olive Drab
TEXT_COLOR = (245, 245, 245)  # White Smoke

# Setup screen and clock
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird - Retro Cave Theme")
clock = pygame.time.Clock()


class Bird:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = 100
        self.y = 300
        self.velocity = 0

    def flap(self):
        self.velocity = FLAP_POWER

    def update(self, dt):
        self.velocity += GRAVITY * dt
        self.y += self.velocity * dt
        if self.y < 0:
            self.y = 0
            self.velocity = 0

    def draw(self, screen):
        # Draw bird: circle for body, triangle for beak
        pygame.draw.circle(
            screen,
            BIRD_COLOR,
            (int(self.x + BIRD_SIZE / 2), int(self.y + BIRD_SIZE / 2)),
            BIRD_SIZE // 2,
        )
        beak_points = [
            (self.x + BIRD_SIZE, self.y + BIRD_SIZE // 2),
            (self.x + BIRD_SIZE + 10, self.y + BIRD_SIZE // 2 - 5),
            (self.x + BIRD_SIZE + 10, self.y + BIRD_SIZE // 2 + 5),
        ]
        pygame.draw.polygon(screen, (255, 165, 0), beak_points)  # Orange beak

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
        # Draw pipes as stalactites (top) and stalagmites (bottom)
        top_height = self.gap_y - PIPE_GAP / 2
        bottom_y = self.gap_y + PIPE_GAP / 2
        # Top pipe (stalactite)
        pygame.draw.polygon(
            screen,
            PIPE_COLOR,
            [
                (self.x, 0),
                (self.x + PIPE_WIDTH, 0),
                (self.x + PIPE_WIDTH / 2, top_height),
            ],
        )
        # Bottom pipe (stalagmite)
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


def draw_background():
    screen.fill(BACKGROUND_COLOR)
    # Draw ground
    ground_height = 50
    pygame.draw.rect(
        screen, GROUND_COLOR, (0, HEIGHT - ground_height, WIDTH, ground_height)
    )


def draw_start_screen(font):
    text = font.render("Press SPACE to Start", True, TEXT_COLOR)
    screen.blit(
        text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2)
    )


def draw_game_over_screen(font, score):
    game_over_text = font.render("Game Over", True, TEXT_COLOR)
    score_text = font.render(f"Score: {score}", True, TEXT_COLOR)
    restart_text = font.render("Press R to Restart", True, TEXT_COLOR)
    screen.blit(
        game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 50)
    )
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))
    screen.blit(
        restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 50)
    )


def main():
    bird = Bird()
    pipes = []
    score = 0
    game_state = "start"
    font = pygame.font.SysFont("comicsans", 30)
    time_between_pipes = (PIPE_SPACING / PIPE_SPEED) * 1000
    last_pipe_time = pygame.time.get_ticks() - time_between_pipes

    while True:
        dt = clock.tick(FPS) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if game_state == "start" and event.key == pygame.K_SPACE:
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
            if bird.y + BIRD_SIZE > HEIGHT:
                game_state = "game_over"
            for pipe in pipes:
                top_rect, bottom_rect = pipe.get_rects()
                if bird.get_rect().colliderect(top_rect) or bird.get_rect().colliderect(
                    bottom_rect
                ):
                    game_state = "game_over"

        draw_background()
        if game_state == "start":
            draw_start_screen(font)
        elif game_state == "playing":
            for pipe in pipes:
                pipe.draw(screen)
            bird.draw(screen)
            score_text = font.render(f"Score: {score}", True, TEXT_COLOR)
            screen.blit(score_text, (10, 10))
        elif game_state == "game_over":
            draw_game_over_screen(font, score)
        pygame.display.update()


if __name__ == "__main__":
    main()
