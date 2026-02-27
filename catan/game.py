from catan import Board, Player, PlayerColor, shuffle_hexes, shuffle_ports
from catan.bank import Bank


class Game:
    def __init__(self):
        self.board = Board(
            shuffle_hexes(),
            shuffle_ports()
        )

        self.bank = Bank()
        self.player_1 = Player(PlayerColor.RED, self.board, self.bank, 0)
        self.player_2 = Player(PlayerColor.BLUE, self.board, self.bank, 1)
        self.player_3 = Player(PlayerColor.GREEN, self.board, self.bank, 2)
        self.player_4 = Player(PlayerColor.ORANGE, self.board, self.bank, 3)

        self.player_1.add_other_players(self.player_2, self.player_3, self.player_4)
        self.player_2.add_other_players(self.player_1, self.player_3, self.player_4)
        self.player_3.add_other_players(self.player_1, self.player_2, self.player_4)
        self.player_4.add_other_players(self.player_1, self.player_2, self.player_3)

    def is_won(self):
        return any([
            player.has_won()
            for player in self._player_order()
        ])

    def _player_order(self):
        return [
            self.player_1,
            self.player_2,
            self.player_3,
            self.player_4
        ]

    def begin_placements(self):
        pass