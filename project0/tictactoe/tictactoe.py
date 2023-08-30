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

    if terminal(board):
        print("Terminal board reached.")
        return

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
    if terminal(board):
        return

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
    if terminal(board):
        return

    exception_text = "Action not valid"
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

    return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """

    num_of_consecutive_signs_X = 0
    num_of_consecutive_signs_O = 0
    last_sign = ""

    print("board: {}".format(board))
    # Vertical
    for row in board:
        print("row: {}".format(row))
        for sign in row:
            if sign == last_sign:
                if sign == last_sign == X:
                    num_of_consecutive_signs_X += 1
                if sign == last_sign == O:
                    num_of_consecutive_signs_O += 1
            last_sign = sign

    # Horizontal
    last_sign = ""
    for horizontal_index in range(len(board) - 1):
        if board[horizontal_index] == last_sign:
            if board[horizontal_index] == X:
                num_of_consecutive_signs_X += 1
            if board[horizontal_index] == O:
                num_of_consecutive_signs_O += 1
        horizontal_index += 1
        last_sign = board[horizontal_index]

    # Diagonal
    if (board[0][0] == board[1][1] == board[2][2] == X) or (board[0][2] == board[1][1] == board[2][0] == X):
        return X

    if (board[0][0] == board[1][1] == board[2][2] == O) or (board[0][2] == board[1][1] == board[2][0] == O):
        return O

    if num_of_consecutive_signs_X == 3:
        return X

    if num_of_consecutive_signs_O == 3:
        return O

    return None


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
    if terminal(board):
        return None

    if player(board) == X:
        return max_value(board)[1]
    elif player(board) == O:
        return min_value(board)[1]


def max_value(board):
    best_action_max = None
    if terminal(board):
        return utility(board)
    v = -sys.maxsize - 1
    for action in actions(board):
        if v > min_value(result(board, action)[0]):
            best_action_max = action
        v = max(v, min_value(result(board, action)[0]))
    return v, best_action_max


def min_value(board):
    best_action_min = None
    if terminal(board):
        return utility(board)
    v = sys.maxsize
    for action in actions(board):
        print("board in min_value: {}".format(board))
        if v < min_value(result(board, action)[0]):
            best_action_min = action
        v = min(v, max_value(result(board, action)[0]))
    return v, best_action_min
