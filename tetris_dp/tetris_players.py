"""Various automatic tetris players."""
import random
from multiprocessing.pool import ThreadPool
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
    new_x = random.randint(0, constants.CONFIG['cols'])
    if new_x > constants.CONFIG['cols'] - len(piece[0]):
        new_x = constants.CONFIG['cols'] - len(piece[0])
    if not helpers.check_collision(board, piece, (new_x, shape_y)):
        shape_x = new_x
    return shape_x, final_shape


def single_stage_player(board, piece):
    """Player which returns the lowest cost move given the current board and piece."""
    cost_to_move = _get_costs_of_moves(board, piece)
    min_cost = min(cost_to_move.keys())
    return cost_to_move[min_cost]


def lookahead_player(board, piece):
    """Player which returns the lowest cost move by evaluating multiple stage lookaheads."""
    cost_to_move = _get_costs_of_moves(board, piece)
    sorted_costs = list(cost_to_move.keys())
    sorted_costs.sort()
    final_adjusted_costs = _simulate_stages(sorted_costs, cost_to_move, board)
    min_future_cost = min(final_adjusted_costs.keys())
    return final_adjusted_costs[min_future_cost]


def _simulate_stages(sorted_costs, cost_to_move, board):
    """Simulate the next few moves of the game and get future costs."""
    pool = ThreadPool(processes=4)
    final_adjusted_costs = {}
    results = []
    for cost in sorted_costs[:4]:
        results.append(pool.apply_async(_simulate_stage_threaded, args=(board, cost_to_move, cost)))
    pool.close()
    pool.join()
    results = [r.get() for r in results]
    for adjusted_cost in results:
        final_adjusted_costs.update(adjusted_cost)
    return final_adjusted_costs


def _simulate_stage_threaded(board, cost_to_move, cost):
    """Simulate the next few moves of the game for a given cost."""
    cur_x, cur_y, cur_piece = cost_to_move[cost]
    future_costs = []
    adjusted_costs = {}
    for _ in range(0, 1):
        interm_board, _ = helpers.get_interm_board(board, cur_piece, (cur_x, cur_y))
        future_cost = 0
        for _ in range(0, 1):
            rand_piece = random.choice(constants.TETRIS_SHAPES)
            best_x, best_y, best_piece = single_stage_player(interm_board, rand_piece)
            interm_board = helpers.add_piece_to_board(
                interm_board, best_piece, (best_x, best_y))
            future_cost += _calculate_simple_cost(interm_board) / 1
        future_costs.append(future_cost)
    expected_future_cost = sum(future_costs) / len(future_costs)
    final_cost = cost + expected_future_cost
    adjusted_costs[final_cost] = cost_to_move[cost]
    return adjusted_costs


def _get_costs_of_moves(board, piece):
    """Get the costs of all the moves given a board and piece."""
    cost_to_move = {}
    max_x = len(board[0])

    for rand_rotation in range(0, 4):
        if rand_rotation:
            piece = helpers.rotate_clockwise(piece)
        for new_x in range(0, max_x - len(piece[0]) + 1):
            interm_piece_y = 0
            while not helpers.check_collision(board, piece, (new_x, interm_piece_y)):
                interm_piece_y += 1
            interm_board, removed_rows = helpers.get_interm_board(
                board, piece, (new_x, interm_piece_y))
            # interm_cost = _calculate_simple_cost(interm_board, removed_rows)
            interm_cost = _calculate_dellacheries_cost(
               interm_board, removed_rows, (new_x, interm_piece_y))
            cost_to_move[interm_cost] = (new_x, interm_piece_y, piece)
    return cost_to_move


def _calculate_simple_cost(board, removed_rows=0):
    """Given a board calculate the cost."""
    max_x = len(board[0])
    max_y = len(board)
    weights = []
    height_cost = 15
    diff_cost = 1
    max_height_cost = 20
    hole_cost = 10
    removed_row_cost = -10
    weights.extend(max_x * [height_cost])
    weights.extend((max_x - 1) * [diff_cost])
    weights.append(max_height_cost)
    weights.append(hole_cost)
    weights.append(removed_row_cost)
    # Get the costs based on col height
    all_heights, costs = _find_column_heights(board, max_x, max_y)

    # Get the costs based on col height differences
    for ind in range(0, len(costs) - 1):
        costs.append(abs(costs[ind + 1] - costs[ind]))

    # Add costs for max height
    costs.append(max(all_heights))
    # Increase costs if holes were created
    costs.append(helpers.find_all_holes(board))
    # Decrease costs if rows were removed
    costs.append(removed_rows)
    return _get_cost_from_vectors(costs, weights)


def _calculate_dellacheries_cost(board, removed_rows, offset):
    """Given a board calculate the cost using Dellacherie's criteria.

    See ref #1 https://hal.inria.fr/hal-00926213/document
    See ref #2 https://pdfs.semanticscholar.org/2d0d/eb544439e96f9f84fe1afc653bbf2f3bcc96.pdf
    See ref #3 https://hal.inria.fr/inria-00418930/document
    (f1) Landing height: The height at which the current piece fell.
    (f2) Eroded pieces: The contribution of the last piece to the cleared lines time the number
     of cleared lines.
    (f3) Row transitions: Number of filled cells adjacent to empty cells
     summed over all rows.
    (f4) Column transition: Same as (f3) summed over all columns.
     Note that borders count as filled cells.
    (f5) Number of holes: The number of empty cells with at least one filled cell above.
    (f6) Cumulative wells: The sum of the accumulated depths of the wells.
    """
    _, off_y = offset

    # Original weights stolen from ref #2 above
    # weights = [4.5001588, -3.4181268, 3.278882, 9.3486953, 7.8992654, 3.3855972]
    weights = [6.5001588, -5.4181268, 3.278882, 9.3486953, 7.8992654, 5.3855972]
    costs = []

    # Add to costs
    # Rule 1
    costs.append(constants.CONFIG['rows'] + 1 - off_y)
    # Rule 2
    costs.append(removed_rows**4)
    # Rule 3
    num_holes, num_wells, row_transitions, col_transitions = helpers.find_holes_and_wells(board)
    costs.append(row_transitions)
    # Rule 4
    costs.append(col_transitions)
    # Rule 5
    costs.append(num_holes)
    # Rule 6
    costs.append(num_wells)

    # Get the final cost
    return _get_cost_from_vectors(costs, weights)


def _get_cost_from_vectors(cost, weights):
    """Use matrix math to get a scalar cost."""
    cost_matrix = numpy.matrix([cost])
    weights_matrix = numpy.matrix([weights])
    get_cost = cost_matrix * weights_matrix.getH()  # transpose
    return get_cost.item(0)


def _find_column_heights(board, max_x, max_y):
    """Find the column heights on the board."""
    all_heights = []
    cost = []

    for x_position in range(0, max_x):
        for y_position in range(0, max_y):
            if board[y_position][x_position] == -1:
                cost.append(99999)
                all_heights.append(99)
                break
            elif board[y_position][x_position]:
                cost.append((21 - y_position)**2)
                all_heights.append(21 - y_position)
                break
    return all_heights, cost
