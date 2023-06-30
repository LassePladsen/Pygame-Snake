from game import Game

def main() -> None:
    game = Game(screen_size=(896, 640),
                screen_title="Snake",
                fps=8)
    game.run()

if __name__ == '__main__':
    main()
