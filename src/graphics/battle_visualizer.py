"""
Pygame Battle Visualizer for Pokemon Battle Simulator
Displays battles with graphics downloaded from Pokemon Showdown
"""
import pygame
import sys
from pathlib import Path
sys.path.append('/workspaces/Black')

from src.graphics.sprite_manager import SpriteManager
from src.battle.simulator import BattlePokemon, BattleSimulator, Move
from typing import Optional, Tuple

class BattleVisualizer:
    """Visual battle display using Pygame"""
    
    # Display constants
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    FPS = 60
    
    # Colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (200, 200, 200)
    DARK_GRAY = (100, 100, 100)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 150, 255)
    YELLOW = (255, 255, 0)
    
    # HP Bar colors
    HP_GREEN = (78, 205, 86)
    HP_YELLOW = (250, 224, 71)
    HP_RED = (240, 67, 82)
    
    def __init__(self):
        """Initialize Pygame and sprite manager"""
        pygame.init()
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("Pokemon Battle Simulator")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 24)
        
        self.sprite_manager = SpriteManager()
        self.running = True
        
        # Sprite surfaces cache
        self.sprites: dict = {}
        
    def load_sprite(self, species: str, back: bool = False) -> Optional[pygame.Surface]:
        """Load and cache Pokemon sprite"""
        cache_key = f"{species}_{back}"
        
        if cache_key in self.sprites:
            return self.sprites[cache_key]
        
        sprite_path = self.sprite_manager.get_sprite(species, back=back, animated=False)
        if sprite_path:
            try:
                sprite = pygame.image.load(sprite_path)
                # Scale up 2x for better visibility
                width, height = sprite.get_size()
                sprite = pygame.transform.scale(sprite, (width * 2, height * 2))
                self.sprites[cache_key] = sprite
                return sprite
            except pygame.error as e:
                print(f"Failed to load sprite: {e}")
                return None
        return None
    
    def draw_hp_bar(self, x: int, y: int, current_hp: int, max_hp: int, width: int = 200):
        """Draw HP bar with color based on HP percentage"""
        height = 20
        percentage = current_hp / max_hp if max_hp > 0 else 0
        
        # Choose color based on HP percentage
        if percentage > 0.5:
            color = self.HP_GREEN
        elif percentage > 0.2:
            color = self.HP_YELLOW
        else:
            color = self.HP_RED
        
        # Draw background
        pygame.draw.rect(self.screen, self.DARK_GRAY, (x, y, width, height))
        
        # Draw HP fill
        fill_width = int(width * percentage)
        if fill_width > 0:
            pygame.draw.rect(self.screen, color, (x, y, fill_width, height))
        
        # Draw border
        pygame.draw.rect(self.screen, self.BLACK, (x, y, width, height), 2)
        
        # Draw HP text
        hp_text = f"{current_hp}/{max_hp}"
        text_surf = self.small_font.render(hp_text, True, self.WHITE)
        text_rect = text_surf.get_rect(center=(x + width // 2, y + height // 2))
        self.screen.blit(text_surf, text_rect)
    
    def draw_stat_boosts(self, x: int, y: int, pokemon: BattlePokemon):
        """Draw stat boost indicators"""
        stats = ['atk', 'defense', 'spa', 'spd', 'spe']
        stat_names = {'atk': 'Atk', 'defense': 'Def', 'spa': 'SpA', 'spd': 'SpD', 'spe': 'Spe'}
        
        boost_y = y
        for stat in stats:
            boost = pokemon.boosts.get(stat, 0)
            if boost != 0:
                boost_text = f"{stat_names[stat]}: {'+' if boost > 0 else ''}{boost}"
                color = self.GREEN if boost > 0 else self.RED
                text_surf = self.small_font.render(boost_text, True, color)
                self.screen.blit(text_surf, (x, boost_y))
                boost_y += 25
    
    def draw_pokemon_info(self, pokemon: BattlePokemon, x: int, y: int, is_opponent: bool = False):
        """Draw Pokemon information panel"""
        # Draw name
        name_text = self.font.render(pokemon.species, True, self.BLACK)
        name_rect = name_text.get_rect(center=(x + 150, y + 20))
        self.screen.blit(name_text, name_rect)
        
        # Draw level
        level_text = self.small_font.render(f"Lv. {pokemon.level}", True, self.DARK_GRAY)
        self.screen.blit(level_text, (x + 10, y + 45))
        
        # Draw HP bar
        self.draw_hp_bar(x + 50, y + 70, pokemon.current_hp, pokemon.max_hp, width=200)
        
        # Draw types
        type_y = y + 100
        for i, ptype in enumerate(pokemon.types):
            type_text = self.small_font.render(ptype.upper(), True, self.WHITE)
            type_rect = pygame.Rect(x + 10 + i * 70, type_y, 60, 25)
            
            # Type colors (simplified)
            type_colors = {
                'Fire': (255, 100, 50), 'Water': (80, 150, 255), 'Grass': (100, 200, 80),
                'Electric': (255, 200, 50), 'Psychic': (255, 100, 150), 'Dragon': (100, 50, 200),
                'Dark': (80, 60, 50), 'Fighting': (150, 50, 50), 'Flying': (150, 150, 255),
                'Normal': (170, 170, 150), 'Poison': (160, 80, 160), 'Ground': (200, 150, 80),
                'Rock': (170, 150, 100), 'Bug': (170, 190, 50), 'Ghost': (100, 80, 150),
                'Steel': (170, 170, 190), 'Ice': (150, 220, 255), 'Fairy': (255, 150, 200),
            }
            color = type_colors.get(ptype, self.GRAY)
            pygame.draw.rect(self.screen, color, type_rect)
            pygame.draw.rect(self.screen, self.BLACK, type_rect, 2)
            text_rect = type_text.get_rect(center=type_rect.center)
            self.screen.blit(type_text, text_rect)
        
        # Draw ability
        ability_text = self.small_font.render(f"Ability: {pokemon.ability}", True, self.DARK_GRAY)
        self.screen.blit(ability_text, (x + 10, y + 135))
        
        # Draw stat boosts if any
        self.draw_stat_boosts(x + 260, y + 70, pokemon)
    
    def draw_battle_scene(self, player_pokemon: BattlePokemon, opponent_pokemon: BattlePokemon, 
                         message: str = ""):
        """Draw the complete battle scene"""
        # Clear screen with background
        self.screen.fill((240, 250, 255))
        
        # Draw background gradient
        for i in range(self.WINDOW_HEIGHT // 2):
            color_value = 200 + int(55 * (i / (self.WINDOW_HEIGHT // 2)))
            pygame.draw.line(self.screen, (color_value, color_value, 255), 
                           (0, i), (self.WINDOW_WIDTH, i))
        
        # Draw ground
        pygame.draw.rect(self.screen, (150, 200, 120), 
                        (0, self.WINDOW_HEIGHT // 2, self.WINDOW_WIDTH, self.WINDOW_HEIGHT // 2))
        
        # Draw opponent (top)
        opponent_x = self.WINDOW_WIDTH - 250
        opponent_y = 100
        opponent_sprite = self.load_sprite(opponent_pokemon.species, back=False)
        if opponent_sprite:
            sprite_rect = opponent_sprite.get_rect(center=(opponent_x, opponent_y))
            self.screen.blit(opponent_sprite, sprite_rect)
        
        # Draw player (bottom)
        player_x = 150
        player_y = 350
        player_sprite = self.load_sprite(player_pokemon.species, back=True)
        if player_sprite:
            sprite_rect = player_sprite.get_rect(center=(player_x, player_y))
            self.screen.blit(player_sprite, sprite_rect)
        
        # Draw info panels
        # Opponent info (top right)
        panel_rect = pygame.Rect(self.WINDOW_WIDTH - 350, 10, 340, 170)
        pygame.draw.rect(self.screen, self.WHITE, panel_rect)
        pygame.draw.rect(self.screen, self.BLACK, panel_rect, 3)
        self.draw_pokemon_info(opponent_pokemon, self.WINDOW_WIDTH - 345, 10, is_opponent=True)
        
        # Player info (bottom left)
        panel_rect = pygame.Rect(10, self.WINDOW_HEIGHT - 180, 340, 170)
        pygame.draw.rect(self.screen, self.WHITE, panel_rect)
        pygame.draw.rect(self.screen, self.BLACK, panel_rect, 3)
        self.draw_pokemon_info(player_pokemon, 15, self.WINDOW_HEIGHT - 175)
        
        # Draw message box at bottom
        if message:
            msg_rect = pygame.Rect(360, self.WINDOW_HEIGHT - 100, self.WINDOW_WIDTH - 370, 90)
            pygame.draw.rect(self.screen, self.WHITE, msg_rect)
            pygame.draw.rect(self.screen, self.BLACK, msg_rect, 3)
            
            # Word wrap message
            words = message.split(' ')
            lines = []
            current_line = []
            for word in words:
                test_line = ' '.join(current_line + [word])
                if self.small_font.size(test_line)[0] < msg_rect.width - 20:
                    current_line.append(word)
                else:
                    lines.append(' '.join(current_line))
                    current_line = [word]
            if current_line:
                lines.append(' '.join(current_line))
            
            # Draw lines
            for i, line in enumerate(lines[:3]):  # Max 3 lines
                text_surf = self.small_font.render(line, True, self.BLACK)
                self.screen.blit(text_surf, (msg_rect.x + 10, msg_rect.y + 10 + i * 25))
        
        pygame.display.flip()
    
    def wait_for_input(self):
        """Wait for user to press a key"""
        waiting = True
        while waiting and self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    waiting = False
                elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False
            self.clock.tick(self.FPS)
    
    def run_demo_battle(self):
        """Run a demo battle visualization"""
        # Create demo Pokemon
        machamp = BattlePokemon(
            species="Machamp",
            level=50,
            types=["Fighting"],
            base_hp=90, base_atk=130, base_def=80,
            base_spa=65, base_spd=85, base_spe=55,
            ability="Guts"
        )
        
        gyarados = BattlePokemon(
            species="Gyarados",
            level=50,
            types=["Water", "Flying"],
            base_hp=95, base_atk=125, base_def=79,
            base_spa=60, base_spd=100, base_spe=81,
            ability="Intimidate"
        )
        
        sim = BattleSimulator()
        
        # Turn 0: Initial state
        self.draw_battle_scene(machamp, gyarados, "A wild Gyarados appeared! (Press any key)")
        self.wait_for_input()
        
        # Turn 1: Intimidate
        sim.apply_switch_in_abilities(gyarados, machamp)
        self.draw_battle_scene(machamp, gyarados, "Gyarados's Intimidate lowered Machamp's Attack!")
        self.wait_for_input()
        
        # Turn 2: Bulk Up
        machamp.boost_by({"atk": 1, "defense": 1})
        self.draw_battle_scene(machamp, gyarados, "Machamp used Bulk Up! Attack and Defense rose!")
        self.wait_for_input()
        
        # Turn 3: Dragon Dance
        gyarados.boost_by({"atk": 1, "spe": 1})
        self.draw_battle_scene(machamp, gyarados, "Gyarados used Dragon Dance! Attack and Speed rose!")
        self.wait_for_input()
        
        # Turn 4: Attack
        waterfall = Move(
            name="Waterfall",
            type="Water",
            category="Physical",
            base_power=80,
            accuracy=100,
            pp=15,
            max_pp=15
        )
        
        damage, _, _ = sim.calculate_move_damage(gyarados, machamp, waterfall)
        machamp.take_damage(damage)
        self.draw_battle_scene(machamp, gyarados, f"Gyarados used Waterfall! Dealt {damage} damage!")
        self.wait_for_input()
        
        # Turn 5: Counter attack
        close_combat = Move(
            name="Close Combat",
            type="Fighting",
            category="Physical",
            base_power=120,
            accuracy=100,
            pp=5,
            max_pp=5
        )
        
        damage, _, _ = sim.calculate_move_damage(machamp, gyarados, close_combat)
        gyarados.take_damage(damage)
        self.draw_battle_scene(machamp, gyarados, f"Machamp used Close Combat! Dealt {damage} damage!")
        self.wait_for_input()
        
        if gyarados.fainted:
            self.draw_battle_scene(machamp, gyarados, "Gyarados fainted! Machamp wins!")
        elif machamp.fainted:
            self.draw_battle_scene(machamp, gyarados, "Machamp fainted! Gyarados wins!")
        else:
            self.draw_battle_scene(machamp, gyarados, "Battle continues!")
        
        self.wait_for_input()
    
    def quit(self):
        """Clean up and quit"""
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    visualizer = BattleVisualizer()
    try:
        visualizer.run_demo_battle()
    finally:
        visualizer.quit()
