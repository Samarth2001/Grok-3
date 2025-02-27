class NeuralNetwork:
    def __init__(self, input_shape, output_shape, learning_rate=0.001):
        self.model = self.build_model(input_shape, output_shape, learning_rate)

    def build_model(self, input_shape, output_shape, learning_rate):
        from tensorflow.keras.models import Sequential
        from tensorflow.keras.layers import Dense
        from tensorflow.keras.optimizers import Adam

        model = Sequential()
        model.add(Dense(24, input_shape=input_shape, activation='relu'))
        model.add(Dense(24, activation='relu'))
        model.add(Dense(output_shape, activation='linear'))

        model.compile(loss='mse', optimizer=Adam(learning_rate=learning_rate))
        return model

    def forward(self, state):
        return self.model.predict(state)

    def train(self, states, targets):
        self.model.fit(states, targets, epochs=1, verbose=0)

    def save(self, filepath):
        self.model.save(filepath)

    def load(self, filepath):
        from tensorflow.keras.models import load_model
        self.model = load_model(filepath)