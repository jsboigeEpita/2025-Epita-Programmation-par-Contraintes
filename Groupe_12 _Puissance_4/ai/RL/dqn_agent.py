# dqn_agent.py
import tensorflow as tf
from tensorflow.keras.models import Model
# Added layers for potential improvements
from tensorflow.keras.layers import Input, Dense, Flatten, Conv2D, BatchNormalization, Add, Activation
from tensorflow.keras.optimizers import Adam
import numpy as np
import random
from collections import deque
import os


class DQNAgent:

    def __init__(self,
                 state_shape=(6, 7, 1),
                 action_size=7,
                 learning_rate=0.00025,
                 gamma=0.99,
                 epsilon=1.0,
                 epsilon_decay=0.9995,
                 epsilon_min=0.05,
                 memory_size=100000,
                 batch_size=128,
                 target_update_freq=1000,
                 use_double_dqn=True,
                 use_dueling_dqn=False
                 ):

        self.state_shape = state_shape
        self.action_size = action_size
        self.memory = deque(maxlen=memory_size)
        self.gamma = gamma
        self.epsilon = epsilon
        # Store initial epsilon for potential resets/scheduling
        self.initial_epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.target_update_freq = target_update_freq
        self.train_step_counter = 0
        self.use_double_dqn = use_double_dqn
        self.use_dueling_dqn = use_dueling_dqn  # Store flag

        # --- Model Building ---
        if self.use_dueling_dqn:
            print("Using Dueling DQN Architecture.")
            print(
                "ERROR: Dueling DQN architecture not implemented. Set use_dueling_dqn=False.")
            exit()
        else:
            self.model = self._build_conv_model()
            self.target_model = self._build_conv_model()
            # self.model = self._build_simpler_model()
            # self.target_model = self._build_simpler_model()

        self.update_target_model()
        # print(f"Agent Initialized. Double DQN: {
        #      self.use_double_dqn}, Dueling DQN: {self.use_dueling_dqn}")
        # print(f"Learning Rate: {self.learning_rate}, Gamma: {
        #      self.gamma}, Target Update Freq: {self.target_update_freq}")
        # self.model.summary()

    def _build_simpler_model(self) -> Model:
        inputs = Input(shape=self.state_shape)
        conv1 = Conv2D(32, kernel_size=(3, 3), padding='same')(inputs)
        act1 = Activation('relu')(conv1)
        flatten = Flatten()(act1)
        dense1 = Dense(128, activation='relu')(flatten)
        outputs = Dense(self.action_size, activation='linear')(dense1)
        model = Model(inputs=inputs, outputs=outputs)
        model.compile(optimizer=Adam(
            learning_rate=self.learning_rate), loss='mse')
        return model

    def _build_conv_model(self) -> Model:
        """ Builds a Convolutional Neural Network model. """
        inputs = Input(shape=self.state_shape)

        # Layer 1
        conv1 = Conv2D(filters=64, kernel_size=(3, 3),
                       padding='same', kernel_initializer='he_uniform')(inputs)
        act1 = Activation('relu')(conv1)

        # Layer 2
        conv2 = Conv2D(filters=128, kernel_size=(3, 3),
                       padding='same', kernel_initializer='he_uniform')(act1)
        act2 = Activation('relu')(conv2)

        # Layer 3
        conv3 = Conv2D(filters=128, kernel_size=(3, 3),
                       padding='same', kernel_initializer='he_uniform')(act2)
        act3 = Activation('relu')(conv3)

        # Flatten and Dense Layers
        flatten = Flatten()(act3)
        dense1 = Dense(256, activation='relu',
                       kernel_initializer='he_uniform')(flatten)

        # Output layer: Linear activation for Q-values
        outputs = Dense(self.action_size, activation='linear',
                        kernel_initializer='he_uniform')(dense1)

        model = Model(inputs=inputs, outputs=outputs)
        optimizer = Adam(learning_rate=self.learning_rate)
        model.compile(optimizer=optimizer, loss='mse')
        return model

    def update_target_model(self):
        self.target_model.set_weights(self.model.get_weights())

    # Store experience in replay memory

    def remember(self, state, action, reward, next_state, done):
        # Ensure states are numpy arrays before adding
        state = np.asarray(state, dtype=np.float32)
        next_state = np.asarray(next_state, dtype=np.float32)
        self.memory.append((state, action, reward, next_state, done))

    # Select an action based on the current state and valid actions

    def act(self, state, valid_actions, force_exploit=False):
        if not valid_actions:
            print("Error: Agent received no valid actions.")
            return None  # Or raise error

        current_epsilon = 0.0 if force_exploit else self.epsilon

        if np.random.rand() <= current_epsilon:
            # Exploration: Choose a random valid action
            return random.choice(valid_actions)
        else:
            # Exploitation: Choose the best valid action according to the main model
            if state.ndim == 2:  # If state is (6, 7)
                state_reshaped = np.expand_dims(
                    np.expand_dims(state, axis=0), axis=-1)
            elif state.ndim == 3:  # If state is (6, 7, 1)
                state_reshaped = np.expand_dims(state, axis=0)
            else:  # Should already be (1, 6, 7, 1) potentially
                state_reshaped = state

            if state_reshaped.shape != (1,) + self.state_shape:
                print(f"Error: State shape mismatch in act. Expected {
                      (1,) + self.state_shape}, got {state_reshaped.shape}")
                return random.choice(valid_actions)  # Fallback

            act_values = self.model.predict(state_reshaped, verbose=0)[0]

            # Mask invalid actions by setting their Q-values low
            masked_act_values = np.full(self.action_size, -np.inf)
            masked_act_values[valid_actions] = act_values[valid_actions]

            best_action = np.argmax(masked_act_values)

            # Sanity check
            if best_action not in valid_actions:
                print(f"CRITICAL Error: Agent chose invalid action {
                      best_action} despite masking.")
                print(f"Original Q-values: {act_values}")
                print(f"Valid actions: {valid_actions}")
                print(f"Masked Q-values: {masked_act_values}")
                # Fallback to a random valid action if error occurs
                return random.choice(valid_actions)

            return best_action

    # Train the model using a batch of experiences from replay memory

    def replay(self):
        if len(self.memory) < self.batch_size:
            return 0.0  # Not enough samples yet

        minibatch = random.sample(self.memory, self.batch_size)

        states = np.array([experience[0] for experience in minibatch])
        actions = np.array([experience[1] for experience in minibatch])
        rewards = np.array([experience[2] for experience in minibatch])
        next_states = np.array([experience[3] for experience in minibatch])
        dones = np.array([experience[4] for experience in minibatch])

        if states.ndim == 3:  # Shape (batch, rows, cols)
            states = np.expand_dims(states, axis=-1)
            next_states = np.expand_dims(next_states, axis=-1)

        # Predict Q-values for next states using the *target* model for stability
        q_next_target = self.target_model.predict(next_states, verbose=0)

        if self.use_double_dqn:
            # Double DQN, select best action using the main model
            q_next_main = self.model.predict(next_states, verbose=0)
            best_actions_next = np.argmax(q_next_main, axis=1)
            # Evaluate the selected action using the targe* model
            # Gather the Q-values from target_model corresponding to the best actions chosen by main_model
            batch_indices = np.arange(self.batch_size)
            q_next_target_selected = q_next_target[batch_indices,
                                                   best_actions_next]
            target_q_values = rewards + \
                (self.gamma * q_next_target_selected * (1 - dones))
        else:
            # Standard DQN, use max Q value directly from the target network
            max_q_next = np.max(q_next_target, axis=1)
            target_q_values = rewards + (self.gamma * max_q_next * (1 - dones))

        # Predict current Q-values using the main model (to update them)
        q_current_main = self.model.predict(states, verbose=0)

        # Create target vector for training: update only the Q-value for the action taken
        target_q_for_training = q_current_main.copy()
        batch_indices = np.arange(self.batch_size)
        target_q_for_training[batch_indices, actions] = target_q_values

        # Train the main model
        history = self.model.fit(states, target_q_for_training,
                                 batch_size=self.batch_size,
                                 epochs=1, verbose=0)
        loss = history.history['loss'][0]

        # Epsilon Decay
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

        # --- Target Network Update ---
        self.train_step_counter += 1
        if self.train_step_counter % self.target_update_freq == 0:
            self.update_target_model()

        return loss

    def load(self, name):
        """Loads model weights."""
        if not os.path.exists(name):
            print(f"Warning: Weights file not found at {
                  name}. Agent will start with initial weights.")
            return False
        try:
            self.model.load_weights(name)
            self.update_target_model()  # Sync target model
            print(f"Model weights loaded successfully from {name}")
            return True
        except Exception as e:
            print(f"Error loading weights from {name}: {e}")
            return False

    def save(self, name):
        """Saves model weights."""
        try:
            self.model.save_weights(name)
            print(f"Model weights saved successfully to {name}")
        except Exception as e:
            print(f"Error saving weights to {name}: {e}")
