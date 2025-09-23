import pygame
import sys
import json
import os

# Initialize pygame
pygame.init()

# Constants
TILE_SIZE = 64
GRID_WIDTH = 8
GRID_HEIGHT = 8
WIDTH = TILE_SIZE * GRID_WIDTH
HEIGHT = TILE_SIZE * GRID_HEIGHT
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE  = (0, 0, 200)
BROWN = (139, 69, 19)
GREEN = (0, 200, 0)
RED   = (200, 0, 0)

# Level legend:
# 0 = empty
# 1 = wall
# 2 = player
# 3 = block
# 4 = target
# 5 = block on target
# 6 = player on target
LEVEL_FILE = "levels.json"

def load_level():
    with open(LEVEL_FILE, "r") as f:
        return json.load(f)

level = load_level()


SESSION_FILE = "session.json"

def get_current_user():
    try:
        with open(SESSION_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"username": "guest", "role": "anonymous"}

def save_score(username, moves):
    scores_file = "scores.json"
    scores = []

    if os.path.exists(scores_file):
        with open(scores_file, "r") as f:
            try:
                scores = json.load(f)
            except json.JSONDecodeError:
                scores = []

    scores.append({"user": username, "moves": moves})

    with open(scores_file, "w") as f:
        json.dump(scores, f, indent=4)

# Find player position
def find_player():
    for y, row in enumerate(level):
        for x, tile in enumerate(row):
            if tile == 2 or tile == 6:
                return x, y
    return None

# Draw the game
def draw_level(screen):
    for y, row in enumerate(level):
        for x, tile in enumerate(row):
            rect = pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE)

            if tile == 1:
                pygame.draw.rect(screen, BLUE, rect)   # wall
            elif tile == 2:
                pygame.draw.rect(screen, GREEN, rect)  # player
            elif tile == 3:
                pygame.draw.rect(screen, BROWN, rect)  # block
            elif tile == 4:
                pygame.draw.rect(screen, WHITE, rect)  # target
            elif tile == 5:
                pygame.draw.rect(screen, RED, rect)    # block on target
            elif tile == 6:
                pygame.draw.rect(screen, GREEN, rect)  # player on target
                pygame.draw.rect(screen, WHITE, rect, 4)

            pygame.draw.rect(screen, BLACK, rect, 1)

# Move function
def move(dx, dy):
    global level
    x, y = find_player()
    target_x, target_y = x + dx, y + dy
    beyond_x, beyond_y = x + 2*dx, y + 2*dy

    current_tile = level[y][x]
    target_tile = level[target_y][target_x]

    # Wall → no move
    if target_tile == 1:
        return False

    # If block
    if target_tile in (3, 5):
        beyond_tile = level[beyond_y][beyond_x]
        if beyond_tile in (0, 4):  # empty or target
            # Move block
            level[beyond_y][beyond_x] = 5 if beyond_tile == 4 else 3
            # Move player
            level[target_y][target_x] = 6 if target_tile == 5 else 2
            # Leave behind correct tile
            level[y][x] = 4 if current_tile == 6 else 0
            return True
        return False  # block can’t move → invalid

    # If empty or target
    elif target_tile in (0, 4):
        level[target_y][target_x] = 6 if target_tile == 4 else 2
        level[y][x] = 4 if current_tile == 6 else 0
        return True

    return False


# Check win condition
def check_win():
    for row in level:
        for tile in row:
            if tile == 4:  # any target left empty
                return False
    return True

# Setup screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sokoban Clone")
clock = pygame.time.Clock()

# Main loop
move_count = 0
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            moved = False
            if event.key == pygame.K_UP:
                moved = move(0, -1)
            elif event.key == pygame.K_DOWN:
                moved = move(0, 1)
            elif event.key == pygame.K_LEFT:
                moved = move(-1, 0)
            elif event.key == pygame.K_RIGHT:
                moved = move(1, 0)

            if moved:  # ✅ only count real moves
                move_count += 1

    screen.fill(BLACK)
    draw_level(screen)

    # Display move counter
    font = pygame.font.SysFont(None, 30)
    text = font.render(f"Moves: {move_count}", True, (255, 255, 255))
    screen.blit(text, (10, 10))

    if check_win():
        user = get_current_user()
        save_score(user["username"], move_count)
        screen.blit(text, (WIDTH // 2 - 100, HEIGHT // 2 - 30))
        pygame.display.flip()
        pygame.time.wait(2000)
        running = False

    pygame.display.flip()
    clock.tick(FPS)

