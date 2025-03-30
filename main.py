import pygame
import sys
import random
import os

# Setup path to ensure modules can be found
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from game_state import GameState, GameMode, SCREEN_WIDTH, SCREEN_HEIGHT, FPS, HIVE_COST, WHITE, BLACK, RED, GREEN
from entities.hive import Hive, HONEY_THRESHOLD
from entities.flower import Flower, FLOWER_DATA
from entities.bee import Bee # Import Bee
from systems.sim import Simulator
from systems.render import Renderer, AssetManager
from ui import menu, hud # Import UI modules for click handling

# --- Helper Functions ---
def check_placement_validity(game_state, item_type, pos):
    """Checks if placing an item at pos is valid (e.g., not overlapping)."""
    new_rect_size = (0, 0)
    min_distance = 0 # Minimum distance to other objects of same/conflicting type

    if item_type == "place_hive":
        new_rect_size = (64, 64) # Match hive size in Hive class
        min_distance = 50 # Min distance between hives
    elif item_type.startswith("place_flower_"):
        new_rect_size = (32, 32) # Match flower size
        min_distance = 10 # Min distance between flowers

    if not new_rect_size[0]: return False # Unknown item type

    new_rect = pygame.Rect(0, 0, *new_rect_size)
    new_rect.center = pos

    # 1. Check screen bounds (allow some margin)
    margin = 10
    if not (margin < new_rect.left and new_rect.right < SCREEN_WIDTH - margin and \
            margin < new_rect.top and new_rect.bottom < SCREEN_HEIGHT - 80 - margin): # Avoid HUD area
        return False

    # 2. Check proximity to other objects
    entities_to_check = []
    if item_type == "place_hive":
        entities_to_check = game_state.hives
    elif item_type.startswith("place_flower_"):
         entities_to_check = game_state.flowers
    # Add checks against other types if needed (e.g., can't place on hive)

    for entity in entities_to_check:
         distance = pygame.Vector2(pos).distance_to(entity.pos)
         if distance < min_distance:
             return False

    # Add more checks if needed (e.g., terrain type in future)

    return True


# --- Main Game Class ---
class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()  # Initialize the sound system
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pixel Hives - A Beekeeper's Story")
        self.clock = pygame.time.Clock()

        # Load and start background music
        try:
            pygame.mixer.music.load('assets/sounds/Among-the-Clouds.mp3')
            pygame.mixer.music.set_volume(0.5)  # Set to 50% volume
            pygame.mixer.music.play(-1)  # -1 means loop indefinitely
        except pygame.error as e:
            print(f"Could not load or play the music: {e}")

        self.asset_manager = AssetManager() # Manage sprites, fonts, sounds
        self.game_state = GameState()
        # Pass asset_manager to Renderer, Simulator, and potentially entities if they load assets directly
        self.renderer = Renderer(self.game_state, self.asset_manager)
        self.simulator = Simulator(self.game_state, self.asset_manager)


    def run(self):
        while self.game_state.running:
            # --- Calculate Delta Time ---
            # dt is time elapsed since last frame in seconds. Crucial for frame-rate independent movement/physics.
            self.game_state.delta_time = self.clock.tick(FPS) / 1000.0

            # --- Event Handling ---
            self.handle_events()

            # --- Game Logic / Simulation ---
            # Only run simulation if in gameplay mode (or maybe market?)
            if self.game_state.game_mode in [GameMode.GAMEPLAY, GameMode.MARKET]:
                 self.simulator.tick(self.game_state.delta_time)

            # --- Update Placement Preview ---
            if self.game_state.show_placement_preview and self.game_state.selected_action:
                 self.game_state.placement_preview_pos = self.game_state.mouse_pos
                 self.game_state.placement_valid = check_placement_validity(
                     self.game_state,
                     self.game_state.selected_action,
                     self.game_state.placement_preview_pos
                 )

            # --- Rendering ---
            self.renderer.draw(self.screen)

            # --- Update Display ---
            pygame.display.flip()

        self.quit_game()

    def handle_events(self):
        gs = self.game_state # Shorthand
        gs.mouse_pos = pygame.mouse.get_pos()
        gs.mouse_pressed = pygame.mouse.get_pressed() # [Left, Middle, Right]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                gs.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Escape logic: close market/instructions, or pause menu?
                    if gs.game_mode == GameMode.MARKET:
                        gs.game_mode = GameMode.GAMEPLAY
                    elif gs.game_mode == GameMode.INSTRUCTIONS:
                        gs.game_mode = GameMode.INTRO
                    # elif gs.game_mode == GameMode.GAMEPLAY:
                        # gs.game_mode = GameMode.PAUSED # Add pause state later
                    else:
                        gs.running = False # Default: quit if in intro
                elif event.key == pygame.K_m:  # 'M' key toggles music
                    gs.toggle_music()
                    print("Music:", "On" if gs.music_enabled else "Off")
                # Volume controls
                elif event.key == pygame.K_COMMA:  # '<' key decreases volume
                    gs.set_music_volume(gs.music_volume - 0.1)
                    print(f"Volume: {int(gs.music_volume * 100)}%")
                elif event.key == pygame.K_PERIOD:  # '>' key increases volume
                    gs.set_music_volume(gs.music_volume + 0.1)
                    print(f"Volume: {int(gs.music_volume * 100)}%")

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left mouse button
                    click_handled = False
                    # --- UI Click Handling (Priority) ---
                    if gs.game_mode == GameMode.INTRO:
                        click_handled = menu.handle_intro_click(gs.mouse_pos)
                    elif gs.game_mode == GameMode.INSTRUCTIONS:
                        click_handled = menu.handle_instructions_click(gs.mouse_pos)
                    elif gs.game_mode == GameMode.MARKET:
                        # Market handles its own buttons first
                        click_handled = menu.handle_market_click(gs.mouse_pos)
                        # Then check HUD buttons if market didn't handle it (e.g., closing market via HUD?)
                        if not click_handled:
                             click_handled = hud.handle_hud_click(gs.mouse_pos)
                    elif gs.game_mode == GameMode.GAMEPLAY:
                         # HUD buttons first
                         click_handled = hud.handle_hud_click(gs.mouse_pos)


                    # --- Gameplay Click Handling (If UI didn't handle it) ---
                    if not click_handled and gs.game_mode == GameMode.GAMEPLAY:
                        self.handle_gameplay_click(gs.mouse_pos)


    def handle_gameplay_click(self, mouse_pos):
        gs = self.game_state

        # --- Action based on selected tool ---
        action = gs.selected_action

        # 1. Check for Kid Click first (high priority interaction)
        for kid in gs.kids:
            if kid.rect.collidepoint(mouse_pos):
                 kid.chase_away() # Kid handles state change and timer
                 # No need to remove here, kid removes itself when fleeing off screen/timer ends
                 return # Action handled

        # 2. Handle Placement Actions
        if action and action.startswith("place_"):
            is_valid = check_placement_validity(gs, action, mouse_pos)
            if is_valid:
                cost = 0
                if action == "place_hive":
                    cost = HIVE_COST
                    if gs.money >= cost:
                         gs.money -= cost
                         new_hive = Hive(mouse_pos, self.asset_manager)
                         gs.add_hive(new_hive)
                         # Add initial bees for the hive
                         for _ in range(new_hive.max_bees):
                             new_bee = Bee(new_hive, self.asset_manager)
                             gs.add_bee(new_bee)
                         print(f"Placed Hive. Cost: ${cost}")
                         # Maybe deselect tool after placement? Optional.
                         # gs.selected_action = "select"
                         # gs.show_placement_preview = False
                    else: print("Not enough money to place hive!")

                elif action.startswith("place_flower_"):
                    flower_type_key = action.split("_")[-1].capitalize()
                    if flower_type_key in FLOWER_DATA:
                         cost = FLOWER_DATA[flower_type_key]["cost"]
                         if gs.money >= cost:
                             gs.money -= cost
                             new_flower = Flower(mouse_pos, flower_type_key, self.asset_manager)
                             gs.add_flower(new_flower)
                             print(f"Planted {flower_type_key}. Cost: ${cost}")
                             # Maybe deselect tool after placement?
                         else: print(f"Not enough money for {flower_type_key}!")

            else:
                 print("Invalid placement location.")
            return # Placement attempt handled

        # 3. Handle Interaction Actions (Water, Harvest, Remove, Select)
        clicked_entity = None
        # Check hives first (usually larger targets)
        for hive in gs.hives:
             if hive.rect.collidepoint(mouse_pos):
                 clicked_entity = hive
                 break
        # Check flowers if no hive clicked
        if not clicked_entity:
             for flower in gs.flowers:
                 if flower.rect.collidepoint(mouse_pos):
                     clicked_entity = flower
                     break

        if action == "water":
             if isinstance(clicked_entity, Flower):
                 clicked_entity.water()
             else: print("Click on a flower to water it.")
             return

        if action == "remove":
             if clicked_entity:
                 # Ask for confirmation later?
                 success = gs.remove_entity(clicked_entity) # Handles refund
                 if success: print("Item removed.")
             else: print("Click on a hive or flower to remove it.")
             return

        # Default "select" action or harvest click
        if action == "select" or action is None:
            if isinstance(clicked_entity, Hive):
                # Try to harvest if clicked with select tool
                if clicked_entity.can_harvest():
                     clicked_entity.harvest(gs)
                     # Add sound/visual effect
                else:
                     print(f"Hive clicked, Honey: {clicked_entity.honey:.1f}/{HONEY_THRESHOLD}") # Info click
            elif isinstance(clicked_entity, Flower):
                 print(f"Flower clicked: {clicked_entity.type}, Health: {clicked_entity.health:.1f}/{clicked_entity.max_health}") # Info click
            # else: Clicked on empty ground with select tool - do nothing or deselect?
            return


    def quit_game(self):
        pygame.mixer.music.stop()  # Stop the music before quitting
        pygame.quit()
        sys.exit()

# --- Main Execution ---
if __name__ == '__main__':
    # Ensure assets folder exists relative to main.py
    # (Usually okay if run from the bee_game directory)
    # import os
    # print("Current Working Dir:", os.getcwd())
    # print("Assets folder exists:", os.path.exists("assets"))

    game = Game()
    game.run()