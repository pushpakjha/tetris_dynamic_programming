#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Very simple tetris implementation
# 
# Control keys:
# Down - Drop stone faster
# Left/Right - Move stone
# Up - Rotate Stone clockwise
# Escape - Quit game
# P - Pause game
#
# Have fun!

# Copyright (c) 2010 "Kevin Chabowski"<kevin@kch42.de>, original tetris game
# Pushpak Jha, added tetris player
import pygame
import sys
import time
from random import randrange as rand

from tetris_dp.helpers import *

FAST_MODE = 0


class TetrisApp(object):
    def __init__(self):
        pygame.init()
        pygame.key.set_repeat(250, 25)
        self.width = config['cell_size']*config['cols']
        self.height = config['cell_size']*config['rows']

        self.screen = pygame.display.set_mode((self.width, self.height))
        self.score = 0
        self.stone = None
        self.stone_x = None
        self.stone_y = None
        self.gameover = None
        self.board = None
        self.paused = None
        pygame.event.set_blocked(pygame.MOUSEMOTION)  # Block mouse movement
        self.init_game()

    def new_stone(self):
        self.stone = tetris_shapes[rand(len(tetris_shapes))]
        self.stone_x = int(config['cols'] / 2 - len(self.stone[0])/2)
        self.stone_y = 0

        if check_collision(self.board, self.stone, (self.stone_x, self.stone_y)):
            self.gameover = True

    def init_game(self):
        self.board = new_board()
        self.new_stone()

    def center_msg(self, msg):
        for i, line in enumerate(msg.splitlines()):
            msg_image = pygame.font.Font(
                pygame.font.get_default_font(), 12).render(
                    line, False, (255, 255, 255), (0, 0, 0))

            msgim_center_x, msgim_center_y = msg_image.get_size()
            msgim_center_x //= 2
            msgim_center_y //= 2

            self.screen.blit(msg_image, (
              self.width // 2-msgim_center_x,
              self.height // 2-msgim_center_y+i*22))

    def draw_matrix(self, matrix, offset):
        off_x, off_y = offset
        for y, row in enumerate(matrix):
            for x, val in enumerate(row):
                try:
                    if val and not FAST_MODE:
                        pygame.draw.rect(
                            self.screen,
                            colors[val],
                            pygame.Rect(
                                (off_x+x) * config['cell_size'],
                                (off_y+y) * config['cell_size'],
                                config['cell_size'],
                                config['cell_size']), 0)
                except IndexError:
                    print('***' * 20)
                    print('YOU SHOULD NOT BE HERE')
                    print(self.board)
                    print(self.stone)
                    print('***' * 20)
                    self.gameover = True

    def move(self, delta_x):
        if not self.gameover and not self.paused:
            new_x = self.stone_x + delta_x
            if new_x < 0:
                new_x = 0
            if new_x > config['cols'] - len(self.stone[0]):
                new_x = config['cols'] - len(self.stone[0])
            if not check_collision(self.board, self.stone, (new_x, self.stone_y)):
                self.stone_x = new_x

    def quit(self):
        self.center_msg("Exiting...")
        pygame.display.update()
        sys.exit()

    def drop(self):
        if not self.gameover and not self.paused:
            self.board = join_matrixes(self.board, self.stone, (self.stone_x, self.stone_y))
            self.new_stone()
            while True:
                for i, row in enumerate(self.board[:-1]):
                    if 0 not in row:
                        self.board = remove_row(self.board, i)
                        self.score += 1
                        break
                else:
                    break

    def rotate_stone(self):
        if not self.gameover and not self.paused:
            new_stone = rotate_clockwise(self.stone)
            if not check_collision(self.board,
                                   new_stone,
                                   (self.stone_x, self.stone_y)):
                self.stone = new_stone

    def toggle_pause(self):
        self.paused = not self.paused

    def start_game(self):
        if self.gameover:
            self.init_game()
            self.gameover = False

    def run(self):
        self.gameover = False
        self.paused = False

        pygame.time.set_timer(pygame.USEREVENT+1, config['delay'])
        pygame_clock = pygame.time.Clock()
        while True:
            self.screen.fill((0, 0, 0))
            if self.gameover:
                self.center_msg("""Game Over! Press space to continue""")
                print('Final Score: {}'.format(self.score))
                time.sleep(1)
                self.quit()
            else:
                if self.paused:
                    self.center_msg("Paused")
                else:
                    self.draw_matrix(self.board, (0, 0))
                    self.draw_matrix(self.stone, (self.stone_x, self.stone_y))
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                else:
                    pass
            # self.stone_x, self.stone = get_random_position(
            #   self.board, self.stone, self.stone_x, self.stone_y)
            self.stone_x, self.stone_y, self.stone = one_step_lookahead(
                self.board, self.stone, self.stone_y)
            self.drop()
            if not FAST_MODE:
                time.sleep(0.15)
            pygame_clock.tick(config['maxfps'])

    def manual_run(self):
        key_actions = {
            'ESCAPE': self.quit,
            'LEFT': lambda: self.move(-1),
            'RIGHT': lambda: self.move(+1),
            'DOWN': self.manual_drop,
            'UP': self.rotate_stone,
            'p': self.toggle_pause,
            'SPACE': self.start_game
        }

        self.gameover = False
        self.paused = False

        pygame.time.set_timer(pygame.USEREVENT + 1, config['delay'])
        pygame_clock = pygame.time.Clock()
        while True:
            self.screen.fill((0, 0, 0))
            if self.gameover:
                self.center_msg("""Game Over! Press space to continue""")
                print('Final Score: {}'.format(self.score))
            else:
                if self.paused:
                    self.center_msg("Paused")
                else:
                    self.draw_matrix(self.board, (0, 0))
                    self.draw_matrix(self.stone,
                                     (self.stone_x,
                                      self.stone_y))
            if not FAST_MODE:
                pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.USEREVENT + 1:
                    self.manual_drop()
                elif event.type == pygame.QUIT:
                    self.quit()
                elif event.type == pygame.KEYDOWN:
                    for key in key_actions:
                        if event.key == eval("pygame.K_" + key):
                            key_actions[key]()

            pygame_clock.tick(config['maxfps'])

    def manual_drop(self):
        if not self.gameover and not self.paused:
            self.stone_y += 1
            if check_collision(self.board, self.stone, (self.stone_x, self.stone_y)):
                self.board = join_matrixes(self.board, self.stone, (self.stone_x, self.stone_y))
                self.new_stone()
                while True:
                    for i, row in enumerate(self.board[:-1]):
                        if 0 not in row:
                            self.board = remove_row(
                                self.board, i)
                            break
                    else:
                        break
