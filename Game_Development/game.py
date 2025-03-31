import pygame
import sys
import random
import math
import os
from pygame.locals import *

# Initialize Pygame
pygame.init()
pygame.mixer.init()  # For sound effects

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GRAVITY = 0.8
JUMP_STRENGTH = -16
PLAYER_SPEED = 5
COIN_VALUE = 10

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY_BLUE = (135, 206, 235)
BROWN = (139, 69, 19)
GREEN = (0, 128, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
TRANSPARENT = (0, 0, 0, 0)

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Sky Chaser")
clock = pygame.time.Clock()

# Fonts
title_font = pygame.font.Font(None, 64)
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)

# Function to load images
def load_image(name, scale=1, alpha=False):
    try:
        # This would normally load from a file, but we'll create placeholder images
        if name == "player":
            img = pygame.Surface((30, 50), pygame.SRCALPHA)
            pygame.draw.rect(img, (50, 100, 200), (0, 0, 30, 50))
            pygame.draw.rect(img, (100, 150, 250), (5, 5, 20, 20))  # Face
            pygame.draw.rect(img, (0, 0, 0), (10, 10, 4, 4))  # Eye
            pygame.draw.rect(img, (0, 0, 0), (20, 10, 4, 4))  # Eye
        elif name == "coin":
            img = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.circle(img, YELLOW, (10, 10), 10)
            pygame.draw.circle(img, (255, 215, 0), (10, 10), 8)  # Inner circle
            pygame.draw.circle(img, (200, 150, 0), (10, 10), 3)  # Center
        elif name == "platform":
            img = pygame.Surface((100, 30), pygame.SRCALPHA)
            pygame.draw.rect(img, BROWN, (0, 0, 100, 30))
            # Add texture
            for i in range(0, 100, 20):
                pygame.draw.line(img, (100, 50, 0), (i, 0), (i, 30), 2)
            pygame.draw.rect(img, (120, 60, 20), (0, 0, 100, 5))  # Top edge
        elif name == "enemy":
            img = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.rect(img, RED, (0, 0, 30, 30))
            pygame.draw.rect(img, (150, 0, 0), (5, 5, 20, 20))  # Body
            pygame.draw.rect(img, (0, 0, 0), (8, 8, 5, 5))  # Eye
            pygame.draw.rect(img, (0, 0, 0), (18, 8, 5, 5))  # Eye
        elif name == "background":
            img = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            # Sky gradient
            for y in range(SCREEN_HEIGHT):
                # Calculate color based on y position (sky gradient)
                blue = max(100, 235 - (y / SCREEN_HEIGHT * 100))
                pygame.draw.line(img, (135, 206, blue), (0, y), (SCREEN_WIDTH, y))
            
            # Add some clouds
            for _ in range(5):
                cloud_x = random.randint(0, SCREEN_WIDTH)
                cloud_y = random.randint(0, SCREEN_HEIGHT // 3)
                cloud_size = random.randint(40, 100)
                
                for i in range(3):  # Draw multiple circles for cloud shape
                    offset_x = random.randint(-20, 20)
                    offset_y = random.randint(-10, 10)
                    pygame.draw.circle(img, (250, 250, 250), 
                                       (cloud_x + offset_x, cloud_y + offset_y), 
                                       cloud_size // 2)
        elif name == "heart":
            img = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.circle(img, (255, 0, 0), (5, 10), 5)  # Left circle
            pygame.draw.circle(img, (255, 0, 0), (15, 10), 5)  # Right circle
            pygame.draw.polygon(img, (255, 0, 0), [(0, 10), (10, 20), (20, 10)])  # Bottom triangle
        elif name == "grapple_point":
            img = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.circle(img, (200, 200, 200), (10, 10), 10, 2)
            pygame.draw.circle(img, (150, 150, 150), (10, 10), 5)
        else:
            # Default image if name not recognized
            img = pygame.Surface((50, 50), pygame.SRCALPHA)
            pygame.draw.rect(img, (200, 200, 200), (0, 0, 50, 50))
            
        if scale != 1:
            width = int(img.get_width() * scale)
            height = int(img.get_height() * scale)
            img = pygame.transform.scale(img, (width, height))
            
        return img
    except pygame.error as e:
        print(f"Unable to load image: {e}")
        # Return a placeholder surface
        placeholder = pygame.Surface((50, 50), pygame.SRCALPHA)
        placeholder.fill((255, 0, 255))  # Magenta for missing textures
        return placeholder

# Load images
player_img = load_image("player")
player_img_left = pygame.transform.flip(player_img, True, False)
coin_img = load_image("coin")
platform_img = load_image("platform")
enemy_img = load_image("enemy")
background_img = load_image("background")
heart_img = load_image("heart")
grapple_point_img = load_image("grapple_point")

# Animation frames (simulated for this example)
player_frames_right = [player_img]
player_frames_left = [player_img_left]
coin_frames = [coin_img]

# Simulating multiple animation frames
for i in range(1, 4):  # Create 3 more slightly different frames
    # Right-facing player frames
    frame = player_img.copy()
    # Modify frame slightly to simulate animation
    pygame.draw.line(frame, (100, 150, 250), (15, 50), (15 + i*5, 45 - i*2), 3)
    player_frames_right.append(frame)
    
    # Left-facing player frames
    frame_left = pygame.transform.flip(frame, True, False)
    player_frames_left.append(frame_left)
    
    # Coin animation frames
    coin_frame = coin_img.copy()
    # Scale each frame slightly differently to simulate shine effect
    scale = 1.0 - i * 0.05
    width = int(coin_img.get_width() * scale)
    height = int(coin_img.get_height() * scale)
    if width > 0 and height > 0:  # Prevent scaling to zero
        coin_frame = pygame.transform.scale(coin_img, (width, height))
        # Center the smaller frame
        new_frame = pygame.Surface((20, 20), pygame.SRCALPHA)
        new_frame.blit(coin_frame, ((20 - width) // 2, (20 - height) // 2))
        coin_frames.append(new_frame)

# UI Elements
def create_button(text, width=200, height=50, color=(100, 100, 200), hover_color=(150, 150, 250)):
    button = {
        'rect': pygame.Rect(0, 0, width, height),
        'color': color,
        'hover_color': hover_color,
        'text': text,
        'text_color': WHITE,
        'hovered': False
    }
    return button

# Create buttons
start_button = create_button("Start Game")
quit_button = create_button("Quit Game")
restart_button = create_button("Restart")
next_level_button = create_button("Next Level")

# Function to draw a button
def draw_button(button, surface):
    color = button['hover_color'] if button['hovered'] else button['color']
    pygame.draw.rect(surface, color, button['rect'])
    pygame.draw.rect(surface, WHITE, button['rect'], 2)  # Border
    
    text_surf = font.render(button['text'], True, button['text_color'])
    text_rect = text_surf.get_rect(center=button['rect'].center)
    surface.blit(text_surf, text_rect)

# Function to check if a button is clicked
def button_clicked(button, mouse_pos, mouse_pressed):
    if button['rect'].collidepoint(mouse_pos):
        button['hovered'] = True
        if mouse_pressed[0]:  # Left mouse button
            return True
    else:
        button['hovered'] = False
    return False

# Particle system
class Particle:
    def __init__(self, x, y, color=(255, 255, 255), velocity=None, size=5, life=30):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.life = life
        self.max_life = life
        if velocity is None:
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 3)
            self.vx = math.cos(angle) * speed
            self.vy = math.sin(angle) * speed
        else:
            self.vx, self.vy = velocity

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.size = max(0, self.size * (self.life / self.max_life))
        return self.life > 0

    def draw(self, surface):
        alpha = int(255 * (self.life / self.max_life))
        color = (*self.color, alpha) if len(self.color) == 3 else self.color
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), int(self.size))

class ParticleSystem:
    def __init__(self):
        self.particles = []
        
    def add_particle(self, x, y, color=(255, 255, 255), velocity=None, size=5, life=30):
        self.particles.append(Particle(x, y, color, velocity, size, life))
        
    def create_explosion(self, x, y, count=10, color=(255, 255, 0), size_range=(2, 8), life_range=(20, 40)):
        for _ in range(count):
            size = random.uniform(*size_range)
            life = random.randint(*life_range)
            self.add_particle(x, y, color, None, size, life)
            
    def update(self):
        self.particles = [p for p in self.particles if p.update()]
        
    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, particle_system):
        super().__init__()
        self.frames_right = player_frames_right
        self.frames_left = player_frames_left
        self.current_frame = 0
        self.animation_speed = 0.2
        self.image = self.frames_right[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.velocity_y = 0
        self.velocity_x = 0
        self.on_ground = False
        self.can_double_jump = False
        self.is_jumping = False
        self.grappling = False
        self.grapple_point = None
        self.grapple_length = 0
        self.grapple_angle = 0
        self.facing_right = True
        self.lives = 3
        self.score = 0
        self.invulnerable = False
        self.invulnerable_timer = 0
        self.animation_timer = 0
        self.particle_system = particle_system
        
        # Dust trail effect timer
        self.dust_timer = 0

    def update(self, platforms):
        # Handle horizontal movement
        self.velocity_x = 0
        keys = pygame.key.get_pressed()
        
        if keys[K_LEFT]:
            self.velocity_x = -PLAYER_SPEED
            self.facing_right = False
            # Create dust particles when running
            self.dust_timer += 1
            if self.on_ground and self.dust_timer % 5 == 0:
                self.particle_system.add_particle(
                    self.rect.right, self.rect.bottom,
                    color=(150, 120, 100),
                    velocity=(random.uniform(0.5, 1.5), random.uniform(-0.5, -1.5)),
                    size=random.uniform(1, 3),
                    life=random.randint(10, 20)
                )
        if keys[K_RIGHT]:
            self.velocity_x = PLAYER_SPEED
            self.facing_right = True
            # Create dust particles when running
            self.dust_timer += 1
            if self.on_ground and self.dust_timer % 5 == 0:
                self.particle_system.add_particle(
                    self.rect.left, self.rect.bottom,
                    color=(150, 120, 100),
                    velocity=(random.uniform(-0.5, -1.5), random.uniform(-0.5, -1.5)),
                    size=random.uniform(1, 3),
                    life=random.randint(10, 20)
                )
            
        # Apply gravity if not grappling
        if not self.grappling:
            self.velocity_y += GRAVITY
            if self.velocity_y > 20:  # Terminal velocity
                self.velocity_y = 20
        else:
            # Grappling hook physics (simplified)
            dx = self.grapple_point[0] - (self.rect.centerx)
            dy = self.grapple_point[1] - (self.rect.centery)
            distance = math.sqrt(dx*dx + dy*dy)
            
            # Calculate tension only if rope is extended
            if distance > self.grapple_length:
                # Normalize direction vector
                dx /= distance
                dy /= distance
                
                # Calculate how much the rope is extended
                extension = distance - self.grapple_length
                
                # Apply force proportional to extension
                tension = extension * 0.1
                self.velocity_x += dx * tension
                self.velocity_y += dy * tension
                
                # Add a small swinging effect
                self.velocity_x *= 0.99
                self.velocity_y *= 0.99
                
                # Add swing particles at the grapple point
                if random.random() < 0.2:
                    self.particle_system.add_particle(
                        self.grapple_point[0], self.grapple_point[1],
                        color=(200, 200, 200),
                        size=random.uniform(1, 2),
                        life=random.randint(5, 15)
                    )
        
        # Move horizontally and check for collisions
        self.rect.x += self.velocity_x
        self.handle_horizontal_collisions(platforms)
        
        # Move vertically and check for collisions
        self.rect.y += self.velocity_y
        self.on_ground = False
        self.handle_vertical_collisions(platforms)
        
        # Check if player is below the screen
        if self.rect.top > SCREEN_HEIGHT:
            self.take_damage()
            self.rect.x, self.rect.y = 100, 100  # Respawn point
            self.velocity_y = 0
            
        # Handle invulnerability timer
        if self.invulnerable:
            self.invulnerable_timer -= 1
            if self.invulnerable_timer <= 0:
                self.invulnerable = False
                
        # Animation
        self.animate()
    
    def animate(self):
        # Only animate when moving or jumping
        if self.velocity_x != 0 or not self.on_ground:
            self.animation_timer += self.animation_speed
            if self.animation_timer >= len(self.frames_right):
                self.animation_timer = 0
                
            self.current_frame = int(self.animation_timer)
            if self.facing_right:
                self.image = self.frames_right[self.current_frame]
            else:
                self.image = self.frames_left[self.current_frame]
        else:
            # Idle animation - just use the first frame
            if self.facing_right:
                self.image = self.frames_right[0]
            else:
                self.image = self.frames_left[0]
                
        # Flash when invulnerable
        if self.invulnerable and self.invulnerable_timer % 6 < 3:
            # Create a semi-transparent version for flashing
            temp_img = self.image.copy()
            temp_img.set_alpha(128)
            self.image = temp_img
    
    def handle_horizontal_collisions(self, platforms):
        collisions = pygame.sprite.spritecollide(self, platforms, False)
        for platform in collisions:
            if self.velocity_x > 0:  # Moving right
                self.rect.right = platform.rect.left
            elif self.velocity_x < 0:  # Moving left
                self.rect.left = platform.rect.right
    
    def handle_vertical_collisions(self, platforms):
        collisions = pygame.sprite.spritecollide(self, platforms, False)
        for platform in collisions:
            if self.velocity_y > 0:  # Moving down, i.e., falling
                self.rect.bottom = platform.rect.top
                self.velocity_y = 0
                self.on_ground = True
                self.can_double_jump = True
                
                # Create landing particles
                if self.is_jumping:
                    for _ in range(5):
                        self.particle_system.add_particle(
                            self.rect.centerx + random.uniform(-10, 10), 
                            self.rect.bottom,
                            color=(150, 120, 100),
                            velocity=(random.uniform(-1, 1), random.uniform(-2, -1)),
                            size=random.uniform(2, 4),
                            life=random.randint(15, 25)
                        )
                self.is_jumping = False
            elif self.velocity_y < 0:  # Moving up, i.e., jumping
                self.rect.top = platform.rect.bottom
                self.velocity_y = 0
    
    def jump(self):
        if self.on_ground:
            self.velocity_y = JUMP_STRENGTH
            self.on_ground = False
            self.is_jumping = True
            
            # Create jump particles
            for _ in range(8):
                self.particle_system.add_particle(
                    self.rect.centerx + random.uniform(-5, 5), 
                    self.rect.bottom,
                    color=(150, 120, 100),
                    velocity=(random.uniform(-1, 1), random.uniform(0, 2)),
                    size=random.uniform(2, 4),
                    life=random.randint(15, 25)
                )
        elif self.can_double_jump:
            self.velocity_y = JUMP_STRENGTH
            self.can_double_jump = False
            
            # Create double jump particles (more colorful)
            for _ in range(12):
                self.particle_system.add_particle(
                    self.rect.centerx + random.uniform(-10, 10), 
                    self.rect.centery + random.uniform(-5, 5),
                    color=(200, 200, 255),
                    velocity=(random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5)),
                    size=random.uniform(3, 6),
                    life=random.randint(20, 30)
                )
    
    def start_grapple(self, point):
        if not self.grappling:
            self.grappling = True
            self.grapple_point = point
            
            # Calculate grapple length (distance between player and grapple point)
            dx = point[0] - self.rect.centerx
            dy = point[1] - self.rect.centery
            self.grapple_length = math.sqrt(dx*dx + dy*dy)
            
            # Create grapple particles
            for _ in range(15):
                progress = _ / 15
                x = self.rect.centerx + dx * progress
                y = self.rect.centery + dy * progress
                self.particle_system.add_particle(
                    x, y,
                    color=(200, 200, 200),
                    velocity=(random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5)),
                    size=random.uniform(1, 3),
                    life=random.randint(10, 20)
                )
    
    def end_grapple(self):
        if self.grappling:
            # Create release particles
            dx = self.grapple_point[0] - self.rect.centerx
            dy = self.grapple_point[1] - self.rect.centery
            for _ in range(10):
                progress = _ / 10
                x = self.rect.centerx + dx * progress
                y = self.rect.centery + dy * progress
                self.particle_system.add_particle(
                    x, y,
                    color=(200, 200, 200),
                    velocity=(random.uniform(-1, 1), random.uniform(-1, 1)),
                    size=random.uniform(1, 3),
                    life=random.randint(5, 15)
                )
                
        self.grappling = False
        self.grapple_point = None
        
    def take_damage(self):
        if not self.invulnerable:
            self.lives -= 1
            self.invulnerable = True
            self.invulnerable_timer = 60  # Invulnerable for 60 frames (1 second at 60 FPS)
            
            # Create damage particles
            for _ in range(20):
                self.particle_system.add_particle(
                    self.rect.centerx + random.uniform(-10, 10), 
                    self.rect.centery + random.uniform(-10, 10),
                    color=(255, 50, 50),
                    velocity=(random.uniform(-2, 2), random.uniform(-2, 2)),
                    size=random.uniform(3, 6),
                    life=random.randint(20, 40)
                )
            
    def collect_coin(self):
        self.score += COIN_VALUE
        
        # Create coin collection particles
        for _ in range(15):
            self.particle_system.add_particle(
                self.rect.centerx + random.uniform(-5, 5), 
                self.rect.centery + random.uniform(-5, 5),
                color=(255, 215, 0),
                velocity=(random.uniform(-1, 1), random.uniform(-2, 0)),
                size=random.uniform(2, 4),
                life=random.randint(20, 30)
            )
        
    def draw_grapple_hook(self, screen):
        if self.grappling and self.grapple_point:
            # Draw a line with a slight wave effect
            steps = 20
            prev_x, prev_y = self.rect.centerx, self.rect.centery
            for i in range(1, steps + 1):
                progress = i / steps
                # Base position on the line
                x = self.rect.centerx + (self.grapple_point[0] - self.rect.centerx) * progress
                y = self.rect.centery + (self.grapple_point[1] - self.rect.centery) * progress
                
                # Add a small sine wave
                if i > 1 and i < steps:
                    wave_amt = math.sin(progress * math.pi * 2 + pygame.time.get_ticks() * 0.01) * 3
                    # Calculate perpendicular vector to the line
                    dx = self.grapple_point[0] - self.rect.centerx
                    dy = self.grapple_point[1] - self.rect.centery
                    length = math.sqrt(dx*dx + dy*dy)
                    if length > 0:
                        # Perpendicular vector
                        px, py = -dy/length, dx/length
                        x += px * wave_amt
                        y += py * wave_amt
                
                # Draw line segment
                pygame.draw.line(screen, (100, 100, 100), (prev_x, prev_y), (x, y), 3)
                prev_x, prev_y = x, y

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.frames = coin_frames
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.animation_timer = 0
        self.animation_speed = 0.1
        self.hover_offset = 0
        self.hover_speed = 0.05
        
    def update(self):
        # Animate the coin
        self.animation_timer += self.animation_speed
        if self.animation_timer >= len(self.frames):
            self.animation_timer = 0
            
        frame_index = int(self.animation_timer)
        if frame_index < len(self.frames):
            self.image = self.frames[frame_index]
            
        # Add a hovering effect
        self.hover_offset = math.sin(pygame.time.get_ticks() * self.hover_speed) * 3
        self.rect.y = self.rect.y + self.hover_offset

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color=BROWN):
        super().__init__()
        # Create a surface with the right dimensions
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Draw the platform using the provided image as a tile
        tile_width = platform_img.get_width()
        tile_height = platform_img.get_height()
        
        for i in range(0, width, tile_width):
            for j in range(0, height, tile_height):
                # Calculate the portion of the tile to use
                src_width = min(tile_width, width - i)
                src_height = min(tile_height, height - j)
                src_rect = pygame.Rect(0, 0, src_width, src_height)
                
                # Draw the tile portion
                self.image.blit(platform_img, (i, j), src_rect)
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, particle_system, platform=None, patrol_distance=100):
        super().__init__()
        self.image = enemy_img.copy()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.platform = platform
        self.start_x = x
        self.patrol_distance = patrol_distance
        self.direction = 1
        self.speed = 2
        self.particle_system = particle_system
        self.animation_timer = 0
        
    def update(self):
        # Simple patrol AI
        self.rect.x += self.speed * self.direction
        
        # Change direction if reached patrol limit
        if self.rect.x > self.start_x + self.patrol_distance:
            self.direction = -1
            self.image = pygame.transform.flip(self.image, True, False)
        elif self.rect.x < self.start_x:
            self.direction = 1
            self.image = pygame.transform.flip(self.image, True, False)
            
        # Stay on platform if assigned
        if self.platform:
            if self.rect.right > self.platform.rect.right:
                self.rect.right = self.platform.rect.right
                self.direction = -1
                self.image = pygame.transform.flip(self.image, True, False)
            elif self.rect.left < self.platform.rect.left:
                self.rect.left = self.platform.rect.left
                self.direction = 1
                self.image = pygame.transform.flip(self.image, True, False)
                
        # Create movement particles occasionally
        self.animation_timer += 1
        if self.animation_timer % 10 == 0:
            self.particle_system.add_particle(
                self.rect.centerx - self.direction * 15, 
                self.rect.bottom,
                color=(200, 100, 100),
                velocity=(random.uniform(-0.5, 0.5), random.uniform(-1, 0)),
                size=random.uniform(1, 2),
                life=random.randint(10, 20)
            )

class Game:
    def __init__(self):
        self.particle_system = ParticleSystem()
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        
        # Create the player
        self.player = Player(100, 100, self.particle_system)
        self.all_sprites.add(self.player)
        
        # Create the level
        self.create_level()
        
        # Game state
        self.game_over = False
        self.level_complete = False
        self.game_state = "menu"  # "menu", "playing", "game_over", "level_complete"
        
        # Position buttons
        start_button['rect'].center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        quit_button['rect'].center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70)
        restart_button['rect'].center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        next_level_button['rect'].center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70)
        
        # Camera offset for scrolling
        self.camera_offset = [0, 0]
        
        # Level tracking
        self.create_level = 1
        self.max_level = 3
        
        # Sound effects (placeholder - would normally load from files)
        self.sounds = {
            'jump': None,
            'coin': None,
            'damage': None,
            'grapple': None
        }
        
    def create_level(self):
        # Clear existing level
        self.all_sprites.empty()
        self.platforms.empty()
        self.coins.empty()
        self.enemies.empty()
        
        # Add player back
        self.all_sprites.add(self.player)
        self.player.rect.x, self.player.rect.y = 100, 100
        self.player.velocity_y = 0
        self.player.velocity_x = 0
        self.player.grappling = False
        
        # Create platforms based on current level
        if self.create_level == 1:
            # Level 1 - Basic platforms
            self.create_platform(0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40)  # Ground
            self.create_platform(100, 400, 100, 20)
            self.create_platform(300, 300, 100, 20)
            self.create_platform(500, 400, 100, 20)
            self.create_platform(700, 300, 100, 20)
            
            # Add coins
            self.create_coin(150, 370)
            self.create_coin(350, 270)
            self.create_coin(550, 370)
            self.create_coin(750, 270)
            
            # Add an enemy
            enemy = Enemy(400, 280, self.particle_system, self.platforms.sprites()[1])
            self.all_sprites.add(enemy)
            self.enemies.add(enemy)
            
        elif self.create_level == 2:
            # Level 2 - More challenging
            self.create_platform(0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40)  # Ground
            self.create_platform(100, 450, 80, 20)
            self.create_platform(250, 350, 80, 20)
            self.create_platform(400, 250, 80, 20)
            self.create_platform(550, 350, 80, 20)
            self.create_platform(700, 450, 80, 20)
            
            # Add coins
            self.create_coin(130, 420)
            self.create_coin(280, 320)
            self.create_coin(430, 220)
            self.create_coin(580, 320)
            self.create_coin(730, 420)
            
            # Add enemies
            enemy1 = Enemy(270, 330, self.particle_system, self.platforms.sprites()[1])
            enemy2 = Enemy(570, 330, self.particle_system, self.platforms.sprites()[3])
            self.all_sprites.add(enemy1, enemy2)
            self.enemies.add(enemy1, enemy2)
            
        elif self.create_level == 3:
            # Level 3 - Final challenge
            self.create_platform(0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40)  # Ground
            self.create_platform(100, 500, 60, 20)
            self.create_platform(200, 400, 60, 20)
            self.create_platform(300, 300, 60, 20)
            self.create_platform(400, 200, 60, 20)
            self.create_platform(500, 300, 60, 20)
            self.create_platform(600, 400, 60, 20)
            self.create_platform(700, 500, 60, 20)
            
            # Add coins
            self.create_coin(130, 470)
            self.create_coin(230, 370)
            self.create_coin(330, 270)
            self.create_coin(430, 170)
            self.create_coin(530, 270)
            self.create_coin(630, 370)
            self.create_coin(730, 470)
            
            # Add enemies
            enemy1 = Enemy(220, 380, self.particle_system, self.platforms.sprites()[1])
            enemy2 = Enemy(420, 180, self.particle_system, self.platforms.sprites()[3])
            enemy3 = Enemy(620, 380, self.particle_system, self.platforms.sprites()[5])
            self.all_sprites.add(enemy1, enemy2, enemy3)
            self.enemies.add(enemy1, enemy2, enemy3)
    
    def create_platform(self, x, y, width, height):
        platform = Platform(x, y, width, height)
        self.all_sprites.add(platform)
        self.platforms.add(platform)
        return platform
    
    def create_coin(self, x, y):
        coin = Coin(x, y)
        self.all_sprites.add(coin)
        self.coins.add(coin)
        return coin
    
    def update_camera(self):
        # Simple camera that follows the player vertically
        target_y = self.player.rect.centery - SCREEN_HEIGHT // 3
        self.camera_offset[1] += (target_y - self.camera_offset[1]) * 0.1
        
        # Don't let camera go above the top of the level
        if self.camera_offset[1] < 0:
            self.camera_offset[1] = 0
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    if self.game_state == "playing":
                        self.game_state = "menu"
                    else:
                        pygame.quit()
                        sys.exit()
                
                if event.key == K_SPACE and self.game_state == "playing":
                    self.player.jump()
                
                if event.key == K_r and self.game_state == "game_over":
                    self.reset_game()
                
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if self.game_state == "playing":
                    # Grappling hook mechanic
                    mouse_pos = pygame.mouse.get_pos()
                    adjusted_mouse_pos = (mouse_pos[0], mouse_pos[1] + self.camera_offset[1])
                    self.player.start_grapple(adjusted_mouse_pos)
                
                # Check menu buttons
                if self.game_state == "menu":
                    if button_clicked(start_button, mouse_pos, (True, False, False)):
                        self.game_state = "playing"
                    elif button_clicked(quit_button, mouse_pos, (True, False, False)):
                        pygame.quit()
                        sys.exit()
                
                elif self.game_state == "game_over":
                    if button_clicked(restart_button, mouse_pos, (True, False, False)):
                        self.reset_game()
                    elif button_clicked(quit_button, mouse_pos, (True, False, False)):
                        pygame.quit()
                        sys.exit()
                
                elif self.game_state == "level_complete":
                    if button_clicked(next_level_button, mouse_pos, (True, False, False)):
                        self.next_level()
                    elif button_clicked(quit_button, mouse_pos, (True, False, False)):
                        pygame.quit()
                        sys.exit()
            
            if event.type == MOUSEBUTTONUP and event.button == 1 and self.game_state == "playing":
                self.player.end_grapple()
    
    def update(self):
        if self.game_state == "playing":
            # Update all game objects
            self.player.update(self.platforms)
            
            # Check for coin collection
            coins_collected = pygame.sprite.spritecollide(self.player, self.coins, True)
            for coin in coins_collected:
                self.player.collect_coin()
            
            # Check for enemy collisions
            if not self.player.invulnerable:
                enemy_hits = pygame.sprite.spritecollide(self.player, self.enemies, False)
                if enemy_hits:
                    self.player.take_damage()
            
            # Update other sprites
            self.coins.update()
            self.enemies.update()
            self.particle_system.update()
            
            # Check if player collected all coins
            if len(self.coins) == 0:
                if self.create_level < self.max_level:
                    self.game_state = "level_complete"
                else:
                    # Game complete
                    self.game_state = "game_over"
                    self.level_complete = True
            
            # Check if player is out of lives
            if self.player.lives <= 0:
                self.game_state = "game_over"
                self.level_complete = False
            
            # Update camera
            self.update_camera()
    
    def draw(self):
        # Draw background
        screen.blit(background_img, (0, 0))
        
        if self.game_state == "menu":
            self.draw_menu()
        elif self.game_state == "playing":
            self.draw_game()
        elif self.game_state == "game_over":
            self.draw_game_over()
        elif self.game_state == "level_complete":
            self.draw_level_complete()
        
        pygame.display.flip()
    
    def draw_menu(self):
        # Draw title
        title_text = title_font.render("Sky Chaser", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        screen.blit(title_text, title_rect)
        
        # Draw buttons
        draw_button(start_button, screen)
        draw_button(quit_button, screen)
        
        # Draw instructions
        instructions = [
            "Use arrow keys to move",
            "Space to jump",
            "Left click to grapple",
            "Collect all coins to complete the level",
            "Avoid enemies!"
        ]
        
        for i, line in enumerate(instructions):
            text = small_font.render(line, True, WHITE)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 
                         SCREEN_HEIGHT // 2 + 150 + i * 30))
    
    def draw_game(self):
        # Draw all sprites with camera offset
        for sprite in self.all_sprites:
            if isinstance(sprite, Player):
                # Player is drawn at screen-relative position
                screen.blit(sprite.image, (sprite.rect.x, sprite.rect.y - self.camera_offset[1]))
            else:
                # Other sprites are drawn with camera offset
                screen.blit(sprite.image, (sprite.rect.x, sprite.rect.y - self.camera_offset[1]))
        
        # Draw grapple hook
        self.player.draw_grapple_hook(screen)
        
        # Draw particles
        self.particle_system.draw(screen)
        
        # Draw UI
        self.draw_ui()
    
    def draw_ui(self):
        # Draw score
        score_text = font.render(f"Score: {self.player.score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        # Draw lives
        for i in range(self.player.lives):
            screen.blit(heart_img, (10 + i * 25, 50))
        
        # Draw level indicator
        level_text = font.render(f"Level: {self.create_level}/{self.max_level}", True, WHITE)
        screen.blit(level_text, (SCREEN_WIDTH - level_text.get_width() - 10, 10))
        
        # Draw coins remaining
        coins_text = font.render(f"Coins: {len(self.coins)}", True, WHITE)
        screen.blit(coins_text, (SCREEN_WIDTH - coins_text.get_width() - 10, 50))
    
    def draw_game_over(self):
        # Draw game over message
        if self.level_complete:
            message = "Congratulations! You completed all levels!"
        else:
            message = "Game Over"
        
        game_over_text = title_font.render(message, True, WHITE)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        screen.blit(game_over_text, game_over_rect)
        
        # Draw final score
        score_text = font.render(f"Final Score: {self.player.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        screen.blit(score_text, score_rect)
        
        # Draw buttons
        if not self.level_complete:
            draw_button(restart_button, screen)
        draw_button(quit_button, screen)
    
    def draw_level_complete(self):
        # Draw level complete message
        complete_text = title_font.render("Level Complete!", True, WHITE)
        complete_rect = complete_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        screen.blit(complete_text, complete_rect)
        
        # Draw score
        score_text = font.render(f"Score: {self.player.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        screen.blit(score_text, score_rect)
        
        # Draw buttons
        draw_button(next_level_button, screen)
        draw_button(quit_button, screen)
    
    def reset_game(self):
        self.player.lives = 3
        self.player.score = 0
        self.create_level = 1
        self.create_level()
        self.game_state = "playing"
        self.game_over = False
        self.level_complete = False
    
    def next_level(self):
        self.create_level += 1
        self.create_level()
        self.game_state = "playing"
    
    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            clock.tick(FPS)

# Main game loop
if __name__ == "__main__":
    game = Game()
    game.run()