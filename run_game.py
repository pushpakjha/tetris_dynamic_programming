import sys
import time

from tetris_dp import TetrisApp
AUTO_RUN = 1


if __name__ == '__main__':
    all_scores = []
    if AUTO_RUN:
        start_time = time.time()
        run_count = 10
        for game_number in range(0, run_count):
            single_game = TetrisApp()
            score = single_game.run()
            print('Score {} for game number {}.'.format(score, game_number))
            sys.stdout.flush()
            all_scores.append(score)
        average_score = sum(all_scores)/len(all_scores)
        print('Average score {} of {} runs in {} seconds.'.format(
            average_score, run_count, time.time()-start_time))
    else:
        App = TetrisApp()
        App.manual_run()
