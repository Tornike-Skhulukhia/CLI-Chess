'''

'''

import time

from rich import print

from board import Board


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

        self._game_status = "initial"

    def __repr__(self):
        print(f"Game with board\n {self.board}")

    def play(self):
        print("Game Started")

        self._game_status = "running"

        # start game and maintain it before necessary
        while self._game_status == "running":

            # draw new board
            self.board.draw(debug_mode=DEBUG_MODE)

            (
                move_was_successfull,
                move_errors,
                next_player_troubles,
            ) = self.board.make_a_move_if_possible(input())

            # make sure it seems valid chess move
            if not move_was_successfull:
                assert len(move_errors) > 0

                for error_text in move_errors:
                    self.board._add_temporary_error(error_text)

                continue

            if next_player_troubles["player_is_checked"]:
                if next_player_troubles["player_is_checkmated"]:
                    # game over, current player lose
                    self.board._add_temporary_error("You lost the game!")

                    self._game_status = "Finished"

                    self.board.draw(debug_mode=DEBUG_MODE)
                else:
                    info = next_player_troubles["move_that_makes_check_disappear"]

                    self.board._add_temporary_error(
                        f'One possible move: {info["piece"]} {info["new_position"]}'
                    )

                    # add it after previous message as draw function gets info from end first
                    self.board._add_temporary_error("Check!")

            time.sleep(0.1)

        # game finished, allow to restart ?
