import pygame
from game_state import GameMode, WHITE, BLACK # Import colors etc

# Basic Asset Manager (can be expanded)
class AssetManager:
    def __init__(self):
        self.sprites = {}
        self.fonts = {}
        self.sounds = {} # Later

    def load_sprite(self, name, path):
        try:
            # Use convert_alpha() for transparency
            self.sprites[name] = pygame.image.load(path).convert_alpha()
            print(f"Loaded sprite: {name} from {path}")
        except pygame.error as e:
            print(f"Error loading sprite {name} at {path}: {e}")
            # Create a placeholder surface
            self.sprites[name] = pygame.Surface((32, 32), pygame.SRCALPHA)
            pygame.draw.rect(self.sprites[name], (255, 0, 255), (0, 0, 32, 32)) # Magenta placeholder

    def get_sprite(self, name):
        return self.sprites.get(name, None) # Return None if not found

    def load_font(self, name, path, size):
        key = f"{name}_{size}"
        try:
            self.fonts[key] = pygame.font.Font(path, size)
            print(f"Loaded font: {name} size {size} from {path}")
        except pygame.error as e:
            print(f"Error loading font {name} at {path}: {e}")
            self.fonts[key] = pygame.font.Font(None, size) # Pygame default font
        except FileNotFoundError:
             print(f"Font file not found: {path}. Using default font.")
             self.fonts[key] = pygame.font.Font(None, size) # Pygame default font


    def get_font(self, name, size):
        return self.fonts.get(f"{name}_{size}", None) # Return None if not found

# --- Renderer Class ---
class Renderer:
    def __init__(self, game_state, asset_manager):
        self.game_state = game_state
        self.asset_manager = asset_manager
        # Pre-load common assets (optional, could load on demand)
        self._load_assets()

        # Import UI modules here to avoid circular imports if they need Renderer
        from ui import menu, hud

        self.menu_renderer = menu # Assign module itself
        self.hud_renderer = hud   # Assign module itself


    def _load_assets(self):
        am = self.asset_manager
        # Sprites
        am.load_sprite('title_screen', 'assets/sprites/title_screen.png')
        am.load_sprite('bee', 'assets/sprites/bee_sprite.png')
        am.load_sprite('hive', 'assets/sprites/hive_sprite.png')
        am.load_sprite('kid', 'assets/sprites/kid_sprite.png')
        am.load_sprite('flower_clover', 'assets/sprites/flower_clover.png')
        am.load_sprite('flower_lavender', 'assets/sprites/flower_lavender.png')
        am.load_sprite('flower_sunflower', 'assets/sprites/flower_sunflower.png')
        am.load_sprite('flower', 'assets/sprites/flower_sprite.png')
        # Background images are missing, will use fallback color
        # am.load_sprite('background_day', 'assets/sprites/background_day.png')
        # am.load_sprite('background_night', 'assets/sprites/background_night.png')
        # Add more sprites as needed

        # Fonts (Make sure the path is correct!)
        try:
             # Place Comfortaa-Regular.ttf (or similar) in assets/
             font_path = 'assets/Comfortaa-Regular.ttf'
             am.load_font('comfortaa', font_path, 18)
             am.load_font('comfortaa', font_path, 24)
             am.load_font('comfortaa', font_path, 36)
             am.load_font('comfortaa', font_path, 48)
        except Exception as e:
             print(f"Could not load Comfortaa font: {e}. Make sure 'assets/Comfortaa-Regular.ttf' exists.")
             # Fallback to default font if Comfortaa fails
             am.load_font('comfortaa', None, 18)
             am.load_font('comfortaa', None, 24)
             am.load_font('comfortaa', None, 36)
             am.load_font('comfortaa', None, 48)


    def draw(self, screen):
        """Draw the entire game screen based on the current state."""
        gs = self.game_state

        # --- Draw Background ---
        self.draw_background(screen)

        # --- Draw based on Game Mode ---
        if gs.game_mode == GameMode.INTRO:
            self.menu_renderer.draw_intro_screen(screen, self.asset_manager, gs)
        elif gs.game_mode == GameMode.INSTRUCTIONS:
            self.menu_renderer.draw_instructions_screen(screen, self.asset_manager, gs)
        elif gs.game_mode == GameMode.GAMEPLAY:
            self.draw_gameplay(screen)
            self.hud_renderer.draw_hud(screen, self.asset_manager, gs) # Draw HUD on top
        elif gs.game_mode == GameMode.MARKET:
            # Draw gameplay elements slightly dimmed?
            self.draw_gameplay(screen, dimmed=True)
            self.menu_renderer.draw_market_screen(screen, self.asset_manager, gs)
            # Maybe draw HUD too? Or hide it in market?
            self.hud_renderer.draw_hud(screen, self.asset_manager, gs)


        # --- Draw Placement Preview (if active) ---
        if gs.game_mode == GameMode.GAMEPLAY and gs.show_placement_preview and gs.selected_action:
             self.draw_placement_preview(screen, gs.selected_action, gs.placement_preview_pos, gs.placement_valid)


        # --- Draw Mouse Cursor (optional custom cursor) ---
        # pygame.mouse.set_visible(False) # Hide default cursor
        # cursor_img = self.asset_manager.get_sprite('cursor_hand')
        # screen.blit(cursor_img, gs.mouse_pos)

        # Update the display (usually done in main loop)
        # pygame.display.flip()


    def draw_background(self, screen):
        """Draws the background, potentially interpolated between day/night."""
        time_ratio = self.game_state.get_time_of_day_ratio() # 0.0 to 1.0

        # Simple switch for now, can interpolate later
        day_img = self.asset_manager.get_sprite('background_day')
        night_img = self.asset_manager.get_sprite('background_night')

        if day_img is None: # Fallback if image failed to load
            screen.fill((135, 206, 250)) # Sky blue
            return
        if night_img is None:
            night_img = day_img # Use day image if night is missing

        # Scale background to fit screen (if needed)
        bg_day_scaled = pygame.transform.scale(day_img, (screen.get_width(), screen.get_height()))
        bg_night_scaled = pygame.transform.scale(night_img, (screen.get_width(), screen.get_height()))

        # Determine alpha for blending (e.g., night fades in during evening)
        # Day: 0.25 - 0.75, Night: 0.75 - 0.25 (wrapping around midnight)
        if 0.25 <= time_ratio < 0.75: # Daytime
             alpha = 0 # Fully day
             screen.blit(bg_day_scaled, (0, 0))
        else: # Nighttime (or transition)
            # Crude transition - fades night in/out over dawn/dusk periods
            if time_ratio >= 0.75: # Dusk transition
                 alpha = min(255, int(255 * (time_ratio - 0.75) / 0.15)) # Fade in over 0.15 duration
            else: # Dawn transition
                 alpha = min(255, int(255 * (0.25 - time_ratio) / 0.15)) # Fade out over 0.15 duration
            alpha = max(0, min(255, alpha)) # Clamp alpha

            screen.blit(bg_day_scaled, (0,0))
            if alpha > 0:
                night_overlay = bg_night_scaled.copy()
                night_overlay.set_alpha(alpha)
                screen.blit(night_overlay, (0,0))


    def draw_gameplay(self, screen, dimmed=False):
        """Draws all the active game entities."""
        gs = self.game_state

        # Draw in order: flowers first, then hives, then bees/kids on top
        for flower in gs.flowers:
            flower.draw(screen)

        for hive in gs.hives:
            hive.draw(screen)

        for bee in gs.bees:
            bee.draw(screen)

        for kid in gs.kids:
            kid.draw(screen)

        if dimmed:
            # Draw a semi-transparent overlay if needed (e.g., for market screen)
            overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128)) # Black with 50% opacity
            screen.blit(overlay, (0, 0))


    def draw_placement_preview(self, screen, item_type, pos, is_valid):
        """Draws a ghost image of the item being placed."""
        sprite_name = ""
        scale = (64, 64) # Default, adjust per item
        if item_type == "place_hive":
             sprite_name = "hive"
             scale = (64, 64)
        elif item_type.startswith("place_flower_"):
             flower_key = item_type.split("_")[-1].capitalize() # Clover, Lavender etc
             # Need FLOWER_DATA from flower.py here or passed in
             from entities.flower import FLOWER_DATA
             if flower_key in FLOWER_DATA:
                 sprite_name = FLOWER_DATA[flower_key]["sprite"]
                 scale = (32, 32)

        if sprite_name:
             image = self.asset_manager.get_sprite(sprite_name)
             if image:
                 image = pygame.transform.scale(image, scale)
                 image.set_alpha(150) # Make it semi-transparent
                 rect = image.get_rect(center=pos)

                 # Draw placement radius/indicator? (Optional)
                 radius = 50 # Example radius to check for conflicts
                 color = (0, 255, 0, 100) if is_valid else (255, 0, 0, 100) # Green/Red tint based on validity
                 # Draw rect background for visibility
                 pygame.draw.rect(screen, color, rect, 2 if not is_valid else 0) # Border if invalid


                 screen.blit(image, rect)

                 # Draw circle indicator
                 temp_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
                 pygame.draw.circle(temp_surf, color, (radius, radius), radius)
                 screen.blit(temp_surf, (pos[0] - radius, pos[1] - radius))