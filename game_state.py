import pygame
from enum import Enum

# Game Modes Enum
class GameMode(Enum):
    INTRO = 1
    INSTRUCTIONS = 2
    GAMEPLAY = 3
    MARKET = 4

# Constants
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60
GAME_DAY_SECONDS = 60 # Real seconds for one game day
HIVE_COST = 20 # Cost to place a new hive

# Colors (example)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 235, 59)
GREEN = (76, 175, 80)
BROWN = (121, 85, 72)
RED = (211, 47, 47)
BLUE = (33, 150, 243)

# --- Game State Class ---
class GameState:
    def __init__(self):
        # Core Variables
        self.game_mode = GameMode.INTRO
        self.running = True
        self.delta_time = 0.0 # Time since last frame in seconds

        # Resources
        self.money = 100
        self.honey = 0.0
        self.wax = 0.0
        self.pollen = 0.0

        # Time & Season
        self.game_time_seconds = 0.0 # Seconds elapsed in current game day
        self.day_count = 1
        self.current_season = "Spring" # Could be enum: Spring, Summer, Autumn, Winter

        # Entities (Lists to hold active game objects)
        self.hives = []
        self.flowers = []
        self.bees = []
        self.kids = []

        # UI State
        self.active_instruction_tab = "Basics" # For instruction screen
        self.selected_action = None # e.g., "place_hive", "water_flower", "remove_item"
        self.show_placement_preview = False
        self.placement_preview_pos = (0, 0)
        self.placement_valid = False # Is the current placement location valid?

        # Upgrades
        self.production_upgrade_level = 0
        self.production_rate_multiplier = 1.0 # Base multiplier

        # Mouse state
        self.mouse_pos = (0, 0)
        self.mouse_pressed = [False, False, False] # Left, Middle, Right

        # Miscellaneous Flags
        self.needs_redraw = True # Flag to force redraw when state changes significantly

    def get_time_of_day_ratio(self):
        """Returns a float between 0.0 (midnight start) and 1.0 (midnight end)"""
        return self.game_time_seconds / GAME_DAY_SECONDS

    def get_base_production_rate(self):
        """Calculates the base honey production rate based on upgrades."""
        # Example base rate - ADJUST AS NEEDED
        base_rate_per_hive_per_second = 0.1
        upgrade_bonus = self.production_upgrade_level * 0.025
        return (base_rate_per_hive_per_second + upgrade_bonus) * self.production_rate_multiplier

    def get_upgrade_cost(self):
        """Calculates the cost of the next production upgrade."""
        initial_cost = 75
        increase_per_level = 50
        return initial_cost + (self.production_upgrade_level * increase_per_level)

    def purchase_upgrade(self):
        """Attempts to purchase the production upgrade."""
        cost = self.get_upgrade_cost()
        if self.money >= cost:
            self.money -= cost
            self.production_upgrade_level += 1
            print(f"Production upgraded to level {self.production_upgrade_level}!")
            return True
        else:
            print(f"Not enough money for upgrade. Need ${cost}, have ${self.money}.")
            return False

    def add_hive(self, hive):
        self.hives.append(hive)

    def add_flower(self, flower):
        self.flowers.append(flower)

    def add_bee(self, bee):
        self.bees.append(bee)

    def add_kid(self, kid):
        self.kids.append(kid)

    def remove_entity(self, entity_to_remove):
        """Removes a given entity (hive, flower, kid) from the game state lists."""
        if entity_to_remove in self.hives:
            # Handle bees associated with this hive if necessary
            bees_to_remove = [bee for bee in self.bees if bee.hive == entity_to_remove]
            for bee in bees_to_remove:
                self.bees.remove(bee)
            self.hives.remove(entity_to_remove)
            self.money += 10 # 50% refund for $20 hive
            print("Hive removed.")
            return True
        elif entity_to_remove in self.flowers:
            self.flowers.remove(entity_to_remove)
            # Refund based on original cost (needs flower type info)
            # Example: Assuming flower object has 'cost' attribute
            if hasattr(entity_to_remove, 'cost'):
                 self.money += entity_to_remove.cost * 0.50
            print("Flower removed.")
            return True
        elif entity_to_remove in self.kids:
            self.kids.remove(entity_to_remove)
            print("Kid removed (chased away).")
            return True
        elif entity_to_remove in self.bees: # Should usually be handled by hive removal
             self.bees.remove(entity_to_remove)
             return True
        return False