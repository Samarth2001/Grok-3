import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Rocket Ascent")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
SILVER = (192, 192, 192)

# Load and scale rocket image (replace 'spacex_rocket.png' with actual image path)
# Note: Ensure you have a suitable SpaceX rocket image file.
try:
    rocket_img = pygame.image.load('starship.png').convert_alpha()
    rocket_img = pygame.transform.smoothscale(rocket_img, (50, 100))
except pygame.error:
    # Fallback to a white rectangle if image loading fails
    rocket_img = pygame.Surface((50, 100))
    rocket_img.fill(WHITE)
    rocket_img = rocket_img.convert_alpha()

# Rocket properties
rocket_rect = rocket_img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
rocket_speed = 300  # pixels per second

# Scroll speed properties
scroll_speed = 200  # initial scroll speed in pixels per second
min_scroll_speed = 100
max_scroll_speed = 500
acceleration = 200  # pixels per second squared

# Spawn rates
base_debris_spawn_rate = 0.5  # spawns per second
k_debris = 0.0001  # increase per altitude unit
max_debris_spawn_rate = 5.0  # cap the spawn rate
satellite_spawn_rate = 0.2  # spawns per second

# Lists for game objects
debris_list = []
satellite_list = []
stars = [(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)) for _ in range(100)]

# Game variables
score = 0
altitude = 0
running = True
clock = pygame.time.Clock()

while running:
    delta_time = clock.tick(60) / 1000.0  # Time since last frame in seconds

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Get keys pressed for continuous movement
    keys = pygame.key.get_pressed()

    # Update rocket horizontal position
    if keys[pygame.K_LEFT]:
        rocket_rect.centerx -= rocket_speed * delta_time
    if keys[pygame.K_RIGHT]:
        rocket_rect.centerx += rocket_speed * delta_time

    # Clamp rocket to screen boundaries
    rocket_rect.left = max(0, rocket_rect.left)
    rocket_rect.right = min(SCREEN_WIDTH, rocket_rect.right)

    # Update scroll speed based on Up/Down keys
    if keys[pygame.K_UP]:
        scroll_speed += acceleration * delta_time
    if keys[pygame.K_DOWN]:
        scroll_speed -= acceleration * delta_time
    scroll_speed = max(min_scroll_speed, min(scroll_speed, max_scroll_speed))

    # Update altitude based on scroll speed
    altitude += scroll_speed * delta_time

    # Spawn debris with increasing rate based on altitude
    debris_spawn_rate = min(base_debris_spawn_rate + k_debris * altitude, max_debris_spawn_rate)
    if random.random() < debris_spawn_rate * delta_time:
        amplitude = random.uniform(50, 150)
        x0 = random.uniform(amplitude, SCREEN_WIDTH - amplitude)
        debris = {
            'rect': pygame.Rect(x0 - 15, 0, 30, 30),
            'x0': x0,
            'amplitude': amplitude,
            'frequency': random.uniform(0.5, 1.5),
            'spawn_time': pygame.time.get_ticks() / 1000.0
        }
        debris_list.append(debris)

    # Spawn satellites at a constant rate
    if random.random() < satellite_spawn_rate * delta_time:
        amplitude = random.uniform(30, 80)
        x0 = random.uniform(amplitude, SCREEN_WIDTH - amplitude)
        satellite = {
            'rect': pygame.Rect(x0 - 5, 0, 10, 10),
            'x0': x0,
            'amplitude': amplitude,
            'frequency': random.uniform(1, 2),
            'spawn_time': pygame.time.get_ticks() / 1000.0
        }
        satellite_list.append(satellite)

    # Update debris positions with horizontal oscillation
    current_time = pygame.time.get_ticks() / 1000.0
    for debris in debris_list[:]:
        t = current_time - debris['spawn_time']
        x = debris['x0'] + debris['amplitude'] * math.sin(debris['frequency'] * t * 2 * math.pi)
        debris['rect'].centerx = x
        debris['rect'].y += scroll_speed * delta_time
        if debris['rect'].top > SCREEN_HEIGHT:
            debris_list.remove(debris)

    # Update satellite positions with horizontal oscillation
    for satellite in satellite_list[:]:
        t = current_time - satellite['spawn_time']
        x = satellite['x0'] + satellite['amplitude'] * math.sin(satellite['frequency'] * t * 2 * math.pi)
        satellite['rect'].centerx = x
        satellite['rect'].y += scroll_speed * delta_time
        if satellite['rect'].top > SCREEN_HEIGHT:
            satellite_list.remove(satellite)

    # Check collisions
    for debris in debris_list:
        if rocket_rect.colliderect(debris['rect']):
            running = False  # Game over on collision with debris

    for satellite in satellite_list[:]:
        if rocket_rect.colliderect(satellite['rect']):
            score += 50  # Collect satellite and increase score
            satellite_list.remove(satellite)

    # Update starfield for background scrolling
    for i in range(len(stars)):
        star_x, star_y = stars[i]
        star_y += scroll_speed * delta_time
        if star_y > SCREEN_HEIGHT:
            star_y -= SCREEN_HEIGHT
            star_x = random.randint(0, SCREEN_WIDTH)
        stars[i] = (star_x, star_y)

    # Render the game scene
    screen.fill(BLACK)

    # Draw stars for the background
    for star in stars:
        pygame.draw.circle(screen, WHITE, (int(star[0]), int(star[1])), 2)

    # Draw debris as gray squares
    for debris in debris_list:
        pygame.draw.rect(screen, GRAY, debris['rect'])

    # Draw satellites as silver circles (representing stars)
    for satellite in satellite_list:
        pygame.draw.circle(screen, SILVER, satellite['rect'].center, 5)

    # Draw the rocket
    screen.blit(rocket_img, rocket_rect)

    # Display score and altitude
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, WHITE)
    altitude_text = font.render(f"Altitude: {int(altitude)}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(altitude_text, (10, 50))

    # Update display
    pygame.display.flip()

# Quit Pygame
pygame.quit()