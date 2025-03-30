import pygame
import random
from entities.kid import Kid, KID_DESPAWN_TIME # Import Kid class for spawning
from game_state import GAME_DAY_SECONDS

KID_SPAWN_CHANCE_PER_SECOND = 0.05 # Chance a kid will spawn each second

class Simulator:
    def __init__(self, game_state, asset_manager):
        self.game_state = game_state
        self.asset_manager = asset_manager
        self.kid_spawn_timer = random.uniform(5.0, 15.0) # Time until first kid check

    def tick(self, dt):
        """Update the game state for one frame."""
        gs = self.game_state # Shorthand

        # --- Time Update ---
        gs.game_time_seconds += dt
        if gs.game_time_seconds >= GAME_DAY_SECONDS:
            gs.game_time_seconds -= GAME_DAY_SECONDS # Reset for next day
            gs.day_count += 1
            # Potentially trigger seasonal changes here
            print(f"--- Day {gs.day_count} Starting ---")
            # Maybe wilt flowers more overnight? Or reset nectar?

        # --- Entity Updates ---
        # Update Flowers (and handle wilting/removal)
        flowers_to_remove = []
        for flower in gs.flowers:
            flower.update(dt)
            if flower.health <= 0:
                flowers_to_remove.append(flower)
        for flower in flowers_to_remove:
             gs.flowers.remove(flower) # Just remove, no refund for wilting
             print(f"{flower.type} wilted and removed.")

        # Update Hives (production handled here or in Hive?)
        for hive in gs.hives:
            hive.update(dt, gs) # Pass game_state for access to flowers/rates

        # Update Bees
        for bee in gs.bees:
            bee.update(dt, gs.flowers) # Bees need list of flowers

        # Update Kids (and handle despawning)
        kids_to_remove = []
        for kid in gs.kids:
            kid.update(dt, gs) # Kid update handles despawning timers and state changes
            # Removal is now handled inside kid.update() or via player click in main.py

        # --- Kid Spawning ---
        self.kid_spawn_timer -= dt
        if self.kid_spawn_timer <= 0:
            # Reset timer for next potential spawn
            self.kid_spawn_timer = random.uniform(5.0, 20.0) # Time between spawn checks

            # Check if a kid should spawn based on chance
            # Make it less likely if many kids exist? More likely if lots of honey?
            max_kids = 3 # Example limit
            if len(gs.kids) < max_kids and random.random() < KID_SPAWN_CHANCE_PER_SECOND * (self.kid_spawn_timer + 1): # Approximation
                if gs.hives: # Only spawn if there's something to target
                     new_kid = Kid(self.asset_manager, gs.hives)
                     gs.add_kid(new_kid)
                     print("A mischievous kid appeared!")
                else:
                    # No hives, reset timer longer?
                    self.kid_spawn_timer = random.uniform(10.0, 25.0)


        # --- Resource Cap / Other Global Checks? ---
        # e.g., gs.honey = min(gs.honey, MAX_HONEY_STORAGE)