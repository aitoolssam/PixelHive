import pygame
from game_state import GameMode, WHITE, BLACK, YELLOW, GREEN, BLUE, BROWN, RED # Colors
from game_state import GAME_DAY_SECONDS # For time display
from entities.flower import FLOWER_DATA # For placement costs
from entities.hive import HIVE_COST

# Store HUD buttons here
hud_buttons = []

# Re-use Button class from menu.py (or define a similar one here)
# For simplicity, let's assume menu.Button is accessible or redefined
from ui.menu import Button

def draw_hud(screen, asset_manager, game_state):
    global hud_buttons
    hud_buttons = [] # Reset buttons each frame

    screen_width = screen.get_width()
    screen_height = screen.get_height()
    font_medium = asset_manager.get_font('comfortaa', 24)
    font_small = asset_manager.get_font('comfortaa', 18)

    # --- Top Bar (Resources, Time) ---
    top_bar_height = 40
    top_bar_rect = pygame.Rect(0, 0, screen_width, top_bar_height)
    pygame.draw.rect(screen, (BLACK + (180,)), top_bar_rect) # Semi-transparent black

    padding = 10
    current_x = padding

    # Money
    money_text = f"$ {game_state.money}"
    money_surf = font_medium.render(money_text, True, YELLOW)
    money_rect = money_surf.get_rect(midleft=(current_x, top_bar_height / 2))
    screen.blit(money_surf, money_rect)
    current_x = money_rect.right + 20

    # Honey
    honey_text = f"Honey: {game_state.honey:.1f}"
    honey_surf = font_small.render(honey_text, True, WHITE)
    honey_rect = honey_surf.get_rect(midleft=(current_x, top_bar_height / 2))
    screen.blit(honey_surf, honey_rect)
    current_x = honey_rect.right + 15

    # Wax
    wax_text = f"Wax: {game_state.wax:.1f}"
    wax_surf = font_small.render(wax_text, True, WHITE)
    wax_rect = wax_surf.get_rect(midleft=(current_x, top_bar_height / 2))
    screen.blit(wax_surf, wax_rect)
    current_x = wax_rect.right + 15

    # Pollen
    pollen_text = f"Pollen: {game_state.pollen:.1f}"
    pollen_surf = font_small.render(pollen_text, True, WHITE)
    pollen_rect = pollen_surf.get_rect(midleft=(current_x, top_bar_height / 2))
    screen.blit(pollen_surf, pollen_rect)
    current_x = pollen_rect.right + 30 # More space before time


    # Day/Time
    day_text = f"Day: {game_state.day_count}"
    day_surf = font_small.render(day_text, True, WHITE)
    day_rect = day_surf.get_rect(midleft=(current_x, top_bar_height / 2))
    screen.blit(day_surf, day_rect)
    current_x = day_rect.right + 15

    # Time of Day (Simple HH:MM format)
    total_minutes_in_day = 24 * 60
    current_minute = int((game_state.get_time_of_day_ratio() * total_minutes_in_day) % total_minutes_in_day)
    hour = (current_minute // 60) % 24
    minute = current_minute % 60
    time_text = f"{hour:02d}:{minute:02d}"
    time_surf = font_small.render(time_text, True, WHITE)
    time_rect = time_surf.get_rect(midleft=(current_x, top_bar_height / 2))
    screen.blit(time_surf, time_rect)
    current_x = time_rect.right + 20

    # Season (Optional)
    # season_text = f"Season: {game_state.current_season}" # Add later if implemented


    # --- Bottom Bar (Actions) ---
    bottom_bar_height = 80
    bottom_bar_y = screen_height - bottom_bar_height
    bottom_bar_rect = pygame.Rect(0, bottom_bar_y, screen_width, bottom_bar_height)
    pygame.draw.rect(screen, (BLACK + (180,)), bottom_bar_rect)

    button_size = 60
    button_padding = 10
    start_x = button_padding
    button_y = bottom_bar_y + (bottom_bar_height - button_size) / 2

    action_buttons = [
        {"action": "select", "label": "Select", "icon": None, "cost": None},
        {"action": "place_hive", "label": f"Hive (${HIVE_COST})", "icon": "hive", "cost": HIVE_COST},
        # Add flowers dynamically
    ]
    # Add flower placement buttons
    for name, data in FLOWER_DATA.items():
         action_buttons.append({
             "action": f"place_flower_{name.lower()}",
             "label": f"{name} (${data['cost']})",
             "icon": data['sprite'],
             "cost": data['cost']
         })

    action_buttons.extend([
        {"action": "water", "label": "Water", "icon": None, "cost": None}, # Add water can icon later
        {"action": "remove", "label": "Remove", "icon": None, "cost": None}, # Add shovel icon later
        {"action": "market", "label": "Market", "icon": None, "cost": None},
    ])


    for i, btn_data in enumerate(action_buttons):
        button_x = start_x + i * (button_size + button_padding)
        is_selected = game_state.selected_action == btn_data["action"]
        can_afford = True
        if btn_data["cost"] is not None and game_state.money < btn_data["cost"]:
             can_afford = False


        # Define callback for each button
        def create_callback(action_name):
            def callback():
                # If the same action is clicked again, deselect it (unless it's 'select' or 'market')
                non_toggle_actions = ["select", "market", "water", "remove"]
                if game_state.selected_action == action_name and action_name not in non_toggle_actions:
                    game_state.selected_action = "select" # Default back to select mode
                    game_state.show_placement_preview = False
                    print(f"Deselected: {action_name}")
                elif action_name == "market":
                     game_state.game_mode = GameMode.MARKET
                     print("Opening Market via HUD")
                else:
                    # Check affordability for placement actions
                    cost = btn_data.get("cost")
                    if cost is not None and game_state.money < cost:
                         print(f"Cannot select {action_name}, not enough money.")
                         # Maybe flash the money display?
                         return # Don't select if cannot afford

                    game_state.selected_action = action_name
                    game_state.show_placement_preview = action_name.startswith("place_")
                    print(f"Selected action: {action_name}")
            return callback

        # Create button (simplified text button for now, icons later)
        btn = Button(button_x, button_y, button_size, button_size,
                     btn_data["label"].split(" ")[0], # Just use first word as temp label
                     font_small, create_callback(btn_data["action"]),
                     bg_color=(YELLOW if is_selected else (BROWN if can_afford else (50,50,50))), # Highlight selected, dim unaffordable
                     hover_color=GREEN if can_afford else (70,70,70)
                     )

        # Draw icon if available (replace text later)
        if btn_data["icon"]:
             icon = asset_manager.get_sprite(btn_data["icon"])
             if icon:
                 icon = pygame.transform.scale(icon, (button_size - 10, button_size - 10)) # Scale icon
                 icon_rect = icon.get_rect(center=btn.rect.center)
                 screen.blit(icon, icon_rect)
                 # Optionally render cost text below icon
                 if btn_data["cost"] is not None:
                     cost_surf = font_small.render(f"${btn_data['cost']}", True, YELLOW if can_afford else RED)
                     cost_rect = cost_surf.get_rect(midtop=(btn.rect.centerx, btn.rect.bottom - 18))
                     screen.blit(cost_surf, cost_rect)

        else: # If no icon, draw the text button
            btn.draw(screen) # Draw the button itself

        # Tooltip (optional) - Show label on hover
        btn.check_hover(game_state.mouse_pos)
        if btn.is_hovered:
             tooltip_surf = font_small.render(btn_data["label"], True, BLACK, WHITE) # Black text on white bg
             tooltip_rect = tooltip_surf.get_rect(midbottom=(btn.rect.centerx, btn.rect.top - 5))
             screen.blit(tooltip_surf, tooltip_rect)

        hud_buttons.append(btn) # Add button for click handling


def handle_hud_click(mouse_pos):
    # Check clicks on bottom bar buttons first
    for button in hud_buttons:
        if button.rect.collidepoint(mouse_pos):
            button.click()
            return True # Click handled by HUD

    # Add checks for clicking top bar elements if needed (e.g., info popups)

    return False # Click not handled by HUD