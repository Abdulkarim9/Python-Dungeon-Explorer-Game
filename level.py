import pygame
import random
import noise
import math
from collections import deque

class DungeonGenerator:
    def __init__(self, width, height, tile_size):
        self.width = width
        self.height = height
        self.tile_size = tile_size
        self.map = [[0 for _ in range(width)] for _ in range(height)]
        
    def generate_dungeon(self):
        """Generate a dungeon using cellular automata."""
        # Initialize with random noise
        self._initialize_random(0.45)
        
        # Apply cellular automata iterations
        for _ in range(5):
            self._apply_cellular_automata()
            
        # Ensure map borders are walls
        self._add_border_walls()
        
        # Find and connect disconnected regions
        self._connect_regions()
        
        # Identify rooms
        rooms = self._identify_rooms()
        
        # Ensure at least one room exists
        if not rooms:
            return self.generate_dungeon()  # Try again
            
        # Place player start location in the first room
        start_pos = self._find_valid_position(rooms[0])
        
        # Place level exit in the last room
        exit_pos = self._find_valid_position(rooms[-1])
        
        # Convert map to a format for rendering (1 = wall, 2 = floor)
        level_map = [[0 for _ in range(self.width)] for _ in range(self.height)]
        for y in range(self.height):
            for x in range(self.width):
                if self.map[y][x] == 1:  # Wall
                    level_map[y][x] = 1
                elif self.map[y][x] == 0:  # Floor
                    level_map[y][x] = 2
                    
        return level_map, (start_pos[0] * self.tile_size, start_pos[1] * self.tile_size), (exit_pos[0] * self.tile_size, exit_pos[1] * self.tile_size)
    
    def _initialize_random(self, wall_chance):
        """Initialize map with random noise."""
        seed = random.randint(0, 10000)
        for y in range(self.height):
            for x in range(self.width):
                # Use Perlin noise for a more natural pattern
                if noise.pnoise2(x / 10, y / 10, base=seed) > wall_chance:
                    self.map[y][x] = 1  # Wall
                else:
                    self.map[y][x] = 0  # Floor
    
    def _apply_cellular_automata(self):
        """Apply one iteration of cellular automata."""
        new_map = [[0 for _ in range(self.width)] for _ in range(self.height)]
        
        for y in range(self.height):
            for x in range(self.width):
                # Count walls in the 3x3 neighborhood
                wall_count = 0
                for ny in range(max(0, y-1), min(self.height, y+2)):
                    for nx in range(max(0, x-1), min(self.width, x+2)):
                        if self.map[ny][nx] == 1:
                            wall_count += 1
                            
                # Apply cellular automata rules
                if self.map[y][x] == 1:
                    # Wall stays a wall if it has 4 or more wall neighbors
                    new_map[y][x] = 1 if wall_count >= 4 else 0
                else:
                    # Floor becomes a wall if it has 5 or more wall neighbors
                    new_map[y][x] = 1 if wall_count >= 5 else 0
                    
        self.map = new_map
    
    def _add_border_walls(self):
        """Add walls around the border of the map."""
        for x in range(self.width):
            self.map[0][x] = 1
            self.map[self.height-1][x] = 1
            
        for y in range(self.height):
            self.map[y][0] = 1
            self.map[y][self.width-1] = 1
    
    def _identify_rooms(self):
        """Identify separate rooms in the dungeon."""
        visited = [[False for _ in range(self.width)] for _ in range(self.height)]
        rooms = []
        
        for y in range(self.height):
            for x in range(self.width):
                if not visited[y][x] and self.map[y][x] == 0:  # Unvisited floor
                    # Perform a BFS to find all connected floor tiles
                    room = []
                    queue = deque([(x, y)])
                    visited[y][x] = True
                    
                    while queue:
                        cx, cy = queue.popleft()
                        room.append((cx, cy))
                        
                        # Check 4 adjacent tiles
                        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                            nx, ny = cx + dx, cy + dy
                            if (0 <= nx < self.width and 0 <= ny < self.height and 
                                not visited[ny][nx] and self.map[ny][nx] == 0):
                                visited[ny][nx] = True
                                queue.append((nx, ny))
                    
                    if len(room) > 20:  # Only consider rooms larger than 20 tiles
                        rooms.append(room)
        
        return rooms
    
    def _connect_regions(self):
        """Connect disconnected regions of the dungeon."""
        visited = [[False for _ in range(self.width)] for _ in range(self.height)]
        regions = []
        
        # Identify all floor regions
        for y in range(self.height):
            for x in range(self.width):
                if not visited[y][x] and self.map[y][x] == 0:  # Unvisited floor
                    region = []
                    self._flood_fill(x, y, visited, region)
                    regions.append(region)
        
        # Connect regions if there's more than one
        if len(regions) > 1:
            # Sort regions by size (descending)
            regions.sort(key=len, reverse=True)
            
            # Keep the largest region and connect others to it
            main_region = regions[0]
            for other_region in regions[1:]:
                self._connect_two_regions(main_region, other_region)
    
    def _flood_fill(self, x, y, visited, region):
        """Perform a flood fill to identify a connected region using an iterative approach."""
        # Create a queue for the flood fill
        queue = deque([(x, y)])
        
        while queue:
            x, y = queue.popleft()
            
            # Skip if out of bounds or already visited or not a floor
            if (x < 0 or y < 0 or x >= self.width or y >= self.height or 
                visited[y][x] or self.map[y][x] != 0):
                continue
                
            visited[y][x] = True
            region.append((x, y))
            
            # Add adjacent cells to the queue
            queue.append((x+1, y))
            queue.append((x-1, y))
            queue.append((x, y+1))
            queue.append((x, y-1))
    
    def _connect_two_regions(self, region1, region2):
        """Connect two regions with a tunnel."""
        # Find the closest points between the two regions
        min_distance = float('inf')
        closest_pair = None
        
        for x1, y1 in region1:
            for x2, y2 in region2:
                # Manhattan distance
                distance = abs(x2 - x1) + abs(y2 - y1)
                if distance < min_distance:
                    min_distance = distance
                    closest_pair = ((x1, y1), (x2, y2))
        
        if closest_pair:
            self._create_tunnel(closest_pair[0], closest_pair[1])
    
    def _create_tunnel(self, pos1, pos2):
        """Create a tunnel between two positions."""
        x1, y1 = pos1
        x2, y2 = pos2
        
        # Randomly decide if we go horizontal then vertical, or vice versa
        if random.random() < 0.5:
            # Horizontal then vertical
            self._create_horizontal_tunnel(x1, x2, y1)
            self._create_vertical_tunnel(y1, y2, x2)
        else:
            # Vertical then horizontal
            self._create_vertical_tunnel(y1, y2, x1)
            self._create_horizontal_tunnel(x1, x2, y2)
    
    def _create_horizontal_tunnel(self, x1, x2, y):
        """Create a horizontal tunnel."""
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.map[y][x] = 0  # Floor
    
    def _create_vertical_tunnel(self, y1, y2, x):
        """Create a vertical tunnel."""
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.map[y][x] = 0  # Floor
    
    def _find_valid_position(self, room):
        """Find a valid position within a room, away from walls."""
        # Get all floor tiles that are surrounded by floor tiles
        valid_positions = []
        for x, y in room:
            is_valid = True
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if not (0 <= nx < self.width and 0 <= ny < self.height and self.map[ny][nx] == 0):
                    is_valid = False
                    break
            if is_valid:
                valid_positions.append((x, y))
        
        if valid_positions:
            return random.choice(valid_positions)
        return room[0]  # Fallback to first position
    
    def spawn_enemies(self, num_enemies, player):
        """Spawn enemies in random valid locations."""
        from enemy import Enemy
        
        # Identify all rooms
        rooms = self._identify_rooms()
        if not rooms:
            return []
            
        # Get player grid position
        player_grid_x = player.rect.centerx // self.tile_size
        player_grid_y = player.rect.centery // self.tile_size
        
        enemies = []
        for _ in range(num_enemies):
            # Choose a random room
            room = random.choice(rooms)
            
            # Find a position that's not too close to the player
            attempts = 0
            while attempts < 50:  # Limit attempts to avoid infinite loop
                pos = random.choice(room)
                
                # Ensure enemy isn't too close to player
                if ((pos[0] - player_grid_x) ** 2 + (pos[1] - player_grid_y) ** 2) > 25:  # Distance squared > 5^2
                    enemy_type = random.choice(['slime', 'ghost', 'spider'])
                    enemy = Enemy(
                        pos[0] * self.tile_size,
                        pos[1] * self.tile_size,
                        self.tile_size,
                        enemy_type
                    )
                    enemies.append(enemy)
                    break
                    
                attempts += 1
                
        return enemies
    
    def spawn_items(self, num_items):
        """Spawn items in random valid locations."""
        from item import Item
        
        # Identify all rooms
        rooms = self._identify_rooms()
        if not rooms:
            return []
            
        items = []
        for _ in range(num_items):
            # Choose a random room
            room = random.choice(rooms)
            
            # Choose a random position
            pos = random.choice(room)
            
            # Create a random item
            item_type = random.choice(['health', 'speed', 'damage'])
            item = Item(
                pos[0] * self.tile_size,
                pos[1] * self.tile_size,
                self.tile_size // 2,
                item_type
            )
            items.append(item)
            
        return items 