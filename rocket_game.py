from OpenGL.GL import *
from OpenGL.GLUT import *
from time import time
from math import sin, cos, sqrt
import random

win_width, win_height = 800, 600
ship_x = 0
bullets = []
falling_circles = []
speed = 0.02
score = 0
game_over = False
missed_circles = 0
game_running = True
game_paused = False
game_quit = False

# Initialize random stars for background
stars = [(random.randint(-400, 400), random.randint(-300, 300)) for _ in range(100)]

# Button Coordinates and Dimensions
button_width = 100
button_height = 40

restart_button = (-win_width//2 + 20, win_height//2 - 50)
play_pause_button = (restart_button[0] + button_width + 10, win_height//2 - 50)
exit_button = (play_pause_button[0] + button_width + 10, win_height//2 - 50)

def draw_stars():
    glColor3f(1.0, 1.0, 1.0)  # White stars
    glPointSize(2)
    glBegin(GL_POINTS)
    for star in stars:
        glVertex2f(star[0], star[1])
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
    num_points = 50
    glColor3f(*color)
    glPointSize(4)
    glBegin(GL_POINTS)
    for i in range(num_points):
        angle = 2 * 3.14159 * i / num_points
        px = x + radius * cos(angle)
        py = y + radius * sin(angle)
        glVertex2f(px, py)
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

    draw_text(x + 10, y - button_height + 10, text, size=18, color=(1, 1, 1))

def click_button(button, state, x, y):
    global game_over, game_paused, score, missed_circles, falling_circles, speed, game_quit

    # Check for left mouse button click (GLUT_LEFT_BUTTON)
    if state == 0:  # Only react on mouse button press
        # Restart button click
        if restart_button[0] <= x <= restart_button[0] + button_width and restart_button[1] - button_height <= y <= restart_button[1]:
            print("Starting Over")
            game_over = False
            game_paused = False
            score = 0
            missed_circles = 0
            falling_circles = []
            speed = 0.02
            glutPostRedisplay()

        # Play/Pause button click
        elif play_pause_button[0] <= x <= play_pause_button[0] + button_width and play_pause_button[1] - button_height <= y <= play_pause_button[1]:
            game_paused = not game_paused
            glutPostRedisplay()

        # Exit button click
        elif exit_button[0] <= x <= exit_button[0] + button_width and exit_button[1] - button_height <= y <= exit_button[1]:
            game_quit = True  # Set the quit flag
            print(f"Goodbye! Final Score: {score}")
            glutPostRedisplay()


def update(value):
    global bullets, falling_circles, score, game_over, missed_circles

    if game_over or game_paused:
        return

    # Update bullets
    bullets = [(px, py + 5, size) for px, py, size in bullets if py < 300]

    # Update falling circles and check for collisions
    new_circles = []
    for cx, cy, size, color in falling_circles:
        cy -= speed * 100  # Make the circles fall down
        if cy < -300:  # Missed the circle
            missed_circles += 1
            if missed_circles >= 3:
                game_over = True
        else:
            # Check for bullet collisions with circles
            for px, py, size in bullets:
                distance = sqrt((px - cx) ** 2 + (py - cy) ** 2)
                if distance <= size:
                    score += 1
                    new_circles.append(None)  # Remove circle on collision
                    bullets = [p for p in bullets if sqrt((p[0] - cx) ** 2 + (p[1] - cy) ** 2) > size]
                    break
            else:
                new_circles.append((cx, cy, size, color))  # Keep the circle if not hit

    falling_circles[:] = [circle for circle in new_circles if circle is not None]

    if random.random() < 0.02:
        new_circle = (random.randint(-400, 400), 300, random.randint(10, 20),
                      (random.random(), random.random(), random.random()))
        falling_circles.append(new_circle)

    glutPostRedisplay()
    glutTimerFunc(16, update, 0)

def display():
    global game_over, game_paused, game_quit

    glClear(GL_COLOR_BUFFER_BIT)

    # Draw background
    draw_stars()

    if game_over:
        draw_text(-50, 0, f"GAME OVER! Score: {score}", size=24, color=(1, 0, 0))
    elif game_paused:
        draw_text(-50, 0, "PAUSED", size=24, color=(1, 1, 0))
    elif game_quit:  # Handle the quit state
        draw_text(-50, 0, "Game Over. Press 'Escape' to close.", size=24, color=(1, 0, 0))
        # Exit the game gracefully
        glutLeaveMainLoop()  # This will stop the glutMainLoop and close the window
    else:
        # Draw game objects
        draw_ship()
        mpl_bullets()
        for cx, cy, size, color in falling_circles:
            mcl_circle(cx, cy, size, color)
        draw_text(-390, 270, f"Score: {score}")

    # Draw buttons
    draw_button(*restart_button, "Restart", (0, 1, 0))  # Green button
    draw_button(*play_pause_button, "Play/Pause", (1, 0.84, 0))  # Amber button
    draw_button(*exit_button, "Exit", (1, 0, 0))  # Red button

    glutSwapBuffers()

def keyboard(key, x, y):
    global ship_x, bullets, game_over

    if game_over or game_paused:
        return

    if key == b'\x1b':  # Escape key to quit
        if game_quit:
            exit(0)
        else:
            print(f"Goodbye! Final Score: {score}")
            exit(0)

    if key == b' ':
        bullets.append((ship_x, -250, random.randint(5, 10)))

    if key == b'Left' and ship_x > -380:
        ship_x -= 20
    elif key == b'Right' and ship_x < 380:
        ship_x += 20

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
