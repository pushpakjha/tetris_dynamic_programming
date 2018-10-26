"""Tetris game with manual and automatic modes.

Control keys for manual mode:
Down - Drop piece faster
Left/Right - Move piece
Up - Rotate Stone clockwise
Escape - Quit game
P - Pause game

Copyright (c) 2010 "Kevin Chabowski"<kevin@kch42.de>, original tetris game
Pushpak Jha, added tetris players
"""
import sys
import time
from random import randrange as rand

import pygame

from tetris_dp import constants
from tetris_dp import helpers
from tetris_dp import tetris_players

FAST_MODE = 0


class TetrisApp:
    """The main tetris application."""
    def __init__(self):
        self.score = 0
        self.piece = None
        self.piece_x = None
        self.piece_y = None
        self.gameover = None
        self.board = None
        self.paused = None
        self.init_game()
        if not FAST_MODE:
            pygame.init()  # pylint: disable=no-member
            pygame.key.set_repeat(250, 25)
            self.width = constants.CONFIG['cell_size']*constants.CONFIG['cols']
            self.height = constants.CONFIG['cell_size']*constants.CONFIG['rows']

            self.screen = pygame.display.set_mode((self.width, self.height))

            pygame.event.set_blocked(pygame.MOUSEMOTION)  # pylint: disable=no-member
            self.font_name = pygame.font.match_font('arial')

    @staticmethod
    def new_board():
        """Spawn a new empty board."""
        board = [[0 for _ in range(constants.CONFIG['cols'])]
                 for _ in range(constants.CONFIG['rows'])]
        board += [[1 for _ in range(constants.CONFIG['cols'])]]
        return board

    def draw_text(self, surf, text, size, x_position, y_position):
        """Draw text on the screen."""
        font = pygame.font.Font(self.font_name, size)
        text_surface = font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x_position, y_position)
        surf.blit(text_surface, text_rect)

    def new_piece(self):
        """Randomly spawn a new piece."""
        self.piece = constants.TETRIS_SHAPES[rand(len(constants.TETRIS_SHAPES))]
        self.piece_x = int(constants.CONFIG['cols'] / 2 - len(self.piece[0])/2)
        self.piece_y = 0

        if helpers.check_collision(self.board, self.piece, (self.piece_x, self.piece_y)):
            self.gameover = True

    def init_game(self):
        """Start a tetris game with a board and piece."""
        self.board = self.new_board()
        self.new_piece()

    def center_msg(self, msg):
        """Helper to add a message on the screen."""
        for i, line in enumerate(msg.splitlines()):
            msg_image = pygame.font.Font(
                pygame.font.get_default_font(), 12).render(
                    line, False, (255, 255, 255), (0, 0, 0))

            msgim_center_x, msgim_center_y = msg_image.get_size()
            msgim_center_x //= 2
            msgim_center_y //= 2

            self.screen.blit(msg_image, (self.width // 2-msgim_center_x,
                                         self.height // 2-msgim_center_y+i*22))

    def draw_matrix(self, board, offset):
        """Draw the actual board using pygame."""
        off_x, off_y = offset
        for y_position, row in enumerate(board):
            for x_position, val in enumerate(row):
                try:
                    if val:
                        pygame.draw.rect(
                            self.screen,
                            constants.COLORS[val],
                            pygame.Rect(
                                (off_x+x_position) * constants.CONFIG['cell_size'],
                                (off_y+y_position) * constants.CONFIG['cell_size'],
                                constants.CONFIG['cell_size'],
                                constants.CONFIG['cell_size']), 0)
                        self.draw_text(
                            self.screen, str(self.score), 18,
                            constants.CONFIG['cell_size'] * constants.CONFIG['rows'] / 20,
                            10)
                except IndexError:
                    print('***' * 20)
                    print('YOU SHOULD NOT BE HERE')
                    print(self.board)
                    print(self.piece)
                    print('***' * 20)
                    self.gameover = True

    def move(self, delta_x):
        """For manual play move the piece left or right."""
        if not self.gameover and not self.paused:
            new_x = self.piece_x + delta_x
            if new_x < 0:
                new_x = 0
            if new_x > constants.CONFIG['cols'] - len(self.piece[0]):
                new_x = constants.CONFIG['cols'] - len(self.piece[0])
            if not helpers.check_collision(self.board, self.piece, (new_x, self.piece_y)):
                self.piece_x = new_x

    def quit(self):
        """Quits the game."""
        self.center_msg("Exiting...")
        pygame.display.update()
        sys.exit()

    def drop(self):
        """Drops the piece into place and spawns the next one."""
        if not self.gameover and not self.paused:
            self.board = helpers.add_piece_to_board(self.board, self.piece,
                                                    (self.piece_x, self.piece_y))
            self.new_piece()
            while True:
                for i, row in enumerate(self.board[:-1]):
                    if 0 not in row:
                        self.board = helpers.remove_row(self.board, i)
                        self.score += 1
                        break
                else:
                    break

    def rotate_piece(self):
        """Rotate a piece as long as it won't cause a collision."""
        if not self.gameover and not self.paused:
            new_piece = helpers.rotate_clockwise(self.piece)
            if not helpers.check_collision(self.board,
                                           new_piece,
                                           (self.piece_x, self.piece_y)):
                self.piece = new_piece

    def toggle_pause(self):
        """Pauses the game."""
        self.paused = not self.paused

    def start_game(self):
        """Starts a tetris game."""
        if self.gameover:
            self.init_game()
            self.gameover = False

    def run(self):  # pylint: disable=too-many-branches
        """Main game loop for the automatic playing tetris game."""
        self.gameover = False
        self.paused = False

        if not FAST_MODE:
            pygame.time.set_timer(pygame.USEREVENT+1, constants.CONFIG['delay'])  # pylint: disable=no-member
            pygame_clock = pygame.time.Clock()
        while True:
            if not FAST_MODE:
                self.screen.fill((0, 0, 0))
            if self.gameover:
                if not FAST_MODE:
                    self.center_msg("""Game Over! Press space to continue""")
                    print('Final Score: {}'.format(self.score))
                    time.sleep(1)
                    self.quit()
                else:
                    return self.score
            else:
                if not FAST_MODE:
                    if self.paused:
                        self.center_msg("Paused")
                    else:
                        self.draw_matrix(self.board, (0, 0))
                        self.draw_matrix(self.piece, (self.piece_x, self.piece_y))
            if not FAST_MODE:
                pygame.display.update()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:  # pylint: disable=no-member
                        self.quit()
                    else:
                        pass
            self.piece_x, self.piece_y, self.piece = tetris_players.single_stage_player(
                self.board, self.piece)
            self.drop()
            if not FAST_MODE:
                time.sleep(0.6)
                pygame_clock.tick(constants.CONFIG['maxfps'])

    def manual_run(self):
        """Main game loop if you want to play manually with the arrow keys."""
        key_actions = {
            'ESCAPE': self.quit,
            'LEFT': lambda: self.move(-1),
            'RIGHT': lambda: self.move(+1),
            'DOWN': self.manual_drop,
            'UP': self.rotate_piece,
            'p': self.toggle_pause,
            'SPACE': self.start_game
        }

        self.gameover = False
        self.paused = False

        pygame.time.set_timer(pygame.USEREVENT + 1, constants.CONFIG['delay'])  # pylint: disable=no-member
        pygame_clock = pygame.time.Clock()
        while True:
            self.screen.fill((0, 0, 0))
            if self.gameover:
                self.center_msg("""Game Over!""")
                print('Final Score: {}'.format(self.score))
                time.sleep(1)
                self.quit()
            else:
                if self.paused:
                    self.center_msg("Paused")
                else:
                    self.draw_matrix(self.board, (0, 0))
                    self.draw_matrix(self.piece,
                                     (self.piece_x,
                                      self.piece_y))
            if not FAST_MODE:
                pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.USEREVENT + 1:  # pylint: disable=no-member
                    self.manual_drop()
                elif event.type == pygame.QUIT:  # pylint: disable=no-member
                    self.quit()
                elif event.type == pygame.KEYDOWN:  # pylint: disable=no-member
                    for key in key_actions:
                        if event.key == eval("pygame.K_" + key):  # pylint: disable=eval-used
                            key_actions[key]()

            pygame_clock.tick(constants.CONFIG['maxfps'])

    def manual_drop(self):
        """The drop function when playing manually.

        This slowly drops a piece to animate a falling piece on the board. When using the
        automatic tetris players we don't care about that so the drop functions are different.
        """
        if not self.gameover and not self.paused:
            self.piece_y += 1
            if helpers.check_collision(self.board, self.piece, (self.piece_x, self.piece_y)):
                self.board = helpers.add_piece_to_board(self.board, self.piece,
                                                        (self.piece_x, self.piece_y))
                self.new_piece()
                while True:
                    for i, row in enumerate(self.board[:-1]):
                        if 0 not in row:
                            self.board = helpers.remove_row(
                                self.board, i)
                            self.score += 1
                            break
                    else:
                        break
