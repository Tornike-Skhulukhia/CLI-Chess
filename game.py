"""
Play chess in CLI with both player being just you.

Can be useful if you do not have friends to play it with, 
or you are doing some testing/development.
"""

import time
from rich import print

from board import Board

# if set to True, moves history and previous game states
# will also be printed on the screen during the game


class Game:
    """
    Basic game class that allows 1 player to play both sides of chess game.

    As you can see from the code, it is very similar to multiplayer_game.py file
    as they use the same API that board provides.

    Feel free to play with the code and change things as needed here.
    """

    def __init__(
        self,
        p1_color="bright_white",
        p2_color="grey3",
        black_cell_color="grey58",
        white_cell_color="grey37",
        previous_move_cell_color="green4",
        debug_mode=True,
    ):
        self.board = Board(
            p1_color=p1_color,
            p2_color=p2_color,
            black_cell_color=black_cell_color,
            white_cell_color=white_cell_color,
            previous_move_cell_color=previous_move_cell_color,
        )

        self.debug_mode = debug_mode

        self._game_status = "initial"

    def __repr__(self):
        print(f"Game with board\n {self.board}")

    def play(self):
        print("Game Started")

        self._game_status = "running"

        # start game and maintain it before necessary
        while self._game_status == "running":

            # draw new board
            self.board.draw(debug_mode=self.debug_mode)

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

                    self.board.draw(debug_mode=self.debug_mode)
                else:
                    info = next_player_troubles["move_that_makes_check_disappear"]

                    self.board._add_temporary_error(
                        f'One possible move: {info["piece"]} {info["new_position"]}'
                    )

                    # add it after previous message as draw function gets info from end first
                    self.board._add_temporary_error("Check!")

            time.sleep(0.1)
