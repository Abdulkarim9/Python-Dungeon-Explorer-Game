import pygame
import random
import math
import time
import noise
from enum import Enum
import numpy as np
import io
import struct

# Initialize Pygame
pygame.init()
# Initialize the mixer with stereo sound
pygame.mixer.init(frequency=44100, size=-16, channels=2)

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
TILE_SIZE = 32
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
BROWN = (139, 69, 19)

# Create the screen with resizable flag
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Dungeon Explorer")
clock = pygame.time.Clock()

# Game states
class GameState(Enum):
    MAIN_MENU = 0
    PLAYING = 1
    GAME_OVER = 2
    VICTORY = 3

# Camera class for scrolling
class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        
    def apply(self, entity):
        """Apply camera to an entity or rect.
        
        This method can handle both:
        - Entity objects with a .rect attribute
        - Direct pygame.Rect objects
        """
        if hasattr(entity, 'rect'):
            return entity.rect.move(self.camera.topleft)
        else:
            # Assume entity is already a pygame.Rect
            return entity.move(self.camera.topleft)
    
    def update(self, target):
        x = -target.rect.x + SCREEN_WIDTH // 2
        y = -target.rect.y + SCREEN_HEIGHT // 2
        
        # Limit scrolling to game map
        x = min(0, x)  # Left border
        y = min(0, y)  # Top border
        x = max(-(self.width - SCREEN_WIDTH), x)  # Right border
        y = max(-(self.height - SCREEN_HEIGHT), y)  # Bottom border
        
        self.camera = pygame.Rect(x, y, self.width, self.height)

    def update_dimensions(self, width, height):
        """Update camera dimensions when window is resized"""
        self.width = width
        self.height = height
        # Keep the camera centered on the same position
        center_x = self.camera.centerx
        center_y = self.camera.centery
        self.camera = pygame.Rect(0, 0, width, height)
        self.camera.centerx = center_x
        self.camera.centery = center_y

# Sound generator
class SoundGenerator:
    def __init__(self):
        self.sounds = {}
        
    def generate_sounds(self):
        # Generate player attack sound
        self._generate_attack_sound()
        # Generate player hit sound
        self._generate_hit_sound()
        # Generate enemy death sound
        self._generate_death_sound()
        # Generate item pickup sound
        self._generate_pickup_sound()
        # Generate background music
        self._generate_background_music()
        
    def _create_sine_wave(self, frequency, duration, volume=0.5, fade_out_start=None):
        # Parameters
        sample_rate = 44100  # Hz
        n_samples = int(sample_rate * duration)
        
        # Create a bytes buffer
        buf = io.BytesIO()
        
        # Generate a stereo sine wave (2 channels)
        for i in range(n_samples):
            t = float(i) / sample_rate
            value = volume * math.sin(2 * math.pi * frequency * t)
            
            # Apply fade out if specified
            if fade_out_start and i > int(n_samples * fade_out_start):
                value *= (n_samples - i) / (n_samples * (1 - fade_out_start))
                
            # Convert to 16-bit signed value for both left and right channels (stereo)
            left_channel = int(value * 32767)
            right_channel = int(value * 32767)
            
            # Pack both channels
            packed_value = struct.pack('hh', left_channel, right_channel)
            buf.write(packed_value)
        
        return pygame.mixer.Sound(buffer=buf.getvalue())
        
    def _generate_attack_sound(self):
        # Create a sharp attack sound at 440 Hz with a short fade out
        self.sounds['attack'] = self._create_sine_wave(440, 0.3, 0.6, 0.5)
    
    def _generate_hit_sound(self):
        # Create a lower hit sound at 220 Hz
        self.sounds['hit'] = self._create_sine_wave(220, 0.2, 0.5, 0.3)
    
    def _generate_death_sound(self):
        # Create a longer death sound with descending frequency
        sample_rate = 44100
        duration = 0.5
        n_samples = int(sample_rate * duration)
        buf = io.BytesIO()
        
        for i in range(n_samples):
            t = float(i) / sample_rate
            progress = float(i) / n_samples
            
            # Descending frequency from 150Hz to 50Hz
            freq = 150 - 100 * progress
            value = 0.7 * math.sin(2 * math.pi * freq * t)
            
            # Apply fade out after halfway
            if i > n_samples // 2:
                value *= (n_samples - i) / (n_samples // 2)
                
            # Convert to 16-bit signed value for stereo (left and right channel)
            left_channel = int(value * 32767)
            right_channel = int(value * 32767)
            packed_value = struct.pack('hh', left_channel, right_channel)
            buf.write(packed_value)
            
        self.sounds['death'] = pygame.mixer.Sound(buffer=buf.getvalue())
    
    def _generate_pickup_sound(self):
        # Create an ascending pickup sound
        sample_rate = 44100
        duration = 0.2
        n_samples = int(sample_rate * duration)
        buf = io.BytesIO()
        
        for i in range(n_samples):
            t = float(i) / sample_rate
            progress = float(i) / n_samples
            
            # Ascending frequency from 400Hz to 800Hz
            freq = 400 + 400 * progress
            value = 0.5 * math.sin(2 * math.pi * freq * t)
            
            # Apply fade out near the end
            if i > int(n_samples * 0.8):
                value *= (n_samples - i) / (n_samples * 0.2)
                
            # Convert to 16-bit signed value for stereo (left and right channel)
            left_channel = int(value * 32767)
            right_channel = int(value * 32767)
            packed_value = struct.pack('hh', left_channel, right_channel)
            buf.write(packed_value)
            
        self.sounds['pickup'] = pygame.mixer.Sound(buffer=buf.getvalue())
    
    def _generate_background_music(self):
        # Create simple background music
        sample_rate = 44100
        duration = 5.0  # shorter to save memory
        n_samples = int(sample_rate * duration)
        buf = io.BytesIO()
        
        for i in range(n_samples):
            t = float(i) / sample_rate
            
            # Multiple tones for richer sound
            value1 = 0.3 * math.sin(2 * math.pi * 180 * t)  # Base tone
            value2 = 0.15 * math.sin(2 * math.pi * 270 * t)  # Harmony
            value3 = 0.05 * math.sin(2 * math.pi * 360 * t * (1 + 0.1 * math.sin(2 * math.pi * 0.1 * t)))  # Modulated
            
            value = value1 + value2 + value3
                
            # Convert to 16-bit signed value for stereo (left and right channel)
            left_channel = int(value * 32767)
            right_channel = int(value * 32767)
            packed_value = struct.pack('hh', left_channel, right_channel)
            buf.write(packed_value)
            
        self.sounds['background'] = pygame.mixer.Sound(buffer=buf.getvalue())
    
    def play_sound(self, sound_name):
        if sound_name in self.sounds:
            self.sounds[sound_name].play()

# Main game function
def main():
    global SCREEN_WIDTH, SCREEN_HEIGHT, screen, clock, TILE_SIZE, BLACK, DARK_GRAY, GRAY, BROWN, GREEN
    
    game_state = GameState.MAIN_MENU
    
    # Import all the game components here to avoid circular imports
    from player import Player
    from level import DungeonGenerator
    from enemy import Enemy
    from item import Item
    from ui import UI
    
    # Initialize game components
    dungeon_generator = DungeonGenerator(100, 100, TILE_SIZE)
    level_map, start_pos, exit_pos = dungeon_generator.generate_dungeon()
    
    player = Player(start_pos[0], start_pos[1], TILE_SIZE)
    camera = Camera(dungeon_generator.width * TILE_SIZE, dungeon_generator.height * TILE_SIZE)
    ui = UI(SCREEN_WIDTH, SCREEN_HEIGHT)
    
    # Create enemy list
    enemies = dungeon_generator.spawn_enemies(10, player)
    
    # Create item list
    items = dungeon_generator.spawn_items(5)
    
    # Sound generator
    sound_gen = SoundGenerator()
    sound_gen.generate_sounds()
    
    # Game level and difficulty variables
    current_level = 1
    max_levels = 5
    difficulty_multiplier = 1.0
    
    # Store button rects from UI for click detection
    start_button_rect = None
    retry_button_rect = None
    exit_button_rect = None
    
    # Main game loop
    running = True
    
    while running:
        dt = clock.tick(FPS) / 1000.0  # Delta time in seconds
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Handle window resize event
            if event.type == pygame.VIDEORESIZE:
                # Update the screen dimensions
                SCREEN_WIDTH, SCREEN_HEIGHT = event.w, event.h
                screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
                # Update the camera and UI
                if game_state == GameState.PLAYING:
                    camera.update_dimensions(SCREEN_WIDTH, SCREEN_HEIGHT)
                # Recreate UI with new dimensions
                ui = UI(SCREEN_WIDTH, SCREEN_HEIGHT)
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                
                if game_state == GameState.MAIN_MENU and event.key == pygame.K_RETURN:
                    game_state = GameState.PLAYING
                    print("Starting game via keyboard")
                
                if game_state == GameState.GAME_OVER and event.key == pygame.K_RETURN:
                    # Reset game
                    current_level = 1
                    difficulty_multiplier = 1.0
                    dungeon_generator = DungeonGenerator(100, 100, TILE_SIZE)
                    level_map, start_pos, exit_pos = dungeon_generator.generate_dungeon()
                    player = Player(start_pos[0], start_pos[1], TILE_SIZE)
                    # Initialize camera with current screen dimensions
                    camera = Camera(dungeon_generator.width * TILE_SIZE, dungeon_generator.height * TILE_SIZE)
                    enemies = dungeon_generator.spawn_enemies(10 * difficulty_multiplier, player)
                    items = dungeon_generator.spawn_items(5)
                    game_state = GameState.PLAYING
                
                if game_state == GameState.VICTORY and event.key == pygame.K_RETURN:
                    running = False
            
            # Handle mouse clicks
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
                mouse_pos = event.pos
                print(f"Mouse clicked at {mouse_pos}")
                
                if game_state == GameState.MAIN_MENU and start_button_rect:
                    print(f"Start button rect: {start_button_rect}")
                    if start_button_rect.collidepoint(mouse_pos):
                        print("Start button clicked!")
                        game_state = GameState.PLAYING
                        sound_gen.play_sound('pickup')  # Play a sound when clicking
                
                if game_state == GameState.GAME_OVER and retry_button_rect:
                    if retry_button_rect.collidepoint(mouse_pos):
                        # Reset game
                        current_level = 1
                        difficulty_multiplier = 1.0
                        dungeon_generator = DungeonGenerator(100, 100, TILE_SIZE)
                        level_map, start_pos, exit_pos = dungeon_generator.generate_dungeon()
                        player = Player(start_pos[0], start_pos[1], TILE_SIZE)
                        enemies = dungeon_generator.spawn_enemies(10 * difficulty_multiplier, player)
                        items = dungeon_generator.spawn_items(5)
                        game_state = GameState.PLAYING
                        sound_gen.play_sound('pickup')
                
                if game_state == GameState.VICTORY and exit_button_rect:
                    if exit_button_rect.collidepoint(mouse_pos):
                        running = False
                        sound_gen.play_sound('pickup')
        
        # Game state logic
        if game_state == GameState.MAIN_MENU:
            # Draw main menu
            screen.fill(BLACK)
            start_button_rect = ui.draw_main_menu(screen)
            
        elif game_state == GameState.PLAYING:
            # Update player
            player.update(dt, level_map, enemies, items, sound_gen)
            
            # Check if player reached exit
            player_center = player.rect.center
            exit_center = (exit_pos[0] + TILE_SIZE // 2, exit_pos[1] + TILE_SIZE // 2)
            if math.dist(player_center, exit_center) < TILE_SIZE:
                current_level += 1
                difficulty_multiplier += 0.2
                
                if current_level > max_levels:
                    game_state = GameState.VICTORY
                else:
                    # Generate new level
                    dungeon_generator = DungeonGenerator(100, 100, TILE_SIZE)
                    level_map, start_pos, exit_pos = dungeon_generator.generate_dungeon()
                    player.rect.x, player.rect.y = start_pos[0], start_pos[1]
                    enemies = dungeon_generator.spawn_enemies(int(10 * difficulty_multiplier), player)
                    items = dungeon_generator.spawn_items(5)
            
            # Update enemies
            for enemy in enemies[:]:
                enemy.update(dt, level_map, player, enemies, sound_gen)
                if enemy.health <= 0:
                    enemies.remove(enemy)
                    player.score += 10
            
            # Update camera
            camera.update(player)
            
            # Check for game over
            if player.health <= 0:
                game_state = GameState.GAME_OVER
            
            # Draw everything
            screen.fill(BLACK)
            
            # Draw map
            for y in range(dungeon_generator.height):
                for x in range(dungeon_generator.width):
                    tile = level_map[y][x]
                    if tile != 0:  # Skip empty tiles
                        tile_rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                        tile_rect = camera.apply(pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
                        
                        if tile == 1:  # Wall
                            pygame.draw.rect(screen, DARK_GRAY, tile_rect)
                            pygame.draw.rect(screen, GRAY, tile_rect, 1)
                        elif tile == 2:  # Floor
                            pygame.draw.rect(screen, BROWN, tile_rect)
                            pygame.draw.rect(screen, DARK_GRAY, tile_rect, 1)
            
            # Draw exit
            exit_rect = pygame.Rect(exit_pos[0], exit_pos[1], TILE_SIZE, TILE_SIZE)
            exit_rect = camera.apply(exit_rect)
            pygame.draw.rect(screen, GREEN, exit_rect)
            
            # Draw items
            for item in items:
                if not item.collected:
                    item_rect = camera.apply(item.rect)
                    item.draw(screen, item_rect)
            
            # Draw enemies
            for enemy in enemies:
                enemy_rect = camera.apply(enemy.rect)
                enemy.draw(screen, enemy_rect)
            
            # Draw player
            player_rect = camera.apply(player.rect)
            player.draw(screen, player_rect)
            
            # Draw UI
            ui.draw_game_ui(screen, player, current_level)
            
        elif game_state == GameState.GAME_OVER:
            # Draw game over screen
            screen.fill(BLACK)
            retry_button_rect = ui.draw_game_over(screen, player.score)
            
        elif game_state == GameState.VICTORY:
            # Draw victory screen
            screen.fill(BLACK)
            exit_button_rect = ui.draw_victory(screen, player.score)
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main() 