import re
import time

from rich import print

from board import Board
from util import _is_chess_move_str, _player_has_check_in_position


class Game:
    """
    Class to handle game initialization,
    retreival and validation of arguments and moves.
    board redrawing after making moves,
    final screens and retries/scores(if needed)
    """

    def __init__(
        self,
        p1_color="bright_white",
        p2_color="grey3",
        black_cell_color="grey58",
        white_cell_color="grey37",
        previous_move_cell_color="green4",
    ):
        """
        Get basic configuration infos to start a game.

        . allow multiple different colors to be used for game.
        """
        self.board = Board(
            p1_color=p1_color,
            p2_color=p2_color,
            black_cell_color=black_cell_color,
            white_cell_color=white_cell_color,
            previous_move_cell_color=previous_move_cell_color,
        )

        """
        Statuses:
            . initial - ready to get user inputs
            . running - game is running
            . finished - game is lost/exited
        """
        self._game_status = "initial"
        self._player_turn = 1  # which player should make a move, first, or second

    def _get_next_move_and_add_error_if_necessary(self):
        move_str = input("Make a move\n").upper()
        move_is_valid = _is_chess_move_str(move_str)

        if not move_is_valid:
            self.board._add_temporary_error("Not a move, try again")

        return move_str, move_is_valid

    def play(self):
        print("Game Started")

        self._game_status = "running"
        print("=" * 100)

        # start game and maintain it before necessary
        while self._game_status == "running":

            # draw new board
            self.board.draw(debug_mode=1)

            if self.board.current_player_is_checkmated():
                self.board._add_temporary_error("You lost the game!")
                self.board.draw(debug_mode=1)
                return

            # get move
            move_str, _move_is_valid = self._get_next_move_and_add_error_if_necessary()

            # make sure it seems valid chess move
            if not _move_is_valid:
                continue

            if self.board.move_a_piece_if_possible_and_add_validation_errors_if_necessary(
                move_str
            ):
                self.board._swap_player_turn()

                # after our move, does opponent has check?
                if _player_has_check_in_position(
                    check_for_current_player=True, board_state=self.board
                ):
                    self.board._add_temporary_error("Check, save your King")

            time.sleep(0.1)

        # game finished, allow to restart
