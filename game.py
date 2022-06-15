import re
import time

from rich import print

from board import Board
from _move_related_functions import _is_chess_move_str


DEBUG_MODE = 1


class Game:
    """
    Class to handle game initialization,
    retreival and validation of arguments and moves.
    board redrawing after making moves,
    final screens and retries/scores(if needed).

    to see all available colors to use for cells and/or pieces visit:
        https://rich.readthedocs.io/en/stable/appendix/colors.html
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
            self.board.draw(debug_mode=DEBUG_MODE)

            # get move
            move_str, _move_is_valid = self._get_next_move_and_add_error_if_necessary()

            # make sure it seems valid chess move
            if not _move_is_valid:
                continue

            # reorganize move_a_piece_if_possible_and_add_validation_errors_if_necessary function
            # later, so that it also returns errors and it is more clear what it does
            if self.board.move_a_piece_if_possible_and_add_validation_errors_if_necessary(
                move_str
            ):
                # after our move, does opponent has check/checkmate?
                troubles = self.board.get_current_player_troubles()

                if troubles["player_is_checked"]:
                    if troubles["player_is_checkmated"]:
                        # game over, current player lose
                        self.board._add_temporary_error("You lost the game!")

                        self._game_status = "Finished"

                        self.board.draw(debug_mode=DEBUG_MODE)
                    else:
                        info = troubles["move_that_makes_check_disappear"]

                        self.board._add_temporary_error(
                            f'possible move out of check : {info["piece"]} to {info["new_position"]}'
                        )

                        # add it after previous message as draw function gets info from end first
                        self.board._add_temporary_error("Check!")

            time.sleep(0.1)

        # game finished, allow to restart ?
