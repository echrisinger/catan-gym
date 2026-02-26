from catan import Game

def main():
    game = Game()
    while not game.is_won():
        game.next_turn()


if __name__ == "__main__":
    main()
