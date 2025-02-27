import numpy as np
import tensorflow as tf
from tensorflow import keras
from collections import deque
import random
import matplotlib.pyplot as plt
import time
import os
import pygame  # Add pygame for better visualization

# Constants for visualization
CELL_SIZE = 40
GRID_COLOR = (50, 50, 50)
SNAKE_COLOR = (0, 255, 0)
SNAKE_HEAD_COLOR = (0, 200, 0)
FOOD_COLOR = (255, 0, 0)
BACKGROUND_COLOR = (0, 0, 0)


# Define the Snake game environment
class SnakeGameEnv:
    def __init__(self, grid_size=10):
        self.grid_size = grid_size
        self.reset()
        self.render_mode = None  # 'human', 'pygame', or None
        self.pygame_initialized = False
        self.screen = None

    def reset(self):
        # Initialize the snake at the center of the grid
        self.snake = deque([(self.grid_size // 2, self.grid_size // 2)])
        self.head = self.snake[0]

        # Place food at a random empty position
        self.place_food()

        # Initialize direction to right
        self.direction = (0, 1)

        # Initialize game state
        self.steps = 0
        self.max_steps = 100 * self.grid_size  # Prevent infinite games
        self.score = 0
        self.done = False

        # Return initial state
        return self._get_state()

    def place_food(self):
        empty_cells = [
            (i, j)
            for i in range(self.grid_size)
            for j in range(self.grid_size)
            if (i, j) not in self.snake
        ]
        if empty_cells:
            self.food = random.choice(empty_cells)
        else:
            self.food = None  # No empty space left

    def step(self, action):
        # Define the movement directions: up, right, down, left
        directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]

        # Update direction
        current_direction_idx = directions.index(self.direction)
        if action == 0:  # Continue in same direction
            new_direction = self.direction
        elif action == 1:  # Turn left
            new_direction = directions[(current_direction_idx - 1) % 4]
        elif action == 2:  # Turn right
            new_direction = directions[(current_direction_idx + 1) % 4]
        else:
            raise ValueError("Invalid action")

        self.direction = new_direction

        # Move snake
        head_i, head_j = self.head
        new_head = (head_i + self.direction[0], head_j + self.direction[1])
        self.head = new_head
        self.snake.appendleft(new_head)

        # Check if food eaten
        reward = 0
        if self.head == self.food:
            self.score += 1
            reward = 10.0  # Reward for eating food
            self.place_food()
        else:
            self.snake.pop()  # Remove tail if food not eaten

        # Check if game is over (collision with boundaries or itself)
        head_i, head_j = self.head
        if (
            head_i < 0
            or head_i >= self.grid_size
            or head_j < 0
            or head_j >= self.grid_size
            or (self.head in list(self.snake)[1:])
            or self.steps >= self.max_steps
        ):
            self.done = True
            reward = -10.0  # Penalty for dying

        # Small reward for surviving each step
        if not self.done:
            reward += 0.1

            # Additional reward for moving towards food
            if self.food:  # Only if food exists
                food_i, food_j = self.food
                dist_to_food = abs(head_i - food_i) + abs(head_j - food_j)
                reward += 0.1 * (1.0 / (dist_to_food + 1))

        self.steps += 1
        return self._get_state(), reward, self.done

    def _get_state(self):
        # Create a state representation
        state = np.zeros((self.grid_size, self.grid_size, 3), dtype=np.float32)

        # Mark the snake body
        for i, j in self.snake:
            if 0 <= i < self.grid_size and 0 <= j < self.grid_size:
                state[i, j, 0] = 1.0

        # Mark the snake head
        head_i, head_j = self.head
        if 0 <= head_i < self.grid_size and 0 <= head_j < self.grid_size:
            state[head_i, head_j, 1] = 1.0

        # Mark the food
        if self.food:
            food_i, food_j = self.food
            state[food_i, food_j, 2] = 1.0

        # Flatten the state to a 1D array
        return state.flatten()

    def render(self, mode="human"):
        self.render_mode = mode

        if mode == "human":
            # Text-based rendering for terminals
            os.system("cls" if os.name == "nt" else "clear")
            grid = np.zeros((self.grid_size, self.grid_size), dtype=str)
            grid[:] = "·"  # Empty cell (using simpler character)

            # Draw snake body
            for i, j in list(self.snake)[1:]:
                if 0 <= i < self.grid_size and 0 <= j < self.grid_size:
                    grid[i, j] = "O"  # Snake body

            # Draw snake head
            head_i, head_j = self.head
            if 0 <= head_i < self.grid_size and 0 <= head_j < self.grid_size:
                grid[head_i, head_j] = "X"  # Snake head

            # Draw food
            if self.food:
                food_i, food_j = self.food
                grid[food_i, food_j] = "*"  # Food

            # Print the grid
            print("+" + "-" * self.grid_size + "+")
            for row in grid:
                print("|" + "".join(row) + "|")
            print("+" + "-" * self.grid_size + "+")
            print(f"Score: {self.score}, Steps: {self.steps}")

        elif mode == "pygame":
            # Initialize pygame if not done yet
            if not self.pygame_initialized:
                pygame.init()
                self.pygame_initialized = True
                window_size = self.grid_size * CELL_SIZE
                self.screen = pygame.display.set_mode((window_size, window_size))
                pygame.display.set_caption("Snake RL")

            self.screen.fill(BACKGROUND_COLOR)

            # Draw grid lines
            for i in range(self.grid_size + 1):
                pygame.draw.line(
                    self.screen,
                    GRID_COLOR,
                    (i * CELL_SIZE, 0),
                    (i * CELL_SIZE, self.grid_size * CELL_SIZE),
                )
                pygame.draw.line(
                    self.screen,
                    GRID_COLOR,
                    (0, i * CELL_SIZE),
                    (self.grid_size * CELL_SIZE, i * CELL_SIZE),
                )

            # Draw snake body
            for i, j in list(self.snake)[1:]:
                if 0 <= i < self.grid_size and 0 <= j < self.grid_size:
                    pygame.draw.rect(
                        self.screen,
                        SNAKE_COLOR,
                        (j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE),
                    )

            # Draw snake head
            head_i, head_j = self.head
            if 0 <= head_i < self.grid_size and 0 <= head_j < self.grid_size:
                pygame.draw.rect(
                    self.screen,
                    SNAKE_HEAD_COLOR,
                    (head_j * CELL_SIZE, head_i * CELL_SIZE, CELL_SIZE, CELL_SIZE),
                )

            # Draw food
            if self.food:
                food_i, food_j = self.food
                pygame.draw.circle(
                    self.screen,
                    FOOD_COLOR,
                    (
                        food_j * CELL_SIZE + CELL_SIZE // 2,
                        food_i * CELL_SIZE + CELL_SIZE // 2,
                    ),
                    CELL_SIZE // 2 - 5,
                )

            # Draw score
            font = pygame.font.SysFont(None, 24)
            score_text = font.render(f"Score: {self.score}", True, (255, 255, 255))
            self.screen.blit(score_text, (5, 5))

            pygame.display.flip()

    def close(self):
        if self.pygame_initialized:
            pygame.quit()
            self.pygame_initialized = False


# Deep Q-Network (DQN) Agent
class DQNAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size

        # Hyperparameters
        self.gamma = 0.95  # Discount factor
        self.epsilon = 1.0  # Exploration rate
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.01
        self.learning_rate = 0.001
        self.batch_size = 64

        # Memory for experience replay
        self.memory = deque(maxlen=10000)

        # Main model (trained every step)
        self.model = self._build_model()

        # Target model (updated periodically)
        self.target_model = self._build_model()
        self.update_target_model()

    def _build_model(self):
        model = keras.Sequential(
            [
                keras.layers.Dense(256, activation="relu", input_dim=self.state_size),
                keras.layers.Dense(256, activation="relu"),
                keras.layers.Dense(self.action_size, activation="linear"),
            ]
        )
        model.compile(
            loss="mse",
            optimizer=keras.optimizers.Adam(learning_rate=self.learning_rate),
        )
        return model

    def update_target_model(self):
        # Copy weights from model to target_model
        self.target_model.set_weights(self.model.get_weights())

    def remember(self, state, action, reward, next_state, done):
        # Store experience in memory
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state, training=True):
        # Epsilon-greedy action selection
        if training and np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)

        act_values = self.model.predict(np.array([state]), verbose=0)
        return np.argmax(act_values[0])

    def replay(self):
        if len(self.memory) < self.batch_size:
            return

        # Sample a batch from memory
        minibatch = random.sample(self.memory, self.batch_size)

        # Extract data
        states = np.array([m[0] for m in minibatch])
        actions = np.array([m[1] for m in minibatch])
        rewards = np.array([m[2] for m in minibatch])
        next_states = np.array([m[3] for m in minibatch])
        dones = np.array([m[4] for m in minibatch])

        # Compute target Q values
        target = self.model.predict(states, verbose=0)
        target_next = self.target_model.predict(next_states, verbose=0)

        for i in range(self.batch_size):
            if dones[i]:
                target[i, actions[i]] = rewards[i]
            else:
                target[i, actions[i]] = rewards[i] + self.gamma * np.max(target_next[i])

        # Train the model
        self.model.fit(states, target, epochs=1, verbose=0)

        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def load(self, name):
        self.model.load_weights(name)

    def save(self, name):
        self.model.save_weights(name)


def train_dqn_agent(episodes=500, grid_size=10, render_freq=50, render_mode="pygame"):
    env = SnakeGameEnv(grid_size=grid_size)
    state_size = env.grid_size * env.grid_size * 3  # State representation size
    action_size = 3  # Actions: continue, turn left, turn right

    agent = DQNAgent(state_size, action_size)

    scores = []
    update_target_freq = 5  # Update target model every 5 episodes

    for e in range(episodes):
        state = env.reset()
        total_reward = 0

        while not env.done:
            action = agent.act(state)
            next_state, reward, done = env.step(action)
            agent.remember(state, action, reward, next_state, done)
            state = next_state
            total_reward += reward

            agent.replay()

            if e % render_freq == 0:
                env.render(mode=render_mode)
                time.sleep(0.05)  # Slower for visualization

            if done:
                if e % render_freq == 0:
                    print(
                        f"Episode: {e}/{episodes}, Score: {env.score}, Epsilon: {agent.epsilon:.2f}"
                    )
                break

        # Update target network every few episodes
        if e % update_target_freq == 0:
            agent.update_target_model()

        scores.append(env.score)

        # Save model every 100 episodes
        if e % 100 == 0:
            agent.save(f"snake_model_ep{e}.h5")

    env.close()
    return agent, scores


def evaluate_agent(agent, episodes=20, grid_size=10, render_mode="pygame"):
    env = SnakeGameEnv(grid_size=grid_size)
    scores = []
    steps = []

    for e in range(episodes):
        state = env.reset()
        while not env.done:
            action = agent.act(state, training=False)
            next_state, _, done = env.step(action)
            state = next_state

            env.render(mode=render_mode)
            time.sleep(0.1)  # Slower for visualization

        scores.append(env.score)
        steps.append(env.steps)
        print(f"Evaluation Episode {e+1}/{episodes}, Score: {env.score}")

    env.close()
    print(f"Average Score: {np.mean(scores):.2f}")
    print(f"Average Steps: {np.mean(steps):.2f}")

    return scores, steps


def human_play(grid_size=10):
    """Human playable version of the game"""
    pygame.init()
    env = SnakeGameEnv(grid_size=grid_size)
    state = env.reset()

    window_size = grid_size * CELL_SIZE
    screen = pygame.display.set_mode((window_size, window_size))
    pygame.display.set_caption("Snake - Human Player")

    clock = pygame.time.Clock()
    running = True

    # Map keys to actions
    # 0: continue, 1: turn left, 2: turn right
    current_action = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_action = 1
                elif event.key == pygame.K_RIGHT:
                    current_action = 2
                elif event.key == pygame.K_UP:
                    current_action = 0

        # Take step with current action
        next_state, reward, done = env.step(current_action)
        state = next_state

        # Reset action after step
        current_action = 0

        # Render
        env.render(mode="pygame")

        if done:
            print(f"Game Over! Score: {env.score}")
            time.sleep(2)
            running = False

        clock.tick(5)  # 5 FPS for human play

    pygame.quit()


if __name__ == "__main__":
    # Choose mode: 'train', 'eval', 'human', 'train_and_eval'
    mode = "train_and_eval"

    if mode == "train":
        # Train the agent
        trained_agent, training_scores = train_dqn_agent(
            episodes=300, grid_size=10, render_freq=50, render_mode="pygame"
        )

        # Save the model
        trained_agent.save("snake_model_final.h5")

        # Plot training progress
        plt.figure(figsize=(10, 5))
        plt.plot(training_scores)
        plt.title("Training Progress")
        plt.xlabel("Episode")
        plt.ylabel("Score")
        plt.savefig("training_progress.png")
        plt.show()

    elif mode == "eval":
        # Load and evaluate a trained model
        env = SnakeGameEnv(grid_size=10)
        state_size = env.grid_size * env.grid_size * 3
        agent = DQNAgent(state_size, 3)
        try:
            agent.load("snake_model_final.h5")
            print("Model loaded successfully!")
            eval_scores, eval_steps = evaluate_agent(agent, episodes=10)
        except:
            print("No saved model found. Train the agent first.")

    elif mode == "human":
        # Play the game yourself
        human_play(grid_size=10)

    elif mode == "train_and_eval":
        # Train and then evaluate
        trained_agent, training_scores = train_dqn_agent(
            episodes=300, grid_size=10, render_freq=50, render_mode="pygame"
        )

        # Save the model
        trained_agent.save("snake_model_final.h5")

        # Evaluate the trained agent
        eval_scores, eval_steps = evaluate_agent(trained_agent, episodes=10)

        # Plot training progress
        plt.figure(figsize=(10, 5))
        plt.plot(training_scores)
        plt.title("Training Progress")
        plt.xlabel("Episode")
        plt.ylabel("Score")
        plt.savefig("training_progress.png")
        plt.show()
