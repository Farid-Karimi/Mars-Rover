import pygame
import random
import math

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 600, 600
GRID_SIZE = 20
CELL_SIZE = WIDTH // GRID_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mars Rover")

# Colors
COLORS = {
    'background': (40, 40, 40),
    'unexplored': (69,24,4),
    'explored': (193,68,14),
    'pit': (150, 0, 0),
    'obstacle': (104,105,109),
    'item': (255, 215, 0),
    'rover': (253,166,0)
}

# first order logic is partially implemented in this class this is the backbone of our descision making
class LogicEngine:
    def __init__(self, game_state):
        self.game = game_state
        self.visited = set()
    
    #returns safe and valid moves as list
    def get_safe_moves(self):
        x, y = self.game.rover_pos
        moves = []
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = x + dx, y + dy
            if self.is_valid(nx, ny) and self.is_safe(nx, ny):
                moves.append((nx, ny))
        return moves
    
    # checking to stay in bound
    def is_valid(self, x, y):
        return 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE
    
    def is_safe(self, x, y):
        cell = self.game.grid[x][y]
        return cell['sensed'] and not cell['pit'] and not cell['obstacle']
    
    def get_best_move(self):
        moves = self.get_safe_moves()
        if not moves:
            return None

        # Prioritize uncollected items first
        item_moves = [pos for pos in moves if 
                     self.game.grid[pos[0]][pos[1]]['item'] and 
                     not self.game.grid[pos[0]][pos[1]]['collected']]
        if item_moves:
            return random.choice(item_moves)

        unexplored = [pos for pos in moves if not self.game.grid[pos[0]][pos[1]]['explored']]
        
        #then we can favor the visited cells as mentioned in project doc
        if unexplored:
            random.shuffle(unexplored)
            return unexplored[0]
        
        recent_moves = [pos for pos in moves if pos not in self.visited]
        if recent_moves:
            return random.choice(recent_moves)
        
        return random.choice(moves) if moves else None

#general functions to make and place map elements
class GameState:
    def __init__(self):
        self.grid = [[{'pit': False, 'obstacle': False, 'item': False, 
                      'collected': False, 'sensed': False, 'explored': False} 
                     for _ in range(GRID_SIZE)] 
                    for _ in range(GRID_SIZE)]
        self.rover_pos = (0, 0)
        self.path_stack = [self.rover_pos]
        self.generate_map()
        self.logic = LogicEngine(self)
        self.grid[0][0]['explored'] = True
        self.update_sensors()
        self.logic.visited.add(self.rover_pos)

    def generate_map(self):
        elements = [
            ('pit', 10), 
            ('obstacle', 7), 
            ('item', 5)
        ]
        for element_type, count in elements:
            for _ in range(count):
                while True:
                    x, y = random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)
                    if (x, y) != (0, 0) and not self.grid[x][y][element_type]:
                        self.grid[x][y][element_type] = True
                        break

    # checking the 4 general direction adjacent blocks and making them ready to be rendered by changing sensed(Boolean)
    def update_sensors(self):
        x, y = self.rover_pos
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                    self.grid[nx][ny]['sensed'] = True

    def move_rover(self, new_pos):
        if self.is_valid_move(new_pos):
            # Mark item as collected and output to log
            if self.grid[new_pos[0]][new_pos[1]]['item'] and self.grid[new_pos[0]][new_pos[1]]['collected'] is not True:
                self.grid[new_pos[0]][new_pos[1]]['collected'] = True
                print(f"Collected item at {new_pos} - Total: {sum(cell['collected'] for row in self.grid for cell in row)}")
            
            self.rover_pos = new_pos
            self.path_stack.append(new_pos)
            self.grid[new_pos[0]][new_pos[1]]['explored'] = True
            self.update_sensors()
            self.logic.visited.add(new_pos)
            if len(self.logic.visited) > 4:
                self.logic.visited.remove(next(iter(self.logic.visited)))

    def is_valid_move(self, pos):
        x, y = pos
        return (0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE 
                and not self.grid[x][y]['obstacle']
                and not self.grid[x][y]['pit'])

    def backtrack(self):
        if len(self.path_stack) > 1:
            self.path_stack.pop()
            self.rover_pos = self.path_stack[-1]
            self.update_sensors()

    def update(self):
        if best_move := self.logic.get_best_move():
            self.move_rover(best_move)
        else:
            self.backtrack()

#showing items as a star
def draw_star(surface, color, center, size): 
    points = []
    for i in range(5):
        angle = math.radians(72*i - 90)
        x = center[0] + math.cos(angle) * size
        y = center[1] + math.sin(angle) * size
        points.append((x, y))
        angle = math.radians(72*i + 18 - 90)
        x = center[0] + math.cos(angle) * size/2
        y = center[1] + math.sin(angle) * size/2
        points.append((x, y))
    pygame.draw.polygon(surface, color, points)

def draw_grid(screen, game_state):
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            cell = game_state.grid[i][j]
            rect = pygame.Rect(i*CELL_SIZE, j*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            
            # Base cell color
            if cell['explored']:
                pygame.draw.rect(screen, COLORS['explored'], rect)
            else:
                pygame.draw.rect(screen, COLORS['unexplored'], rect)
            
            # Draw hazards/items if sensed
            if cell['sensed']:
                center = (i*CELL_SIZE + CELL_SIZE//2, j*CELL_SIZE + CELL_SIZE//2)
                
                if cell['pit']:
                    pygame.draw.circle(screen, COLORS['pit'], center, CELL_SIZE//3)
                    pygame.draw.circle(screen, (0, 0, 0), center, CELL_SIZE//4)
                elif cell['obstacle']:
                    pygame.draw.rect(screen, COLORS['obstacle'], 
                                   (i*CELL_SIZE + 2, j*CELL_SIZE + 2, 
                                    CELL_SIZE-4, CELL_SIZE-4), 
                                   border_radius=3)
                elif cell['item']:
                    # Draw star with different color if collected
                    if cell['collected']:
                        draw_star(screen, (150, 150, 0), center, CELL_SIZE//3)  # Dimmed yellow
                        pygame.draw.circle(screen, (100, 100, 0), center, 3) 
                    else:
                        draw_star(screen, COLORS['item'], center, CELL_SIZE//3)

    # get rover Cords
    x, y = game_state.rover_pos
    rover_center = (x*CELL_SIZE + CELL_SIZE//2, y*CELL_SIZE + CELL_SIZE//2)
    
    # Draw rover
    rover_rect = pygame.Rect(
        x*CELL_SIZE + CELL_SIZE//4,
        y*CELL_SIZE + CELL_SIZE//4,
        CELL_SIZE//2,
        CELL_SIZE//2
    )
    
    # Car body
    pygame.draw.rect(screen, COLORS['rover'], rover_rect, border_radius=3)
    
    # Wheels
    wheel_radius = CELL_SIZE//7
    pygame.draw.circle(screen, (0, 0, 0),  # left down wheel
                      (x*CELL_SIZE + CELL_SIZE//4, y*CELL_SIZE + CELL_SIZE*3//4),
                      wheel_radius)
    pygame.draw.circle(screen, (0, 0, 0),  # right down wheel
                      (x*CELL_SIZE + CELL_SIZE*3//4, y*CELL_SIZE + CELL_SIZE*3//4),
                      wheel_radius)

    pygame.draw.circle(screen, (0, 0, 0),  # left up wheel
                      (x*CELL_SIZE + CELL_SIZE//4, y*CELL_SIZE + CELL_SIZE//4),
                      wheel_radius)
    pygame.draw.circle(screen, (0, 0, 0),  # right up wheel
                      (x*CELL_SIZE + CELL_SIZE*3//4, y*CELL_SIZE + CELL_SIZE//4),
                      wheel_radius)
    

def main():
    game = GameState()
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        game.update()

        # Check for game over
        x, y = game.rover_pos
        if game.grid[x][y]['pit']:
            print("Game Over! Rover fell into a pit.")
            running = False

        # Render
        screen.fill(COLORS['background'])
        draw_grid(screen, game)
        pygame.display.flip()
        clock.tick(20) # can be lower it for slower animation

    pygame.quit()

if __name__ == "__main__":
    main()