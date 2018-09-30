"""Various automatic tetris players."""
import random

import numpy

from tetris_dp import constants
from tetris_dp import helpers


def random_player(board, piece, shape_x, shape_y):
    """Player which returns a random move for a given piece and board."""
    shape_x = shape_x
    final_shape = piece

    # Get random rotation
    rand_rotation = random.randint(0, 3)
    for _ in range(0, rand_rotation):
        piece = helpers.rotate_clockwise(piece)
    if not helpers.check_collision(board, piece, (shape_x, shape_y)):
        final_shape = piece

    # Get random x_position position
    new_x = random.randint(0, 9)
    if new_x > constants.CONFIG['cols'] - len(piece[0]):
        new_x = constants.CONFIG['cols'] - len(piece[0])
    if not helpers.check_collision(board, piece, (new_x, shape_y)):
        shape_x = new_x
    return shape_x, final_shape


def lookahead_player(board, piece):
    """Player which returns the lowest cost move by evaluating multiple stage lookaheads."""
    cost_to_move = get_costs_of_moves(board, piece)
    sorted_costs = list(cost_to_move.keys())
    sorted_costs.sort()
    final_adjusted_costs = simulate_stages(sorted_costs, cost_to_move, board)
    min_future_cost = min(final_adjusted_costs.keys())
    return final_adjusted_costs[min_future_cost]


def simulate_stages(sorted_costs, cost_to_move, board):
    """Simulate the next few moves of the game and get future costs."""
    final_adjusted_costs = {}
    for cost in sorted_costs[:3]:
        cur_x, cur_y, cur_piece = cost_to_move[cost]
        future_costs = []
        for _ in range(0, 5):
            interm_board = helpers.get_interm_board(board, cur_piece, (cur_x, cur_y))
            for _ in range(0, 3):
                rand_piece = random.choice(constants.TETRIS_SHAPES)
                best_x, best_y, best_piece = single_stage_player(interm_board, rand_piece)
                interm_board = helpers.add_piece_to_board(
                    interm_board, best_piece, (best_x, best_y))
            future_cost = calculate_simple_cost(interm_board)
            future_costs.append(future_cost)
        expected_future_cost = sum(future_costs)/len(future_costs)/3
        final_cost = str(cost + expected_future_cost)
        final_adjusted_costs[final_cost] = cost_to_move[cost]
    return final_adjusted_costs


def single_stage_player(board, piece):
    """Player which returns the lowest cost move given the current board and piece."""
    cost_to_move = get_costs_of_moves(board, piece)
    min_cost = min(cost_to_move.keys())
    return cost_to_move[min_cost]


def get_costs_of_moves(board, piece):
    """Get the costs of all the moves given a board and piece."""
    cost_to_move = {}
    max_x = len(board[0])
    # Get random rotation
    for rand_rotation in range(0, 4):
        if rand_rotation:
            piece = helpers.rotate_clockwise(piece)
        for new_x in range(0, max_x - len(piece[0]) + 1):
            interm_piece_y = 0
            while not helpers.check_collision(board, piece, (new_x, interm_piece_y)):
                interm_piece_y += 1
            interm_board = helpers.get_interm_board(board, piece, (new_x, interm_piece_y))
            interm_cost = calculate_simple_cost(interm_board)
            cost_to_move[interm_cost] = (new_x, interm_piece_y, piece)
    return cost_to_move


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
    cost.append(helpers.find_all_holes(board))
    cost.append(1)
    cost_matrix = numpy.matrix([cost])
    weights_matrix = numpy.matrix([weights])
    get_cost = cost_matrix*weights_matrix.getH()
    return get_cost.item(0)
