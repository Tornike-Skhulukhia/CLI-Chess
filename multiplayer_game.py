import socket
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

        # is used only when doing 2 player game
        self.player_number = None

    def __repr__(self):
        print(f"Game with board\n {self.board}")

    def add_current_player_trouble_messages_if_needed(self):

        # if we have any trouble, show it to us
        current_player_troubles = self.board.get_current_player_troubles()

        if current_player_troubles["player_is_checked"]:
            if current_player_troubles["player_is_checkmated"]:
                # game over, current player lost
                self.board._add_temporary_error("What a nice checkmate!")

                exit()
            else:
                info = current_player_troubles["move_that_makes_check_disappear"]

                self.board._add_temporary_error(
                    f'(Maybe {info["piece"].position} {info["new_position"]}?)'
                )

                # add it after previous message as draw function gets info from end first
                self.board._add_temporary_error("Check!")

    def play(self, connection):
        print("Game Started")

        # start game and maintain it before necessary
        while True:
            self.add_current_player_trouble_messages_if_needed()

            # draw new board  | rotate only for player 2
            self.board.draw(
                rotate_180_deg=self.player_number == 2, debug_mode=DEBUG_MODE
            )

            if self.board._player_turn == self.player_number:

                # white moves
                move_str = input("Type move in format like 'e2 e4'\n")

                (
                    move_was_successfull,
                    move_errors,
                    next_player_troubles,
                ) = self.board.make_a_move_if_possible(move_str)

                # make sure it seems valid chess move
                if not move_was_successfull:

                    for error_text in move_errors:
                        self.board._add_temporary_error(error_text)

                    continue

                connection.send(move_str.encode("utf8"))
            else:
                # black moves
                print("Waiting for opponent...")

                data = connection.recv(1024)
                if not data:
                    # when connection closes
                    break
                else:
                    move_str = data.decode("utf8")
                    # as we sent it after validating, this move
                    # should always be OK in this state
                    (
                        move_was_successfull,
                        move_errors,
                        next_player_troubles,
                    ) = self.board.make_a_move_if_possible(move_str)

    def start_game_hosting(self, host, port):
        print(
            f"Game hosting started on {host=} {port=}, please connect second player to start the game"
        )

        # start server
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((host, port))

        # wait for 1 connecton
        server.listen(1)

        # do not do anything until 1 connection is received
        # from second player game
        connected_sock, _ = server.accept()

        # which player is this?
        self.player_number = 1

        # start game
        self.play(connection=connected_sock)

        server.close()

    def connect_to_hosted_game(self, host, port):
        # start socket
        client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_sock.connect((host, port))

        # which player is this?
        self.player_number = 2

        print(f"Connected to host {host=} {port=}")

        # connect to given socket
        self.play(connection=client_sock)
