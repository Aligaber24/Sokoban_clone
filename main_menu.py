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

font = pygame.font.SysFont(None, 36)

STATE = "menu"
SESSION_FILE = "session.json"
LEVEL_FILE = "levels.json"


# ----------------- Button -----------------
class Button:
    def __init__(self, x, y, w, h, text, color, text_color=BLACK):
        self.rect = pygame.Rect(x, y, w, h)
        self.base_color = color
        self.hover_color = tuple(max(0, c - 30) for c in color)
        self.pressed_color = tuple(max(0, c - 60) for c in color)
        self.text = text
        self.text_color = text_color
        self.is_pressed = False

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            color = self.pressed_color if self.is_pressed else self.hover_color
        else:
            color = self.base_color

        pygame.draw.rect(screen, color, self.rect, border_radius=12)
        label = font.render(self.text, True, self.text_color)
        text_rect = label.get_rect(center=self.rect.center)
        if self.is_pressed:
            text_rect.move_ip(0, 2)
        screen.blit(label, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.is_pressed = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.is_pressed and self.rect.collidepoint(event.pos):
                self.is_pressed = False
                return True
            self.is_pressed = False
        return False


# ----------------- User -----------------
def get_current_user():
    try:
        with open(SESSION_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"username": "guest", "role": "anonymous"}

current_user = get_current_user()


# ----------------- Utility -----------------
def draw_text(text, x, y, color=BLACK):
    label = font.render(text, True, color)
    screen.blit(label, (x, y))


# ----------------- Level Saving -----------------
def save_level(grid):
    # Always overwrite with the new level
    with open(LEVEL_FILE, "w") as f:
        json.dump(grid, f, indent=4)
    print("✅ Level saved (overwritten)")

    # Clear leaderboard when new level is saved
    with open("scores.json", "w") as f:
        json.dump([], f, indent=4)
    print("🏆 Leaderboard reset (new level)")



# ----------------- Editor -----------------
def editor_screen():
    grid_size = 8
    tile_size = 50
    grid = [[0 for _ in range(grid_size)] for _ in range(grid_size)]
    selected = 1

    editing = True
    while editing:
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
                    editing = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                gx, gy = x // tile_size, y // tile_size
                if 0 <= gx < grid_size and 0 <= gy < grid_size:
                    if event.button == 1:
                        grid[gy][gx] = selected
                    elif event.button == 3:
                        grid[gy][gx] = 0

        draw_background()
        for y in range(grid_size):
            for x in range(grid_size):
                rect = pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size)
                val = grid[y][x]
                if val == 1:
                    pygame.draw.rect(screen, (139, 69, 19), rect)
                elif val == 2:
                    pygame.draw.circle(screen, (255, 0, 0), rect.center, tile_size // 3)
                elif val == 3:
                    pygame.draw.rect(screen, (0, 0, 255), rect.inflate(-10, -10))
                elif val == 4:
                    pygame.draw.circle(screen, (0, 200, 0), rect.center, tile_size // 4)
                pygame.draw.rect(screen, (200, 200, 200), rect, 1)

        draw_text(f"Selected: {selected}", 410, 50)
        draw_text("0: Empty", 410, 90)
        draw_text("1: Wall", 410, 130)
        draw_text("2: Player", 410, 170)
        draw_text("3: Block", 410, 210)
        draw_text("4: Goal", 410, 250)
        draw_text("Press S to Save,", 410, 350)
        draw_text("ESC to Exit", 410, 370)
        pygame.display.flip()


# ----------------- Leaderboard -----------------
def load_leaderboard():
    try:
        with open("scores.json", "r") as f:
            scores = json.load(f)
            scores.sort(key=lambda x: x["moves"])
            return scores[:5]
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def leaderboard_screen():
    global STATE
    draw_background()
    draw_text("🏆 Leaderboard - Top 5", 160, 50)

    scores = load_leaderboard()
    if not scores:
        draw_text("No scores yet!", 200, 150)
    else:
        y = 120
        for i, entry in enumerate(scores, start=1):
            draw_text(f"{i}. {entry['user']} - {entry['moves']} moves", 150, y)
            y += 40

    back_button.draw(screen)
    pygame.display.flip()


# ----------------- Menu -----------------
def create_menu_buttons():
    buttons = []
    y = 120
    buttons.append(Button(200, y, 200, 40, "Play Game", (144, 238, 144))); y += 60
    buttons.append(Button(200, y, 200, 40, "Leaderboard", (173, 216, 230))); y += 60

    if current_user["role"] == "admin":
        buttons.append(Button(200, y, 200, 40, "Puzzle Editor", (255, 182, 193))); y += 60
        buttons.append(Button(200, y, 200, 40, "Logout", (255, 160, 122))); y += 60
        buttons.append(Button(200, y, 200, 40, "Exit", (220, 220, 220)))
    else:
        buttons.append(Button(200, y, 200, 40, "Logout", (255, 160, 122))); y += 60
        buttons.append(Button(200, y, 200, 40, "Exit", (220, 220, 220)))
    return buttons

menu_buttons = create_menu_buttons()
back_button = Button(200, 340, 200, 40, "Back", (200, 200, 200))

def menu_screen():
    draw_background()
    draw_text(f"Logged in as: {current_user['username']} ", 190, 40)
    for b in menu_buttons:
        b.draw(screen)
    pygame.display.flip()

import random

particles = []
for _ in range(30):  # number of falling circles
    x = random.randint(0, WIDTH)
    y = random.randint(-HEIGHT, 0)
    speed = random.uniform(0.3, 1.2)   # slower fall
    size = random.randint(5, 12)
    particles.append({"x": x, "y": y, "speed": speed, "size": size})

def draw_background():
    screen.fill((240, 248, 255))  # pastel blue

    for p in particles:
        pygame.draw.circle(screen, (200, 230, 255), (p["x"], p["y"]), p["size"])
        p["y"] += p["speed"]

        # Reset when off-screen
        if p["y"] > HEIGHT:
            p["y"] = random.randint(-20, -5)
            p["x"] = random.randint(0, WIDTH)
            p["speed"] = random.uniform(0.3, 1.2)
            p["size"] = random.randint(5, 12)


# ----------------- Main loop -----------------
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if STATE == "menu":
            for b in menu_buttons:
                if b.handle_event(event):
                    if b.text == "Play Game":
                        subprocess.run([sys.executable, "game.py"])
                    elif b.text == "Leaderboard":
                        STATE = "leaderboard"
                    elif b.text == "Puzzle Editor":
                        editor_screen()
                    elif b.text == "Logout":
                        current_user = {"username": "guest", "role": "anonymous"}
                        with open(SESSION_FILE, "w") as f:
                            json.dump(current_user, f)
                        running = False
                        pygame.quit()
                        subprocess.run([sys.executable, "login.py"])
                        sys.exit()
                    elif b.text == "Exit":
                        running = False

        elif STATE == "leaderboard":
            if back_button.handle_event(event):
                STATE = "menu"

    if STATE == "menu":
        menu_screen()
    elif STATE == "leaderboard":
        leaderboard_screen()

pygame.quit()
