from src.environment.game_env import GameEnvironment
from src.agents.dqn_agent import DQNAgent
from src.training.trainer import Trainer
import json

def load_hyperparameters(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def main():
    hyperparameters = load_hyperparameters('config/hyperparameters.json')
    
    # Initialize the game environment
    env = GameEnvironment()
    
    # Initialize the DQN agent
    agent = DQNAgent(state_size=env.state_size, action_size=env.action_size, hyperparameters=hyperparameters)
    
    # Initialize the trainer
    trainer = Trainer(env, agent, hyperparameters)
    
    # Start the training process
    trainer.train()

if __name__ == "__main__":
    main()