class BaseAgent:
    def __init__(self):
        pass

    def act(self, state):
        raise NotImplementedError("This method should be overridden by subclasses.")

    def learn(self, state, action, reward, next_state, done):
        raise NotImplementedError("This method should be overridden by subclasses.")