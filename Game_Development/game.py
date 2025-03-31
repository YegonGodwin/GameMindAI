import pygame
import sys
import random
import math
from pygame.locals import *

# Initialize Pygame
pygame.init()

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

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Sky Chaser")
clock = pygame.time.Clock()

# Font
font = pygame.font.Font(None, 36)

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 50))
        self.image.fill((255, 100, 100))  # Player color
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.velocity_y = 0
        self.velocity_x = 0
        self.on_ground = False
        self.can_double_jump = False
        self.grappling = False
        self.grapple_point = None
        self.grapple_length = 0
        self.grapple_angle = 0
        self.facing_right = True
        self.lives = 3
        self.score = 0
        self.invulnerable = False
        self.invulnerable_timer = 0

    def update(self, platforms):
        # Handle horizontal movement
        self.velocity_x = 0
        keys = pygame.key.get_pressed()
        
        if keys[K_LEFT]:
            self.velocity_x = -PLAYER_SPEED
            self.facing_right = False
        if keys[K_RIGHT]:
            self.velocity_x = PLAYER_SPEED
            self.facing_right = True
            
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
            elif self.velocity_y < 0:  # Moving up, i.e., jumping
                self.rect.top = platform.rect.bottom
                self.velocity_y = 0
    
    def jump(self):
        if self.on_ground:
            self.velocity_y = JUMP_STRENGTH
            self.on_ground = False
        elif self.can_double_jump:
            self.velocity_y = JUMP_STRENGTH
            self.can_double_jump = False
    
    def start_grapple(self, point):
        if not self.grappling:
            self.grappling = True
            self.grapple_point = point
            
            # Calculate grapple length (distance between player and grapple point)
            dx = point[0] - self.rect.centerx
            dy = point[1] - self.rect.centery
            self.grapple_length = math.sqrt(dx*dx + dy*dy)
    
    def end_grapple(self):
        self.grappling = False
        self.grapple_point = None
        
    def take_damage(self):
        if not self.invulnerable:
            self.lives -= 1
            self.invulnerable = True
            self.invulnerable_timer = 60  # Invulnerable for 60 frames (1 second at 60 FPS)
            
    def collect_coin(self):
        self.score += COIN_VALUE
        
    def draw_grapple_hook(self, screen):
        if self.grappling and self.grapple_point:
            pygame.draw.line(screen, (100, 100, 100), 
                            (self.rect.centerx, self.rect.centery), 
                            self.grapple_point, 3)

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color=BROWN):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((15, 15), pygame.SRCALPHA)
        pygame.draw.circle(self.image, YELLOW, (7, 7), 7)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, platform=None, patrol_distance=100):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.platform = platform
        self.start_x = x
        self.patrol_distance = patrol_distance
        self.direction = 1
        self.speed = 2
        
    def update(self):
        # Simple patrol AI
        self.rect.x += self.speed * self.direction
        
        # Change direction if reached patrol limit
        if self.rect.x > self.start_x + self.patrol_distance:
            self.direction = -1
        elif self.rect.x < self.start_x:
            self.direction = 1
            
        # Stay on platform if assigned
        if self.platform:
            if self.rect.right > self.platform.rect.right:
                self.rect.right = self.platform.rect.right
                self.direction = -1
            elif self.rect.left < self.platform.rect.left:
                self.rect.left = self.platform.rect.left
                self.direction = 1

class Game:
    def __init__(self):
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        
        # Create the player
        self.player = Player(100, 100)
        self.all_sprites.add(self.player)
        
        # Create the level
        self.create_level()
        
        # Game state
        self.game_over = False
        self.level_complete = False
        
    def create_level(self):
        # Ground
        ground = Platform(0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40)
        self.platforms.add(ground)
        self.all_sprites.add(ground)
        
        # Create some platforms
        platforms = [
            (100, 450, 200, 20),
            (400, 400, 150, 20),
            (200, 320, 100, 20),
            (400, 250, 200, 20),
            (100, 200, 150, 20),
            (550, 150, 200, 20)
        ]
        
        for plat in platforms:
            x, y, width, height = plat
            p = Platform(x, y, width, height)
            self.platforms.add(p)
            self.all_sprites.add(p)
            
            # Add an enemy to some platforms
            if random.random() > 0.5:
                e = Enemy(x + width//2, y - 30, p, width - 30)
                self.enemies.add(e)
                self.all_sprites.add(e)
            
            # Add coins above platforms
            for i in range(3):
                coin_x = x + (i * width//3) + width//6
                coin_y = y - 30
                c = Coin(coin_x, coin_y)
                self.coins.add(c)
                self.all_sprites.add(c)
        
        # Add some grapple points (just visual markers, not functional in this demo)
        self.grapple_points = [
            (300, 100),
            (500, 80),
            (150, 120),
            (650, 200)
        ]
        
    def check_collisions(self):
        # Check coin collisions
        coin_collisions = pygame.sprite.spritecollide(self.player, self.coins, True)
        for coin in coin_collisions:
            self.player.collect_coin()
            
        # Check enemy collisions
        if not self.player.invulnerable:
            enemy_collisions = pygame.sprite.spritecollide(self.player, self.enemies, False)
            if enemy_collisions:
                self.player.take_damage()
                
                # Knockback effect
                if self.player.facing_right:
                    self.player.velocity_x = -10
                else:
                    self.player.velocity_x = 10
                self.player.velocity_y = -5
                
        # Check for level completion (all coins collected)
        if len(self.coins) == 0:
            self.level_complete = True
            
        # Check for game over
        if self.player.lives <= 0:
            self.game_over = True
            
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == KEYDOWN:
                if event.key == K_UP or event.key == K_SPACE:
                    self.player.jump()
                elif event.key == K_q:
                    # Press Q to grapple (simplified mechanic)
                    # Find closest grapple point in range
                    if not self.player.grappling:
                        closest_dist = float('inf')
                        closest_point = None
                        for point in self.grapple_points:
                            dx = point[0] - self.player.rect.centerx
                            dy = point[1] - self.player.rect.centery
                            dist = math.sqrt(dx*dx + dy*dy)
                            if dist < 200 and dist < closest_dist:  # Max grapple range of 200 pixels
                                closest_dist = dist
                                closest_point = point
                                
                        if closest_point:
                            self.player.start_grapple(closest_point)
                elif event.key == K_e:
                    # Press E to release grapple
                    self.player.end_grapple()
                    
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                # Alternative: click to grapple
                if not self.player.grappling:
                    point = event.pos
                    dx = point[0] - self.player.rect.centerx
                    dy = point[1] - self.player.rect.centery
                    dist = math.sqrt(dx*dx + dy*dy)
                    if dist < 200:  # Max grapple range
                        self.player.start_grapple(point)
                else:
                    self.player.end_grapple()
                    
    def update(self):
        if not self.game_over and not self.level_complete:
            self.player.update(self.platforms)
            self.enemies.update()
            self.check_collisions()
            
    def draw_hud(self):
        # Draw score
        score_text = font.render(f"Score: {self.player.score}", True, WHITE)
        screen.blit(score_text, (20, 20))
        
        # Draw lives
        lives_text = font.render(f"Lives: {self.player.lives}", True, WHITE)
        screen.blit(lives_text, (SCREEN_WIDTH - 120, 20))
        
    def draw_grapple_points(self):
        # Draw grapple points as targets
        for point in self.grapple_points:
            pygame.draw.circle(screen, (200, 200, 200), point, 10, 2)
            pygame.draw.circle(screen, (150, 150, 150), point, 5)
            
    def draw(self):
        screen.fill(SKY_BLUE)
        
        # Draw all sprites
        self.all_sprites.draw(screen)
        
        # Draw grapple hook if active
        self.player.draw_grapple_hook(screen)
        
        # Draw grapple points
        self.draw_grapple_points()
        
        # Draw HUD
        self.draw_hud()
        
        # Draw game over or level complete message
        if self.game_over:
            game_over_text = font.render("GAME OVER", True, WHITE)
            screen.blit(game_over_text, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2))
            restart_text = font.render("Press R to restart", True, WHITE)
            screen.blit(restart_text, (SCREEN_WIDTH//2 - 120, SCREEN_HEIGHT//2 + 50))
        
        elif self.level_complete:
            level_complete_text = font.render("LEVEL COMPLETE!", True, WHITE)
            screen.blit(level_complete_text, (SCREEN_WIDTH//2 - 120, SCREEN_HEIGHT//2))
            next_level_text = font.render("Press N for next level", True, WHITE)
            screen.blit(next_level_text, (SCREEN_WIDTH//2 - 130, SCREEN_HEIGHT//2 + 50))
        
        pygame.display.flip()

def main():
    game = Game()
    
    # Main game loop
    while True:
        game.handle_events()
        game.update()
        game.draw()
        clock.tick(FPS)
        
        # Check for restart
        keys = pygame.key.get_pressed()
        if (game.game_over or game.level_complete) and keys[K_r]:
            game = Game()  # Restart game
            
        # Next level (would normally load a new level)
        if game.level_complete and keys[K_n]:
            game = Game()  # For now, just restart with same level

if __name__ == "__main__":
    main()