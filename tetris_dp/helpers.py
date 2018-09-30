"""Tetris player logic."""
import copy
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


def get_interm_board(board, shape, offset):
    off_x, off_y = offset
    interm_board = copy.deepcopy(board)
    for cy, row in enumerate(shape):
        # print('cy: {}'.format(cy))
        # print('row: {}'.format(row))
        for cx, val in enumerate(row):
            # print('cx: {}'.format(cx))
            # print('val: {}'.format(val))
            y_offset = cy + off_y
            if interm_board[y_offset][cx + off_x] and val:
                interm_board[0][cx + off_x] = -1
                # print('y_offset: {}'.format(y_offset))
                # print('cx + off_x: {}'.format(cx + off_x))
            else:
                interm_board[y_offset][cx + off_x] += val
    for i, row in enumerate(interm_board[:-1]):
        if 0 not in row:
            interm_board = remove_row(interm_board, i)
    return interm_board


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
        #print('RAND ROTOTATION: {}'.format(rand_rotation))
        for new_x in range(0, max_x - len(shape[0]) + 1):
            #print('NEW X: {}'.format(new_x))
            interm_shape_y = 0
            while not check_collision(board, shape, (new_x, interm_shape_y)):
                interm_shape_y += 1
            interm_board = get_interm_board(board, shape, (new_x, interm_shape_y - 1))
            interm_cost = calculate_simple_cost(interm_board)
            #print('INTERM COST: {}'.format(interm_cost))
            cost_to_move[interm_cost] = (new_x, interm_shape_y, shape)
    min_cost = min(cost_to_move.keys())
    return cost_to_move[min_cost]


def calculate_simple_cost(board):
    max_x = len(board[0])
    max_y = len(board)
    all_heights = []
    cost = []
    weights = []
    cleared_rows = 0
    height_cost = 15
    diff_cost = 3
    max_height_cost = 10
    clear_row_cost = -10
    hole_cost = 0.5
    weights.extend(max_x * [height_cost])
    weights.extend((max_x - 1) * [diff_cost])
    # weights.append(clear_row_cost)
    weights.append(max_height_cost)
    weights.append(hole_cost)
    weights.append(-1)
    # Get the costs based on col height
    for x in range(0, max_x):
        for y in range(0, max_y):
            if board[y][x] == -1:
                cost.append(99999)
                break
            elif board[y][x]:
                cost.append((25 - y))
                all_heights.append(25-y)
                break
    # Get the costs based on col height differences
    for ind in range(0, len(cost) - 1):
        cost.append(abs(cost[ind + 1] - cost[ind]))
    # Reduce the cost if rows got cleared
    for _, row in enumerate(board[:-1]):
        if 0 not in row:
            cleared_rows += 1
    # cost.append(cleared_rows)
    # Add cost for max height
    cost.append(max(all_heights))
    # Increase costs if holes were created
    cost.append(find_all_holes(board))
    cost.append(1)
    # print('cost list: {}'.format(cost))
    # print('interm board: {}'.format(board))
    cost_matrix = numpy.matrix([cost])
    weights_matrix = numpy.matrix([weights])
    get_cost = cost_matrix*weights_matrix.getH()
    return get_cost.item(0)


def find_all_holes(board):
    max_x = len(board[0]) - 1
    max_y = len(board) - 1
    total_holes = 0
    for x in range(0, max_x):
        for y in range(0, max_y):
            if find_holes_in_board(board, x, y, max_x, max_y):
                total_holes += 1
    # print('total_holes: {}'.format(total_holes))
    return total_holes


def find_holes_in_board(board, x, y, max_x, max_y):
    filled = 0
    plus_y = y + 1
    minus_y = y - 1
    if plus_y > max_y:
        plus_y = max_y
    if minus_y < 0:
        minus_y = 0
    plus_x = x + 1
    minus_x = x - 1
    if plus_x > max_x:
        plus_x = max_x
    if minus_x < 0:
        minus_x = 0
    if board[plus_y][x]:
        filled += 1
    if board[minus_y][x]:
        filled += 1
    if board[y][plus_x]:
        filled += 1
    if board[y][minus_x]:
        filled += 1
    if filled >= 3 and not board[y][x]:
        return True
    else:
        return False
