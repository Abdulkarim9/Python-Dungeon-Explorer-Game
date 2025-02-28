import pygame
import math
import random

class UI:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font_large = pygame.font.Font(None, 64)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)
        self.font_tiny = pygame.font.Font(None, 24)
        
        # Particle effects for UI
        self.particles = []
        self.star_particles = []
        
        # Initialize star particles for menu background
        self._init_star_particles(100)
        
        # Title glow effect
        self.title_glow = 0
        self.title_glow_dir = 1
        
    def _init_star_particles(self, count):
        """Initialize star particles for background effects."""
        # Clear existing particles when reinitializing
        self.star_particles = []
        
        for _ in range(count):
            particle = {
                'x': random.randint(0, self.screen_width),
                'y': random.randint(0, self.screen_height),
                'size': random.uniform(1, 3),
                'speed': random.uniform(5, 20),
                'angle': random.uniform(0, math.pi * 2),
                'color': (
                    random.randint(200, 255),
                    random.randint(200, 255),
                    random.randint(200, 255)
                ),
                'twinkle_speed': random.uniform(0.5, 2.0),
                'twinkle_offset': random.uniform(0, math.pi * 2)
            }
            self.star_particles.append(particle)
    
    def update_particles(self, dt):
        """Update particle animations."""
        # Update star particles
        for p in self.star_particles:
            p['x'] += math.cos(p['angle']) * p['speed'] * dt
            p['y'] += math.sin(p['angle']) * p['speed'] * dt
            
            # Wrap around screen
            if p['x'] < 0:
                p['x'] = self.screen_width
            elif p['x'] > self.screen_width:
                p['x'] = 0
                
            if p['y'] < 0:
                p['y'] = self.screen_height
            elif p['y'] > self.screen_height:
                p['y'] = 0
        
        # Update title glow
        self.title_glow += 0.05 * self.title_glow_dir
        if self.title_glow > 1.0:
            self.title_glow = 1.0
            self.title_glow_dir = -1
        elif self.title_glow < 0.0:
            self.title_glow = 0.0
            self.title_glow_dir = 1
    
    def draw_text_with_shadow(self, surface, text, font, color, pos, shadow_color=(0, 0, 0), shadow_offset=2):
        """Draw text with a shadow effect."""
        # Draw shadow
        shadow_surf = font.render(text, True, shadow_color)
        shadow_rect = shadow_surf.get_rect(center=(pos[0] + shadow_offset, pos[1] + shadow_offset))
        surface.blit(shadow_surf, shadow_rect)
        
        # Draw text
        text_surf = font.render(text, True, color)
        text_rect = text_surf.get_rect(center=pos)
        surface.blit(text_surf, text_rect)
        
        return text_rect
    
    def draw_button(self, surface, text, font, color, rect, hover=False, is_start_button=False):
        """Draw a button with hover effect."""
        # Create gradient colors based on button type
        if is_start_button:
            # Use green color scheme for start button
            if hover:
                # Brighter colors when hovering
                top_color = (40, 200, 80)  # Bright green top
                bottom_color = (20, 150, 50)  # Darker green bottom
                border_color = (255, 255, 255)  # White border
                glow_color = (100, 255, 150, 30)  # Green glow
                
                # Draw pulsing glow effect when hovering
                pulse = (math.sin(pygame.time.get_ticks() * 0.005) + 1) / 2  # 0 to 1 pulsing
                for offset in range(15, 0, -3):
                    glow_rect = rect.copy()
                    glow_rect.inflate_ip(offset * 2, offset * 2)
                    glow_alpha = int(30 * (1 - (offset / 15)) * (0.7 + 0.3 * pulse))
                    current_glow = (glow_color[0], glow_color[1], glow_color[2], glow_alpha)
                    pygame.draw.rect(surface, current_glow, glow_rect, border_radius=15)
            else:
                # Normal colors
                top_color = (30, 160, 60)  # Green top
                bottom_color = (20, 120, 40)  # Darker green bottom
                border_color = (150, 255, 180)  # Light green border
        else:
            # Use blue color scheme for other buttons
            if hover:
                # Brighter colors when hovering
                top_color = (80, 120, 255)  # Blue top
                bottom_color = (40, 80, 200)  # Darker blue bottom
                border_color = (255, 255, 255)  # White border
                glow_color = (100, 150, 255, 30)  # Subtle glow
                
                # Draw glow effect when hovering
                for offset in range(8, 0, -2):
                    glow_rect = rect.copy()
                    glow_rect.inflate_ip(offset * 2, offset * 2)
                    pygame.draw.rect(surface, glow_color, glow_rect, border_radius=12)
            else:
                # Normal colors
                top_color = (60, 80, 180)  # Blue top
                bottom_color = (30, 50, 150)  # Darker blue bottom
                border_color = (150, 180, 255)  # Light blue border
        
        # Draw button background with gradient
        height = rect.height
        for y in range(height):
            # Calculate gradient color for this row
            progress = y / height
            current_color = (
                int(top_color[0] * (1 - progress) + bottom_color[0] * progress),
                int(top_color[1] * (1 - progress) + bottom_color[1] * progress),
                int(top_color[2] * (1 - progress) + bottom_color[2] * progress)
            )
            
            # Draw a horizontal line for this part of the gradient
            pygame.draw.line(
                surface, 
                current_color, 
                (rect.left, rect.top + y), 
                (rect.right - 1, rect.top + y)
            )
        
        # Draw button border
        pygame.draw.rect(surface, border_color, rect, width=2, border_radius=10)
        
        # Add slight 3D effect
        pygame.draw.line(surface, border_color, rect.topleft, rect.topright, width=2)
        pygame.draw.line(surface, border_color, rect.topleft, rect.bottomleft, width=2)
        
        if hover:
            # Add highlight effect on hover
            highlight_rect = pygame.Rect(rect.left + 2, rect.top + 2, rect.width - 4, 5)
            
            if is_start_button:
                highlight_color = (170, 255, 200)
            else:
                highlight_color = (170, 200, 255)
            
            pygame.draw.rect(surface, highlight_color, highlight_rect, border_radius=5)
        
        # Button text with shadow
        shadow_surf = font.render(text, True, (0, 0, 0))
        text_surf = font.render(text, True, color)
        
        # Position text
        if is_start_button:
            # Calculate icon and text positioning to avoid overlap
            icon_size = 10  # Smaller icon size
            left_padding = 40  # Additional left padding
            right_padding = 40  # Additional right padding
            
            # Total icon width including the triangle part
            icon_total_width = icon_size * 1.5
            
            # Calculate text width for centering
            text_width = text_surf.get_width()
            
            # Calculate available space for text and icon with proper padding
            available_width = rect.width - (left_padding + right_padding)
            
            # Space between text and icon
            text_icon_spacing = 15
            
            # Calculate positions ensuring the icon doesn't get too close to the right edge
            # Center the text and icon combination in the available space
            total_content_width = text_width + text_icon_spacing + icon_total_width
            content_start_x = rect.left + left_padding + (available_width - total_content_width) // 2
            
            # Position text
            text_x = content_start_x
            shadow_rect = shadow_surf.get_rect()
            text_rect = text_surf.get_rect()
            
            shadow_rect.topleft = (text_x + 2, rect.centery - shadow_rect.height // 2 + 2)
            text_rect.topleft = (text_x, rect.centery - text_rect.height // 2)
            
            # Position icon with proper spacing after text
            icon_x = text_x + text_width + text_icon_spacing
            icon_y = rect.centery
            
            # Draw play icon (triangle)
            play_icon_points = [
                (icon_x, icon_y - icon_size),
                (icon_x, icon_y + icon_size),
                (icon_x + icon_size * 1.5, icon_y)
            ]
            
            # Shadow for play icon
            pygame.draw.polygon(surface, (0, 0, 0), [
                (p[0] + 2, p[1] + 2) for p in play_icon_points
            ])
            
            # Play icon
            pygame.draw.polygon(surface, (255, 255, 255), play_icon_points)
        else:
            shadow_rect = shadow_surf.get_rect(center=(rect.centerx + 2, rect.centery + 2))
            text_rect = text_surf.get_rect(center=rect.center)
        
        # Draw text shadow and text
        surface.blit(shadow_surf, shadow_rect)
        surface.blit(text_surf, text_rect)
    
    def draw_progress_bar(self, surface, value, max_value, rect, color, bg_color=(50, 50, 50), border_color=(200, 200, 200)):
        """Draw a progress bar (health, etc.)."""
        # Background
        pygame.draw.rect(surface, bg_color, rect, border_radius=3)
        
        # Progress bar (clamp value between 0 and max_value)
        fill_width = int((max(0, min(value, max_value)) / max_value) * rect.width)
        if fill_width > 0:
            fill_rect = pygame.Rect(rect.x, rect.y, fill_width, rect.height)
            pygame.draw.rect(surface, color, fill_rect, border_radius=3)
        
        # Border
        pygame.draw.rect(surface, border_color, rect, width=1, border_radius=3)
    
    def draw_main_menu(self, surface):
        """Draw the main menu screen and return the start button rect."""
        self.update_particles(0.016)  # Assume ~60 FPS
        
        # Fill background with very dark blue for better contrast
        surface.fill((5, 10, 20))
        
        # Draw background stars
        for particle in self.star_particles:
            pygame.draw.circle(
                surface,
                particle['color'],
                (int(particle['x']), int(particle['y'])),
                particle['size']
            )
        
        # Draw game title with enhanced glow
        title_text = "DUNGEON EXPLORER"
        title_pos = (self.screen_width // 2, self.screen_height // 4)
        
        # Create a clean glow effect with a single layer
        glow_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        glow_color = (0, 191, 255, 50 + int(20 * math.sin(self.title_glow * 5)))
        glow_font = pygame.font.Font(None, 72)  # Slightly larger font for glow
        glow_text = glow_font.render(title_text, True, glow_color)
        glow_rect = glow_text.get_rect(center=(title_pos[0], title_pos[1]))
        
        # Apply more controlled blur effect
        blur_offset = 3
        for dx in range(-blur_offset, blur_offset + 1):
            for dy in range(-blur_offset, blur_offset + 1):
                # Skip center to avoid double rendering
                if dx == 0 and dy == 0:
                    continue
                    
                # Calculate distance from center for fade effect
                distance = math.sqrt(dx*dx + dy*dy)
                alpha_factor = 1.0 - (distance / (blur_offset + 1))
                
                # Only draw if the alpha factor is significant
                if alpha_factor > 0.2:
                    current_glow = glow_text.copy()
                    current_glow.set_alpha(int(glow_color[3] * alpha_factor))
                    offset_rect = glow_rect.copy()
                    offset_rect.x += dx * 2
                    offset_rect.y += dy * 2
                    glow_surface.blit(current_glow, offset_rect)
                
        surface.blit(glow_surface, (0, 0))
        
        # Draw a clean, strong black outline for the title
        outline_color = (0, 0, 0)
        outline_positions = [
            (-3, -3), (0, -3), (3, -3),
            (-3, 0), (3, 0),
            (-3, 3), (0, 3), (3, 3)
        ]
        
        title_font = self.font_large
        for dx, dy in outline_positions:
            outline_surf = title_font.render(title_text, True, outline_color)
            outline_rect = outline_surf.get_rect(center=(title_pos[0] + dx, title_pos[1] + dy))
            surface.blit(outline_surf, outline_rect)
        
        # Draw main title text with a bright, easy-to-read color
        title_surf = title_font.render(title_text, True, (60, 230, 255))  # Bright cyan blue
        title_rect = title_surf.get_rect(center=title_pos)
        surface.blit(title_surf, title_rect)
        
        # Draw subtitle
        subtitle_text = "A Procedurally Generated Adventure"
        subtitle_pos = (self.screen_width // 2, self.screen_height // 4 + 60)
        self.draw_text_with_shadow(
            surface,
            subtitle_text,
            self.font_small,
            (200, 200, 255),
            subtitle_pos,
            shadow_offset=2
        )
        
        # Draw larger start button with additional padding
        button_width = 280  # Increased from 240 to add padding
        start_button_rect = pygame.Rect(
            self.screen_width // 2 - button_width // 2,
            self.screen_height // 2,
            button_width,
            60
        )
        
        # Check if mouse is hovering over button
        mouse_pos = pygame.mouse.get_pos()
        start_hover = start_button_rect.collidepoint(mouse_pos)
        
        self.draw_button(
            surface,
            "START GAME",
            self.font_medium,
            (255, 255, 255),
            start_button_rect,
            hover=start_hover,
            is_start_button=True
        )
        
        # Draw controls
        controls_text = "Controls: WASD or Arrow Keys to move, SPACE to attack"
        controls_pos = (self.screen_width // 2, self.screen_height - 100)
        self.draw_text_with_shadow(
            surface,
            controls_text,
            self.font_tiny,
            (180, 180, 180),
            controls_pos
        )
        
        # Draw footer
        footer_text = "Created with Pygame - No External Assets"
        footer_pos = (self.screen_width // 2, self.screen_height - 50)
        self.draw_text_with_shadow(
            surface,
            footer_text,
            self.font_tiny,
            (100, 100, 100),
            footer_pos
        )
        
        return start_button_rect
    
    def draw_game_ui(self, surface, player, current_level):
        """Draw the in-game user interface."""
        # Draw health bar
        health_bar_rect = pygame.Rect(20, 20, 200, 20)
        self.draw_progress_bar(surface, player.health, player.max_health, health_bar_rect, (255, 0, 0))
        
        # Draw health text
        health_text = f"{int(player.health)}/{player.max_health} HP"
        self.draw_text_with_shadow(surface, health_text, self.font_tiny, (255, 255, 255), (health_bar_rect.centerx, health_bar_rect.centery))
        
        # Draw score
        score_text = f"Score: {player.score}"
        self.draw_text_with_shadow(surface, score_text, self.font_small, (255, 255, 255), (self.screen_width - 100, 30))
        
        # Draw current level
        level_text = f"Level {current_level}"
        self.draw_text_with_shadow(surface, level_text, self.font_small, (255, 255, 255), (self.screen_width // 2, 30))
        
        # Draw stats
        stats_x = 20
        stats_y = 60
        
        # Attack power
        attack_text = f"Attack: {player.attack_power}"
        self.draw_text_with_shadow(surface, attack_text, self.font_tiny, (255, 165, 0), (stats_x + 50, stats_y))
        
        # Speed
        speed_text = f"Speed: {int(player.speed)}"
        self.draw_text_with_shadow(surface, speed_text, self.font_tiny, (255, 255, 0), (stats_x + 50, stats_y + 25))
        
        # Draw item indicators (last 3 collected)
        if player.items:
            item_text = "Recent Items: "
            self.draw_text_with_shadow(surface, item_text, self.font_tiny, (255, 255, 255), (self.screen_width - 250, 70))
            
            for i, item in enumerate(player.items[-3:]):
                if item == 'health':
                    color = (255, 0, 0)
                    icon = "♥"
                elif item == 'speed':
                    color = (255, 255, 0)
                    icon = "→"
                elif item == 'damage':
                    color = (255, 165, 0)
                    icon = "⚔"
                    
                self.draw_text_with_shadow(surface, icon, self.font_small, color, (self.screen_width - 150 + i * 30, 70))
    
    def draw_game_over(self, surface, score):
        """Draw the game over screen and return the retry button rect."""
        self.update_particles(0.016)  # Assume 60 FPS for animation
        
        # Draw dark overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        surface.blit(overlay, (0, 0))
        
        # Draw star particles for background
        for p in self.star_particles:
            # Twinkle effect
            twinkle = (math.sin(pygame.time.get_ticks() * 0.001 * p['twinkle_speed'] + p['twinkle_offset']) + 1) / 2
            size = p['size'] * (0.7 + 0.3 * twinkle)
            
            alpha = int(150 + 105 * twinkle)
            color = p['color'] + (alpha,)
            
            # Create a small surface for the star with alpha
            star_surf = pygame.Surface((int(size * 2), int(size * 2)), pygame.SRCALPHA)
            pygame.draw.circle(star_surf, color, (int(size), int(size)), size)
            
            surface.blit(star_surf, (p['x'] - size, p['y'] - size))
        
        # Draw game over text
        game_over_text = "GAME OVER"
        game_over_pos = (self.screen_width // 2, self.screen_height // 3)
        self.draw_text_with_shadow(
            surface,
            game_over_text,
            self.font_large,
            (255, 0, 0),
            game_over_pos
        )
        
        # Draw score
        score_text = f"Final Score: {score}"
        score_pos = (self.screen_width // 2, self.screen_height // 3 + 70)
        self.draw_text_with_shadow(
            surface,
            score_text,
            self.font_medium,
            (255, 255, 255),
            score_pos
        )
        
        # Draw retry button
        retry_button_rect = pygame.Rect(
            self.screen_width // 2 - 100,
            self.screen_height // 2 + 50,
            200,
            50
        )
        
        # Check if mouse is hovering over button
        mouse_pos = pygame.mouse.get_pos()
        retry_hover = retry_button_rect.collidepoint(mouse_pos)
        
        self.draw_button(
            surface,
            "RETRY",
            self.font_medium,
            (255, 255, 255),
            retry_button_rect,
            hover=retry_hover
        )
        
        # Draw message
        message_text = "Better luck next time! Try collecting more power-ups."
        message_pos = (self.screen_width // 2, self.screen_height // 2 + 150)
        self.draw_text_with_shadow(
            surface,
            message_text,
            self.font_small,
            (200, 200, 200),
            message_pos
        )
        
        return retry_button_rect
    
    def draw_victory(self, surface, score):
        """Draw the victory screen and return the exit button rect."""
        self.update_particles(0.016)  # Assume 60 FPS for animation
        
        # Draw dark overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))
        
        # Draw star particles for background
        for p in self.star_particles:
            # Twinkle effect
            twinkle = (math.sin(pygame.time.get_ticks() * 0.001 * p['twinkle_speed'] + p['twinkle_offset']) + 1) / 2
            size = p['size'] * (0.7 + 0.3 * twinkle)
            
            alpha = int(150 + 105 * twinkle)
            color = p['color'] + (alpha,)
            
            # Create a small surface for the star with alpha
            star_surf = pygame.Surface((int(size * 2), int(size * 2)), pygame.SRCALPHA)
            pygame.draw.circle(star_surf, color, (int(size), int(size)), size)
            
            surface.blit(star_surf, (p['x'] - size, p['y'] - size))
        
        # Create firework particles
        if random.random() < 0.05:  # 5% chance each frame
            # Random position near the top of the screen
            x = random.randint(100, self.screen_width - 100)
            y = random.randint(100, self.screen_height - 200)
            
            # Random color
            r = random.randint(150, 255)
            g = random.randint(150, 255)
            b = random.randint(150, 255)
            color = (r, g, b)
            
            # Create explosion
            for _ in range(50):
                angle = random.uniform(0, math.pi * 2)
                speed = random.uniform(50, 150)
                lifetime = random.uniform(0.5, 1.5)
                
                particle = {
                    'x': x,
                    'y': y,
                    'vx': math.cos(angle) * speed,
                    'vy': math.sin(angle) * speed,
                    'timer': lifetime,
                    'max_timer': lifetime,
                    'color': color,
                    'gravity': 50
                }
                
                self.particles.append(particle)
        
        # Update and draw firework particles
        for particle in self.particles[:]:
            particle['timer'] -= 0.016  # Assume 60 FPS
            
            if particle['timer'] <= 0:
                self.particles.remove(particle)
            else:
                # Update position with gravity
                particle['x'] += particle['vx'] * 0.016
                particle['y'] += particle['vy'] * 0.016
                particle['vy'] += particle['gravity'] * 0.016
                
                # Draw particle
                alpha = int(255 * (particle['timer'] / particle['max_timer']))
                size = 2 * (particle['timer'] / particle['max_timer'])
                
                pygame.draw.circle(
                    surface,
                    particle['color'] + (alpha,),
                    (int(particle['x']), int(particle['y'])),
                    int(size)
                )
        
        # Draw victory text
        victory_text = "VICTORY!"
        victory_pos = (self.screen_width // 2, self.screen_height // 3)
        self.draw_text_with_shadow(
            surface,
            victory_text,
            self.font_large,
            (255, 215, 0),  # Gold
            victory_pos
        )
        
        # Draw score
        score_text = f"Final Score: {score}"
        score_pos = (self.screen_width // 2, self.screen_height // 3 + 70)
        self.draw_text_with_shadow(
            surface,
            score_text,
            self.font_medium,
            (255, 255, 255),
            score_pos
        )
        
        # Draw congratulations
        congrats_text = "You have conquered all the dungeons!"
        congrats_pos = (self.screen_width // 2, self.screen_height // 2)
        self.draw_text_with_shadow(
            surface,
            congrats_text,
            self.font_medium,
            (255, 255, 255),
            congrats_pos
        )
        
        # Draw exit button
        exit_button_rect = pygame.Rect(
            self.screen_width // 2 - 100,
            self.screen_height // 2 + 100,
            200,
            50
        )
        
        # Check if mouse is hovering over button
        mouse_pos = pygame.mouse.get_pos()
        exit_hover = exit_button_rect.collidepoint(mouse_pos)
        
        self.draw_button(
            surface,
            "EXIT",
            self.font_medium,
            (255, 255, 255),
            exit_button_rect,
            hover=exit_hover
        )
        
        # Draw credits
        credits_text = "Thanks for playing!"
        credits_pos = (self.screen_width // 2, self.screen_height - 50)
        self.draw_text_with_shadow(
            surface,
            credits_text,
            self.font_small,
            (200, 200, 200),
            credits_pos
        )
        
        return exit_button_rect 