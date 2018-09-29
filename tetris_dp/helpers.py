"""Tetris player logic."""
import numpy
import random

# The configuration
config = {
    'cell_size':	20,
    'cols':		10,
    'rows':		20,
    'delay':	750,
    'maxfps':	30
}

colors = [(0,   0,   0), (255, 0,   0), (0,   150, 0), (0,   0,   255),
          (255, 120, 0), (255, 255, 0), (180, 0,   255), (0,   220, 220)]

# Define the shapes of the single parts
tetris_shapes = [
    [[1, 1, 1],
     [0, 1, 0]],

    [[0, 2, 2],
     [2, 2, 0]],

    [[3, 3, 0],
     [0, 3, 3]],

    [[4, 0, 0],
     [4, 4, 4]],

    [[0, 0, 5],
     [5, 5, 5]],

    [[6, 6, 6, 6]],

    [[7, 7],
     [7, 7]]
]


def rotate_clockwise(shape):
    return [[shape[y][x] for y in range(len(shape))] for x in range(len(shape[0]) - 1, -1, -1)]


def check_collision(board, shape, offset):
    off_x, off_y = offset
    for cy, row in enumerate(shape):
        for cx, cell in enumerate(row):
            try:
                if cell and board[cy + off_y][cx + off_x]:
                    return True
            except IndexError:
                return True
    return False


def remove_row(board, row):
    del board[row]
    return [[0 for _ in range(config['cols'])]] + board


def join_matrixes(mat1, mat2, mat2_off):
    off_x, off_y = mat2_off
    for cy, row in enumerate(mat2):
        for cx, val in enumerate(row):
            mat1[cy + off_y - 1][cx + off_x] += val
    return mat1


def get_interm_board(mat1, mat2, mat2_off):
    off_x, off_y = mat2_off
    interm_mat = new_board()
    for cy, row in enumerate(mat2):
        for cx, val in enumerate(row):
            interm_mat[cy + off_y - 1][cx + off_x] = mat1[cy + off_y - 1][cx + off_x] + val
    return interm_mat


def new_board():
    board = [[0 for _ in range(config['cols'])] for _ in range(config['rows'])]
    board += [[1 for _ in range(config['cols'])]]
    return board


def get_random_position(board, shape, shape_x, shape_y):
    shape_x = shape_x
    final_shape = shape

    # Get random rotation
    rand_rotation = random.randint(0, 3)
    for _ in range(0, rand_rotation):
        shape = rotate_clockwise(shape)
    if not check_collision(board, shape, (shape_x, shape_y)):
        final_shape = shape

    # Get random x position
    new_x = random.randint(0, 9)
    if new_x > config['cols'] - len(shape[0]):
        new_x = config['cols'] - len(shape[0])
    if not check_collision(board, shape, (new_x, shape_y)):
        shape_x = new_x
    return shape_x, final_shape


def one_step_lookahead(board, shape, shape_y):
    cost_to_move = {}
    max_x = len(board[0])
    # Get random rotation
    for rand_rotation in range(0, 4):
        if rand_rotation:
            shape = rotate_clockwise(shape)
        for new_x in range(0, max_x - len(shape[0]) + 1):
            interm_shape_y = shape_y + 1
            while not check_collision(board, shape, (new_x, interm_shape_y)):
                interm_shape_y += 1
            interm_board = get_interm_board(board, shape, (new_x, interm_shape_y))
            interm_cost = calculate_simple_cost(interm_board)
            cost_to_move[interm_cost] = (new_x, interm_shape_y, shape)
    min_cost = min(cost_to_move.keys())
    return cost_to_move[min_cost]


def calculate_simple_cost(board):
    max_x = len(board[0])
    max_y = len(board)
    cost = []
    weights = []
    height_cost = 5
    diff_cost = 1
    weights.extend(max_x * [height_cost])
    weights.extend((max_x - 1) * [diff_cost])
    for x in range(0, max_x):
        for y in range(0, max_y):
            if board[y][x]:
                cost.append(20 - y)
                break
    for ind in range(0, len(cost) - 1):
        cost.append(cost[ind + 1] - cost[ind])
    cost_matrix = numpy.matrix([cost])
    weights_matrix = numpy.matrix([weights])
    get_cost = cost_matrix*weights_matrix.getH()
    return get_cost.item(0)
