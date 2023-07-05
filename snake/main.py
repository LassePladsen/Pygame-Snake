from snakegame import SnakeGame


def main() -> None:
    game = SnakeGame(screen_size=(640, 480),
                     title="Snake",
                     fps=11)
    game.run()


if __name__ == '__main__':
    main()
