import numpy as np
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam

class DQNAgent:
    def __init__(self, state_size, action_size, hyperparameters):
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = hyperparameters["learning_rate"]
        self.discount_factor = hyperparameters["discount_factor"]
        self.batch_size = hyperparameters["batch_size"]
        self.memory = []
        self.epsilon = hyperparameters["exploration_strategy"]["initial_epsilon"]
        self.final_epsilon = hyperparameters["exploration_strategy"]["final_epsilon"]
        self.epsilon_decay = (self.epsilon - self.final_epsilon) / hyperparameters["exploration_strategy"]["decay_steps"]
        self.model = self._build_model()

    def _build_model(self):
        model = Sequential()
        model.add(Dense(24, input_dim=self.state_size, activation='relu'))
        model.add(Dense(24, activation='relu'))
        model.add(Dense(self.action_size, activation='linear'))
        model.compile(loss='mse', optimizer=Adam(learning_rate=self.learning_rate))
        return model

    def select_action(self, state):
        if np.random.rand() <= self.epsilon:
            return np.random.choice(self.action_size)
        state = np.reshape(state, [1, self.state_size])
        q_values = self.model.predict(state, verbose=0)
        return np.argmax(q_values[0])

    def store_experience(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))
        # Decay epsilon
        if self.epsilon > self.final_epsilon:
            self.epsilon -= self.epsilon_decay

    def learn(self):
        # Call the training function with the batch size
        self.train(self.batch_size)

    def train(self, batch_size):
        import random
        import numpy as np
        
        if len(self.memory) < batch_size:
            return
            
        minibatch = random.sample(self.memory, batch_size)
        states = np.zeros((batch_size, self.state_size))
        targets = np.zeros((batch_size, self.action_size))
        
        for i, (state, action, reward, next_state, done) in enumerate(minibatch):
            state = np.reshape(state, [1, self.state_size])
            next_state = np.reshape(next_state, [1, self.state_size])
            
            target = reward
            if not done:
                target += self.discount_factor * np.amax(self.model.predict(next_state, verbose=0)[0])
                
            target_f = self.model.predict(state, verbose=0)
            target_f[0][action] = target
            
            states[i] = state
            targets[i] = target_f
            
        self.model.fit(states, targets, epochs=1, verbose=0, batch_size=batch_size)