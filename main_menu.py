import pygame
import sys
import subprocess

pygame.init()

# Constants
WIDTH, HEIGHT = 600, 400
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sokoban Platform")

font = pygame.font.SysFont(None, 40)

STATE = "menu"

def draw_text(text, x, y, color=BLACK):
    label = font.render(text, True, color)
    screen.blit(label, (x, y))

def menu_screen():
    screen.fill(WHITE)
    draw_text("Welcome to Sokoban!", 180, 50)
    draw_text("1. Play Game", 200, 150)
    draw_text("2. Leaderboard", 200, 200)
    draw_text("3. Puzzle Editor (Admin)", 200, 250)
    draw_text("4. Exit", 200, 300)
    pygame.display.flip()

def leaderboard_screen():
    screen.fill(WHITE)
    draw_text("Leaderboard (placeholder)", 160, 50)
    draw_text("Press ESC to return", 180, 300)
    pygame.display.flip()

def editor_screen():
    screen.fill(WHITE)
    draw_text("Puzzle Editor (Admin only)", 140, 150)
    draw_text("Press ESC to return", 180, 300)
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
                    subprocess.run([sys.executable, "game.py"])  # Run game.py
                elif event.key == pygame.K_2:  # Leaderboard
                    STATE = "leaderboard"
                elif event.key == pygame.K_3:  # Editor
                    STATE = "editor"
                elif event.key == pygame.K_4:  # Exit
                    running = False
            else:
                if event.key == pygame.K_ESCAPE:
                    STATE = "menu"

    if STATE == "menu":
        menu_screen()
    elif STATE == "leaderboard":
        leaderboard_screen()
    elif STATE == "editor":
        editor_screen()

pygame.quit()
sys.exit()
