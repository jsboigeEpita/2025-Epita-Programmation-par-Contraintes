import tensorflow as tf
from ai.RL.dqn_agent import DQNAgent
import board
from board import ConnectFourBoard

MODEL_PATH = "./ai/RL/models/connect4-dqn-selfplay-latest.weights.h5"


def get_move(state, player):
    agent = DQNAgent(state_shape=(ConnectFourBoard.ROW_COUNT, ConnectFourBoard.COLUMN_COUNT, 1),
                     action_size=ConnectFourBoard.COLUMN_COUNT,
                     use_double_dqn=True)

    temp_board = ConnectFourBoard()
    temp_board.board = state.copy()

    valid_moves = temp_board.get_valid_locations()

    col = agent.act(state, valid_moves)
    if col not in valid_moves:
        raise ValueError(f"Invalid move: {col} not in {valid_moves}")

    return col


def name():
    return "DQN Agent"
