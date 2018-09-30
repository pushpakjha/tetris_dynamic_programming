"""Tetris player logic."""
import copy
import random
import numpy

from tetris_dp.constants import CONFIG


def rotate_clockwise(piece):
    """Rotate the piece clockwise."""
    return [[piece[y_position][x_position] for y_position in range(len(piece))]
            for x_position in range(len(piece[0]) - 1, -1, -1)]


def check_collision(board, piece, offset):
    """Check if the piece, board and given position causes a collision."""
    off_x, off_y = offset
    for row_index, row in enumerate(piece):
        for column_index, cell in enumerate(row):
            try:
                if cell and board[row_index + off_y][column_index + off_x]:
                    return True
            except IndexError:
                return True
    return False


def remove_row(board, row):
    """Remove a filled row from the board."""
    del board[row]
    return [[0 for _ in range(CONFIG['cols'])]] + board


def add_piece_to_board(board, piece, offset):
    """Add the piece to the board at the given position."""
    off_x, off_y = offset
    for row_index, row in enumerate(piece):
        for column_index, val in enumerate(row):
            board[row_index + off_y - 1][column_index + off_x] += val
    return board


def get_interm_board(board, piece, offset):
    """Add a piece to a deepcopy of the board and return it for cost evaluation.

    Note since some of the out of bounds conditions are weird this function checks to see
    if pieces will overlap with something on the board. If found it will return -1 at the
    top of the board for the cost functions to associate it with being an invalid move.
    """
    off_x, off_y = offset
    interm_board = copy.deepcopy(board)
    for row_index, row in enumerate(piece):
        for column_index, val in enumerate(row):
            y_offset = row_index + off_y
            if interm_board[y_offset][column_index + off_x] and val:
                interm_board[0][column_index + off_x] = -1
            else:
                interm_board[y_offset][column_index + off_x] += val
    for i, row in enumerate(interm_board[:-1]):
        if 0 not in row:
            interm_board = remove_row(interm_board, i)
    return interm_board


def new_board():
    """Spawn a new empty board."""
    board = [[0 for _ in range(CONFIG['cols'])] for _ in range(CONFIG['rows'])]
    board += [[1 for _ in range(CONFIG['cols'])]]
    return board


def get_random_position(board, piece, shape_x, shape_y):
    """Player which returns a random move for a given piece and board."""
    shape_x = shape_x
    final_shape = piece

    # Get random rotation
    rand_rotation = random.randint(0, 3)
    for _ in range(0, rand_rotation):
        piece = rotate_clockwise(piece)
    if not check_collision(board, piece, (shape_x, shape_y)):
        final_shape = piece

    # Get random x_position position
    new_x = random.randint(0, 9)
    if new_x > CONFIG['cols'] - len(piece[0]):
        new_x = CONFIG['cols'] - len(piece[0])
    if not check_collision(board, piece, (new_x, shape_y)):
        shape_x = new_x
    return shape_x, final_shape


def one_step_lookahead(board, piece):
    """Player which returns the lowest cost move given the current board and piece."""
    cost_to_move = {}
    max_x = len(board[0])
    # Get random rotation
    for rand_rotation in range(0, 4):
        if rand_rotation:
            piece = rotate_clockwise(piece)
        for new_x in range(0, max_x - len(piece[0]) + 1):
            interm_shape_y = 0
            while not check_collision(board, piece, (new_x, interm_shape_y)):
                interm_shape_y += 1
            interm_board = get_interm_board(board, piece, (new_x, interm_shape_y - 1))
            interm_cost = calculate_simple_cost(interm_board)
            cost_to_move[interm_cost] = (new_x, interm_shape_y, piece)
    min_cost = min(cost_to_move.keys())
    return cost_to_move[min_cost]


def calculate_simple_cost(board):
    """Given a board calculate the cost."""
    max_x = len(board[0])
    max_y = len(board)
    all_heights = []
    cost = []
    weights = []
    height_cost = 15
    diff_cost = 3
    max_height_cost = 50
    hole_cost = 5
    weights.extend(max_x * [height_cost])
    weights.extend((max_x - 1) * [diff_cost])
    weights.append(max_height_cost)
    weights.append(hole_cost)
    weights.append(-1)

    # Get the costs based on col height
    for x_position in range(0, max_x):
        for y_position in range(0, max_y):
            if board[y_position][x_position] == -1:
                cost.append(99999)
                break
            elif board[y_position][x_position]:
                cost.append((25 - y_position)**2)
                all_heights.append(25-y_position)
                break

    # Get the costs based on col height differences
    for ind in range(0, len(cost) - 1):
        cost.append(abs(cost[ind + 1] - cost[ind]))

    # Add cost for max height
    cost.append(max(all_heights))

    # Increase costs if holes were created
    cost.append(find_all_holes(board))
    cost.append(1)
    cost_matrix = numpy.matrix([cost])
    weights_matrix = numpy.matrix([weights])
    get_cost = cost_matrix*weights_matrix.getH()
    return get_cost.item(0)


def find_all_holes(board):
    """Find all empty holes in board."""
    max_x = len(board[0]) - 1
    max_y = len(board) - 1
    total_holes = 0
    for x_position in range(0, max_x):
        for y_position in range(0, max_y):
            if find_holes_in_board(board, x_position, y_position, max_x, max_y):
                total_holes += 1
    return total_holes


def find_holes_in_board(board, x_position, y_position, max_x, max_y):
    """Looks for a hole at a single spot on the board."""
    found_hole = False
    filled = 0
    plus_y = y_position + 1
    minus_y = y_position - 1
    if plus_y > max_y:
        plus_y = max_y
        filled += 1
    if minus_y < 0:
        minus_y = 0
    plus_x = x_position + 1
    minus_x = x_position - 1
    if plus_x > max_x:
        plus_x = max_x
        filled += 1
    if minus_x < 0:
        minus_x = 0
        filled += 1
    if board[plus_y][x_position]:
        filled += 1
    if board[minus_y][x_position]:
        filled += 1
    if board[y_position][plus_x]:
        filled += 1
    if board[y_position][minus_x]:
        filled += 1
    if filled >= 3 and not board[y_position][x_position]:
        found_hole = True
    return found_hole
