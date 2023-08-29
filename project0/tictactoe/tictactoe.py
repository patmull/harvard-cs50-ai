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
    for row in board():
        for sign in row:
            if sign == last_sign:
                num_of_consecutive_signs += 1
            last_sign = sign

    # TODO: Add another options for the winners

    if num_of_consecutive_signs == 3:
        return player(board)
    else:
        return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    raise NotImplementedError


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    raise NotImplementedError


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    raise NotImplementedError
