import unittest
from board import Board, INVALID_MOVE_ERROR_TEXT


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.board = Board()

    def _assert_was_successful_move(self, move):
        if move not in ("O-O", "O-O-O"):
            _from, _to = move.upper().split()

            # before move cells were correctly positioned on board
            self.assertTrue(_from in self.board.positions_to_pieces)

            # make a move
            success, errors, next_player_troubles = self.board.make_a_move_if_possible(
                move
            )

            self.assertTrue(success)
            self.assertTrue(len(errors) == 0)

            # after move cells were correctly positioned on board
            self.assertTrue(_to in self.board.positions_to_pieces)
            self.assertTrue(_from not in self.board.positions_to_pieces)
        else:
            # castling
            success, errors, next_player_troubles = self.board.make_a_move_if_possible(
                move
            )

            self.assertTrue(success)
            self.assertTrue(len(errors) == 0)

    def _assert_was_not_successful_move(self, move):
        success, errors, next_player_troubles = self.board.make_a_move_if_possible(move)

        self.assertFalse(success)
        self.assertTrue(len(errors) == 1)
        self.assertTrue(errors[0] == INVALID_MOVE_ERROR_TEXT)
