import pygame
import random
import math
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pygame Shooter")

# Constants
NUM_ENEMIES = 7
ENEMY_SIZE = 50
PROJECTILE_SPEEDgac = 6
ENEMY_SPEED = 2
player_speed = 5
BLACK = (0, 0, 0)

# Load assets
try:
    enemy_frames = [pygame.image.load(f"assets/enemy.gif").convert_alpha() for _ in range(NUM_ENEMIES)]
    player_frames = [pygame.image.load("assets/enemy-ship.png").convert_alpha() for _ in range(4)]
    player_projectile_image = pygame.image.load("assets/bullet1.png").convert_alpha()
    PROJECTILE_SHAPES = [
        pygame.transform.scale(pygame.image.load(f"assets/Asteroids/small-a.png").convert_alpha(), (30, 30)),
        pygame.transform.scale(pygame.image.load(f"assets/Asteroids/med-b.png").convert_alpha(), (30, 30)),
        pygame.transform.scale(pygame.image.load(f"assets/Asteroids/big-a.png").convert_alpha(), (30, 30)),
    ]
    background = pygame.image.load("assets/background.png").convert()
    midground = pygame.image.load("assets/midground.png").convert_alpha()
    foreground = pygame.image.load("assets/foreground.png").convert_alpha()

    collision_effect = pygame.image.load("assets/explosions-a6.png").convert_alpha()  # Explosion effect
    collision_sound = pygame.mixer.Sound("assets/explosion.wav")  # Sound for collision
    player_sound = pygame.mixer.Sound("assets/lasergun.mp3")  # Sound for player shooting
except pygame.error as e:
    print(f"Error loading image: {e}")
    sys.exit()

# Player properties
player_x = SCREEN_WIDTH // 2
player_y = SCREEN_HEIGHT - 100
player_speed = 5
player_frame_index = 0
player_animation_speed = 5
player_angle = 0
player_projectiles = []

# Initialize enemies
enemies = []
for i in range(NUM_ENEMIES):
    enemies.append({
        "x": random.randint(0, SCREEN_WIDTH - ENEMY_SIZE),
        "y": random.randint(0, SCREEN_HEIGHT // 5),
        "speed": random.choice([-ENEMY_SPEED, ENEMY_SPEED]),
        "rotation": 0,
        "direction": random.choice([-1, 1]),
        "frame": pygame.transform.scale(enemy_frames[i], (ENEMY_SIZE, ENEMY_SIZE)),
        "projectile_timer": 0,
    })

# Enemy projectiles
projectiles = []

# Spawn a projectile
def spawn_projectile(enemy):
    angle = random.uniform(-45, 90)
    dx = math.cos(math.radians(angle)) * PROJECTILE_SPEED
    dy = math.sin(math.radians(angle)) * PROJECTILE_SPEED
    projectiles.append({
        "x": enemy["x"] + ENEMY_SIZE // 2,
        "y": enemy["y"] + ENEMY_SIZE,
        "dx": dx,
        "dy": dy,
        "shape": random.choice(PROJECTILE_SHAPES),
    })

# Function to spawn a new player projectile
def spawn_player_projectile(x, y, angle):
    radian_angle = math.radians(angle)
    dx = math.cos(radian_angle) * PROJECTILE_SPEED
    dy = -math.sin(radian_angle) * PROJECTILE_SPEED
    player_projectiles.append({
        "x": x,
        "y": y,
        "dx": dx,
        "dy": dy,
        "shape": player_projectile_image,
    })
    player_sound.play()  # Play player shooting sound when firing

# Collision detection
def check_collision(obj1, obj2, size1, size2):
    distance = math.sqrt((obj1["x"] - obj2["x"])**2 + (obj1["y"] - obj2["y"])**2)
    return distance < (size1 // 2 + size2 // 2)

# Display collision effect
def show_collision_effect(x, y):
    screen.blit(collision_effect, (x, y))

# Main game loop
def main():
    global player_x, player_y, player_frame_index, player_angle

    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:  # Fire projectile
                    spawn_player_projectile(player_x, player_y, player_angle)

        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
            player_angle = 90
        if keys[pygame.K_RIGHT] and player_x < SCREEN_WIDTH:
            player_x += player_speed
            player_angle = -90
        if keys[pygame.K_UP] and player_y > 0:
            player_y -= player_speed
            player_angle = 0
        if keys[pygame.K_DOWN] and player_y < SCREEN_HEIGHT:
            player_y += player_speed
            player_angle %= 180

        # Update enemies
        for enemy in enemies:
            enemy["x"] += enemy["speed"]
            if enemy["x"] <= 0 or enemy["x"] >= SCREEN_WIDTH - ENEMY_SIZE:
                enemy["speed"] *= -1
            enemy["projectile_timer"] += 1
            if enemy["projectile_timer"] >= random.randint(60, 120):
                spawn_projectile(enemy)
                enemy["projectile_timer"] = 0

        # Move projectiles
        for proj in player_projectiles[:]:
            proj["x"] += proj["dx"]
            proj["y"] += proj["dy"]
            if proj["y"] < 0:
                player_projectiles.remove(proj)

        for proj in projectiles[:]:
            proj["x"] += proj["dx"]
            proj["y"] += proj["dy"]
            if proj["y"] > SCREEN_HEIGHT:
                projectiles.remove(proj)

        # Check collisions
        for enemy in enemies[:]:
            for proj in player_projectiles[:]:
                if check_collision(proj, enemy, 30, ENEMY_SIZE):
                    enemies.remove(enemy)
                    player_projectiles.remove(proj)
                    show_collision_effect(enemy["x"], enemy["y"])  # Show explosion
                    collision_sound.play()  # Play explosion sound
                    break

        for proj in projectiles[:]:
            if check_collision(proj, {"x": player_x, "y": player_y}, 30, 50):
                print("Game Over!")
                running = False

        # Drawing
        screen.fill(BLACK)
        screen.blit(background, (0, 0))

        for enemy in enemies:
            screen.blit(enemy["frame"], (enemy["x"], enemy["y"]))

        for proj in player_projectiles:
            screen.blit(proj["shape"], (proj["x"], proj["y"]))

        for proj in projectiles:
            screen.blit(proj["shape"], (proj["x"], proj["y"]))

        player_rotated = pygame.transform.rotate(player_frames[player_frame_index], player_angle)
        screen.blit(player_rotated, (player_x, player_y))

        pygame.display.flip()
        pygame.time.Clock().tick(60)

# Run the game
main()
