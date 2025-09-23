import pygame
import sys
import json
import os
import subprocess

pygame.init()

# Screen setup
WIDTH, HEIGHT = 600, 400
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 120, 255)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sokoban Login")

font = pygame.font.SysFont(None, 36)

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

# ----------------- Input Box -----------------
class InputBox:
    def __init__(self, x, y, w, h, text=""):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = BLACK
        self.text = text
        self.txt_surface = font.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # toggle active if clicked
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    return self.text
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.txt_surface = font.render(self.text, True, self.color)
        return None

    def draw(self, screen):
        # Draw text
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        # Draw rect
        pygame.draw.rect(screen, self.color, self.rect, 2)

# ----------------- Screens -----------------
def draw_text(text, x, y, color=BLACK):
    label = font.render(text, True, color)
    screen.blit(label, (x, y))

def login_screen(username_box, password_box, message=""):
    screen.fill(WHITE)
    draw_text("Login to Sokoban", 200, 40)

    draw_text("Username:", 100, 120)
    username_box.draw(screen)

    draw_text("Password:", 100, 200)
    password_box.draw(screen)

    draw_text("Press ENTER to Login", 180, 300)
    draw_text("Press TAB to Switch to Register", 140, 340)

    if message:
        draw_text(message, 150, 80, BLUE)

    pygame.display.flip()

def register_screen(username_box, password_box, message=""):
    screen.fill(WHITE)
    draw_text("Register New User", 200, 40)

    draw_text("Username:", 100, 120)
    username_box.draw(screen)

    draw_text("Password:", 100, 200)
    password_box.draw(screen)

    draw_text("Press ENTER to Register", 180, 300)
    draw_text("Press TAB to Switch to Login", 160, 340)

    if message:
        draw_text(message, 150, 80, BLUE)

    pygame.display.flip()

# ----------------- Main -----------------
def main():
    running = True
    state = "login"

    username_box = InputBox(250, 120, 200, 40)
    password_box = InputBox(250, 200, 200, 40)
    message = ""

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    # switch between login/register
                    state = "register" if state == "login" else "login"
                    username_box.text = ""
                    password_box.text = ""
                    username_box.txt_surface = font.render("", True, BLACK)
                    password_box.txt_surface = font.render("", True, BLACK)
                    message = ""

                elif event.key == pygame.K_RETURN:
                    username = username_box.text.strip()
                    password = password_box.text.strip()
                    if state == "login":
                        user = authenticate(username, password)
                        if user:
                            with open(SESSION_FILE, "w") as f:
                                json.dump(user, f)
                            running = False        # ✅ stop login loop
                            pygame.quit()          # ✅ close login window
                            subprocess.run([sys.executable, "main_menu.py"])
                        else:
                            message = "❌ Invalid login"
                    elif state == "register":
                        if register_user(username, password):
                            message = "✅ Registered successfully!"
                        else:
                            message = "⚠️ Username already exists"

            username_box.handle_event(event)
            password_box.handle_event(event)

        if state == "login":
            login_screen(username_box, password_box, message)
        else:
            register_screen(username_box, password_box, message)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
