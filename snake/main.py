from snakegame import SnakeGame

def main() -> None:
    game = SnakeGame(screen_size=(896, 640),
                     title="Snake",
                     fps=10)
    game.grow()
    game.run()

if __name__ == '__main__':
    main()
