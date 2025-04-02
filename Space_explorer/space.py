import pygame
import random
import math
from pygame.locals import *

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Stellar Explorer")
clock = pygame.time.Clock()

#players and ship movement
class Ship:
    def __init__(self):
        self.x = 400
        self.y = 300
        self.speed = 5
        self.angle = 0
        self.fuel = 100
        self.health = 100
        self.image = pygame.Surface((30, 20))
        self.image.fill((0, 255, 255))  # Cyan ship
    
    def move(self, keys):
        if keys[K_LEFT]: self.angle -= 5
        if keys[K_RIGHT]: self.angle += 5
        if keys[K_UP] and self.fuel > 0:
            self.x += math.cos(math.radians(self.angle)) * self.speed
            self.y -= math.sin(math.radians(self.angle)) * self.speed
            self.fuel -= 0.1

#planets and procedural movement

class Planet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.randint(20, 50)
        self.color = (
            random.randint(50, 200),
            random.randint(50, 200),
            random.randint(50, 200)
        )
        self.resources = random.randint(10, 100)

def generate_galaxy(num_planets):
    planets = []
    for _ in range(num_planets):
        x = random.randint(0, 1600)  # Larger than screen for exploration
        y = random.randint(0, 1200)
        planets.append(Planet(x, y))
    return planets
#main

def main():
    ship = Ship()
    planets = generate_galaxy(20)
    camera_x, camera_y = 0, 0
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
        
        keys = pygame.key.get_pressed()
        ship.move(keys)
        
        # Camera follows ship
        camera_x = ship.x - 400
        camera_y = ship.y - 300
        
        # Drawing
        screen.fill((0, 0, 20))  # Dark space background
        
        # Draw stars
        for _ in range(100):
            x = random.randint(0, 800)
            y = random.randint(0, 600)
            pygame.draw.circle(screen, (255, 255, 255), (x, y), 1)
        
        # Draw planets (relative to camera)
        for planet in planets:
            pygame.draw.circle(
                screen,
                planet.color,
                (int(planet.x - camera_x), int(planet.y - camera_y)),
                planet.size
            )
        
        # Draw rotated ship
        rotated_ship = pygame.transform.rotate(ship.image, ship.angle)
        screen.blit(rotated_ship, (400 - rotated_ship.get_width() // 2, 300 - rotated_ship.get_height() // 2))
        
        # UI (Fuel & Health)
        pygame.draw.rect(screen, (255, 165, 0), (10, 10, ship.fuel * 2, 20))
        pygame.draw.rect(screen, (255, 0, 0), (10, 40, ship.health * 2, 20))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()