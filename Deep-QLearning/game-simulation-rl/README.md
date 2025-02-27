# Game Simulation with Reinforcement Learning

This project implements a game simulation using reinforcement learning techniques, specifically utilizing a Deep Q-Network (DQN) algorithm. The goal is to create an intelligent agent that can learn to play the game effectively through interaction with the environment.

## Project Structure

The project is organized into the following directories and files:

- `src/`: Contains the main source code for the project.
  - `environment/`: Defines the game environment.
    - `game_env.py`: Implements the `GameEnvironment` class for simulating the game.
    - `utils.py`: Provides utility functions for state normalization and action space definitions.
  - `agents/`: Contains the agent implementations.
    - `dqn_agent.py`: Implements the `DQNAgent` class for the Deep Q-Network algorithm.
    - `base_agent.py`: Defines a `BaseAgent` class as a template for other agents.
  - `models/`: Contains the neural network architecture.
    - `neural_network.py`: Defines the `NeuralNetwork` class for the DQN agent.
  - `training/`: Manages the training process.
    - `trainer.py`: Implements the `Trainer` class for managing the training loop.
    - `rewards.py`: Contains functions for calculating rewards based on game state and actions.
  - `visualization/`: Handles the visualization of the game environment.
    - `renderer.py`: Implements the `Renderer` class for rendering the game state and performance metrics.
  
- `config/`: Contains configuration files.
  - `hyperparameters.json`: Stores hyperparameters for the reinforcement learning model.

- `main.py`: The entry point of the application that initializes the environment, agent, and trainer, and starts the training process.

- `requirements.txt`: Lists the dependencies required for the project, such as TensorFlow, NumPy, and Matplotlib.

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd game-simulation-rl
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Configure the hyperparameters in `config/hyperparameters.json` as needed.

## Usage

To run the game simulation, execute the following command:
```
python main.py
```

## Algorithms Used

This project primarily utilizes the Deep Q-Learning algorithm, which is a model-free reinforcement learning algorithm that combines Q-Learning with deep neural networks. The agent learns to make decisions by maximizing cumulative rewards through exploration and exploitation strategies.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.