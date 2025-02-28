import pygame
import random
import math
import noise

class Enemy:
    def __init__(self, x, y, size, enemy_type):
        self.rect = pygame.Rect(x, y, size, size)
        self.size = size
        self.enemy_type = enemy_type
        self.speed = 0
        self.health = 0
        self.damage = 0
        self.attack_range = 0
        self.detection_range = 0
        self.color = (0, 0, 0)
        self.anim_frame = 0
        self.anim_timer = 0
        self.anim_speed = 0
        self.direction = random.randint(0, 3)  # 0: right, 1: down, 2: left, 3: up
        self.state = 'idle'  # idle, chase, attack
        self.target = None
        self.move_timer = 0
        self.particles = []
        self.hit_flash_timer = 0
        
        # Set properties based on enemy type
        if enemy_type == 'slime':
            self.speed = 80
            self.health = 30
            self.damage = 10
            self.attack_range = size
            self.detection_range = size * 5
            self.color = (0, 255, 0)  # Green
            self.anim_speed = 0.15
        elif enemy_type == 'ghost':
            self.speed = 120
            self.health = 20
            self.damage = 15
            self.attack_range = size * 1.5
            self.detection_range = size * 7
            self.color = (200, 200, 255)  # Light blue
            self.anim_speed = 0.1
        elif enemy_type == 'spider':
            self.speed = 150
            self.health = 15
            self.damage = 20
            self.attack_range = size
            self.detection_range = size * 6
            self.color = (128, 0, 128)  # Purple
            self.anim_speed = 0.05
        
    def update(self, dt, level_map, player, enemies, sound_gen):
        # Reset movement
        old_x, old_y = self.rect.x, self.rect.y
        
        # Update animation
        self.anim_timer += dt
        if self.anim_timer >= self.anim_speed:
            self.anim_timer = 0
            self.anim_frame = (self.anim_frame + 1) % 4
        
        # Update hit flash timer
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= dt
        
        # Update particles
        for particle in self.particles[:]:
            particle['timer'] -= dt
            if particle['timer'] <= 0:
                self.particles.remove(particle)
            else:
                particle['x'] += particle['vx'] * dt
                particle['y'] += particle['vy'] * dt
        
        # Calculate distance to player
        player_center = player.rect.center
        enemy_center = self.rect.center
        dx = player_center[0] - enemy_center[0]
        dy = player_center[1] - enemy_center[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Determine AI state
        if distance <= self.attack_range:
            self.state = 'attack'
        elif distance <= self.detection_range:
            self.state = 'chase'
        else:
            self.state = 'idle'
        
        # Execute AI behavior based on state
        if self.state == 'idle':
            self._idle_behavior(dt, level_map)
        elif self.state == 'chase':
            self._chase_behavior(dt, level_map, player_center)
        elif self.state == 'attack':
            self._attack_behavior(dt, player, sound_gen)
        
        # Check for collision with walls
        tile_size = self.size
        
        if self.enemy_type != 'ghost':  # Ghosts can move through walls
            # Calculate grid position
            grid_x1 = max(0, int(self.rect.left // tile_size))
            grid_y1 = max(0, int(self.rect.top // tile_size))
            grid_x2 = min(len(level_map[0]) - 1, int(self.rect.right // tile_size))
            grid_y2 = min(len(level_map) - 1, int(self.rect.bottom // tile_size))
            
            # Check collision with walls
            collision = False
            for y in range(grid_y1, grid_y2 + 1):
                for x in range(grid_x1, grid_x2 + 1):
                    if y < len(level_map) and x < len(level_map[0]):
                        if level_map[y][x] == 1:  # Wall
                            wall_rect = pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size)
                            if self.rect.colliderect(wall_rect):
                                collision = True
                                break
                if collision:
                    break
            
            if collision:
                self.rect.x, self.rect.y = old_x, old_y
                self.direction = random.randint(0, 3)  # Change direction when hitting a wall
    
    def _idle_behavior(self, dt, level_map):
        """Random wandering behavior."""
        self.move_timer -= dt
        
        if self.move_timer <= 0:
            # Randomly change direction
            self.direction = random.randint(0, 3)
            self.move_timer = random.uniform(1.0, 3.0)  # Random movement duration
        
        # Move based on direction
        if self.direction == 0:  # Right
            self.rect.x += self.speed * dt * 0.5  # Move slower when idle
        elif self.direction == 1:  # Down
            self.rect.y += self.speed * dt * 0.5
        elif self.direction == 2:  # Left
            self.rect.x -= self.speed * dt * 0.5
        elif self.direction == 3:  # Up
            self.rect.y -= self.speed * dt * 0.5
    
    def _chase_behavior(self, dt, level_map, player_pos):
        """Chase the player."""
        # Calculate direction to player
        dx = player_pos[0] - self.rect.centerx
        dy = player_pos[1] - self.rect.centery
        
        # Normalize direction
        length = math.sqrt(dx*dx + dy*dy)
        if length > 0:
            dx /= length
            dy /= length
        
        # Set direction based on movement
        if abs(dx) > abs(dy):
            self.direction = 0 if dx > 0 else 2  # Right or Left
        else:
            self.direction = 1 if dy > 0 else 3  # Down or Up
        
        # Move towards player
        self.rect.x += dx * self.speed * dt
        self.rect.y += dy * self.speed * dt
    
    def _attack_behavior(self, dt, player, sound_gen):
        """Attack the player."""
        # Only attack on certain animation frames to avoid constant damage
        if self.anim_frame == 1:
            player.take_damage(self.damage, sound_gen)
            
            # Create attack particles
            player_center = player.rect.center
            enemy_center = self.rect.center
            
            for _ in range(5):
                angle = math.atan2(
                    player_center[1] - enemy_center[1],
                    player_center[0] - enemy_center[0]
                ) + random.uniform(-0.5, 0.5)
                
                speed = random.uniform(50, 150)
                lifetime = random.uniform(0.2, 0.5)
                
                particle = {
                    'x': enemy_center[0],
                    'y': enemy_center[1],
                    'vx': math.cos(angle) * speed,
                    'vy': math.sin(angle) * speed,
                    'timer': lifetime,
                    'max_timer': lifetime,
                    'color': self.color
                }
                
                self.particles.append(particle)
    
    def take_damage(self, amount):
        """Take damage and create visual effect."""
        self.health -= amount
        self.hit_flash_timer = 0.1  # Flash for 0.1 seconds
        
        # Create damage particles
        enemy_center = self.rect.center
        
        for _ in range(10):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 150)
            lifetime = random.uniform(0.3, 0.7)
            
            particle = {
                'x': enemy_center[0],
                'y': enemy_center[1],
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'timer': lifetime,
                'max_timer': lifetime,
                'color': (255, 0, 0)  # Red for damage
            }
            
            self.particles.append(particle)
    
    def draw(self, surface, rect):
        """Draw the enemy."""
        # Determine drawing color (flash white when hit)
        color = (255, 255, 255) if self.hit_flash_timer > 0 else self.color
        
        # Draw based on enemy type
        if self.enemy_type == 'slime':
            self._draw_slime(surface, rect, color)
        elif self.enemy_type == 'ghost':
            self._draw_ghost(surface, rect, color)
        elif self.enemy_type == 'spider':
            self._draw_spider(surface, rect, color)
            
        # Draw particles
        for particle in self.particles:
            alpha = int(255 * (particle['timer'] / particle['max_timer']))
            particle_color = particle['color']
            
            # Calculate position adjusted for camera
            pos = (
                int(particle['x'] - self.rect.x + rect.x),
                int(particle['y'] - self.rect.y + rect.y)
            )
            
            size = int(4 * (particle['timer'] / particle['max_timer']))
            pygame.draw.circle(surface, particle_color, pos, size)
    
    def _draw_slime(self, surface, rect, color):
        """Draw a slime enemy."""
        # Draw body
        height = int(self.size * (0.7 + 0.3 * math.sin(self.anim_frame * math.pi / 2)))
        body_rect = pygame.Rect(
            rect.x, 
            rect.y + (self.size - height),
            self.size,
            height
        )
        
        # Draw slime body
        pygame.draw.ellipse(surface, color, body_rect)
        
        # Draw eyes
        eye_size = self.size // 8
        eye_offset = self.size // 4
        left_eye_pos = (rect.centerx - eye_offset, rect.centery - eye_size)
        right_eye_pos = (rect.centerx + eye_offset, rect.centery - eye_size)
        
        pygame.draw.circle(surface, (0, 0, 0), left_eye_pos, eye_size)
        pygame.draw.circle(surface, (0, 0, 0), right_eye_pos, eye_size)
    
    def _draw_ghost(self, surface, rect, color):
        """Draw a ghost enemy."""
        # Draw body
        body_rect = pygame.Rect(rect.x, rect.y, self.size, self.size)
        
        # Make the ghost float up and down
        offset = int(4 * math.sin(self.anim_frame * math.pi / 2))
        body_rect.y += offset
        
        # Draw ghost body (upper circle)
        pygame.draw.circle(surface, color, (rect.centerx, rect.centery + offset), self.size // 2)
        
        # Draw ghost "tail" (wavy bottom)
        tail_height = self.size // 2
        points = []
        wave_segments = 3
        
        for i in range(wave_segments + 1):
            x = rect.x + (i * self.size) // wave_segments
            y = rect.centery + offset + tail_height // 2
            
            # Add wave to bottom edge
            if i % 2 == 0:
                y += tail_height // 4
                
            points.append((x, y))
        
        # Connect top corners
        points.insert(0, (rect.x, rect.centery + offset))
        points.append((rect.right, rect.centery + offset))
        
        pygame.draw.polygon(surface, color, points)
        
        # Draw eyes
        eye_size = self.size // 8
        eye_offset = self.size // 5
        left_eye_pos = (rect.centerx - eye_offset, rect.centery - eye_offset // 2 + offset)
        right_eye_pos = (rect.centerx + eye_offset, rect.centery - eye_offset // 2 + offset)
        
        pygame.draw.circle(surface, (0, 0, 0), left_eye_pos, eye_size)
        pygame.draw.circle(surface, (0, 0, 0), right_eye_pos, eye_size)
    
    def _draw_spider(self, surface, rect, color):
        """Draw a spider enemy."""
        # Draw body (two circles for head and abdomen)
        head_radius = self.size // 4
        body_radius = self.size // 3
        
        head_pos = (rect.centerx, rect.centery - head_radius // 2)
        body_pos = (rect.centerx, rect.centery + body_radius // 2)
        
        # Draw legs
        leg_count = 4
        leg_length = self.size // 2
        
        for i in range(leg_count):
            angle1 = math.pi * 0.2 + (math.pi * 0.8 * i / (leg_count - 1)) + math.sin(self.anim_frame * math.pi / 2) * 0.1
            angle2 = math.pi * 1.2 + (math.pi * 0.8 * i / (leg_count - 1)) + math.sin(self.anim_frame * math.pi / 2) * 0.1
            
            # Left leg
            start_x, start_y = head_pos
            end_x = start_x - leg_length * math.cos(angle1)
            end_y = start_y - leg_length * math.sin(angle1)
            pygame.draw.line(surface, color, (start_x, start_y), (end_x, end_y), 2)
            
            # Right leg
            start_x, start_y = head_pos
            end_x = start_x + leg_length * math.cos(angle2)
            end_y = start_y - leg_length * math.sin(angle2)
            pygame.draw.line(surface, color, (start_x, start_y), (end_x, end_y), 2)
        
        # Draw body parts
        pygame.draw.circle(surface, color, body_pos, body_radius)
        pygame.draw.circle(surface, color, head_pos, head_radius)
        
        # Draw eyes
        eye_size = self.size // 10
        eye_offset = self.size // 8
        left_eye_pos = (head_pos[0] - eye_offset, head_pos[1] - eye_offset // 2)
        right_eye_pos = (head_pos[0] + eye_offset, head_pos[1] - eye_offset // 2)
        
        pygame.draw.circle(surface, (255, 0, 0), left_eye_pos, eye_size)
        pygame.draw.circle(surface, (255, 0, 0), right_eye_pos, eye_size) 