import numpy as np
import tensorflow as tf
from tensorflow import keras
from collections import deque
import random
import matplotlib.pyplot as plt
from IPython.display import clear_output
import time


# Define the Snake game environment
class SnakeGameEnv:
    def __init__(self, grid_size=10):
        self.grid_size = grid_size
        self.reset()

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

        # Update direction (cannot go in the opposite direction)
        current_direction_idx = directions.index(self.direction)
        if action == 0:  # Continue in the same direction
            new_direction = self.direction
        elif action == 1:  # Turn left
            new_direction = directions[(current_direction_idx - 1) % 4]
        elif action == 2:  # Turn right
            new_direction = directions[(current_direction_idx + 1) % 4]

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
            or self.head in list(self.snake)[1:]
            or self.steps >= self.max_steps
        ):
            self.done = True
            reward = -10.0  # Penalty for dying

        # Small reward for surviving each step
        if not self.done:
            reward += 0.1

            # Additional reward for moving towards food
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

    def render(self):
        grid = np.zeros((self.grid_size, self.grid_size), dtype=str)
        grid[:] = "⬛"  # Empty cell

        # Draw snake body
        for i, j in list(self.snake)[1:]:
            if 0 <= i < self.grid_size and 0 <= j < self.grid_size:
                grid[i, j] = "🟩"  # Snake body

        # Draw snake head
        head_i, head_j = self.head
        if 0 <= head_i < self.grid_size and 0 <= head_j < self.grid_size:
            grid[head_i, head_j] = "🟦"  # Snake head

        # Draw food
        if self.food:
            food_i, food_j = self.food
            grid[food_i, food_j] = "🍎"  # Food

        # Print the grid
        for row in grid:
            print("".join(row))
        print(f"Score: {self.score}, Steps: {self.steps}")


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


# Training function
def train_dqn_agent(episodes=1000, grid_size=10, render_freq=100):
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

            if done:
                if e % render_freq == 0:
                    clear_output(wait=True)
                    print(
                        f"Episode: {e}/{episodes}, Score: {env.score}, Epsilon: {agent.epsilon:.2f}"
                    )
                    env.render()
                    time.sleep(0.5)

                break

        # Update target network every few episodes
        if e % update_target_freq == 0:
            agent.update_target_model()

        scores.append(env.score)

        # Save model every 100 episodes
        if e % 100 == 0:
            agent.save(f"snake_model_ep{e}.h5")

    return agent, scores


# Evaluation function
def evaluate_agent(agent, episodes=100, grid_size=10):
    env = SnakeGameEnv(grid_size=grid_size)
    scores = []
    steps = []

    for e in range(episodes):
        state = env.reset()
        while not env.done:
            action = agent.act(state, training=False)
            next_state, _, done = env.step(action)
            state = next_state

            if e < 5:  # Display first 5 episodes
                clear_output(wait=True)
                print(f"Evaluation Episode: {e+1}/{episodes}")
                env.render()
                time.sleep(0.1)

        scores.append(env.score)
        steps.append(env.steps)

    print(f"Average Score: {np.mean(scores)}")
    print(f"Average Steps: {np.mean(steps)}")

    return scores, steps


# Main execution
if __name__ == "__main__":
    # Train the agent
    trained_agent, training_scores = train_dqn_agent(
        episodes=500, grid_size=10, render_freq=100
    )

    # Plot training progress
    plt.figure(figsize=(10, 5))
    plt.plot(training_scores)
    plt.title("Training Progress")
    plt.xlabel("Episode")
    plt.ylabel("Score")
    plt.show()

    # Evaluate the trained agent
    eval_scores, eval_steps = evaluate_agent(trained_agent, episodes=50, grid_size=10)

    # Save the final model
    trained_agent.save("snake_model_final.h5")
