import pygame
import random

# Flower Type Data
FLOWER_DATA = {
    "Clover": {"cost": 15, "health": 100, "wilting_rate": 0.05, "sprite": "flower_clover"},
    "Lavender": {"cost": 25, "health": 80, "wilting_rate": 0.08, "sprite": "flower_lavender"},
    "Sunflower": {"cost": 35, "health": 60, "wilting_rate": 0.12, "sprite": "flower_sunflower"},
    "Dandelion": {"cost": 10, "health": 120, "wilting_rate": 0.03, "sprite": "flower_dandelion"},
}

WATERING_HEAL_AMOUNT = 50 # Amount health restored by watering

class Flower:
    def __init__(self, pos, flower_type, asset_manager):
        if flower_type not in FLOWER_DATA:
            raise ValueError(f"Unknown flower type: {flower_type}")

        self.asset_manager = asset_manager
        self.type = flower_type
        data = FLOWER_DATA[self.type]

        self.cost = data["cost"]
        self.max_health = data["health"]
        self.health = self.max_health
        self.wilting_rate = data["wilting_rate"] # Health lost per second
        self.sprite_name = data["sprite"]

        self.image = self.asset_manager.get_sprite(self.sprite_name)
        self.image = pygame.transform.scale(self.image, (32, 32)) # Example size
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.Vector2(pos)

        self.is_wilting = True # Starts losing health immediately
        self.pollinators = set() # Bees currently visiting this flower

    def update(self, dt):
        if self.is_wilting:
            self.health -= self.wilting_rate * dt
            if self.health <= 0:
                self.health = 0
                # Flower "dies" - could be removed by simulation system
                # print(f"{self.type} at {self.pos} wilted.")
                pass # Let sim.py handle removal

    def water(self):
        self.health = min(self.max_health, self.health + WATERING_HEAL_AMOUNT)
        print(f"Watered {self.type}. Health: {self.health:.1f}/{self.max_health}")
        # Maybe add a visual indicator briefly?

    def can_be_pollinated(self):
        # Can bees visit this flower? Check health, maybe max pollinators?
        return self.health > 10 # Example: Needs some health left

    def add_pollinator(self, bee):
        self.pollinators.add(bee)

    def remove_pollinator(self, bee):
        self.pollinators.discard(bee)

    def draw(self, screen):
        # Adjust appearance based on health? (e.g., slightly faded when low)
        alpha = int(max(50, 255 * (self.health / self.max_health))) # Fade effect
        temp_image = self.image.copy()
        temp_image.set_alpha(alpha)
        screen.blit(temp_image, self.rect)

        # Draw health indicator (optional)
        if self.health < self.max_health * 0.9: # Only show if not full
            health_ratio = self.health / self.max_health
            bar_width = self.rect.width * 0.8
            bar_height = 4
            bar_x = self.rect.centerx - bar_width / 2
            bar_y = self.rect.top - bar_height - 2

            # Background of health bar
            pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
            # Foreground (current health)
            health_color = (0, 200, 0) if health_ratio > 0.5 else ((255, 255, 0) if health_ratio > 0.2 else (200, 0, 0))
            pygame.draw.rect(screen, health_color, (bar_x, bar_y, bar_width * health_ratio, bar_height))