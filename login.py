import pygame
import sys
import json
import os
import subprocess

pygame.init()

# Screen setup
WIDTH, HEIGHT = 600, 450
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 120, 255)
LIGHT_BLUE = (173, 216, 230)
GREEN = (144, 238, 144)
PINK = (255, 182, 193)
GRAY = (180, 180, 180)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sokoban Login")

font = pygame.font.SysFont(None, 32)

USER_FILE = "users.json"
SESSION_FILE = "session.json"  # temporary file to pass user info

# ----------------- User Management -----------------
def load_users():
    if not os.path.exists(USER_FILE):
        users = [{"username": "admin", "password": "admin", "role": "admin"}]
        save_users(users)
        return users
    with open(USER_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)

def register_user(username, password, role="player"):
    users = load_users()
    for u in users:
        if u["username"] == username:
            return False
    users.append({"username": username, "password": password, "role": role})
    save_users(users)
    return True

def authenticate(username, password):
    users = load_users()
    for u in users:
        if u["username"] == username and u["password"] == password:
            return u
    return None


#moving background
import random

particles = []
for _ in range(30):  # number of falling objects
    x = random.randint(0, WIDTH)
    y = random.randint(-HEIGHT, 0)
    speed = random.uniform(0.3, 1.2)   # ✅ much slower
    size = random.randint(5, 12)
    particles.append({"x": x, "y": y, "speed": speed, "size": size})


def draw_background():
    screen.fill((240, 248, 255))  # pastel sky blue

    for p in particles:
        pygame.draw.circle(screen, (200, 230, 255), (p["x"], p["y"]), p["size"])
        p["y"] += p["speed"]

        # Respawn at top when off-screen
        if p["y"] > HEIGHT:
            p["y"] = random.randint(-20, -5)
            p["x"] = random.randint(0, WIDTH)
            p["speed"] = random.uniform(0.3, 1.2)  # ✅ keep slow when respawning
            p["size"] = random.randint(5, 12)


# ----------------- Input Box -----------------
class InputBox:
    def __init__(self, x, y, w, h, text="", is_password=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.color_inactive = GRAY
        self.color_active = BLUE
        self.color = self.color_inactive
        self.text = text
        self.txt_surface = font.render(text, True, BLACK)
        self.active = False
        self.is_password = is_password

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            self.color = self.color_active if self.active else self.color_inactive
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
            # Mask if password
            display_text = "●" * len(self.text) if self.is_password else self.text
            self.txt_surface = font.render(display_text, True, BLACK)

    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, self.rect, border_radius=10)
        pygame.draw.rect(screen, self.color, self.rect, 2, border_radius=10)
        screen.blit(self.txt_surface, (self.rect.x + 10, self.rect.y + 8))


# ----------------- Button -----------------
class Button:
    def __init__(self, x, y, w, h, text, color, text_color=BLACK):
        self.rect = pygame.Rect(x, y, w, h)
        self.base_color = color
        self.hover_color = tuple(max(0, c - 30) for c in color)   # darker hover
        self.pressed_color = tuple(max(0, c - 60) for c in color) # darker pressed
        self.text = text
        self.text_color = text_color
        self.is_pressed = False

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            if self.is_pressed:
                color = self.pressed_color
            else:
                color = self.hover_color
        else:
            color = self.base_color

        pygame.draw.rect(screen, color, self.rect, border_radius=12)
        label = font.render(self.text, True, self.text_color)
        text_rect = label.get_rect(center=self.rect.center)
        if self.is_pressed:  # shift text slightly down when pressed
            text_rect.move_ip(0, 2)
        screen.blit(label, text_rect)

    def handle_event(self, event):
        """Handles press + release state and returns True if fully clicked"""
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.is_pressed = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.is_pressed and self.rect.collidepoint(event.pos):
                self.is_pressed = False
                return True  # full click detected
            self.is_pressed = False
        return False

    def is_clicked(self, event):
        """Alias for backwards compatibility"""
        return self.handle_event(event)

# ----------------- Screens -----------------
def draw_text(text, x, y, color=BLACK):
    label = font.render(text, True, color)
    screen.blit(label, (x, y))

def login_register_screen(username_box, password_box, message="", state="login"):
    draw_background() # pastel background

    # Title
    title = font.render("🔑 Sokoban " + ("Login" if state == "login" else "Register"), True, BLACK)
    screen.blit(title, (200, 40))

    # Labels
    draw_text("Username:", 100, 120)
    username_box.draw(screen)

    draw_text("Password:", 100, 200)
    password_box.draw(screen)

    # Buttons
    if state == "login":
        login_button.draw(screen)
        signup_button.draw(screen)
        guest_button.draw(screen)
    else:
        register_button.draw(screen)
        back_button.draw(screen)

    if message:
        draw_text(message, 150, 80, BLUE)

    pygame.display.flip()

# ----------------- Main -----------------
def main():
    running = True
    state = "login"

    username_box = InputBox(250, 120, 200, 40)
    password_box = InputBox(250, 200, 200, 40, is_password=True)
    message = ""

    global login_button, signup_button, guest_button, register_button, back_button
    login_button = Button(200, 280, 200, 40, "Login", GREEN)
    signup_button = Button(200, 330, 200, 40, "Sign Up", PINK)
    guest_button = Button(200, 380, 200, 40, "Continue as Guest", LIGHT_BLUE)
    register_button = Button(200, 280, 200, 40, "Register", GREEN)
    back_button = Button(200, 330, 200, 40, "Back to Login", LIGHT_BLUE)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            username_box.handle_event(event)
            password_box.handle_event(event)

            # --- Handle clicks ---
            if state == "login":
                if login_button.is_clicked(event):
                    username = username_box.text.strip()
                    password = password_box.text.strip()
                    user = authenticate(username, password)
                    if user:
                        with open(SESSION_FILE, "w") as f:
                            json.dump(user, f)
                        running = False
                        pygame.quit()
                        subprocess.run([sys.executable, "main_menu.py"])
                    else:
                        message = "❌ Invalid login"

                elif signup_button.is_clicked(event):
                    state = "register"
                    message = ""

                elif guest_button.is_clicked(event):
                    user = {"username": "guest", "role": "anonymous"}
                    with open(SESSION_FILE, "w") as f:
                        json.dump(user, f)
                    running = False
                    pygame.quit()
                    subprocess.run([sys.executable, "main_menu.py"])

            elif state == "register":
                if register_button.is_clicked(event):
                    username = username_box.text.strip()
                    password = password_box.text.strip()
                    if register_user(username, password):
                        message = "✅ Registered successfully!"
                    else:
                        message = "⚠️ Username already exists"

                elif back_button.is_clicked(event):
                    state = "login"
                    message = ""

        login_register_screen(username_box, password_box, message, state)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
