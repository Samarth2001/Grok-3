import numpy as np

class GameEnvironment:
    def __init__(self):
        # Define state and action space dimensions
        self.state_size = 4
        self.action_size = 5
        
        # Game parameters
        self.grid_size = 10
        self.player_pos = [0, 0]
        self.goal_pos = [9, 9]
        self.obstacle_pos = [[5, 5], [4, 6], [6, 4]]
        
        # Initialize state
        self.state = self.reset()

    def reset(self):
        # Reset player position
        self.player_pos = [0, 0]
        self.state = self._get_state()
        return self.state

    def step(self, action):
        # Move player based on action
        # 0: NO_OP, 1: LEFT, 2: RIGHT, 3: UP, 4: DOWN
        if action == 1:
            self.player_pos[0] = max(0, self.player_pos[0] - 1)
        elif action == 2:
            self.player_pos[0] = min(self.grid_size - 1, self.player_pos[0] + 1)
        elif action == 3:
            self.player_pos[1] = max(0, self.player_pos[1] - 1)
        elif action == 4:
            self.player_pos[1] = min(self.grid_size - 1, self.player_pos[1] + 1)
        
        # Update state
        self.state = self._get_state()
        
        # Check if goal is reached
        goal_reached = self.player_pos == self.goal_pos
        
        # Check collision with obstacles
        collision = any(self.player_pos == obstacle for obstacle in self.obstacle_pos)
        
        # Calculate reward and done flag
        if goal_reached:
            reward = 10
            done = True
        elif collision:
            reward = -5
            done = True
        else:
            # Small negative reward for each step
            reward = -0.1
            done = False
        
        # Add info dictionary (required for standard gym interface)
        info = {}
        
        return self.state, reward, done, info

    def render(self):
        self.display_state(self.state)

    def _get_state(self):
        # Convert game state to a numerical representation
        # Normalize positions to [0,1] for the neural network
        norm_player_x = self.player_pos[0] / self.grid_size
        norm_player_y = self.player_pos[1] / self.grid_size
        norm_goal_x = self.goal_pos[0] / self.grid_size
        norm_goal_y = self.goal_pos[1] / self.grid_size
        
        return np.array([norm_player_x, norm_player_y, norm_goal_x, norm_goal_y])

    def display_state(self, state):
        print("\n" + "-" * (self.grid_size + 2))
        for y in range(self.grid_size):
            row = "|"
            for x in range(self.grid_size):
                if [x, y] == self.player_pos:
                    row += "P"
                elif [x, y] == self.goal_pos:
                    row += "G"
                elif any([x, y] == obstacle for obstacle in self.obstacle_pos):
                    row += "X"
                else:
                    row += " "
            row += "|"
            print(row)
        print("-" * (self.grid_size + 2))
        print(f"Player position: {self.player_pos}")