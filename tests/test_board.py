import unittest

from tests.base import BaseTest
from tests.real_game_info_retrieval_functions import (
    get_real_game_chess_moves_history_from_pgn_file,
)
from board import Board


class TestBoard(BaseTest):
    def test_board_moves_counted_correctly(self):
        self.assertEqual(self.board.total_moves_count, 0)

        self._assert_was_successful_move("e2 e3")
        self.assertEqual(self.board.total_moves_count, 1)

        self._assert_was_successful_move("e7 e5")
        self.assertEqual(self.board.total_moves_count, 2)

        self._assert_was_successful_move("e3 e4")
        self.assertEqual(self.board.total_moves_count, 3)

        # make sure pieces move counts are also correct
        self.assertTrue(self.board.positions_to_pieces["E4"].moves_count == 2)
        self.assertTrue(self.board.positions_to_pieces["E5"].moves_count == 1)

    def test_pieces_moves_counted_correctly(self):
        self.assertEqual(self.board.positions_to_pieces["E2"].moves_count, 0)
        self.assertEqual(self.board.positions_to_pieces["E7"].moves_count, 0)

        self._assert_was_successful_move("e2 e3")
        self.assertEqual(self.board.positions_to_pieces["E3"].moves_count, 1)
        self.assertEqual(self.board.positions_to_pieces["E7"].moves_count, 0)

        self._assert_was_successful_move("e7 e5")
        self.assertEqual(self.board.positions_to_pieces["E3"].moves_count, 1)
        self.assertEqual(self.board.positions_to_pieces["E5"].moves_count, 1)

        self._assert_was_successful_move("e3 e4")
        self.assertEqual(self.board.positions_to_pieces["E4"].moves_count, 2)
        self.assertEqual(self.board.positions_to_pieces["E5"].moves_count, 1)

    def test_player_turn_changes_correctly(self):
        self.assertEqual(self.board._player_turn, 1)
        self._assert_was_successful_move("e2 e3")

        self.assertEqual(self.board._player_turn, 2)
        self._assert_was_successful_move("e7 e5")

        self.assertEqual(self.board._player_turn, 1)
        self._assert_was_successful_move("g1 f3")

        self.assertEqual(self.board._player_turn, 2)
        self._assert_was_successful_move("b8 c6")

        self.assertEqual(self.board._player_turn, 1)

    def test_check_identified_correctly(self):

        self.board.apply_chess_notation_moves([["e4", "d5", "Bb5"]])

        # there is a check
        self.assertTrue(self.board._current_player_has_active_check)
        # player can not do anything that is not fixing check
        self._assert_was_not_successful_move("G8 F6")
        self._assert_was_not_successful_move("D8 D6")

        # stop check using knight
        self._assert_was_successful_move("B8 C6")

        # white has no checks
        self.assertFalse(self.board._current_player_has_active_check)
        # and does some random move
        self._assert_was_successful_move("B1 C3")

        # black still has no check
        self.assertFalse(self.board._current_player_has_active_check)
        # black also does some random move
        self._assert_was_successful_move("A8 B8")

        # white kills previous black knight and makes check again
        self._assert_was_successful_move("B5 C6")

        # black has check again
        self.assertTrue(self.board._current_player_has_active_check)

        # and can not move king in also checked position
        self._assert_was_not_successful_move("E8 D7")

        # but can use bishop to hide check
        self._assert_was_successful_move("C8 D7")

    def test_can_load_games_from_chess_notations_list_without_errors(self):
        games_moves = get_real_game_chess_moves_history_from_pgn_file(
            "./tests/assets/master_games.pgn"
        )

        for game_moves in games_moves:
            board = Board()
            # must not cause errors when applying these moves.
            # before applying each move, we check
            # that it is correct/valid, and raise exception if not,
            # so if no errors raised, it is a good sign
            board.apply_chess_notation_moves(game_moves)
            
            # break  # remove break in last steps

    def test_correctly_identifies_checkmates(self):
        self.board.apply_chess_notation_moves(
            [
                ["e4", "e5"],
                ["Bc4", "Nc6"],
                ["Qf3", "d6"],
            ]
        )

        success, errors, next_player_troubles = self.board.make_a_move_if_possible(
            "F3 F7",
        )

        # move was sucessfull
        self.assertTrue(success)
        # no errors
        self.assertTrue(len(errors) == 0)
        # troubles is not empty
        self.assertTrue(bool(next_player_troubles))
        # but it has checkmate information correctly
        self.assertTrue(next_player_troubles["player_is_checkmated"])


if __name__ == "__main__":
    unittest.main()
