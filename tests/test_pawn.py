import unittest

from .base import BaseTest


class TestPawn(BaseTest):
    def test_forward_by_one_cell(self):
        self._assert_was_successful_move("e2 e3")

    def test_forward_by_two_cells(self):
        self._assert_was_successful_move("e2 e4")

    def test_can_only_move_2_cells_forward_only_on_first_move(self):
        # white starts
        self._assert_was_successful_move("e2 e3")
        # black continues
        self._assert_was_successful_move("e7 e5")

        # white pawn cant move 2 cells
        self._assert_was_not_successful_move("e3 e5")
        # but can move 1 cell forward
        self._assert_was_successful_move("e3 e4")

    def test_can_not_make_illegal_moves(self):
        self._assert_was_not_successful_move("e2 e6")
        self._assert_was_not_successful_move("e2 d3")
        self._assert_was_not_successful_move("e2 g4")
        self._assert_was_not_successful_move("e2 c3")
        self._assert_was_not_successful_move("e2 d2")

    def test_can_not_move_backwards(self):
        self._assert_was_successful_move("e2 e3")
        self._assert_was_successful_move("e7 e5")
        self._assert_was_not_successful_move("e3 e2")

    def test_can_do_normal_kill(self):
        # pieces numbers are correct before kill
        self.assertTrue(len(self.board.player_1_pieces) == 16)
        self.assertTrue(len(self.board.player_2_pieces) == 16)

        self._assert_was_successful_move("e2 e4")
        self._assert_was_successful_move("d7 d5")
        piece_being_killed = self.board.positions_to_pieces["D5"]
        self._assert_was_successful_move("e4 d5")

        # pieces numbers are correct after kill
        self.assertTrue(len(self.board.player_1_pieces) == 16)
        self.assertTrue(len(self.board.player_2_pieces) == 15)

        # correct piece in killed pieces
        self.assertIn(piece_being_killed, self.board.killed_opponent_pieces[1])
        self.assertTrue(len(self.board.killed_opponent_pieces[2]) == 0)

    def test_can_not_do_invalid_kill(self):
        self._assert_was_successful_move("e2 e4")
        self._assert_was_successful_move("d7 d5")
        self._assert_was_not_successful_move("e4 f5")

    def test_can_not_cause_check_by_move(self):
        self.board.apply_chess_notation_moves(
            [
                ["e3", "e5"],
                ["Nf3", "Bb4"],
            ]
        )
        self._assert_was_not_successful_move("d2 d3")

    def test_can_do_an_passant(self):
        pass

    def test_do_pawn_promotion(self):
        pass


if __name__ == "__main__":
    unittest.main()
