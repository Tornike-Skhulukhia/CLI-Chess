import unittest

from .base import BaseTest


class TestKing(BaseTest):
    def test_can_move_normally(self):
        self._assert_was_successful_move("e2 e4")
        self._assert_was_successful_move("a7 a5")
        self._assert_was_successful_move("e1 e2")

    def test_can_not_make_illegal_piece_moves(self):
        self._assert_was_successful_move("e2 e4")
        self._assert_was_successful_move("a7 a5")
        self._assert_was_not_successful_move("e1 c3")
        self._assert_was_not_successful_move("e1 f3")
        self._assert_was_not_successful_move("e1 d1")
        self._assert_was_not_successful_move("e1 f1")

    def test_can_not_move_into_checked_cell(self):
        self.board.apply_chess_notation_moves([["d3", "e5"], ["Bg5", "Qxg5"]])
        self._assert_was_not_successful_move("e1 d2")

    def test_can_short_castle(self):
        self.board.apply_chess_notation_moves(
            [
                ["d4", "Nf6"],
                ["c4", "e6"],
                ["Nf3", "b6"],
                ["g3", "Bb7"],
                ["Bg2", "Bb4+"],
                ["Bd2", "c5"],
                ["Bxb4", "cxb4"],
            ]
        )

        self._assert_was_successful_move("O-O")
        self._assert_was_successful_move("O-O")
        self._assert_was_not_successful_move("O-O")

    def test_can_long_castle(self):
        self.board.apply_chess_notation_moves(
            [
                ["d3", "d5"],
                ["Bf4", "Bg4"],
                ["Nc3", "Nf6"],
                ["Qd2", "e6"],
            ]
        )
        self._assert_was_not_successful_move("O-O")
        self._assert_was_successful_move("O-O-O")

    def test_can_not_castle_if_middle_cell_has_check(self):
        self.board.apply_chess_notation_moves(
            [
                ["d3", "d5"],
                ["Bf4", "Bg4"],
                ["Nc3", "Nf6"],
                ["Qd2", "e6"],
                ["e3", "Bb4"],
            ]
        )

        self._assert_was_not_successful_move("O-O-O")



if __name__ == "__main__":
    unittest.main()
