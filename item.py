import pygame
import math
import random

class Item:
    def __init__(self, x, y, size, item_type):
        self.rect = pygame.Rect(x, y, size * 2, size * 2)
        self.size = size
        self.item_type = item_type
        self.collected = False
        self.anim_frame = 0
        self.anim_timer = 0
        self.anim_speed = 0.1  # seconds per frame
        self.hover_offset = 0
        self.hover_direction = 1
        self.particles = []
        self.particle_timer = 0
        self.particle_interval = 0.2  # seconds
        self.rotation = 0
        self.rotation_speed = 45  # degrees per second
        
        # Set color based on type
        if item_type == 'health':
            self.color = (255, 0, 0)  # Red
            self.effect_value = 25  # Heal 25 health
        elif item_type == 'speed':
            self.color = (255, 255, 0)  # Yellow
            self.effect_value = 50  # Increase speed by 50
        elif item_type == 'damage':
            self.color = (255, 165, 0)  # Orange
            self.effect_value = 10  # Increase damage by 10
    
    def update(self, dt):
        """Update item animation and particles."""
        # Update animation
        self.anim_timer += dt
        if self.anim_timer >= self.anim_speed:
            self.anim_timer = 0
            self.anim_frame = (self.anim_frame + 1) % 4
        
        # Update hover effect
        self.hover_offset += self.hover_direction * dt * 10
        if abs(self.hover_offset) > 5:
            self.hover_direction *= -1
        
        # Update rotation
        self.rotation = (self.rotation + self.rotation_speed * dt) % 360
        
        # Spawn particles
        self.particle_timer += dt
        if self.particle_timer >= self.particle_interval:
            self.particle_timer = 0
            
            # Add a new particle
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(5, 15)
            lifetime = random.uniform(0.5, 1.0)
            
            particle = {
                'x': self.rect.centerx + random.uniform(-self.size / 2, self.size / 2),
                'y': self.rect.centery + random.uniform(-self.size / 2, self.size / 2),
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'timer': lifetime,
                'max_timer': lifetime,
                'color': self.color,
                'size': random.uniform(1, 3)
            }
            
            self.particles.append(particle)
        
        # Update existing particles
        for particle in self.particles[:]:
            particle['timer'] -= dt
            if particle['timer'] <= 0:
                self.particles.remove(particle)
            else:
                particle['x'] += particle['vx'] * dt
                particle['y'] += particle['vy'] * dt
    
    def collect(self, player):
        """Apply the item's effect to the player."""
        self.collected = True
        
        if self.item_type == 'health':
            player.health = min(player.max_health, player.health + self.effect_value)
        elif self.item_type == 'speed':
            player.speed += self.effect_value
        elif self.item_type == 'damage':
            player.attack_power += self.effect_value
            
        # Add item to player's inventory
        player.items.append(self.item_type)
        
        # Increase score
        player.score += 50
    
    def draw(self, surface, rect):
        """Draw the item and its particles."""
        if self.collected:
            return
            
        # Draw particles
        for particle in self.particles:
            # Calculate opacity based on remaining time
            alpha = int(255 * (particle['timer'] / particle['max_timer']))
            
            # Calculate position adjusted for camera
            pos = (
                int(particle['x'] - self.rect.x + rect.x),
                int(particle['y'] - self.rect.y + rect.y)
            )
            
            # Draw the particle
            size = int(particle['size'] * (0.5 + 0.5 * (particle['timer'] / particle['max_timer'])))
            pygame.draw.circle(surface, particle['color'], pos, size)
        
        # Calculate draw position with hover effect
        draw_y = rect.y + self.hover_offset
        
        # Draw the item based on its type
        if self.item_type == 'health':
            self._draw_health_item(surface, rect.x, draw_y)
        elif self.item_type == 'speed':
            self._draw_speed_item(surface, rect.x, draw_y)
        elif self.item_type == 'damage':
            self._draw_damage_item(surface, rect.x, draw_y)
    
    def _draw_health_item(self, surface, x, y):
        """Draw a health potion item."""
        # Draw bottle
        bottle_color = (200, 0, 0)  # Dark red
        bottle_width = self.size * 1.2
        bottle_height = self.size * 1.5
        
        # Base of the bottle
        bottle_rect = pygame.Rect(
            x + (self.rect.width - bottle_width) // 2,
            y + (self.rect.height - bottle_height) // 2,
            bottle_width,
            bottle_height
        )
        
        pygame.draw.rect(surface, bottle_color, bottle_rect, border_radius=int(self.size * 0.3))
        
        # Neck of the bottle
        neck_width = bottle_width * 0.5
        neck_height = self.size * 0.4
        neck_rect = pygame.Rect(
            x + (self.rect.width - neck_width) // 2,
            y + (self.rect.height - bottle_height) // 2 - neck_height,
            neck_width,
            neck_height
        )
        
        pygame.draw.rect(surface, bottle_color, neck_rect, border_radius=int(self.size * 0.1))
        
        # Cork
        cork_width = neck_width * 0.8
        cork_height = self.size * 0.2
        cork_rect = pygame.Rect(
            x + (self.rect.width - cork_width) // 2,
            y + (self.rect.height - bottle_height) // 2 - neck_height - cork_height,
            cork_width,
            cork_height
        )
        
        pygame.draw.rect(surface, (139, 69, 19), cork_rect, border_radius=int(self.size * 0.1))
        
        # Liquid inside (with wave animation)
        liquid_level = self.size * (0.8 + 0.1 * math.sin(self.anim_frame * math.pi / 2))
        liquid_rect = pygame.Rect(
            bottle_rect.x + bottle_rect.width * 0.1,
            bottle_rect.y + bottle_rect.height - liquid_level,
            bottle_rect.width * 0.8,
            liquid_level
        )
        
        pygame.draw.rect(surface, (255, 50, 50), liquid_rect, border_radius=int(self.size * 0.1))
        
        # Highlight/shine
        shine_pos = (bottle_rect.x + bottle_rect.width * 0.2, bottle_rect.y + bottle_rect.height * 0.3)
        shine_size = self.size * 0.2
        pygame.draw.circle(surface, (255, 150, 150), shine_pos, shine_size)
    
    def _draw_speed_item(self, surface, x, y):
        """Draw a speed boost item."""
        # Draw a winged shoe
        shoe_color = (255, 220, 0)  # Gold
        
        # Shoe base
        shoe_width = self.size * 1.2
        shoe_height = self.size * 0.8
        
        base_points = [
            (x + self.rect.width // 2 - shoe_width // 2, y + self.rect.height // 2),
            (x + self.rect.width // 2 + shoe_width // 2, y + self.rect.height // 2),
            (x + self.rect.width // 2 + shoe_width // 3, y + self.rect.height // 2 + shoe_height),
            (x + self.rect.width // 2 - shoe_width // 3, y + self.rect.height // 2 + shoe_height)
        ]
        
        pygame.draw.polygon(surface, shoe_color, base_points)
        
        # Shoe top (ankle part)
        top_rect = pygame.Rect(
            x + self.rect.width // 2 - shoe_width // 4,
            y + self.rect.height // 2 - shoe_height * 0.5,
            shoe_width // 2,
            shoe_height * 0.5
        )
        
        pygame.draw.rect(surface, shoe_color, top_rect, border_radius=int(self.size * 0.1))
        
        # Wings
        wing_offset = math.sin(self.anim_frame * math.pi / 2) * 2
        
        # Left wing
        left_wing_points = [
            (x + self.rect.width // 2 - shoe_width // 4, y + self.rect.height // 2),
            (x + self.rect.width // 2 - shoe_width, y + self.rect.height // 2 - shoe_height // 2 - wing_offset),
            (x + self.rect.width // 2 - shoe_width * 0.8, y + self.rect.height // 2 - shoe_height - wing_offset),
            (x + self.rect.width // 2 - shoe_width // 2, y + self.rect.height // 2 - shoe_height * 0.3)
        ]
        
        pygame.draw.polygon(surface, (240, 240, 240), left_wing_points)
        
        # Right wing
        right_wing_points = [
            (x + self.rect.width // 2 + shoe_width // 4, y + self.rect.height // 2),
            (x + self.rect.width // 2 + shoe_width, y + self.rect.height // 2 - shoe_height // 2 - wing_offset),
            (x + self.rect.width // 2 + shoe_width * 0.8, y + self.rect.height // 2 - shoe_height - wing_offset),
            (x + self.rect.width // 2 + shoe_width // 2, y + self.rect.height // 2 - shoe_height * 0.3)
        ]
        
        pygame.draw.polygon(surface, (240, 240, 240), right_wing_points)
    
    def _draw_damage_item(self, surface, x, y):
        """Draw a damage boost item."""
        # Draw a weapon (sword)
        center_x = x + self.rect.width // 2
        center_y = y + self.rect.height // 2
        
        # Rotate the sword
        rotation_rad = math.radians(self.rotation)
        
        # Blade
        blade_length = self.size * 1.5
        blade_width = self.size * 0.3
        
        blade_top = (
            center_x + math.sin(rotation_rad) * blade_length,
            center_y - math.cos(rotation_rad) * blade_length
        )
        
        # Calculate perpendicular points for width
        perp_x = math.cos(rotation_rad) * blade_width / 2
        perp_y = math.sin(rotation_rad) * blade_width / 2
        
        blade_left = (center_x - perp_x, center_y - perp_y)
        blade_right = (center_x + perp_x, center_y + perp_y)
        
        # Draw blade
        pygame.draw.polygon(surface, (200, 200, 200), [blade_left, blade_right, blade_top])
        
        # Draw handle
        handle_length = self.size * 0.7
        handle_width = self.size * 0.2
        
        handle_bottom = (
            center_x - math.sin(rotation_rad) * handle_length,
            center_y + math.cos(rotation_rad) * handle_length
        )
        
        handle_left = (center_x - perp_x, center_y - perp_y)
        handle_right = (center_x + perp_x, center_y + perp_y)
        
        # Draw handle
        pygame.draw.polygon(surface, (139, 69, 19), [handle_left, handle_right, handle_bottom])
        
        # Draw guard
        guard_width = self.size * 0.8
        
        guard_left = (
            center_x - math.cos(rotation_rad) * guard_width / 2,
            center_y - math.sin(rotation_rad) * guard_width / 2
        )
        
        guard_right = (
            center_x + math.cos(rotation_rad) * guard_width / 2,
            center_y + math.sin(rotation_rad) * guard_width / 2
        )
        
        pygame.draw.line(surface, (255, 165, 0), guard_left, guard_right, int(self.size * 0.2))
        
        # Add glow effect
        glow_radius = self.size * (0.4 + 0.1 * math.sin(self.anim_frame * math.pi))
        glow_surf = pygame.Surface((int(glow_radius * 2), int(glow_radius * 2)), pygame.SRCALPHA)
        
        for r in range(int(glow_radius), 0, -2):
            alpha = 150 * (r / glow_radius)
            pygame.draw.circle(glow_surf, (255, 165, 0, alpha), (int(glow_radius), int(glow_radius)), r)
            
        surface.blit(glow_surf, (blade_top[0] - glow_radius, blade_top[1] - glow_radius)) 