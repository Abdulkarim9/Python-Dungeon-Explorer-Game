import pygame
import math
import random

class Player:
    def __init__(self, x, y, size):
        self.rect = pygame.Rect(x, y, size, size)
        self.size = size
        self.color = (0, 191, 255)  # Deep Sky Blue
        self.speed = 200  # pixels per second
        self.health = 100
        self.max_health = 100
        self.attack_power = 20
        self.attack_cooldown = 0.3  # seconds
        self.attack_timer = 0
        self.is_attacking = False
        self.attack_range = size * 1.5
        self.attack_angle = 0  # direction of attack in radians
        self.invulnerable_timer = 0
        self.invulnerable_duration = 1.0  # seconds
        self.score = 0
        self.items = []
        
        # Animation parameters
        self.anim_frame = 0
        self.anim_timer = 0
        self.anim_speed = 0.1  # seconds per frame
        self.direction = 0  # 0: right, 1: down, 2: left, 3: up
        self.moving = False
        
        # Particle system for attacks
        self.particles = []
        
    def update(self, dt, level_map, enemies, items, sound_gen):
        old_x, old_y = self.rect.x, self.rect.y
        
        # Process movement
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= self.speed * dt
            self.direction = 2
            self.moving = True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += self.speed * dt
            self.direction = 0
            self.moving = True
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= self.speed * dt
            self.direction = 3
            self.moving = True
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += self.speed * dt
            self.direction = 1
            self.moving = True
            
        if dx == 0 and dy == 0:
            self.moving = False
        
        # Update position
        self.rect.x += dx
        self.rect.y += dy
        
        # Check for collisions with walls
        tile_size = self.size
        
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
            
        # Process attack
        self.attack_timer -= dt
        if self.attack_timer <= 0:
            if keys[pygame.K_SPACE]:
                self.attack(enemies, sound_gen)
                self.attack_timer = self.attack_cooldown
                
        # Update invulnerability timer
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= dt
            
        # Collect items
        for item in items:
            if not item.collected and self.rect.colliderect(item.rect):
                item.collect(self)
                sound_gen.play_sound('pickup')
                
        # Update attack particles
        for particle in self.particles[:]:
            particle['timer'] -= dt
            if particle['timer'] <= 0:
                self.particles.remove(particle)
                
        # Update animation
        if self.moving:
            self.anim_timer += dt
            if self.anim_timer >= self.anim_speed:
                self.anim_timer = 0
                self.anim_frame = (self.anim_frame + 1) % 4
                
    def attack(self, enemies, sound_gen):
        self.is_attacking = True
        sound_gen.play_sound('attack')
        
        # Calculate attack direction based on player direction
        angle_offset = 0
        if self.direction == 0:  # right
            angle_offset = 0
        elif self.direction == 1:  # down
            angle_offset = math.pi / 2
        elif self.direction == 2:  # left
            angle_offset = math.pi
        elif self.direction == 3:  # up
            angle_offset = -math.pi / 2
            
        # Check for enemies in range
        player_center = self.rect.center
        for enemy in enemies:
            enemy_center = enemy.rect.center
            dx = enemy_center[0] - player_center[0]
            dy = enemy_center[1] - player_center[1]
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance <= self.attack_range:
                # Calculate angle to enemy
                angle_to_enemy = math.atan2(dy, dx)
                angle_diff = abs(angle_to_enemy - angle_offset)
                # Normalize angle difference to [0, pi]
                angle_diff = min(angle_diff, 2 * math.pi - angle_diff)
                
                # Check if enemy is in attack cone (60 degrees)
                if angle_diff <= math.pi / 3:
                    enemy.take_damage(self.attack_power)
                    
        # Create attack particles
        for _ in range(10):
            angle = angle_offset + random.uniform(-math.pi/6, math.pi/6)
            speed = random.uniform(100, 200)
            lifetime = random.uniform(0.2, 0.5)
            
            particle = {
                'x': player_center[0],
                'y': player_center[1],
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'timer': lifetime,
                'max_timer': lifetime,
                'color': (255, 255, 0)  # Yellow
            }
            
            self.particles.append(particle)
            
    def take_damage(self, amount, sound_gen=None):
        if self.invulnerable_timer <= 0:
            self.health -= amount
            self.invulnerable_timer = self.invulnerable_duration
            if sound_gen:
                sound_gen.play_sound('hit')
                
    def draw(self, surface, rect):
        # Draw player character
        player_color = self.color
        if self.invulnerable_timer > 0 and int(pygame.time.get_ticks() / 100) % 2 == 0:
            player_color = (255, 255, 255)  # Flash white when invulnerable
            
        # Base character shape
        pygame.draw.circle(surface, player_color, rect.center, self.size // 2)
        
        # Draw eyes based on direction
        eye_size = self.size // 8
        eye_offset_x = self.size // 4
        eye_offset_y = self.size // 6
        
        if self.direction == 0:  # Right
            left_eye_pos = (rect.centerx + eye_offset_x, rect.centery - eye_offset_y)
            right_eye_pos = (rect.centerx + eye_offset_x, rect.centery + eye_offset_y)
        elif self.direction == 1:  # Down
            left_eye_pos = (rect.centerx - eye_offset_y, rect.centery + eye_offset_x)
            right_eye_pos = (rect.centerx + eye_offset_y, rect.centery + eye_offset_x)
        elif self.direction == 2:  # Left
            left_eye_pos = (rect.centerx - eye_offset_x, rect.centery - eye_offset_y)
            right_eye_pos = (rect.centerx - eye_offset_x, rect.centery + eye_offset_y)
        else:  # Up
            left_eye_pos = (rect.centerx - eye_offset_y, rect.centery - eye_offset_x)
            right_eye_pos = (rect.centerx + eye_offset_y, rect.centery - eye_offset_x)
            
        pygame.draw.circle(surface, (0, 0, 0), left_eye_pos, eye_size)
        pygame.draw.circle(surface, (0, 0, 0), right_eye_pos, eye_size)
        
        # Draw mouth based on direction and animation frame
        mouth_offset = self.size // 3
        mouth_width = self.size // 4
        mouth_height = self.size // 8
        
        if self.moving:
            mouth_height = int(mouth_height * (1 + 0.5 * math.sin(self.anim_frame * math.pi / 2)))
            
        if self.direction == 0:  # Right
            mouth_rect = pygame.Rect(
                rect.centerx + mouth_offset - mouth_width // 2,
                rect.centery - mouth_height // 2,
                mouth_width,
                mouth_height
            )
        elif self.direction == 1:  # Down
            mouth_rect = pygame.Rect(
                rect.centerx - mouth_width // 2,
                rect.centery + mouth_offset - mouth_height // 2,
                mouth_width,
                mouth_height
            )
        elif self.direction == 2:  # Left
            mouth_rect = pygame.Rect(
                rect.centerx - mouth_offset - mouth_width // 2,
                rect.centery - mouth_height // 2,
                mouth_width,
                mouth_height
            )
        else:  # Up
            mouth_rect = pygame.Rect(
                rect.centerx - mouth_width // 2,
                rect.centery - mouth_offset - mouth_height // 2,
                mouth_width,
                mouth_height
            )
            
        pygame.draw.rect(surface, (0, 0, 0), mouth_rect)
        
        # Draw attack particles
        for particle in self.particles:
            alpha = int(255 * (particle['timer'] / particle['max_timer']))
            color = particle['color'] + (alpha,)
            pos = (
                int(particle['x'] - self.rect.x + rect.x),
                int(particle['y'] - self.rect.y + rect.y)
            )
            
            size = int(5 * (particle['timer'] / particle['max_timer']))
            pygame.draw.circle(surface, color[:3], pos, size)
            
        # Draw attack indicator when attacking
        if self.is_attacking:
            attack_rect = pygame.Rect(
                rect.centerx - self.attack_range,
                rect.centery - self.attack_range,
                self.attack_range * 2,
                self.attack_range * 2
            )
            
            # Draw attack arc
            start_angle = -math.pi / 6 + (self.direction * math.pi / 2)
            end_angle = math.pi / 6 + (self.direction * math.pi / 2)
            
            points = [rect.center]
            for angle in [start_angle, (start_angle + end_angle) / 2, end_angle]:
                x = rect.centerx + math.cos(angle) * self.attack_range
                y = rect.centery + math.sin(angle) * self.attack_range
                points.append((x, y))
                
            pygame.draw.polygon(surface, (255, 255, 0, 128), points)
            
            # Reset attack flag
            self.is_attacking = False 