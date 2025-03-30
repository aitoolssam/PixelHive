import pygame
import random
import math

# Bee States
class BeeState:
    IDLE = 0        # In hive
    FLYING_OUT = 1  # Leaving hive to find flower
    FORAGING = 2    # At flower, gathering nectar/pollen
    RETURNING = 3   # Flying back to hive

class Bee:
    def __init__(self, hive, asset_manager):
        self.hive = hive # The hive this bee belongs to
        self.asset_manager = asset_manager
        self.image = self.asset_manager.get_sprite('bee') # Get pre-loaded sprite
        self.image = pygame.transform.scale(self.image, (16, 16)) # Example size
        self.rect = self.image.get_rect(center=hive.rect.center)
        self.pos = pygame.Vector2(self.rect.center) # Use Vector2 for movement

        self.state = BeeState.IDLE
        self.target_flower = None
        self.forage_timer = 0.0
        self.speed = 80 # Pixels per second
        self.wander_target = None

    def find_flower(self, flowers):
        """Finds a nearby flower that isn't targeted by too many other bees."""
        nearby_flowers = [f for f in flowers if self.pos.distance_to(f.pos) < 200 and f.can_be_pollinated()] # Example range
        if not nearby_flowers:
            return None

        # Basic: pick a random nearby flower for now
        return random.choice(nearby_flowers) if nearby_flowers else None

    def update(self, dt, flowers):
        if self.state == BeeState.IDLE:
            # Decide to fly out? Add delay?
            if random.random() < 0.01: # Chance to start flying out
                 self.target_flower = self.find_flower(flowers)
                 if self.target_flower:
                     self.state = BeeState.FLYING_OUT
                 else: # No flowers nearby, maybe wander briefly then return to idle
                     pass

        elif self.state == BeeState.FLYING_OUT:
            if self.target_flower and self.target_flower in flowers: # Check if flower still exists
                direction = (self.target_flower.pos - self.pos)
                if direction.length() < 5: # Reached flower
                    self.pos = self.target_flower.pos
                    self.state = BeeState.FORAGING
                    self.forage_timer = random.uniform(2.0, 4.0) # Time to forage
                    self.target_flower.add_pollinator(self) # Notify flower
                else:
                    self.pos += direction.normalize() * self.speed * dt
                    self.rect.center = self.pos
            else: # Target flower disappeared or was invalid
                self.state = BeeState.RETURNING # Go back home

        elif self.state == BeeState.FORAGING:
            self.forage_timer -= dt
            if self.forage_timer <= 0:
                if self.target_flower:
                    self.target_flower.remove_pollinator(self) # Notify flower we're done
                self.state = BeeState.RETURNING
                self.target_flower = None # Clear target

        elif self.state == BeeState.RETURNING:
            direction = (pygame.Vector2(self.hive.rect.center) - self.pos)
            if direction.length() < 5: # Reached hive
                self.pos = pygame.Vector2(self.hive.rect.center)
                self.state = BeeState.IDLE
                self.hive.receive_bee(self) # Notify hive bee returned (carrying resources)
            else:
                self.pos += direction.normalize() * self.speed * dt
                self.rect.center = self.pos

        # Keep bee within screen bounds (basic) - might need refinement
        self.pos.x = max(0, min(self.pos.x, SCREEN_WIDTH))
        self.pos.y = max(0, min(self.pos.y, SCREEN_HEIGHT))
        self.rect.center = self.pos


    def draw(self, screen):
        # Don't draw if idle inside hive (or make it look like it's inside)
        if self.state != BeeState.IDLE:
            screen.blit(self.image, self.rect)

# Need Screen Dimensions available - either pass GameState or constants
from game_state import SCREEN_WIDTH, SCREEN_HEIGHT