import numpy as np
import random
import math
import time
from board import ConnectFourBoard

ROW_COUNT = 6
COLUMN_COUNT = 7
EMPTY = 0

class MCTSNode:
    """ Represents a node in the Monte Carlo Search Tree. """
    def __init__(self, state: ConnectFourBoard, parent=None, move=None):
        self.state = state
        self.parent = parent
        self.move = move # Move (column) that led to this state
        self.children = {}
        self.visits = 0 # N
        self.value = 0.0 # Q: Sum of simulation results relative to the AI player
        self.player_turn = self._get_player_turn()
        self.untried_moves = self.state.get_valid_locations()
        random.shuffle(self.untried_moves)

    def _get_player_turn(self):
        board = self.state.get_board()
        p1_pieces = np.count_nonzero(board == 1)
        p2_pieces = np.count_nonzero(board == 2)
        return 1 if p1_pieces == p2_pieces else 2

    def is_fully_expanded(self):
        return len(self.untried_moves) == 0

    def is_terminal(self):
        return self.state.game_over # Use attribute from board.py

    def select_best_child(self, exploration_weight=1.414):
        best_score = -float('inf')
        best_child = None

        for move, child in self.children.items():
            if child.visits == 0:
                return child # Prioritize unvisited children

            # UCB1 calculation - value Q is stored relative to the AI player
            exploit_term = child.value / child.visits
            log_term = math.log(self.visits) if self.visits > 0 else 0
            explore_term = exploration_weight * math.sqrt(log_term / child.visits)

            # Adjust score based on whose turn it is at the *parent* (self)
            # If it's the AI's turn at parent, maximize Q/N + explore
            # If it's opponent's turn at parent, they want to minimize AI's Q, so we maximize -(Q/N) + explore (from AI perspective)
            if self.player_turn != child.player_turn: # If AI moved to child
                 ucb_score = exploit_term + explore_term
            else: # If Opponent moved to child
                 ucb_score = -exploit_term + explore_term

            if ucb_score > best_score:
                best_score = ucb_score
                best_child = child

        return best_child

    def expand(self):
        if not self.untried_moves:
             print("Warning: Expand called on fully expanded node.")
             return self

        move = self.untried_moves.pop()
        next_state = ConnectFourBoard()
        next_state.board = np.copy(self.state.get_board())
        next_state.drop_piece(move, self.player_turn) # Use current node's player

        child_node = MCTSNode(state=next_state, parent=self, move=move)
        self.children[move] = child_node
        return child_node

def _mcts_select(node: MCTSNode):
    """ Phase 1: Select node using UCB1. """
    current_node = node
    while not current_node.is_terminal():
        if not current_node.is_fully_expanded():
            return current_node
        else:
            current_node = current_node.select_best_child()
            if current_node is None:
                 print("Error: select_best_child returned None in select phase")
                 return node # Fallback
    return current_node

def _mcts_expand(node: MCTSNode):
     """ Phase 2: Expand selected node if not terminal. """
     if not node.is_terminal():
         return node.expand()
     return node

def _mcts_simulate(node: MCTSNode, ai_original_piece: int):
    """
    Phase 3: Simulate a playout from the given node's state using an improved policy.
    Policy: 1. Win if possible, 2. Block opponent win if necessary, 3. Random.
    Returns result relative to the original AI player (+1 AI win, -1 AI loss, 0 draw).
    """
    if node.is_terminal():
        winner = node.state.winner
    else:
        # Simulate from a copy of the node's state
        temp_board = ConnectFourBoard()
        temp_board.board = np.copy(node.state.get_board())
        current_sim_player = node.player_turn # Player whose turn it is at this node

        while not temp_board.game_over:
            valid_moves = temp_board.get_valid_locations()
            if not valid_moves: break # Should be caught by game_over, but safety

            move = -1 # Reset move choice
            opponent_sim_player = 3 - current_sim_player

            # Priority 1: Check for winning move for current_sim_player
            for col in valid_moves:
                row = temp_board.get_next_open_row(col)
                if row != -1:
                    # Temporarily place piece to check for win
                    temp_board.board[row][col] = current_sim_player
                    if temp_board.is_winning_move(current_sim_player):
                        move = col
                        temp_board.board[row][col] = EMPTY
                        break
                    temp_board.board[row][col] = EMPTY

            # Priority 2: If no winning move, check for blocking move
            if move == -1:
                for col in valid_moves:
                    row = temp_board.get_next_open_row(col)
                    if row != -1:
                        temp_board.board[row][col] = opponent_sim_player
                        if temp_board.is_winning_move(opponent_sim_player):
                            move = col # Must block this column
                            temp_board.board[row][col] = EMPTY
                            break
                        temp_board.board[row][col] = EMPTY

            # Priority 3: If no win or block, choose randomly
            if move == -1:
                move = random.choice(valid_moves)

            # Perform the chosen move on the simulation board
            temp_board.drop_piece(move, current_sim_player)
            current_sim_player = 3 - current_sim_player

        winner = temp_board.winner

    # Determine result relative to the original AI player
    if winner == ai_original_piece: return 1.0
    elif winner == (3 - ai_original_piece): return -1.0
    else: return 0.0

def _mcts_backpropagate(node: MCTSNode, result: float):
    """ Phase 4: Update node statistics with result relative to AI player. """
    current_node = node
    while current_node is not None:
        current_node.visits += 1
        current_node.value += result # Accumulate result relative to AI
        current_node = current_node.parent

def get_move(board, piece, iterations=2000):
    start_time = time.time()

    root_state = ConnectFourBoard()
    root_state.board = np.copy(board)
    if root_state.game_over: return None # Game already over
    root_node = MCTSNode(state=root_state)
    root_node.player_turn = piece # Ensure root knows the actual current player

    valid_locations_at_root = root_state.get_valid_locations()
    if not valid_locations_at_root: return None # No moves possible

    if len(valid_locations_at_root) == 1:
        return valid_locations_at_root[0] # Only one possible move

    for i in range(iterations):
        selected_node = _mcts_select(root_node)
        expanded_node = _mcts_expand(selected_node)
        simulation_result = _mcts_simulate(expanded_node, piece) # Result relative to AI (piece)
        _mcts_backpropagate(expanded_node, simulation_result)

    # Choose best move based on most visits (robust)
    best_move = -1
    most_visits = -1

    if not root_node.children: # Should only happen if iterations=0 or root is terminal
         return random.choice(valid_locations_at_root) if valid_locations_at_root else None

    for move, child in root_node.children.items():
        if child.visits > most_visits:
            most_visits = child.visits
            best_move = move

    if best_move == -1: # Fallback if no children somehow
         return random.choice(valid_locations_at_root) if valid_locations_at_root else None

    return best_move

def name():
    """ Returns the name of this AI algorithm. """
    return "MonteCarlo AI"
