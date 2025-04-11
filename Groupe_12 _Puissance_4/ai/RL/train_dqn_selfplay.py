import numpy as np
import random
import time
import math
import sys
import os
import tensorflow as tf
from collections import deque

if tf.config.list_physical_devices('GPU'):
    tf.keras.mixed_precision.set_global_policy('mixed_float16')

try:
    from board import ConnectFourBoard  # Your board implementation
    from dqn_agent import DQNAgent    # The enhanced DQN agent class
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Make sure board.py and dqn_agent.py are in the same directory.")
    sys.exit(1)

PLAYER1 = 1
PLAYER2 = 2
EMPTY = 0

AGENT_ID = 1
OPPONENT_ID = -1


# Training Parameters
TOTAL_EPISODES = 100000
MAX_STEPS_PER_EPISODE = 100
SAVE_FREQ = 500             # How often to save weights (in episode
LOG_FREQ = 50               # How often to print episode summary
WEIGHTS_FILE_PATTERN = "connect4-dqn-selfplay-ep{}.weights.h5"
LATEST_WEIGHTS_FILE = "connect4-dqn-selfplay-latest.weights.h5"

REPLAY_EVERY_N_AGENT_MOVES = 1

# DQN Agent Hyperparameters
LEARNING_RATE = 0.00025
GAMMA = 0.99
EPSILON_START = 1.0
EPSILON_DECAY = 0.9998
EPSILON_MIN = 0.05
MEMORY_SIZE = 500000
BATCH_SIZE = 1024
TARGET_UPDATE_FREQ = 2000
USE_DOUBLE_DQN = True


# Translates board from PLAYER1/PLAYER2 to AGENT_ID/OPPONENT_ID.
def translate_board_to_agent(board_state, agent_player_id):
    agent_board = np.zeros_like(board_state, dtype=np.float32)
    opponent_player_id = PLAYER2 if agent_player_id == PLAYER1 else PLAYER1
    agent_board[board_state == agent_player_id] = AGENT_ID
    agent_board[board_state == opponent_player_id] = OPPONENT_ID
    return np.expand_dims(agent_board, axis=-1)  # Add channel dim


def print_game_board(board_state):
    print("\n  0   1   2   3   4   5   6 ")
    print("-----------------------------")
    for r in range(ConnectFourBoard.ROW_COUNT):
        print("|", end="")
        for c in range(ConnectFourBoard.COLUMN_COUNT):
            if board_state[r, c] == PLAYER1:
                print(" X ", end="|")
            elif board_state[r, c] == PLAYER2:
                print(" O ", end="|")
            else:
                print("   ", end="|")
        print("\n-----------------------------")
    print()


def get_move(state, player):
    # Model is stored as a .h5 model file in the current directory
    model = tf.keras.models.load_model(
        "./models/connect4-dqn-selfplay-latest.weights.h5")
    state = np.expand_dims(state, axis=0)
    state = np.expand_dims(state, axis=-1)
    q_values = model.predict(state)
    valid_moves = np.where(state[0, :, :, 0] == 0)[1]
    q_values[0, valid_moves] = -np.inf
    action = np.argmax(q_values[0])
    return action


def name():
    return "DQN Agent"


if __name__ == "__main__":
    print("--- Starting DQN Self-Play Training ---")

    # --- Initialize Environment and Agent ---
    env = ConnectFourBoard()
    state_shape = (ConnectFourBoard.ROW_COUNT,
                   ConnectFourBoard.COLUMN_COUNT, 1)
    action_size = ConnectFourBoard.COLUMN_COUNT

    agent = DQNAgent(state_shape=state_shape,
                     action_size=action_size,
                     learning_rate=LEARNING_RATE,
                     gamma=GAMMA,
                     epsilon=EPSILON_START,
                     epsilon_decay=EPSILON_DECAY,
                     epsilon_min=EPSILON_MIN,
                     memory_size=MEMORY_SIZE,
                     batch_size=BATCH_SIZE,
                     target_update_freq=TARGET_UPDATE_FREQ,
                     use_double_dqn=USE_DOUBLE_DQN)

    # Load Previous Weights (Optional)
    start_episode = 0
    if os.path.exists(LATEST_WEIGHTS_FILE):
        print(f"Loading weights from {LATEST_WEIGHTS_FILE}")
        if agent.load(LATEST_WEIGHTS_FILE):
            print("Loaded previous weights. Resuming training.")
        else:
            print("Failed to load weights. Starting from scratch.")
    else:
        print("No previous weights found. Starting from scratch.")

    total_steps = 0
    # Track rewards of last 100 episodes for avg
    episode_rewards = deque(maxlen=100)
    episode_losses = deque(maxlen=100)

    # Counter for replay frequency control
    agent_moves_since_last_replay = 0

    print(f"Training for {TOTAL_EPISODES} episodes...")

    for e in range(start_episode, TOTAL_EPISODES):
        episode_start_time = time.time()
        env.reset()

        player_id_agent = random.choice([PLAYER1, PLAYER2])
        player_id_opponent = PLAYER2 if player_id_agent == PLAYER1 else PLAYER1

        current_player_env = PLAYER1

        current_board_state = env.get_board()
        done = False
        step_in_episode = 0
        episode_reward_sum = 0  # Track the learning agent's reward sum for this episode
        episode_loss_sum = 0
        # How many times the learning agent moved (and potentially replayed)
        agent_learn_move_count = 0

        # Temporary storage for the learning agent's transitions this episode
        episode_memory = []

        last_agent_state = None
        last_agent_action = None

        while not done and step_in_episode < MAX_STEPS_PER_EPISODE:
            valid_locations = env.get_valid_locations()
            if not valid_locations:
                done = True
                # Ensure the last transition reflects the draw if agent made last move
                if episode_memory:
                    s, a, r, ns, d = episode_memory[-1]
                    if not d:
                        episode_memory[-1] = (s, a, 0.0, ns, True)
                break

            action = -1

            # Determine whose turn it is
            is_learning_agent_turn = (current_player_env == player_id_agent)

            # Select Action
            if is_learning_agent_turn:
                state_agent_view = translate_board_to_agent(
                    current_board_state, player_id_agent)
                last_agent_state = state_agent_view

                # Use exploration
                action = agent.act(
                    state_agent_view, valid_locations, force_exploit=False)
                if action is None:
                    print(
                        f"Error: Learning Agent failed to produce action in episode {e+1}.")
                    done = True
                    break

                last_agent_action = action

            else:
                state_opponent_view = translate_board_to_agent(
                    current_board_state, player_id_opponent)

                # NO exploration
                action = agent.act(state_opponent_view,
                                   valid_locations, force_exploit=True)
                if action is None:
                    print(
                        f"Error: Opponent Agent failed to produce action in episode {e+1}.")
                    done = True
                    break

            row_placed = env.drop_piece(action, current_player_env)
            if row_placed == -1:
                print(f"CRITICAL ERROR: Episode {
                      e+1}, Player {current_player_env} chose invalid action {action}.")
                done = True
                break

            next_board_state = env.get_board()
            step_in_episode += 1
            total_steps += 1

            # Reward Calculation & Memory Management (Focus on Learning Agent)
            game_over = env.game_over
            winner = env.winner  # None, PLAYER1, or PLAYER2

            # We only store experiences and assign rewards from the perspective of the learning agent
            if is_learning_agent_turn:
                reward = 0.0  # Default reward for non-terminal move
                is_terminal_state_after_agent = False

                if game_over:
                    is_terminal_state_after_agent = True
                    if winner == player_id_agent:
                        reward = 1.0  # Agent won
                        episode_reward_sum += reward
                    elif winner is None:  # Draw
                        reward = 0.0  # Draw reward (agent didn't lose)
                        episode_reward_sum += reward

                next_state_agent_view = translate_board_to_agent(
                    next_board_state, player_id_agent)
                # Store the transition for the learning agent
                episode_memory.append((last_agent_state, last_agent_action,
                                      reward, next_state_agent_view, is_terminal_state_after_agent))
                agent_learn_move_count += 1

                # Agent Learning Step
                agent_moves_since_last_replay += 1
                if agent_moves_since_last_replay >= REPLAY_EVERY_N_AGENT_MOVES:
                    loss = agent.replay()
                    if loss is not None:
                        episode_loss_sum += loss
                    agent_moves_since_last_replay = 0  # Reset counter

            else:
                if game_over:
                    if winner == player_id_opponent:  # Learning Agent Lost
                        # Update the last stored transition in episode_memory for the learning agent
                        if episode_memory:
                            s, a, r, ns, d = episode_memory.pop()
                            episode_memory.append((s, a, -1.0, ns, True))
                            episode_reward_sum -= 1.0  # Agent lost

                    elif winner is None:
                        if episode_memory:
                            s, a, r, ns, d = episode_memory.pop()
                            # Mark as done, reward remains 0.0 for draw
                            episode_memory.append((s, a, 0.0, ns, True))
                            episode_reward_sum += 0.0  # Agent didn't lose

            current_board_state = next_board_state
            done = game_over
            if not done:
                # Switch environment player
                current_player_env = PLAYER2 if current_player_env == PLAYER1 else PLAYER1

        # End of Episode
        episode_duration = time.time() - episode_start_time

        # Add this episode's transitions (from learning agent's perspective) to main replay buffer
        for experience in episode_memory:
            agent.remember(*experience)

        # Logging
        episode_rewards.append(episode_reward_sum)
        avg_reward = sum(episode_rewards) / \
            len(episode_rewards) if episode_rewards else 0.0
        # Calculate avg loss per learning step in the episode
        avg_loss_episode = episode_loss_sum / \
            (agent_learn_move_count /
             REPLAY_EVERY_N_AGENT_MOVES) if agent_learn_move_count > 0 else 0.0
        if agent_learn_move_count > 0:
            episode_losses.append(avg_loss_episode)
        avg_loss_hist = sum(episode_losses) / \
            len(episode_losses) if episode_losses else 0.0

        if (e + 1) % LOG_FREQ == 0:
            print(f"Ep {e+1}/{TOTAL_EPISODES} | Steps: {step_in_episode} | Duration: {episode_duration:.2f}s | "
                  f"Epsilon: {agent.epsilon:.4f} | "
                  # Removed MM Depth
                  f"Ep Reward: {episode_reward_sum:.1f} | Avg Reward (100): {
                avg_reward:.3f} | "
                f"Avg Loss (100): {avg_loss_hist:.4f}")

        # Saving Weights
        if (e + 1) % SAVE_FREQ == 0:
            save_path = WEIGHTS_FILE_PATTERN.format(e+1)
            agent.save(save_path)
            # Overwrite latest for easy loading
            agent.save(LATEST_WEIGHTS_FILE)

    # End of Training
    print("\n--- Self-Play Training Finished ---")
    final_save_path = WEIGHTS_FILE_PATTERN.format(TOTAL_EPISODES)
    agent.save(final_save_path)
    agent.save(LATEST_WEIGHTS_FILE)
    print(f"Final model weights saved to {
          final_save_path} and {LATEST_WEIGHTS_FILE}")
