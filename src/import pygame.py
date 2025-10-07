import pygame
import sys
import math
import time

pygame.init()
pygame.display.set_caption("Free Fall — Planet Gravity Simulator")

# --- Initial window ---
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 22)
title_font = pygame.font.SysFont(None, 28)

# --- Colors ---
WHITE = (255, 255, 255)
BG = (245, 245, 250)
BLACK = (10, 10, 10)
BLUE = (50, 140, 255)
GRAY = (200, 200, 200)
ACTIVE = pygame.Color('lightskyblue3')
GREEN = (0, 170, 80)
RED = (200, 50, 50)
PANEL_BG = (230, 230, 230)

# --- Physics defaults ---
# GRAVITY constant removed; we will use current_gravity set by planet
BALL_RADIUS = 20        # px (visual fixed)
RESTUTION = 0.6         # bounce coefficient (you can change)
DT_FIXED = 1/60         # used as a fall-back for dt

# --- Planets (gravity m/s^2 and background color) ---
PLANETS = [
    ("Mercury", 3.7,  (150, 150, 150)),
    ("Venus",   8.87, (255, 200, 120)),
    ("Earth",   9.81, (120, 180, 255)),
    ("Moon",    1.62, (200, 200, 200)),
    ("Mars",    3.71, (255, 120, 90)),
    ("Jupiter", 24.79,(240, 200, 160)),
    ("Neptune", 11.15,(120, 140, 255))
]
current_planet_index = 2  # default Earth

# --- UI helpers ---
class InputBox:
    def __init__(self, x, y, w, h, text='', label=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.label = label
        self.active = False
        self.color_inactive = GRAY
        self.color_active = ACTIVE
        self.color = self.color_inactive
        self.txt_surface = font.render(self.text, True, BLACK)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            self.color = self.color_active if self.active else self.color_inactive
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
                self.color = self.color_inactive
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                # allow digits, dot and minus
                if event.unicode.isdigit() or event.unicode in ".-":
                    self.text += event.unicode
            self.txt_surface = font.render(self.text, True, BLACK)

    def draw(self, surf):
        # label on the left
        label_surface = font.render(self.label, True, BLACK)
        surf.blit(label_surface, (self.rect.x - 140, self.rect.y + 6))
        # box
        pygame.draw.rect(surf, WHITE, self.rect)
        pygame.draw.rect(surf, self.color, self.rect, 2)
        surf.blit(self.txt_surface, (self.rect.x + 6, self.rect.y + 6))

    def set_pos(self, x, y):
        self.rect.x = x
        self.rect.y = y

    def get_value(self, default=0.0):
        try:
            return float(self.text)
        except Exception:
            return default


class Button:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text

    def set_pos(self, x, y):
        self.rect.x = x
        self.rect.y = y

    def draw(self, surf, bg_color, text_color=WHITE):
        pygame.draw.rect(surf, bg_color, self.rect, border_radius=6)
        s = title_font.render(self.text, True, text_color)
        surf.blit(s, s.get_rect(center=self.rect.center))

    def clicked(self, pos):
        return self.rect.collidepoint(pos)


# --- Create inputs (positions updated each frame) ---
weight_box = InputBox(0, 0, 120, 30, text="2.0", label="Weight (kg):")
height_box = InputBox(0, 0, 120, 30, text="10.0", label="Height (m):")
air_box = InputBox(0, 0, 120, 30, text="0.05", label="Air k (drag):")

restart_btn = Button(0, 0, 120, 36, "Restart")
bounce_btn = Button(0, 0, 140, 36, "Bounce: OFF")

# planet buttons container (we'll build rects dynamically)
planet_button_rects = []

# --- Simulation state variables (set in reset_sim) ---
def reset_simulation():
    global mass, initial_height_m, height_m, air_k, velocity, acceleration
    global time_elapsed, fall_time, impact_velocity, peak_speed, falling, start_time
    global current_gravity

    # parse inputs safely
    mass = weight_box.get_value(1.0)
    initial_height_m = max(0.001, height_box.get_value(5.0))
    height_m = initial_height_m   # current height above ground (m)
    air_k = max(0.0, air_box.get_value(0.0))

    # planet gravity
    current_gravity = PLANETS[current_planet_index][1]

    velocity = 0.0
    acceleration = 0.0
    time_elapsed = 0.0
    fall_time = None             # time of first impact recorded here
    impact_velocity = None       # velocity right before first impact
    peak_speed = 0.0             # max |v| during motion
    falling = True
    start_time = time.time()

# initialize
reset_simulation()
bounce_enabled = False

# --- Main loop ---
running = True
while running:
    dt = clock.tick(60) / 1000.0
    if dt <= 0:
        dt = DT_FIXED

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.VIDEORESIZE:
            WIDTH, HEIGHT = event.w, event.h
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            # inputs, buttons and planet buttons
            weight_box.handle_event(event)
            height_box.handle_event(event)
            air_box.handle_event(event)

            if restart_btn.clicked(event.pos):
                reset_simulation()

            if bounce_btn.clicked(event.pos):
                bounce_enabled = not bounce_enabled
                bounce_btn.text = "Bounce: ON" if bounce_enabled else "Bounce: OFF"

            # check planet button clicks
            for idx, rect in enumerate(planet_button_rects):
                if rect.collidepoint(event.pos):
                    current_planet_index = idx
                    reset_simulation()
                    break

        elif event.type == pygame.KEYDOWN:
            weight_box.handle_event(event)
            height_box.handle_event(event)
            air_box.handle_event(event)
            # Enter in any input applies changes (reset sim)
            if event.key == pygame.K_RETURN:
                reset_simulation()

    # --- layout (dynamic to avoid overlap) ---
    left_margin = 24
    top_margin = 18
    input_x = left_margin + 160
    spacing = 48

    weight_box.set_pos(input_x, top_margin)
    height_box.set_pos(input_x, top_margin + spacing)
    air_box.set_pos(input_x, top_margin + 2*spacing)

    restart_btn.set_pos(input_x + 170, top_margin - 2)
    bounce_btn.set_pos(input_x + 170, top_margin + spacing - 2)

    # planet buttons layout (below controls)
    planet_button_rects = []
    planet_area_x = left_margin
    planet_area_y = top_margin + 3*spacing + 6
    btn_w = 110
    btn_h = 34
    btn_gap = 12
    for i, (name, gval, color) in enumerate(PLANETS):
        bx = planet_area_x + i * (btn_w + btn_gap)
        by = planet_area_y
        rect = pygame.Rect(bx, by, btn_w, btn_h)
        planet_button_rects.append(rect)

    # ground and visual scale
    ground_y = HEIGHT - 120
    max_visual_height = max(60, ground_y - (top_margin + 160))  # px available for the fall (leave space for controls)

    # compute scale factor so initial_height_m maps into available pixels
    # Avoid division by zero; also if initial_height is very small, guard scale
    if initial_height_m > 0:
        scale_factor = max_visual_height / initial_height_m
    else:
        scale_factor = 1.0

    # --- physics update ---
    if falling:
        # quadratic drag: Fd = k * v * |v|
        drag = air_k * velocity * abs(velocity)
        # use per-planet gravity
        current_gravity = PLANETS[current_planet_index][1]
        acceleration = current_gravity - (drag / mass)
        velocity += acceleration * dt
        height_m -= velocity * dt   # height above ground (m)
        time_elapsed += dt

        # track peak speed (magnitude)
        if abs(velocity) > peak_speed:
            peak_speed = abs(velocity)

        # collision with ground (height_m <= 0)
        if height_m <= 0:
            # record first impact info (before velocity inversion)
            if impact_velocity is None:
                impact_velocity = velocity
                fall_time = time_elapsed

            # clamp to ground
            height_m = 0.0

            if bounce_enabled:
                # invert velocity with restitution, preserving sign convention
                velocity = -velocity * RESTUTION
                # if bounce is tiny, stop bouncing
                if abs(velocity) < 0.1:
                    velocity = 0.0
                    falling = False
            else:
                velocity = 0.0
                falling = False

    # map height_m -> screen y
    y_pos = ground_y - (height_m * scale_factor)
    # keep ball visually inside top margin if scale_factor changes drastically
    top_limit = top_margin + BALL_RADIUS + 6
    if y_pos < top_limit:
        y_pos = top_limit

    # --- draw background & ground (planet background) ---
    planet_color = PLANETS[current_planet_index][2]
    screen.fill(planet_color)  # planet-specific background color

    # control panel background
    panel_rect = pygame.Rect(12, 12, min(920, WIDTH-24), 220)
    pygame.draw.rect(screen, PANEL_BG, panel_rect, border_radius=8)

    # ground
    pygame.draw.line(screen, BLACK, (0, ground_y), (WIDTH, ground_y), 3)

    # --- draw ball ---
    ball_x = WIDTH // 2
    pygame.draw.circle(screen, BLUE, (ball_x, int(y_pos)), BALL_RADIUS)
    # weight hover label
    wlabel = font.render(f"{mass:.2f} kg", True, BLACK)
    screen.blit(wlabel, (ball_x - wlabel.get_width() // 2, int(y_pos) - BALL_RADIUS - 26))

    # --- draw inputs and buttons ---
    title = title_font.render("Free-Fall Controls", True, BLACK)
    screen.blit(title, (left_margin, top_margin - 8))
    weight_box.draw(screen)
    height_box.draw(screen)
    air_box.draw(screen)
    restart_btn.draw(screen, GREEN)
    bounce_btn.draw(screen, RED if bounce_enabled else GRAY)

    # draw planet buttons
    for idx, rect in enumerate(planet_button_rects):
        name = PLANETS[idx][0]
        color = (100, 200, 255) if idx == current_planet_index else (120, 120, 140)
        pygame.draw.rect(screen, color, rect, border_radius=6)
        lab = font.render(name, True, WHITE)
        screen.blit(lab, (rect.x + (rect.w - lab.get_width())//2, rect.y + (rect.h - lab.get_height())//2))

    # --- info area (bottom-left) ---
    info_x = 24
    info_y = HEIGHT - 100
    info_spacing = 26

    # Velocity display:
    if fall_time is None:
        # still falling (no first impact yet) — show current velocity
        vel_display = velocity
        vel_label = f"Velocity: {vel_display:.3f} m/s"
    else:
        # after first impact — show impact and peak
        impact_v_str = f"{impact_velocity:.3f} m/s" if impact_velocity is not None else "-"
        vel_label = f"Impact v: {impact_v_str}   Peak v: {peak_speed:.3f} m/s"

    acc_label = f"Acceleration: {acceleration:.3f} m/s²" if falling else "Acceleration: 0.000 m/s²"
    time_label = f"Elapsed time: {time_elapsed:.3f} s"
    fall_label = f"Time to ground (first): {fall_time:.3f} s" if fall_time is not None else "Time to ground (first): -"

    # show current planet and its gravity
    planet_name = PLANETS[current_planet_index][0]
    planet_g = PLANETS[current_planet_index][1]
    screen.blit(font.render(f"Planet: {planet_name}  (g = {planet_g:.2f} m/s²)", True, BLACK), (info_x, info_y - 40))

    screen.blit(font.render(vel_label, True, BLACK), (info_x, info_y))
    screen.blit(font.render(acc_label, True, BLACK), (info_x, info_y + info_spacing))
    screen.blit(font.render(time_label, True, BLACK), (info_x, info_y + 2*info_spacing))
    screen.blit(font.render(fall_label, True, BLACK), (info_x, info_y + 3*info_spacing))

    # small help
    help_text = font.render("Click a field, type value, press ENTER to apply. Click planet to switch gravity. Resize window freely.", True, BLACK)
    screen.blit(help_text, (24, HEIGHT - 30))

    pygame.display.flip()

pygame.quit()
sys.exit()
