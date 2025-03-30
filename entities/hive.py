import pygame
from entities.bee import Bee # Import Bee to create them

HIVE_COST = 20
HIVE_CAPACITY = 5
HONEY_THRESHOLD = 10 # Amount needed to harvest

class Hive:
    def __init__(self, pos, asset_manager):
        self.asset_manager = asset_manager
        self.image = self.asset_manager.get_sprite('hive') # Get pre-loaded sprite
        self.image = pygame.transform.scale(self.image, (64, 64)) # Example size
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.Vector2(pos)

        self.honey = 0.0
        self.wax = 0.0
        self.pollen = 0.0
        self.max_bees = HIVE_CAPACITY
        # Associated bees are managed in GameState.bees, filtered by hive reference

        self.production_timer = 0.0 # Timer for resource generation ticks

    def get_associated_bees(self, all_bees):
        """Returns a list of bees belonging to this hive."""
        return [bee for bee in all_bees if bee.hive == self]

    def update(self, dt, game_state):
        # Production logic based on nearby flowers and active bees
        # This is a simplified model: assumes production happens if flowers are near
        # A more complex model would tie it directly to returning bees

        base_rate = game_state.get_base_production_rate() # Per second
        production_this_frame = 0

        # Simple check: Any flowers nearby? (Refine distance/efficiency later)
        nearby_flowers = False
        for flower in game_state.flowers:
             distance = self.pos.distance_to(flower.pos)
             if distance < 150: # Example range for hive influence
                 nearby_flowers = True
                 break # At least one flower is enough for this simple model

        if nearby_flowers:
             # Production occurs even if bees aren't literally returning *this* frame
             # Assumes bees are generally working if flowers are available
             production_this_frame = base_rate * dt

        if production_this_frame > 0:
            self.honey += production_this_frame
            self.wax += production_this_frame * 0.10 # 10% of honey rate
            self.pollen += production_this_frame * 0.20 # 20% of honey rate

        # Ensure bees are created up to capacity if conditions met (e.g., enough resources?)
        # Bee creation logic might live elsewhere (e.g., in sim.py when placing hive)


    def receive_bee(self, bee):
        """Called when a bee returns to the hive."""
        # In a more complex model, returning bees would directly add resources
        # print(f"Bee returned to hive {self.rect.center}")
        pass

    def can_harvest(self):
        return self.honey >= HONEY_THRESHOLD

    def harvest(self, game_state):
        if self.can_harvest():
            harvested_honey = self.honey
            harvested_wax = self.wax
            harvested_pollen = self.pollen

            game_state.honey += harvested_honey
            game_state.wax += harvested_wax
            game_state.pollen += harvested_pollen

            self.honey = 0.0
            self.wax = 0.0
            self.pollen = 0.0
            print(f"Harvested: {harvested_honey:.2f} Honey, {harvested_wax:.2f} Wax, {harvested_pollen:.2f} Pollen")
            return True
        return False

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        # Draw resource level indicator (e.g., a simple bar)
        if self.honey > 0:
            fill_ratio = min(1.0, self.honey / HONEY_THRESHOLD)
            indicator_height = 5
            indicator_width = self.rect.width * fill_ratio
            indicator_rect = pygame.Rect(
                self.rect.left,
                self.rect.bottom + 2,
                indicator_width,
                indicator_height
            )
            pygame.draw.rect(screen, (255, 193, 7), indicator_rect) # Amber color