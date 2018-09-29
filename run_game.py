from tetris_dp import TetrisApp
AUTO_RUN = 1

if __name__ == '__main__':
    App = TetrisApp()
    if AUTO_RUN:
        App.run()
    else:
        App.manual_run()
