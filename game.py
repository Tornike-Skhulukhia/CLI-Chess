import re
import time

from rich import print

from board import Board


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

    @staticmethod
    def _is_move_str(move):
        """
        Just validate that move has proper format, not any logic yet

        Format:
            "E2 E4" - not case sensitive
        """
        move = move.upper().strip()
        parts = move.split()

        print(f"Checking move {move}")

        try:
            if all(
                [
                    len(parts) == 2,
                    len(parts[0]) == 2,
                    len(parts[1]) == 2,
                    parts[0][0] in "ABCDEFGH",
                    parts[1][0] in "ABCDEFGH",
                    parts[0][1] in "12345678",
                    parts[1][1] in "12345678",
                ]
            ):
                return move
        except:
            return False
        return False

    def _get_next_move_and_add_error_if_necessary(self):
        move_str = input("Make a move\n").upper()
        move_is_valid = self._is_move_str(move_str)

        if not move_is_valid:
            self.board._add_temporary_error("Not a move, try again")

        return move_str, move_is_valid

    def _swap_player_turn(self):
        if self._player_turn == 1:
            self._player_turn = 2
        else:
            self._player_turn = 1

    def play(self):
        print("Game Started")

        self._game_status = "running"
        print("=" * 100)

        # start game and maintain it before necessary
        while self._game_status == "running":

            # draw new board
            self.board.draw(self._player_turn)

            # get move
            move_str, _move_is_valid = self._get_next_move_and_add_error_if_necessary()

            # make sure it seems valid chess move
            if not _move_is_valid:
                continue

            if self.board.move_a_piece_if_possible_and_add_validation_errors_if_necessary(
                move_str, self._player_turn
            ):
                self._swap_player_turn()

            time.sleep(0.1)

        # game finished, allow to restart
