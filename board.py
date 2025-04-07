import numpy as np

ROW_COUNT = 6
COLUMN_COUNT = 7


def create_board():
    return np.zeros((ROW_COUNT, COLUMN_COUNT), dtype=int)


def drop_piece(board, row, col, piece):
    board[row][col] = piece


def is_valid_location(board, col):
    return board[0][col] == 0


def get_next_open_row(board, col):
    """Find the first empty row in the given column"""
    for r in range(ROW_COUNT-1, -1, -1):
        # for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r
    return -1  # Column is full


def winning_move(board, piece):
    # Check horizontal locations
    for c in range(COLUMN_COUNT-3):
        for r in range(ROW_COUNT):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                return True

    # Check vertical locations
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT-3):
            if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                return True

    # Check positively sloped diagonals
    for c in range(COLUMN_COUNT-3):
        for r in range(ROW_COUNT-3):
            if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                return True

    # Check negatively sloped diagonals
    for c in range(COLUMN_COUNT-3):
        for r in range(3, ROW_COUNT):
            if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                return True

    return False


def print_board(board):
    print(board)
    print("---------------------------")


def game_over(board):
    return winning_move(board, 1) or winning_move(board, 2) or len(get_valid_locations(board)) == 0


def get_valid_locations(board):
    """Return list of valid column numbers"""
    valid_locations = []
    for col in range(COLUMN_COUNT):
        if is_valid_location(board, col):
            valid_locations.append(col)
    return valid_locations


"""
# Example usage for human vs human game
if __name__ == "__main__":
    board = create_board()
    game_over = False
    turn = 0  # Player 1 starts (1), Player 2 is (2)

    while not game_over:
        # Alternate turns
        current_player = 1 if turn == 0 else 2
        valid_moves = get_valid_locations(board)

        print_board(board)
        print(f"Player {current_player}'s turn")
        print(f"Valid moves: {valid_moves}")

        # Get player input
        while True:
            try:
                col = int(input("Choose column (0-6): "))
                if col in valid_moves:
                    break
                else:
                    print("Invalid move. Try again.")
            except ValueError:
                print("Please enter a number between 0 and 6")

        # Make the move
        row = get_next_open_row(board, col)
        drop_piece(board, row, col, current_player)

        # Check for win
        if winning_move(board, current_player):
            print_board(board)
            print(f"Player {current_player} wins!")
            game_over = True

        # Check for tie
        if len(get_valid_locations(board)) == 0:
            print_board(board)
            print("Game Over - It's a tie!")
            game_over = True

        turn = 1 - turn  # Switch players
    """
