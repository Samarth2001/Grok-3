import numpy as np

class Trainer:
    def __init__(self, environment, agent, hyperparameters):
        self.agent = agent
        self.environment = environment
        self.num_episodes = hyperparameters["num_episodes"]
        self.max_steps = hyperparameters["max_steps_per_episode"]
        self.render = hyperparameters["render"]
        self.performance_log = []

    def run_episode(self):
        state = self.environment.reset()
        total_reward = 0

        for step in range(self.max_steps):
            # Select an action
            action = self.agent.select_action(state)
            
            # Take action and observe the next state and reward
            next_state, reward, done, _ = self.environment.step(action)
            
            # Store the experience in agent's memory
            self.agent.store_experience(state, action, reward, next_state, done)
            
            # Learn from experience
            self.agent.learn()
            
            # Update state and accumulate reward
            state = next_state
            total_reward += reward
            
            # Render if enabled
            if self.render and step % 10 == 0:
                self.environment.render()

            if done:
                break

        return total_reward, step + 1

    def train(self):
        for episode in range(self.num_episodes):
            total_reward, steps = self.run_episode()
            self.performance_log.append(total_reward)
            
            print(f"Episode {episode+1}/{self.num_episodes}, " +
                  f"Steps: {steps}/{self.max_steps}, " +
                  f"Total Reward: {total_reward:.2f}, " +
                  f"Epsilon: {self.agent.epsilon:.4f}")

    def save_performance(self, filename):
        with open(filename, 'w') as f:
            for reward in self.performance_log:
                f.write(f"{reward}\n")