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
        games_moves = [
            [
                ["e4", "d5"],
                ["Bb5+"],
            ]
        ]

        for game_moves in games_moves:
            board = Board()
            board.apply_chess_notation_moves(game_moves)
            self.assertTrue(board._current_player_has_active_check)

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

            break  # remove break in last steps

    def test_correctly_identifies_checkmates(self):
        self.board.apply_chess_notation_moves([])


if __name__ == "__main__":
    unittest.main()
