"""Tetris player logic."""
import random

# The configuration
config = {
    'cell_size':	20,
    'cols':		10,
    'rows':		20,
    'delay':	750,
    'maxfps':	30
}


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
            mat1[cy+off_y-1	][cx+off_x] += val
    return mat1


def new_board():
    board = [[0 for _ in range(config['cols'])] for _ in range(config['rows'])]
    board += [[1 for _ in range(config['cols'])]]
    return board


def get_random_position(board, shape, shape_x, shape_y):
    stone_x = shape_x
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
        stone_x = new_x

    return stone_x, final_shape
