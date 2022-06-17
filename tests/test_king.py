import unittest

from tests.base import BaseTest


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
        # king must jump over check-ed cell to make castle
        self.board.apply_chess_notation_moves(
            [
                ["d3", "d5"],
                ["Bf4", "Bg4"],
                ["Nc3", "Nf6"],
                ["Qd2", "e6"],
                ["e3", "Bb4"],
            ]
        )
        # it must not be possible
        self._assert_was_not_successful_move("0-0-0")

        # but after clearing check
        self.board.apply_chess_notation_moves([["Be2", "a6"]])

        # castle should works
        self._assert_was_successful_move("O-O-O")

    def test_king_can_not_move_where_there_is_check(self):
        self.board.apply_chess_notation_moves(
            [
                ["f4", "f5"],
                ["Kf2", "Kf7"],
                ["Kg3", "Kg6"],
            ]
        )

        self._assert_was_not_successful_move("g3 g4")
        self._assert_was_successful_move("g3 f2")

    def test_can_not_move_closer_than_one_cell_in_between_opponent_king(self):
        self.board.apply_chess_notation_moves(
            [
                ["f4", "f5"],
                ["Kf2", "Kf7"],
                ["Kg3", "Kg6"],
                [
                    "Kh4",
                ],
            ]
        )

        # black can not move to too close to white
        self._assert_was_not_successful_move("g6 g5")
        self._assert_was_not_successful_move("g6 h5")

        # but can move on other places
        self._assert_was_successful_move("g6 h6")

        # white also can not move to black king
        self._assert_was_not_successful_move("h4 h5")

        # but can move down
        self._assert_was_successful_move("h4 h3")


if __name__ == "__main__":
    unittest.main()
