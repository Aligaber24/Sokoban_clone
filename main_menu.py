import pygame
import sys
import subprocess
import json
pygame.init()

# Constants
WIDTH, HEIGHT = 600, 400
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sokoban Platform")

font = pygame.font.SysFont(None, 40)

STATE = "menu"

SESSION_FILE = "session.json"
LEVEL_FILE = "levels.json"

def save_level(grid):
    # Always overwrite with the new level
    with open(LEVEL_FILE, "w") as f:
        json.dump(grid, f, indent=4)
    print("✅ Level saved (overwritten)")


def editor_screen():
    pygame.event.clear()
    grid_size = 8
    tile_size = 50
    grid = [[0 for _ in range(grid_size)] for _ in range(grid_size)]
    selected = 1  # start with wall

    editing = True
    while editing:
        print(1)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                editing = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    editing = False
                elif event.key == pygame.K_0:
                    selected = 0
                elif event.key == pygame.K_1:
                    selected = 1
                elif event.key == pygame.K_2:
                    selected = 2
                elif event.key == pygame.K_3:
                    selected = 3
                elif event.key == pygame.K_4:
                    selected = 4
                elif event.key == pygame.K_s:
                    save_level(grid)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                gx, gy = x // tile_size, y // tile_size
                if 0 <= gx < grid_size and 0 <= gy < grid_size:
                    if event.button == 1:  # left click
                        grid[gy][gx] = selected
                    elif event.button == 3:  # right click clears
                        grid[gy][gx] = 0

        # Draw editor grid
        screen.fill(WHITE)
        for y in range(grid_size):
            for x in range(grid_size):
                rect = pygame.Rect(x*tile_size, y*tile_size, tile_size, tile_size)
                val = grid[y][x]
                if val == 1:  # Wall
                    pygame.draw.rect(screen, (139, 69, 19), rect)
                elif val == 2:  # Goal
                    pygame.draw.circle(screen, (0, 200, 0), rect.center, tile_size//4)
                elif val == 3:  # Block
                    pygame.draw.rect(screen, (0, 0, 255), rect.inflate(-10, -10))
                elif val == 4:  # Player
                    pygame.draw.circle(screen, (255, 0, 0), rect.center, tile_size//3)
                pygame.draw.rect(screen, (200,200,200), rect, 1)  # grid lines

        draw_text(f"Selected: {selected}", 400, 50)
        draw_text("0: Empty", 400, 90)
        draw_text("1: Wall", 400, 130)
        draw_text("2: player", 400, 170)
        draw_text("3: Block", 400, 210)
        draw_text("4: goal", 400, 250)

        draw_text("Press S to Save, ESC to Exit", 300, 350)
        pygame.display.flip()

def get_current_user():
    try:
        with open(SESSION_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"username": "guest", "role": "anonymous"}

current_user = get_current_user()

def draw_text(text, x, y, color=BLACK):
    label = font.render(text, True, color)
    screen.blit(label, (x, y))

def menu_screen():
    screen.fill(WHITE)
    draw_text(f"Logged in as: {current_user['username']} ({current_user['role']})", 120, 40)
    draw_text("1. Play Game", 200, 120)
    draw_text("2. Leaderboard", 200, 170)

    if current_user["role"] == "admin":  # ✅ Only admins see this
        draw_text("3. Puzzle Editor (Admin)", 200, 220)
        draw_text("4. Logout", 200, 270)
        draw_text("5. Exit", 200, 320)
    else:
        draw_text("3. Logout", 200, 220)
        draw_text("4. Exit", 200, 270)

    pygame.display.flip()


def load_leaderboard():
    try:
        with open("scores.json", "r") as f:
            scores = json.load(f)
            # sort by moves (ascending = fewer moves is better)
            scores.sort(key=lambda x: x["moves"])
            return scores[:5]  # top 5
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def leaderboard_screen():
    screen.fill(WHITE)
    draw_text("🏆 Leaderboard - Top 5", 160, 50)

    scores = load_leaderboard()
    if not scores:
        draw_text("No scores yet!", 200, 150)
    else:
        y = 120
        for i, entry in enumerate(scores, start=1):
            draw_text(f"{i}. {entry['user']} - {entry['moves']} moves", 150, y)
            y += 40

    draw_text("Press ESC to return", 180, 350)
    pygame.display.flip()


# Main loopp
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if STATE == "menu":
                if event.key == pygame.K_1:  # Play
                    subprocess.run([sys.executable, "game.py"])

                elif event.key == pygame.K_2:  # Leaderboard
                    STATE = "leaderboard"

                elif event.key == pygame.K_3:
                    if current_user["role"] == "admin":
                        print("Opening editor...")
                        editor_screen()  # ✅ directly run editor
                    else:
                        # Logout (guest/player)
                        current_user = {"username": "guest", "role": "anonymous"}
                        with open(SESSION_FILE, "w") as f:
                            json.dump(current_user, f)
                        running = False
                        pygame.quit()
                        subprocess.run([sys.executable, "login.py"])
                        sys.exit()

                elif event.key == pygame.K_4:
                    if current_user["role"] == "admin":
                        # Logout (admin)
                        current_user = {"username": "guest", "role": "anonymous"}
                        with open(SESSION_FILE, "w") as f:
                            json.dump(current_user, f)
                        running = False
                        pygame.quit()
                        subprocess.run([sys.executable, "login.py"])
                        sys.exit()
                    else:
                        running = False

                elif event.key == pygame.K_5 and current_user["role"] == "admin":
                    running = False

            else:  # In leaderboard
                if event.key == pygame.K_ESCAPE:
                    STATE = "menu"

    if STATE == "menu":
        menu_screen()
    elif STATE == "leaderboard":
        leaderboard_screen()

pygame.quit()




