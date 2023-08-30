"""
Tic Tac Toe Player
"""
import copy
import sys
X = "X"
O = "O"
EMPTY = None


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

    if board == initial_state():
        print("board at initial state")
        return X

    # Game is already over
    # WARNING: KEEPING THIS THERE WOULD RESULT IN A FAULTY CODE WITH A MAXIMUM RECURSION ERROR!!!

    list_of_num_of_X = [row.count(X) for row in board]
    list_of_num_of_O = [row.count(O) for row in board]

    sum_of_X = sum(list_of_num_of_X)
    sum_of_O = sum(list_of_num_of_O)

    print("sum_of_X: {}".format(sum_of_X))
    print("sum_of_Y: {}".format(sum_of_O))

    if sum_of_X > sum_of_O:
        return O
    elif sum_of_X == sum_of_O:
        return X
    else:
        raise ValueError("Unexpected number of X's and O's.")


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """

    all_possible_actions = set()

    print("board: {}".format(board))

    for i, row in enumerate(board):
        for j, character in enumerate(row):
            if character != X and character != O:
                all_possible_actions.add((i, j))

    print("all_possible_actions: {}".format(all_possible_actions))
    return all_possible_actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    """
    print("action type:")
    print(action)
    print(type(action))
    """

    exception_text = "Invalid action"
    print("board: {}".format(board))
    print("player(board): {}".format(player(board)))
    print("action: {}".format(action))

    if not isinstance(action, tuple):
        raise Exception(exception_text)

    if type(action[0]) != int or type(action[1]) != int:
        raise Exception(exception_text)

    # Just to make it clear that the original should be left unmodified
    new_board = copy.deepcopy(board)
    # print("new_board: {}".format(new_board))

    new_board[action[0]][action[1]] = player(board)

    print("new_board: {}".format(new_board))

    return new_board


def check_horizontal_winner(board, player_sign):
    print("board in check_horizontal_winner: {}".format(board))
    if ((board[0][0] == board[1][0] == board[2][0] == player_sign)
            or (board[0][0] == board[1][0] == board[2][0] == player_sign)
            or (board[2][0] == board[2][1] == board[2][2] == player_sign)):
        return player_sign
    else:
        return None


def check_vertical_winner(board, player_sign):
    if ((board[0][0] == board[0][1] == board[0][2] == player_sign)
            or (board[1][0] == board[1][1] == board[1][2] == player_sign)
            or (board[2][0] == board[2][1] == board[2][2] == player_sign)):
        return player_sign
    else:
        return None


def check_diagonal_winner(board, player_sign):
    # Diagonal
    if (board[0][0] == board[1][1] == board[2][2] == X) or (board[0][2] == board[1][1] == board[2][0] == player_sign):
        return player_sign
    else:
        return None


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """

    num_of_consecutive_signs_X = 0
    num_of_consecutive_signs_O = 0
    last_sign = ""
    winner_player = None

    print("board in winner: {}".format(board))

    # Horizontal
    if winner_player is None:
        print("winner_player is none board: {}".format(board))
        winner_player = check_horizontal_winner(board, X)
    if winner_player is None:
        winner_player = check_horizontal_winner(board, O)
    if winner_player is None:
        winner_player = check_diagonal_winner(board, X)
    if winner_player is None:
        winner_player = check_diagonal_winner(board, O)
    if winner_player is None:
        winner_player = check_vertical_winner(board, X)
    if winner_player is None:
        winner_player = check_vertical_winner(board, O)

    return winner_player


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """

    def full_board_filled(actual_board):
        for row in actual_board:
            for sign in row:
                if sign is None:
                    return False

        return True

    print("board before winner: {}".format(board))
    if winner(board) is None:
        return False
    else:
        if winner(board) == X or winner(board) == O or full_board_filled(board):
            return True
        else:
            return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) is not None:
        if winner(board) == X:
            print("return 1")
            return 1

        if winner(board) == O:
            print("return O")
            return -1
    else:
        print("return 0")
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    print("Terminal board check in minimax")
    if terminal(board):
        return None

    if player(board) == X:
        print("board in minimax: {}".format(board))
        return max_value(board)[1]
    elif player(board) == O:
        print("board in minimax: {}".format(board))
        return min_value(board)[1]


def max_value(board):
    best_action_max = None
    print("Terminal board check in max_value")
    print("board in max_value: {}".format(board))
    if terminal(board):
        return utility(board), best_action_max
    v = -sys.maxsize - 1
    for action in actions(board):
        min_val = min_value(result(board, action))[0]
        if min_val > v:
            v = min_val
            best_action_max = action
    return v, best_action_max


def min_value(board):
    best_action_min = None
    print("Terminal board check in min_value")
    if terminal(board):
        return utility(board), best_action_min
    v = sys.maxsize
    for action in actions(board):
        print("board in min_value: {}".format(board))
        max_val = max_value(result(board, action))[0]
        if max_val < v:
            v = max_val
            best_action_min = action

        print("v: {}".format(v))
        print("best_action_min: {}".format(best_action_min))
    return v, best_action_min
