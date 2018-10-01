import sys
from tetris_dp import TetrisApp
AUTO_RUN = 1

if __name__ == '__main__':
    all_scores = []
    if AUTO_RUN:
        run_count = 10
        for game_number in range(0, run_count):
            App = TetrisApp()
            score = App.run()
            all_scores.append(score)
            print('Score {} for game number {}.'.format(score, game_number))
            sys.stdout.flush()
        average_score = sum(all_scores)/len(all_scores)
        print('Average score {} of {} runs.'.format(average_score, run_count))
    else:
        App = TetrisApp()
        App.manual_run()
