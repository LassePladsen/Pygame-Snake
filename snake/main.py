from snakegame import SnakeGame

def main() -> None:
    game = SnakeGame(screen_size=(896, 640),
                     screen_title="Snake",
                     fps=3)
    game.run()

if __name__ == '__main__':
    main()
