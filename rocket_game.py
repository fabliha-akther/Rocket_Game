from OpenGL.GL import *
from OpenGL.GLUT import *
from time import time
from math import sin, cos, sqrt
import random

# Game window dimensions
win_width, win_height = 800, 600

# Player state
ship_x = 0
bullets = []
falling_circles = []

# Game status and settings
speed = 0.02
score = 0
game_over = False
missed_circles = 0
game_paused = False
game_quit = False

# Starfield background
stars = [(random.randint(-400, 400), random.randint(-300, 300)) for _ in range(100)]

# UI buttons
button_width = 100
button_height = 40
restart_button = (-win_width//2 + 20, win_height//2 - 50)
play_pause_button = (restart_button[0] + button_width + 10, win_height//2 - 50)
exit_button = (play_pause_button[0] + button_width + 10, win_height//2 - 50)

def draw_stars():
    glColor3f(1.0, 1.0, 1.0)
    glPointSize(2)
    glBegin(GL_POINTS)
    for x, y in stars:
        glVertex2f(x, y)
    glEnd()

def draw_text(x, y, text, size=18, color=(1, 1, 1)):
    glColor3f(*color)
    glRasterPos2f(x, y)
    for char in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

def draw_ship():
    glColor3f(0.2, 0.7, 1)
    glBegin(GL_TRIANGLES)
    glVertex2f(ship_x, -250)
    glVertex2f(ship_x - 20, -280)
    glVertex2f(ship_x + 20, -280)
    glEnd()

def mcl_circle(x, y, radius, color):
    glColor3f(*color)
    glPointSize(4)
    glBegin(GL_POINTS)
    for i in range(50):
        angle = 2 * 3.14159 * i / 50
        glVertex2f(x + radius * cos(angle), y + radius * sin(angle))
    glEnd()

def mpl_bullets():
    for px, py, size in bullets:
        glColor3f(random.random(), random.random(), random.random())
        glPointSize(size)
        glBegin(GL_POINTS)
        glVertex2f(px, py)
        glEnd()

def draw_button(x, y, text, color):
    glColor3f(*color)
    glBegin(GL_QUADS)
    glVertex2f(x, y)
    glVertex2f(x + button_width, y)
    glVertex2f(x + button_width, y - button_height)
    glVertex2f(x, y - button_height)
    glEnd()
    draw_text(x + 10, y - button_height + 10, text)

def click_button(button, state, x, y):
    global game_over, game_paused, score, missed_circles, falling_circles, speed, game_quit
    if state == 0:  # Mouse button pressed
        if restart_button[0] <= x <= restart_button[0] + button_width and \
           restart_button[1] - button_height <= y <= restart_button[1]:
            game_over = False
            game_paused = False
            score = 0
            missed_circles = 0
            falling_circles = []
            speed = 0.02
            glutPostRedisplay()

        elif play_pause_button[0] <= x <= play_pause_button[0] + button_width and \
             play_pause_button[1] - button_height <= y <= play_pause_button[1]:
            game_paused = not game_paused
            glutPostRedisplay()

        elif exit_button[0] <= x <= exit_button[0] + button_width and \
             exit_button[1] - button_height <= y <= exit_button[1]:
            game_quit = True
            glutPostRedisplay()

def update(value):
    global bullets, falling_circles, score, game_over, missed_circles
    if game_over or game_paused:
        return

    bullets = [(x, y + 5, s) for x, y, s in bullets if y < 300]

    new_circles = []
    for cx, cy, size, color in falling_circles:
        cy -= speed * 100
        if cy < -300:
            missed_circles += 1
            if missed_circles >= 3:
                game_over = True
        else:
            for px, py, bs in bullets:
                if sqrt((px - cx)**2 + (py - cy)**2) <= size:
                    score += 1
                    bullets = [b for b in bullets if sqrt((b[0] - cx)**2 + (b[1] - cy)**2) > size]
                    break
            else:
                new_circles.append((cx, cy, size, color))
    falling_circles[:] = [c for c in new_circles if c is not None]

    if random.random() < 0.02:
        falling_circles.append((
            random.randint(-400, 400), 300,
            random.randint(10, 20),
            (random.random(), random.random(), random.random())
        ))

    glutPostRedisplay()
    glutTimerFunc(16, update, 0)

def display():
    glClear(GL_COLOR_BUFFER_BIT)
    draw_stars()

    if game_over:
        draw_text(-50, 0, f"GAME OVER! Score: {score}", 24, (1, 0, 0))
    elif game_paused:
        draw_text(-50, 0, "PAUSED", 24, (1, 1, 0))
    elif game_quit:
        draw_text(-50, 0, "Game Over. Press 'Escape' to close.", 24, (1, 0, 0))
        glutLeaveMainLoop()
    else:
        draw_ship()
        mpl_bullets()
        for cx, cy, size, color in falling_circles:
            mcl_circle(cx, cy, size, color)
        draw_text(-390, 270, f"Score: {score}")

    draw_button(*restart_button, "Restart", (0, 1, 0))
    draw_button(*play_pause_button, "Play/Pause", (1, 0.84, 0))
    draw_button(*exit_button, "Exit", (1, 0, 0))
    glutSwapBuffers()

def keyboard(key, x, y):
    global ship_x, bullets, game_over
    if game_over or game_paused:
        return

    if key == b'\x1b':
        exit(0)

    if key == b' ':
        bullets.append((ship_x, -250, random.randint(5, 10)))

def special_keys(key, x, y):
    global ship_x
    if key == GLUT_KEY_LEFT and ship_x > -380:
        ship_x -= 20
    elif key == GLUT_KEY_RIGHT and ship_x < 380:
        ship_x += 20

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(win_width, win_height)
    glutCreateWindow(b"Shoot the Circles!")
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-400, 400, -300, 300, -1, 1)

    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_keys)
    glutMouseFunc(click_button)
    glutTimerFunc(16, update, 0)
    glutMainLoop()

main()
