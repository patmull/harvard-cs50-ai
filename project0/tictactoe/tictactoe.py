"""
Tic Tac Toe Player
"""
import copy
import math

X = "X"
O = "O"
EMPTY = None


class GameState:
    player_last_played = None


game_state = GameState


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """

    # Game is already over
    if board == initial_state():
        game_state.player_last_played = X
        return X

    if terminal(board):
        game_state.player_last_played = None
        return

    if game_state.player_last_played == X:
        return O
    elif game_state.player_last_played == O:
        return X
    else:
        return ValueError("THe value of the variable is neither X, and neither O.")


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    all_possible_actions = set()

    if terminal(board):
        return

    for i in board():
        for j in board():
            if board[i][j] != X and board[i][j] != O:
                all_possible_actions.add((i, j))

    return all_possible_actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    if type(action) != tuple:
        raise ValueError

    if type(action[0]) != int or type(action[1]) != int:
        raise ValueError

    # Just to make it clear that the original should be left unmodified
    new_board = copy.deepcopy(board)
    new_board[action[0]][action[1]] = player(board)

    raise new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """

    num_of_consecutive_signs = 0
    last_sign = ""

    # Vertical
    for row in board():
        for sign in row:
            if sign == last_sign:
                num_of_consecutive_signs += 1
            last_sign = sign

    # TODO: Add another options for the winners
    max_vertical_index = len(board())

    # Horizontal
    last_sign = ""
    for horizontal_index in range(board()[0]):
        if board()[horizontal_index] == last_sign:
            num_of_consecutive_signs += 1
        horizontal_index += 1
        last_sign = board()[horizontal_index]

    # Diagonal
    if (board[0][0] == board[1][1] == board[2][2]) or (board[0][2] == board[1][1] == board[2][0]):
        return player(board)

    if num_of_consecutive_signs == 3:
        return player(board)
    else:
        return False


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """

    def only_empty(actual_board):
        for row in actual_board:
            for sign in row:
                if sign is not None:
                    return False

        return True

    if winner(board) or only_empty(board):
        return True
    else:
        return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board):
        if winner(board) == X:
            return 1

        if winner(board) == O:
            return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    raise NotImplementedError
