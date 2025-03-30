import pygame
import os
import sys

# Add parent directory to path so we can import game_state
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from game_state import GameMode, WHITE, BLACK, YELLOW, GREEN, BLUE # Import colors etc
from entities.flower import FLOWER_DATA # For market/instructions

# Simple Button Class (Example)
class Button:
    def __init__(self, x, y, width, height, text, font, callback=None, text_color=BLACK, bg_color=WHITE, hover_color=YELLOW):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.callback = callback
        self.text_color = text_color
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.is_hovered = False

    def draw(self, screen):
        if self.bg_color != (0,0,0,0):  # Only draw background if not fully transparent
            color = self.hover_color if self.is_hovered else self.bg_color
            pygame.draw.rect(screen, color, self.rect, border_radius=5)
            pygame.draw.rect(screen, BLACK, self.rect, width=1, border_radius=5) # Border

        if self.text:  # Only draw text if there is any
            text_surf = self.font.render(self.text, True, self.text_color)
            text_rect = text_surf.get_rect(center=self.rect.center)
            screen.blit(text_surf, text_rect)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def click(self):
        if self.is_hovered and self.callback:
            self.callback()
            return True
        return False

# --- Menu Drawing Functions ---

# Store buttons globally within the module or pass them around
intro_buttons = []
instruction_buttons = []
market_buttons = []

def draw_intro_screen(screen, asset_manager, game_state):
    global intro_buttons
    intro_buttons = [] # Reset buttons each draw call

    screen_width = screen.get_width()
    screen_height = screen.get_height()
    font_medium = asset_manager.get_font('comfortaa', 24)

    # Draw the title screen background
    title_bg = asset_manager.get_sprite('title_screen')
    if title_bg:
        # Scale to fit screen if needed
        scaled_bg = pygame.transform.scale(title_bg, (screen_width, screen_height))
        screen.blit(scaled_bg, (0, 0))
    else:
        # Fallback to solid color if image not found
        screen.fill((135, 206, 235))  # Sky blue fallback

    # Create invisible buttons that match the image's button positions
    button_w, button_h = 200, 50
    button_x = (screen_width / 2 - button_w / 2) - 150  # Moved left 150 pixels

    def start_game():
        game_state.game_mode = GameMode.GAMEPLAY
        game_state.selected_action = "select"  # Set default action to select
        game_state.show_placement_preview = False
        print("Starting Game")

    def open_instructions():
        game_state.game_mode = GameMode.INSTRUCTIONS
        game_state.active_instruction_tab = "Basics" # Reset to first tab
        print("Opening Instructions")

    def quit_game():
        game_state.running = False

    # Create invisible buttons that match the image's button positions
    start_button = Button(
        button_x, 430, button_w, button_h,  # Moved up 50 pixels from 480
        "", font_medium, start_game,
        bg_color=(0,0,0,0), hover_color=(255,255,255,30)
    )
    
    instr_button = Button(
        button_x, 500, button_w, button_h,  # Moved up 50 pixels from 550
        "", font_medium, open_instructions,
        bg_color=(0,0,0,0), hover_color=(255,255,255,30)
    )
    
    quit_button = Button(
        button_x, 570, button_w, button_h,  # Moved up 50 pixels from 620
        "", font_medium, quit_game,
        bg_color=(0,0,0,0), hover_color=(255,255,255,30)
    )

    intro_buttons.extend([start_button, instr_button, quit_button])

    # Draw button hover effects (subtle highlight when mouse over)
    for button in intro_buttons:
        button.check_hover(game_state.mouse_pos)
        if button.is_hovered:
            hover_surface = pygame.Surface((button_w, button_h), pygame.SRCALPHA)
            hover_surface.fill((255, 255, 255, 30))  # White with 30 alpha
            screen.blit(hover_surface, button.rect)

def handle_intro_click(mouse_pos):
    for button in intro_buttons:
        if button.rect.collidepoint(mouse_pos):
            button.click()
            return True # Indicate click was handled
    return False


def draw_instructions_screen(screen, asset_manager, game_state):
    global instruction_buttons
    instruction_buttons = []

    screen_width = screen.get_width()
    screen_height = screen.get_height()
    font_large = asset_manager.get_font('comfortaa', 36)
    font_medium = asset_manager.get_font('comfortaa', 24)
    font_small = asset_manager.get_font('comfortaa', 18)

    # Background Panel
    panel_rect = pygame.Rect(screen_width * 0.1, screen_height * 0.1, screen_width * 0.8, screen_height * 0.8)
    pygame.draw.rect(screen, (50, 50, 70, 220), panel_rect, border_radius=10) # Semi-transparent dark blue/grey
    pygame.draw.rect(screen, WHITE, panel_rect, width=2, border_radius=10)

    # Title
    title_surf = font_large.render("How to Play", True, WHITE)
    title_rect = title_surf.get_rect(center=(screen_width / 2, panel_rect.top + 40))
    screen.blit(title_surf, title_rect)

    # Tabs
    tab_names = ["Basics", "Flowers", "Upgrades"]
    tab_width = panel_rect.width / len(tab_names)
    tab_height = 40
    tab_y = panel_rect.top + 80

    for i, name in enumerate(tab_names):
        tab_rect = pygame.Rect(panel_rect.left + i * tab_width, tab_y, tab_width, tab_height)
        is_active = game_state.active_instruction_tab == name

        # Tab Button - Reuse Button class or draw manually
        bg_color = BLUE if is_active else (80, 80, 100)
        hover_color = (100, 100, 200)
        text_color = WHITE

        # Create a simple button function for tabs
        def set_tab_callback(tab_name):
             def callback():
                 game_state.active_instruction_tab = tab_name
                 print(f"Switched to tab: {tab_name}")
             return callback

        tab_button = Button(tab_rect.x, tab_rect.y, tab_rect.width, tab_rect.height, name, font_medium,
                            set_tab_callback(name), text_color=text_color, bg_color=bg_color, hover_color=hover_color)
        instruction_buttons.append(tab_button)
        tab_button.check_hover(game_state.mouse_pos)
        tab_button.draw(screen)


    # Content Area
    content_y = tab_y + tab_height + 20
    content_rect = pygame.Rect(panel_rect.left + 20, content_y, panel_rect.width - 40, panel_rect.bottom - content_y - 70) # Space for back button

    # Draw content based on active tab
    text_lines = []
    if game_state.active_instruction_tab == "Basics":
        text_lines = [
            "Welcome to Pixel Hives!",
            "Goal: Build a thriving bee garden.",
            " ",
            "Controls:",
            "- Click HUD buttons to select actions (Place Hive, Plant Flower, etc.).",
            "- Click on the ground to place selected items.",
            "- Click on Hives (when full) to Harvest.",
            "- Click on Flowers to Water them.",
            "- Click on Kids to chase them away!",
            " ",
            "Resources:",
            "- Honey: Main product, earn money by selling.",
            "- Wax & Pollen: Secondary products.",
            "- Money ($): Used for buying items and upgrades.",
            " ",
            "Watch out for the day/night cycle and mischievous kids!",
        ]
    elif game_state.active_instruction_tab == "Flowers":
        text_lines = ["Flower Types:", " "]
        for name, data in FLOWER_DATA.items():
             text_lines.append(f"- {name} (${data['cost']}):")
             text_lines.append(f"   Health: {data['health']}, Wilts {'slowly' if data['wilting_rate'] < 0.06 else ('normally' if data['wilting_rate'] < 0.1 else 'quickly')}.")
             text_lines.append(" ") # Spacing
        text_lines.extend([
            "Keep flowers healthy by watering them.",
            "Wilted flowers disappear!",
            "Flowers attract bees and make your garden beautiful."
        ])
    elif game_state.active_instruction_tab == "Upgrades":
         # Get current cost and level from game_state
         current_level = game_state.production_upgrade_level
         next_cost = game_state.get_upgrade_cost()
         current_bonus = current_level * 0.025
         next_bonus = (current_level + 1) * 0.025

         text_lines = [
             "Upgrades help improve your production!",
             " ",
             "Production Rate Upgrade:",
             f"- Current Level: {current_level} (+{current_bonus*100:.1f}% Honey Rate)",
             f"- Next Level Cost: ${next_cost}",
             f"- Next Level Bonus: +{next_bonus*100:.1f}% Honey Rate",
             " ",
             "Purchase upgrades in the Market screen.",
             "(More upgrades might be added later!)",
         ]


    # Render text lines
    line_height = font_small.get_linesize()
    for i, line in enumerate(text_lines):
        line_surf = font_small.render(line, True, WHITE)
        line_rect = line_surf.get_rect(topleft=(content_rect.left + 10, content_rect.top + 10 + i * line_height))
        if line_rect.bottom < content_rect.bottom - 10: # Check if it fits
             screen.blit(line_surf, line_rect)
        else:
             break # Stop rendering if text overflows


    # Back Button
    def back_to_intro():
        game_state.game_mode = GameMode.INTRO

    back_button = Button(
        panel_rect.centerx - 75, panel_rect.bottom - 60, 150, 40,
        "Back", font_medium, back_to_intro
    )
    instruction_buttons.append(back_button)
    back_button.check_hover(game_state.mouse_pos)
    back_button.draw(screen)

def handle_instructions_click(mouse_pos):
     for button in instruction_buttons:
         if button.rect.collidepoint(mouse_pos):
             button.click()
             return True
     return False


def draw_market_screen(screen, asset_manager, game_state):
    global market_buttons
    market_buttons = []

    screen_width = screen.get_width()
    screen_height = screen.get_height()
    font_large = asset_manager.get_font('comfortaa', 36)
    font_medium = asset_manager.get_font('comfortaa', 24)
    font_small = asset_manager.get_font('comfortaa', 18)

    # Background Panel (similar to instructions)
    panel_rect = pygame.Rect(screen_width * 0.15, screen_height * 0.15, screen_width * 0.7, screen_height * 0.7)
    pygame.draw.rect(screen, (60, 80, 60, 230), panel_rect, border_radius=10) # Semi-transparent green
    pygame.draw.rect(screen, WHITE, panel_rect, width=2, border_radius=10)

    # Title
    title_surf = font_large.render("Market", True, WHITE)
    title_rect = title_surf.get_rect(center=(screen_width / 2, panel_rect.top + 40))
    screen.blit(title_surf, title_rect)

    # Sections: Sell Resources | Buy Upgrades
    section_y = panel_rect.top + 90
    section_height = panel_rect.height - 150 # Reserve space for title and close button
    sell_rect = pygame.Rect(panel_rect.left + 20, section_y, panel_rect.width * 0.4 - 30, section_height)
    buy_rect = pygame.Rect(sell_rect.right + 20, section_y, panel_rect.width * 0.6 - 30, section_height)

    # --- Sell Section ---
    sell_title_surf = font_medium.render("Sell Resources", True, WHITE)
    sell_title_rect = sell_title_surf.get_rect(midtop=(sell_rect.centerx, sell_rect.top + 10))
    screen.blit(sell_title_surf, sell_title_rect)

    # Example: Sell Honey (add Wax, Pollen later)
    honey_price = 1.50 # $ per unit of honey (adjust)
    sell_y = sell_title_rect.bottom + 20

    honey_text = f"Honey: {game_state.honey:.2f} units"
    honey_surf = font_small.render(honey_text, True, WHITE)
    honey_rect = honey_surf.get_rect(topleft=(sell_rect.left + 10, sell_y))
    screen.blit(honey_surf, honey_rect)

    def sell_all_honey():
        amount = game_state.honey
        if amount > 0:
            earnings = amount * honey_price
            game_state.money += earnings
            game_state.honey = 0
            print(f"Sold {amount:.2f} honey for ${earnings:.2f}")
        else:
            print("No honey to sell.")

    sell_honey_button = Button(
        sell_rect.left + 10, honey_rect.bottom + 10, sell_rect.width - 20, 40,
        f"Sell All (${honey_price:.2f}/unit)", font_small, sell_all_honey, bg_color=GREEN
    )
    market_buttons.append(sell_honey_button)
    # Add buttons for Wax and Pollen...

    # --- Buy Section ---
    buy_title_surf = font_medium.render("Buy Upgrades", True, WHITE)
    buy_title_rect = buy_title_surf.get_rect(midtop=(buy_rect.centerx, buy_rect.top + 10))
    screen.blit(buy_title_surf, buy_title_rect)

    buy_y = buy_title_rect.bottom + 20
    upgrade_cost = game_state.get_upgrade_cost()
    current_level = game_state.production_upgrade_level
    can_afford = game_state.money >= upgrade_cost

    upgrade_text = f"Prod. Rate Lvl {current_level+1}"
    cost_text = f"Cost: ${upgrade_cost}"

    def purchase_rate_upgrade():
        success = game_state.purchase_upgrade()
        if success:
             # Maybe play a sound effect
             pass

    buy_upgrade_button = Button(
        buy_rect.left + 10, buy_y, buy_rect.width - 20, 50,
        upgrade_text, font_medium, purchase_rate_upgrade,
        bg_color=BLUE if can_afford else (100, 100, 100), # Dim if cannot afford
        text_color=WHITE if can_afford else (180, 180, 180)
    )
    # Add cost text below or beside button
    cost_surf = font_small.render(cost_text, True, WHITE)
    cost_rect = cost_surf.get_rect(midtop=(buy_upgrade_button.rect.centerx, buy_upgrade_button.rect.bottom + 5))
    screen.blit(cost_surf, cost_rect)

    market_buttons.append(buy_upgrade_button)
    # Add more upgrades here...

    # --- Close Button ---
    def close_market():
        game_state.game_mode = GameMode.GAMEPLAY
        print("Closing Market")

    close_button = Button(
        panel_rect.centerx - 75, panel_rect.bottom - 60, 150, 40,
        "Close", font_medium, close_market
    )
    market_buttons.append(close_button)


    # Draw all buttons
    for button in market_buttons:
        button.check_hover(game_state.mouse_pos)
        button.draw(screen)


def handle_market_click(mouse_pos):
     for button in market_buttons:
         if button.rect.collidepoint(mouse_pos):
             # Special check for disabled buttons (like unaffordable upgrade)
             if isinstance(button, Button) and button.bg_color != (100, 100, 100): # Crude check for disabled color
                 button.click()
                 return True
             elif not isinstance(button, Button): # Handle non-Button clickables if any
                 button.click()
                 return True
     return False