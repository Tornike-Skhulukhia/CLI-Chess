import unittest

from tests.base import BaseTest


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

    def test_can_do_an_passant_left(self):
        self.board.apply_chess_notation_moves(
            [
                ["e4", "a6"],
                ["e5", "d5"],
            ]
        )

        self._assert_was_successful_move("E5 D6")

    def test_can_not_do_an_passant_left_too_late(self):
        self.board.apply_chess_notation_moves(
            [
                ["e4", "a6"],
                ["e5", "d5"],
                ["a4", "a5"],
            ]
        )

        self._assert_was_not_successful_move("E5 D6")

    def test_can_do_an_passant_right(self):
        self.board.apply_chess_notation_moves(
            [
                ["e4", "a6"],
                ["e5", "f5"],
            ]
        )

        self._assert_was_successful_move("E5 F6")

    def test_can_not_do_an_passant_right_too_late(self):
        self.board.apply_chess_notation_moves(
            [
                ["e4", "a6"],
                ["e5", "f5"],
                ["a4", "a5"],
            ]
        )

        self._assert_was_not_successful_move("E5 F6")

    def test_can_do_pawn_promotion_with_queen(self):
        # white promoted queen next to king
        self.board.apply_chess_notation_moves(
            [["b4", "c5"], ["bxc5", "a6"], ["c6", "a5"], ["c7", "a4"], ["cxd8=Q+"]]
        )

        # so it can not move other pieces because of check
        self._assert_was_not_successful_move("h7 h6")
        self._assert_was_not_successful_move("g8 f6")

        # so king kills it itself
        self._assert_was_successful_move("e8 d8")

        # white makes random move
        self._assert_was_successful_move("g1 F3")

        # black makes random move which is allowed now
        self._assert_was_successful_move("h7 h6")

    def test_can_do_pawn_promotion_with_knight(self):
        # white promoted queen next to king
        self.board.apply_chess_notation_moves(
            [["b4", "c5"], ["bxc5", "a6"], ["c6", "a5"], ["c7", "a4"], ["cxd8=N"]]
        )

        # black no check, as white promoted into Knight, do some random move
        self._assert_was_successful_move("h7 h6")

        # make sure new knight can not move like rook or bishop
        self._assert_was_not_successful_move("d8 c8")
        self._assert_was_not_successful_move("d8 b6")

        # but can do like knight
        self._assert_was_successful_move("d8 c6")


if __name__ == "__main__":
    unittest.main()
