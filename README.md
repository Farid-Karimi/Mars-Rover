# Mars Rover Exploration Game

## Overview
This project simulates a Mars rover navigating a grid-based map using first-order logic principles. The rover must explore the map, avoid hazards (pits and obstacles), and collect items (stars) while making decisions based on its sensor data and exploration history.


## Modeling to First-Order Logic

### 1. **Grid Representation**
The map is modeled as a 2D grid where each cell can contain:
- **Pits**: Dangerous areas the rover must avoid.
- **Obstacles**: Blocking structures the rover cannot pass through.
- **Items**: Collectible stars the rover should prioritize.
- **Explored/Unexplored**: Tracks whether the rover has visited a cell.
- **Sensed**: Indicates whether the rover has detected the cell's contents.

Each cell is represented as a tuple `(x, y)` with properties:
- `pit(x, y)`: True if the cell contains a pit.
- `obstacle(x, y)`: True if the cell contains an obstacle.
- `item(x, y)`: True if the cell contains a collectible item.
- `explored(x, y)`: True if the rover has visited the cell.
- `sensed(x, y)`: True if the rover has detected the cell's contents.

### 2. **First-Order Logic Rules**
The rover's decision-making is based on logical rules implemented in the `LogicEngine` class. These rules are derived from first-order logic principles:

#### a. **Safe Movement**
A cell is safe to move into if:
- It has been sensed.
- It does not contain a pit or obstacle.

```python
safe(x, y) ⇔ sensed(x, y) ∧ ¬pit(x, y) ∧ ¬obstacle(x, y)
```

#### b. **Movement Prioritization**
The rover prioritizes moves based on the following rules:
1. **Item Collection**: If an uncollected item is sensed, move toward it.
   ```python
   prioritize_item(x, y) ⇔ item(x, y) ∧ ¬collected(x, y)
   ```
2. **Exploration**: If no items are available, prioritize unexplored cells.
   ```python
   prioritize_unexplored(x, y) ⇔ ¬explored(x, y)
   ```
3. **Backtracking**: If no safe moves are available, backtrack to previously explored cells.

#### c. **Dead-End Handling**
If the rover cannot move forward, it backtracks to the last safe position:
```python
dead_end(x, y) ⇔ ∀(dx, dy) ∈ directions: ¬safe(x + dx, y + dy)
```

## Logic Engine

The `LogicEngine` class implements the decision-making logic for the rover. It uses the following methods:

### 1. **`get_safe_moves()`**
- **Purpose**: Identifies all safe adjacent cells.
- **Logic**:
  ```python
  safe_moves = [(x + dx, y + dy) for (dx, dy) in directions 
                if safe(x + dx, y + dy)]
  ```

### 2. **`get_best_move()`**
- **Purpose**: Determines the optimal move based on prioritization rules.
- **Logic**:
  1. Check for uncollected items in sensed cells.
  2. If no items, prioritize unexplored cells.
  3. If no unexplored cells, choose a random safe move.
  4. If no safe moves, backtrack.

### 3. **`is_safe(x, y)`**
- **Purpose**: Checks if a cell is safe to move into.
- **Logic**:
  ```python
  is_safe(x, y) ⇔ sensed(x, y) ∧ ¬pit(x, y) ∧ ¬obstacle(x, y)
  ```

## Movement Strategy

The rover's movement is guided by the following strategy:

### 1. **Item Collection**
- The rover prioritizes moving toward uncollected items within its sensed area.
- Once an item is collected, it is marked as `collected` and no longer prioritized.

### 2. **Exploration**
- If no items are available, the rover explores unexplored cells.
- It avoids revisiting recently visited cells to prevent loops.

### 3. **Backtracking**
- If the rover reaches a dead end, it backtracks to the last safe position.
- Backtracking ensures the rover can continue exploring other areas.

### 4. **Sensor Updates**
- The rover's sensors detect adjacent cells (3x3 area around its position).
- Sensor data is used to update the `sensed` property of cells.

## Example Decision Flow

1. **Initial State**:
   - Rover at `(0, 0)`.
   - Adjacent cells sensed: `(0, 1)`, `(1, 0)`, `(1, 1)`.

2. **Item Detection**:
   - If `(1, 1)` contains an uncollected item, move to `(1, 1)`.

3. **Exploration**:
   - If no items are detected, move to the nearest unexplored cell.

4. **Dead End**:
   - If no safe moves are available, backtrack to the last safe position.

## Visualization

The game uses Pygame to visualize the grid, rover, and map elements:
- **Rover**: Represented as a car-like icon with wheels and a body.
- **Items**: Stars that change appearance when collected.
- **Pits**: Red circles indicating dangerous areas.
- **Obstacles**: Gray rectangles representing blocking structures.

## Conclusion

This project demonstrates how first-order logic can be applied to model decision-making in a grid-based exploration game. The rover's behavior is governed by logical rules that prioritize safety, item collection, and efficient exploration. The `LogicEngine` class serves as the core decision-making component, ensuring the rover navigates the map intelligently while avoiding hazards and collecting items.

This approach can be extended to more complex scenarios, such as:
- Multi-agent systems with multiple rovers.
- Dynamic environments with moving obstacles.
- Advanced pathfinding algorithms (e.g., A* or Dijkstra's).
