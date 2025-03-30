import pygame
import random
import math
from game_state import SCREEN_WIDTH, SCREEN_HEIGHT # For spawn positions

KID_SPEED = 60 # Pixels per second
KID_DESPAWN_TIME = 5.0 # Seconds before despawning if not clicked
KID_STEAL_AMOUNT = 5 # Amount of honey stolen

class KidState:
    SPAWNING = 0
    MOVING_TO_HIVE = 1
    STEALING = 2 # At hive, attempting to steal
    FLEEING = 3 # Clicked by player

class Kid:
    def __init__(self, asset_manager, hives):
        self.asset_manager = asset_manager
        self.image = self.asset_manager.get_sprite('kid')
        self.image = pygame.transform.scale(self.image, (40, 50)) # Example size

        self.pos = self._get_spawn_pos()
        self.rect = self.image.get_rect(center=self.pos)

        self.state = KidState.SPAWNING
        self.target_hive = self._find_target_hive(hives)
        self.speed = KID_SPEED
        self.despawn_timer = KID_DESPAWN_TIME
        self.flee_timer = 0.0 # How long to flee after being clicked

    def _get_spawn_pos(self):
        """Gets a random spawn position around the edges."""
        edge = random.choice(['top', 'bottom', 'left', 'right'])
        margin = 50 # Distance from edge
        if edge == 'top':
            return pygame.Vector2(random.randint(margin, SCREEN_WIDTH - margin), margin)
        elif edge == 'bottom':
            return pygame.Vector2(random.randint(margin, SCREEN_WIDTH - margin), SCREEN_HEIGHT - margin)
        elif edge == 'left':
            return pygame.Vector2(margin, random.randint(margin, SCREEN_HEIGHT - margin))
        else: # right
            return pygame.Vector2(SCREEN_WIDTH - margin, random.randint(margin, SCREEN_HEIGHT - margin))

    def _find_target_hive(self, hives):
        """Finds the nearest hive to target."""
        if not hives:
            return None
        hives.sort(key=lambda h: self.pos.distance_to(h.pos))
        return hives[0]

    def update(self, dt, game_state):
        self.despawn_timer -= dt

        if self.state == KidState.SPAWNING:
            # Brief pause or animation? For now, move directly to target
            if self.target_hive:
                self.state = KidState.MOVING_TO_HIVE
            else:
                 # No hives, just despawn after timer
                 if self.despawn_timer <= 0:
                     game_state.remove_entity(self) # Remove self
                 return # Do nothing else


        if self.state == KidState.MOVING_TO_HIVE:
            if self.target_hive not in game_state.hives: # Target hive removed?
                self.target_hive = self._find_target_hive(game_state.hives) # Find new one
                if not self.target_hive:
                    self.state = KidState.FLEEING # Flee if no hives left
                    self.flee_timer = 2.0
                    self.despawn_timer = 2.0 # Despawn quickly
                    return

            direction = (self.target_hive.pos - self.pos)
            if direction.length() < 10: # Reached hive vicinity
                self.pos = self.target_hive.pos # Snap roughly to target
                self.state = KidState.STEALING
                # Add logic for actual stealing here or in sim.py
                print(f"Kid reached hive {self.target_hive.rect.center}!")
                # Attempt steal immediately - could have a short timer
                if self.target_hive.honey > 0:
                    stolen_honey = min(self.target_hive.honey, KID_STEAL_AMOUNT)
                    self.target_hive.honey -= stolen_honey
                    # Note: Stolen honey doesn't go to player! It's just lost.
                    print(f"Kid stole {stolen_honey:.2f} honey!")
                    # Kid should probably flee after stealing
                    self.state = KidState.FLEEING
                    self.flee_timer = 3.0
                    self.despawn_timer = 3.0 # Give time to flee off screen
                else:
                    # Hive empty, flee anyway
                    self.state = KidState.FLEEING
                    self.flee_timer = 2.0
                    self.despawn_timer = 2.0

            else:
                self.pos += direction.normalize() * self.speed * dt
                self.rect.center = self.pos

        elif self.state == KidState.STEALING:
             # This state might be very brief if stealing happens instantly on arrival
             # Could add a timer here if stealing takes time
             pass

        elif self.state == KidState.FLEEING:
            # Move away from center of screen or just off edge?
            # Simple: move towards spawn edge
            # Better: move directly away from the hive it targeted? Or away from player click?
            flee_direction = (self.pos - pygame.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)).normalize()
            if flee_direction.length() == 0: # Avoid division by zero if perfectly centered
                 flee_direction = pygame.Vector2(1, 0)
            self.pos += flee_direction * self.speed * 1.5 * dt # Flee faster
            self.rect.center = self.pos
            self.flee_timer -= dt
            if self.flee_timer <= 0 or not (0 < self.rect.centerx < SCREEN_WIDTH and 0 < self.rect.centery < SCREEN_HEIGHT):
                 # Remove kid if flee timer runs out or it goes off-screen
                 if self in game_state.kids: # Check if already removed
                      game_state.remove_entity(self)
                 return # Stop processing


        # Check for despawn timer if not fleeing (fleeing handles its own removal)
        if self.state != KidState.FLEEING and self.despawn_timer <= 0:
             if self in game_state.kids: # Check if not already removed (e.g. by click)
                 print("Kid got bored and left.")
                 game_state.remove_entity(self)

    def chase_away(self):
        """Called when the player clicks on the kid."""
        print("Kid chased away!")
        self.state = KidState.FLEEING
        self.flee_timer = 3.0 # Give it time to run off screen
        self.despawn_timer = 3.0 # Ensure it gets removed


    def draw(self, screen):
        screen.blit(self.image, self.rect)