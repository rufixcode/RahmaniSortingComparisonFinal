import pygame
import sys
import math
import time

pygame.init()
pygame.display.set_caption("Planetary Free Fall Simulator")

# --- Window setup ---
WIDTH, HEIGHT = 1100, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
clock = pygame.time.Clock()

# --- Fonts ---
font_small = pygame.font.SysFont("segoeui", 18)
font_medium = pygame.font.SysFont("segoeui", 22, bold=True)
font_large = pygame.font.SysFont("segoeui", 28, bold=True)

# --- Colors ---
WHITE = (255, 255, 255)
BG = (245, 245, 250)
BLACK = (25, 25, 25)
GRAY = (200, 200, 200)
LIGHTGRAY = (230, 230, 235)
BLUE = (70, 140, 255)
GREEN = (0, 180, 90)
RED = (220, 60, 60)
SIDEBAR_BG = (250, 250, 253)

# --- Planet data ---
PLANETS = [
    ("Mercury", 3.7),
    ("Venus", 8.87),
    ("Earth", 9.81),
    ("Moon", 1.62),
    ("Mars", 3.71),
    ("Jupiter", 24.79),
    ("Neptune", 11.15),
]
current_planet = 2  # Earth by default

# --- Physics parameters ---
BALL_RADIUS = 18
RESTUTION = 0.6
DT_FIXED = 1 / 60

# --- UI helper classes ---
class Button:
    def __init__(self, text, rect):
        self.text = text
        self.rect = pygame.Rect(rect)
        self.active = False

    def draw(self, surf):
        color = BLUE if self.active else LIGHTGRAY
        pygame.draw.rect(surf, color, self.rect, border_radius=6)
        txt = font_small.render(self.text, True, BLACK if not self.active else WHITE)
        surf.blit(txt, txt.get_rect(center=self.rect.center))

    def click(self, pos):
        return self.rect.collidepoint(pos)


class InputBox:
    def __init__(self, label, value, rect):
        self.label = label
        self.text = str(value)
        self.rect = pygame.Rect(rect)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.unicode.isdigit() or event.unicode in ".-":
                self.text += event.unicode

    def draw(self, surf):
        # label
        label_surf = font_small.render(self.label, True, BLACK)
        surf.blit(label_surf, (self.rect.x, self.rect.y - 24))
        # box
        pygame.draw.rect(surf, WHITE, self.rect)
        pygame.draw.rect(surf, BLUE if self.active else GRAY, self.rect, 2)
        txt = font_small.render(self.text, True, BLACK)
        surf.blit(txt, (self.rect.x + 8, self.rect.y + 8))

    def value(self, default=0.0):
        try:
            return float(self.text)
        except:
            return default


# --- Create UI Elements ---
input_mass = InputBox("Mass (kg)", 2.0, (40, 150, 100, 32))
input_height = InputBox("Height (m)", 10.0, (40, 210, 100, 32))
input_air = InputBox("Air Drag (k)", 0.05, (40, 270, 100, 32))
restart_btn = Button("Restart", (40, 330, 100, 34))

planet_buttons = [Button(name, (30, 420 + i * 45, 120, 36)) for i, (name, _) in enumerate(PLANETS)]

# --- Simulation state ---
def reset_sim():
    global mass, height_m, velocity, acceleration, time_elapsed, gravity
    global impact_velocity, fall_time, falling

    mass = input_mass.value(2.0)
    height_m = input_height.value(10.0)
    velocity = 0.0
    acceleration = 0.0
    time_elapsed = 0.0
    impact_velocity = None
    fall_time = None
    falling = True
    gravity = PLANETS[current_planet][1]

reset_sim()

# --- Main loop ---
running = True
while running:
    dt = clock.tick(60) / 1000
    if dt <= 0:
        dt = DT_FIXED

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            WIDTH, HEIGHT = event.w, event.h
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if restart_btn.click(event.pos):
                reset_sim()
            for i, btn in enumerate(planet_buttons):
                if btn.click(event.pos):
                    current_planet = i
                    for b in planet_buttons:
                        b.active = False
                    btn.active = True
                    reset_sim()
            input_mass.handle_event(event)
            input_height.handle_event(event)
            input_air.handle_event(event)
        elif event.type == pygame.KEYDOWN:
            input_mass.handle_event(event)
            input_height.handle_event(event)
            input_air.handle_event(event)
            if event.key == pygame.K_RETURN:
                reset_sim()

    # --- Physics ---
    if falling:
        drag = input_air.value(0.0) * velocity * abs(velocity)
        acceleration = gravity - (drag / mass)
        velocity += acceleration * dt
        height_m -= velocity * dt
        time_elapsed += dt
        if height_m <= 0:
            height_m = 0
            impact_velocity = velocity
            fall_time = time_elapsed
            velocity = 0
            falling = False

    # --- Drawing ---
    screen.fill(BG)
    sidebar_width = 200
    pygame.draw.rect(screen, SIDEBAR_BG, (0, 0, sidebar_width, HEIGHT))

    # Sidebar labels
    title = font_large.render("Controls", True, BLACK)
    screen.blit(title, (40, 90))
    input_mass.draw(screen)
    input_height.draw(screen)
    input_air.draw(screen)
    restart_btn.draw(screen)

    sub_title = font_medium.render("Planets", True, BLACK)
    screen.blit(sub_title, (40, 380))
    for btn in planet_buttons:
        btn.draw(screen)

    # Gravity bar visual
    g_bar_x = 30
    g_bar_y = 420 + len(PLANETS) * 45 + 30
    max_g = max(p[1] for p in PLANETS)
    bar_w = 120
    for i, (name, g) in enumerate(PLANETS):
        bar_h = int((g / max_g) * 40)
        pygame.draw.rect(screen, BLUE if i == current_planet else GRAY,
                         (g_bar_x + i * 18, g_bar_y + (40 - bar_h), 12, bar_h))
    screen.blit(font_small.render("Gravity comparison", True, BLACK), (40, g_bar_y + 50))

    # Simulation space
    sim_area = pygame.Rect(sidebar_width + 20, 40, WIDTH - sidebar_width - 40, HEIGHT - 80)
    pygame.draw.rect(screen, WHITE, sim_area, border_radius=8)
    ground_y = sim_area.bottom - 40
    scale_factor = (sim_area.height - 100) / max(1, input_height.value(10.0))
    ball_y = ground_y - height_m * scale_factor
    pygame.draw.line(screen, GRAY, (sim_area.left, ground_y), (sim_area.right, ground_y), 3)
    pygame.draw.circle(screen, BLUE, (sim_area.centerx, int(ball_y)), BALL_RADIUS)

    # Data labels
    data_x = sidebar_width + 40
    data_y = HEIGHT - 100
    screen.blit(font_small.render(f"Planet: {PLANETS[current_planet][0]}  (g={gravity:.2f} m/s²)", True, BLACK), (data_x, data_y))
    screen.blit(font_small.render(f"Time elapsed: {time_elapsed:.3f} s", True, BLACK), (data_x, data_y + 22))
    if fall_time:
        screen.blit(font_small.render(f"Fall time: {fall_time:.3f} s", True, BLACK), (data_x, data_y + 44))
        screen.blit(font_small.render(f"Impact velocity: {impact_velocity:.3f} m/s", True, BLACK), (data_x, data_y + 66))

    pygame.display.flip()

pygame.quit()
sys.exit()