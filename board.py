"""
Not implemented:
    . king castling | +
    . an passant    | +
    . exchanging pawn to queen or other pieces when in the end...
Known Bugs
    . 
"""


import copy
import os

from rich import print

from _move_related_functions import (
    _is_chess_basic_move_str,
    _is_chess_notation_move_str,
)
from _notation_converters import (
    convert_basic_move_notation_to_chess_notation,
    convert_chess_notation_to_basic_move_notation,
)
from pieces import Bishop, King, Knight, Pawn, Piece, Queen, Rook

INVALID_MOVE_ERROR_TEXT = "Invalid move"
NOT_A_CHESS_MOVE_ERROR_TEXT = "Not a chess move"
# NO_YOUR_PIECE_ON_CELL_ERROR_FORMAT_TEXT = "Sorry, there is no your piece on cell {}"
# CANNOT_DO_CASTLE_ERROR_TEXT = "You can not castle that way"
# SUCCESSFULL_CASTLING_TEXT = "Successfull castle"


class Board:
    def __init__(
        self,
        p1_color="bright_white",
        p2_color="grey3",
        black_cell_color="grey58",
        white_cell_color="grey37",
        previous_move_cell_color="green4",
    ):
        # colors to draw player pieces
        self.p1_color = p1_color
        self.p2_color = p2_color

        # colors to draw cells on board
        self._black_cell_color = black_cell_color
        self._white_cell_color = white_cell_color

        # what color to use to draw last move cells
        self._previous_move_cell_color = previous_move_cell_color

        # holds each player piece
        self.player_1_pieces = []
        self.player_2_pieces = []

        # holds who killed what info
        self.killed_opponent_pieces = {1: [], 2: []}

        # last move started at and ended at points
        self._from_cell = None
        self._to_cell = None

        # holds different errors that until
        # they show up when calling board's draw method
        self.errors_to_display = []

        # who should play now(1 or 2)
        self._player_turn = 1

        self.total_moves_count = 0
        # stores moves with just starting and ending cells, like [ ["E2 E4", "G8 F6"], ]
        self.moves = []
        # stores moves with chess notation like [ ["e4", "Nf6"], ]
        self.chess_notation_moves = []

        self._initialize_pieces()

    def __repr__(self):
        self.draw(debug_mode=1)

        return f"<Board object>"

    def apply_chess_notation_moves(self, moves_list):
        """

        Get list of moves written in chess notation like this:
            [
                ['d4', 'Nf6'],
                ['c4', 'e6'],
                ['Nf3', 'b6'],
                ['g3', 'Bb7'],
                ['Bg2', 'Bb4+'],
                ['Bd2', 'c5'],
            ]
        and apply them to current board configuration if possible (ex: https://www.chess.com/games/view/15792867)

        currently checks and other warnings/errors are not rendered at all, but validations are still in place,
        so for example if last position after these moves causes check, player will not be able to play
        something that does not stop king from checking, so just the errors are not visible(we may change that if needed)
        """

        if len(moves_list) > 0:
            if not isinstance(moves_list[0], list):
                raise ValueError("Invalid input, please use lists of lists")

        for moves in moves_list:
            for move in moves:
                assert _is_chess_notation_move_str(move)

                basic_move_str = convert_chess_notation_to_basic_move_notation(
                    move, self
                )

                (
                    move_was_successfull,
                    move_errors,
                    next_player_troubles,
                ) = self.make_a_move_if_possible(basic_move_str)

                if not move_was_successfull:
                    raise ValueError(
                        f"Can not apply move {move} ({basic_move_str}) to board"
                    )

                if next_player_troubles["player_is_checkmated"]:
                    raise ValueError(
                        "Game is over, please use this function to load games that are not finished"
                    )

    def get_deepcopy(self):
        return copy.deepcopy(self)

    @property
    def current_player_pieces(self):
        return [self.player_2_pieces, self.player_1_pieces][self._player_turn == 1]

    @property
    def opponent_player_pieces(self):
        return [self.player_2_pieces, self.player_1_pieces][self._player_turn == 2]

    @property
    def current_player_king(self):
        return [i for i in self.current_player_pieces if i.piece_name == "king"][0]

    @property
    def opponent_player_king(self):
        return [i for i in self.opponent_player_pieces if i.piece_name == "king"][0]

    @property
    def index_based_positions_to_pieces(self):
        index_based_positions_to_pieces = {
            i.index_based_position: i
            for i in [*self.player_1_pieces, *self.player_2_pieces]
        }

        return index_based_positions_to_pieces

    @property
    def positions_to_pieces(self):
        positions_to_pieces = {}

        # assign each chess position string to corresponding piece
        for piece in [*self.player_1_pieces, *self.player_2_pieces]:
            positions_to_pieces[piece.position] = piece

        return positions_to_pieces

    def _get_player_rook_info_if_possible_to_do_castling_with_it(
        self, castling_case="short"
    ):
        """
        return rooks old and new positions, if castling can be done, None otherwise
        """
        assert castling_case in ("short", "long")

        positions_info = {
            "short": {
                1: "H1",
                2: "H8",
            },
            "long": {
                1: "A1",
                2: "A8",
            },
        }

        # make sure cells between Rook and King are free
        # check only B column here as 2 cells from King sides are checked in king check method
        if (
            castling_case == "long"
            and {1: "B1", 2: "B8"}[self._player_turn] in self.positions_to_pieces
        ):
            return None

        position_to_expect_rook_on = positions_info[castling_case][self._player_turn]

        if position_to_expect_rook_on in self.positions_to_pieces:
            piece = self.positions_to_pieces[position_to_expect_rook_on]

            if (
                piece.piece_name == "rook"
                and piece.moves_count == 0
                and piece.player_number == self._player_turn
            ):
                position_if_castled = {
                    "short": {
                        1: "F1",
                        2: "F8",
                    },
                    "long": {
                        1: "D1",
                        2: "D8",
                    },
                }[castling_case][self._player_turn]

                return piece.position, position_if_castled

        return None

    @property
    def _current_player_has_active_check(self):
        return self._player_has_check_in_position()

    def _get_player_king_info_if_possible_to_do_castling_with_it(
        self, castling_case="short"
    ):
        """
        Return kings new position, if castling can be done, None otherwise
        """
        assert castling_case in ("short", "long")

        king = self.current_player_king

        # in chess king can not castle if it has active check
        # or have already moved even once
        if king.moves_count > 0 or self._current_player_has_active_check:
            return None

        # make sure cells that castling needs are free
        taken_positions = self.positions_to_pieces
        for i in {
            "short": {
                1: ["F1", "G1"],
                2: ["F8", "G8"],
            },
            "long": {
                1: ["D1", "C1"],
                2: ["D8", "C8"],
            },
        }[castling_case][self._player_turn]:

            if i in taken_positions:
                return None

        # check cells nearby, are they free from checks?
        cells_info = {
            "short": {
                1: "F1",
                2: "F8",
            },
            "long": {
                1: "D1",
                2: "D8",
            },
        }

        # checking 1 cell for checks is enough here, as we check current
        # cell before this steps and king position after castle ends in
        # outer function that in general removes technically possible moves
        # from possible moves if after the move check is present
        cell = cells_info[castling_case][self._player_turn]

        # king must not have checks not only before and after, but also
        # in between those as well, so check for this
        copied_board_state = self.get_deepcopy()
        copied_king = copied_board_state.positions_to_pieces[king.position]

        copied_king.apply_move_info_to_board(
            board_state=copied_board_state,
            move_info={"new_position": cell, "killed_opponent_piece_position": None},
            swap_player_turn=False,
        )

        if copied_board_state._current_player_has_active_check:
            return None

        # if (
        #     self.positions_to_pieces.get("B4")
        #     and self.positions_to_pieces.get("B4").piece_name == "bishop"
        # ):
        #     breakpoint()

        king_position_if_castled = {
            "short": {
                1: "G1",
                2: "G8",
            },
            "long": {
                1: "C1",
                2: "C8",
            },
        }[castling_case][self._player_turn]

        return king_position_if_castled

    def get_current_player_pieces_with_piece_prefix(self, chess_notation):
        """
        "" --> all Pawns
        K - king
        N - nights
        B - bishops

        e.t.c
        """
        return [
            i
            for i in self.current_player_pieces
            if i.chess_notation_prefix == chess_notation
        ]

    def _swap_player_turn(self):
        if self._player_turn == 1:
            self._player_turn = 2
        else:
            self._player_turn = 1

    def _add_temporary_error(self, error_text):
        self.errors_to_display.append(error_text)

    def _add_temporary_error_at_first_position(self, error_text):
        self.errors_to_display.insert(0, error_text)

    def _reset_errors(self):
        self.errors_to_display = []

    def update_moves_history(self, last_move_from, last_move_to, move_info):
        """
        We store 2 type of history, 1 with just moves like ("g1 f3", "e7 e5")

        and other with official chess notation, like like ("Nf3", "e5")

        ! Make sure to run this function before changing state of board after specific valid move
        as it needs current playing state to make correct conversion of notations
        """
        self._update_last_move_on_board_info(_from=last_move_from, _to=last_move_to)

        # first player adds new move item in histories
        if self.total_moves_count % 2 == 0:
            self.moves.append([])
            self.chess_notation_moves.append([])

        ### update last move item
        # for basic moves history

        # if it seems castling case, save moves info as castling notation, not the basic from-to cells notation
        if move_info and move_info.get("castle_notation"):
            basic_move_str = move_info["castle_notation"]

        else:
            basic_move_str = f"{last_move_from} {last_move_to}"

        self.moves[-1].append(basic_move_str)

        # for chess notation history
        chess_notation_move = convert_basic_move_notation_to_chess_notation(
            basic_move_str=basic_move_str,
            board_state_before_move=self,
        )

        self.chess_notation_moves[-1].append(chess_notation_move)

        # not actually needed, just for check
        assert (
            convert_chess_notation_to_basic_move_notation(
                chess_notation=chess_notation_move, board_state_before_move=self
            )
            == basic_move_str
        )

        self.total_moves_count += 1

    def _initialize_pieces(self):
        """
        Create all pieces as they should be when game starts
        and assign them to current board object.
        """

        col_1, col_2 = self.p1_color, self.p2_color

        pieces_1 = [
            Rook(color=col_1, position="A1", player_number=1),
            Knight(color=col_1, position="B1", player_number=1),
            Bishop(color=col_1, position="F1", player_number=1),
            Queen(color=col_1, position="D1", player_number=1),
            King(color=col_1, position="E1", player_number=1),
            Bishop(color=col_1, position="C1", player_number=1),
            Knight(color=col_1, position="G1", player_number=1),
            Rook(color=col_1, position="H1", player_number=1),
            Pawn(color=col_1, position="A2", player_number=1),
            Pawn(color=col_1, position="B2", player_number=1),
            Pawn(color=col_1, position="C2", player_number=1),
            Pawn(color=col_1, position="D2", player_number=1),
            Pawn(color=col_1, position="E2", player_number=1),
            Pawn(color=col_1, position="F2", player_number=1),
            Pawn(color=col_1, position="G2", player_number=1),
            Pawn(color=col_1, position="H2", player_number=1),
        ]

        pieces_2 = [
            Rook(color=col_2, position="A8", player_number=2),
            Knight(color=col_2, position="B8", player_number=2),
            Bishop(color=col_2, position="F8", player_number=2),
            Queen(color=col_2, position="D8", player_number=2),
            King(color=col_2, position="E8", player_number=2),
            Bishop(color=col_2, position="C8", player_number=2),
            Knight(color=col_2, position="G8", player_number=2),
            Rook(color=col_2, position="H8", player_number=2),
            Pawn(color=col_2, position="A7", player_number=2),
            Pawn(color=col_2, position="B7", player_number=2),
            Pawn(color=col_2, position="C7", player_number=2),
            Pawn(color=col_2, position="D7", player_number=2),
            Pawn(color=col_2, position="E7", player_number=2),
            Pawn(color=col_2, position="F7", player_number=2),
            Pawn(color=col_2, position="G7", player_number=2),
            Pawn(color=col_2, position="H7", player_number=2),
        ]

        self.player_1_pieces = pieces_1
        self.player_2_pieces = pieces_2

    def _remove_piece_from_pieces(self, piece_to_kill):
        if piece_to_kill:
            assert piece_to_kill in [*self.player_2_pieces, *self.player_1_pieces]

        if piece_to_kill.player_number == 2:
            self.player_2_pieces = [
                i for i in self.player_2_pieces if i is not piece_to_kill
            ]
        else:
            self.player_1_pieces = [
                i for i in self.player_1_pieces if i is not piece_to_kill
            ]

    def _get_cell_color_based_on_cell_indices(self, row_index, col_index):

        # if cell is starting or ending position of a previous move, colorize
        # it differently than normal black/white
        position = Piece.index_based_position_to_position((row_index, col_index))

        if position == self._from_cell or position == self._to_cell:
            return self._previous_move_cell_color

        # normal cells case
        if (row_index % 2 == 0 and col_index % 2 == 0) or (
            row_index % 2 == 1 and col_index % 2 == 1
        ):
            # black
            cell_color = self._black_cell_color
        else:
            # white
            cell_color = self._white_cell_color

        return cell_color

    def _update_last_move_on_board_info(self, _from, _to):
        self._to_cell = _to
        self._from_cell = _from

    def _player_has_check_in_position(self):
        # check if current player has check
        king_position = self.current_player_king.position
        opponent_pieces = self.opponent_player_pieces

        # get all possible killing moves that opponent pieces can make
        # for pawns, we care only about killing cells here, as they can't push King forward :-)

        for piece in opponent_pieces:
            cells_on_which_opponent_can_kill_piece = (
                piece.get_all_possible_cells_where_this_piece_can_kill(
                    board_state=self,
                )
            )

            if king_position in cells_on_which_opponent_can_kill_piece:
                return True

        return False

    @staticmethod
    def _clear_screen():
        os.system("clear")

    def draw(self, debug_mode=False):
        """
        Draw all pieces where they are belonging to, with given params
        """
        if not debug_mode:
            self._clear_screen()

        print(f"{self.errors_to_display=}")
        print(f"{self.moves=}")
        print(f"{self.chess_notation_moves=}")
        print()

        # later rewrite this function, so that we generate some data structure
        # that stores info about what to print and in what color and when,
        # so that applying different styles after basic moves, will be much easier

        # breakpoint()

        for row_index in range(8):
            # row number
            print(f"[grey37]{8 - row_index}[/]", end="")

            for col_index in range(8):
                cell_bg_color = self._get_cell_color_based_on_cell_indices(
                    row_index, col_index
                )

                # cell with piece on it
                if (row_index, col_index) in self.index_based_positions_to_pieces:
                    piece = self.index_based_positions_to_pieces[(row_index, col_index)]

                    text_to_print = (
                        f"[{piece.color} on {cell_bg_color}]{piece.piece_icon}[/]"
                    )

                else:
                    # empty cell
                    text_to_print = f"[on {cell_bg_color}] [/]"

                print(text_to_print, end="")

            # show which player's turn it is
            if row_index == 0:
                if self._player_turn == 2:
                    print(f"[{self.p2_color}] ⬤[/]", end="")
                else:
                    print(f"  ", end="")

            if row_index == 7:
                if self._player_turn == 1:
                    print(f"[{self.p1_color}] ⬤[/]", end="")
                else:
                    print(f"  ", end="")

            # display killed pieces if any
            if row_index in (0, 7):
                # pieces that player 2 killed
                killed_pieces_to_draw = (
                    self.killed_opponent_pieces[2]
                    if row_index == 0
                    else self.killed_opponent_pieces[1]
                )

                if killed_pieces_to_draw:
                    # left padding
                    print(" " * 2, end="")

                    # killed pieces
                    for piece in killed_pieces_to_draw:
                        print(
                            f"[{piece.color} on {self._black_cell_color}]{piece.piece_icon}[/]",
                            end=" ",
                        )

            # display errors if any
            if 2 <= row_index <= 6 and len(self.errors_to_display) > 0:
                error_text = self.errors_to_display.pop()

                print(
                    # padding from board
                    " " * 5,
                    # actual error message
                    f"[yellow]{error_text}[/]",
                    end="",
                )

            # newline
            print()

        # draw column names
        print(f"[grey37] abcdefgh[/]")
        # draw row numbers

        # reset errors after every frame update
        self._reset_errors()

    def kill_piece(self, killed_opponent_piece):
        """
        Remove piece from player pieces list and
        add into other players killed pieces list
        """

        if killed_opponent_piece.player_number == 1:
            killer_player_number = 2
        else:
            killer_player_number = 1

        self.killed_opponent_pieces[killer_player_number].append(killed_opponent_piece)

        self._remove_piece_from_pieces(killed_opponent_piece)

    def get_move_info_if_it_is_valid_move_str(self, move_str):
        """
        Returns False if move does not seem valid, dictionary with move info otherwise
        """
        move_info = False
        piece = None
        _from = ""
        _to = ""

        if not _is_chess_basic_move_str(move_str):
            return move_info, piece, _from, _to

        move_str = move_str.upper()

        # if castle was requested
        if move_str in ("O-O", "O-O-O"):

            king = self.current_player_king

            possible_moves = king.get_possible_moves(board_state=self)

            for i in possible_moves:
                if i.get("castle_notation") == move_str:
                    move_info = i
                    _from = king.position
                    _to = i["new_position"]
                    piece = king
                    break

        else:
            # normal moves
            move_start, move_end = move_str.split()

            if move_start in {i.position for i in self.current_player_pieces}:
                _piece = self.positions_to_pieces[move_start]

                # can that piece make that move ?
                possible_moves = _piece.get_possible_moves(board_state=self)

                for i in possible_moves:  # if piece can move there
                    if i["new_position"] == move_end:
                        move_info = i
                        _from = move_start
                        _to = move_end
                        piece = _piece
                        break

        return move_info, piece, _from, _to

    def make_a_move_if_possible(self, move_str):
        """
        Main entry point from game, gets move string, if possible applies new move to board,
        otherwise, returns errors.

        args:
            1. move_str - string like "E2 E4", "B1 C3". It is written in basic notation
                        with "from_cell to_cell" format, as it is making lots of things much
                        clear to work with and we use mainly this notation in code, but also
                        have function that converts chess notation like "e4", "NC3" to basic
                        notation, which allows use to load games from pgn files using
                        apply_chess_notation_moves method here. Please look at it if needed.

        Returns tuple of 3 things:
                1. success flag - success status of move (True/False)

                2. list of errors - if move was not successfull, possible error can
                                be invalid move as a string. we use this error texts to
                                display in CLI. They can be more detailed, like specifically why
                                is move not legal, because of checks, piece can not move
                                that way, move string has incorrect format or something else,
                                but for our purposes this granularity is not necessary for now.

                3. next player troubles - dictionary containing information if after successfull
                                move(which causes next one to be the active player on board) player has
                                active checks, or checkmates, so that outer calling functions can finish
                                game, display that there is a check e.t.c
                                For example, lets say this function processed valid move from white
                                player that caused checkmate to black player, in that case
                                1-st argument of this function will be True, second will be [],
                                and third(this one) will be the dictionary with few keys like
                                player_is_checked or player_is_checkmated with boolean values,
                                for more info see get_current_player_troubles method.

                                If move is not successfull, this dictionary is empty, as it makes
                                no sense to check for checks/checkmates again if move was not valid,
                                so not applied to board.

        """
        move_info, piece, _from, _to = self.get_move_info_if_it_is_valid_move_str(
            move_str
        )

        if not move_info:
            return False, [INVALID_MOVE_ERROR_TEXT], {}

        # run it before making actual changes as current notations translations implementation
        # needs board state info before making actual move on board itself
        

        # as conversions that happen, make decisions based on current board state, not after move
        self.update_moves_history(
            last_move_from=_from, last_move_to=_to, move_info=move_info
        )

        piece.apply_move_info_to_board(
            board_state=self,
            move_info=move_info,
        )

        # after each move, check if opponent has checkmate or check
        # and return this info here for easier access
        # here we have next player as after previous moves, player turn was switched
        next_player_troubles = self.get_current_player_troubles()

        return True, [], next_player_troubles

    def get_current_player_troubles(self):
        return_me = {
            "player_is_checked": False,
            "player_is_checkmated": False,
            "move_that_makes_check_disappear": {},
        }

        # no check -> no checkmate, easy
        if not self._player_has_check_in_position():
            # no troubles
            return return_me

        return_me["player_is_checked"] = True

        for piece in self.current_player_pieces:
            possible_moves = piece.get_possible_moves(board_state=self)

            if len(possible_moves) > 0:
                return_me["move_that_makes_check_disappear"] = {
                    "piece": piece,
                    "new_position": possible_moves[0]["new_position"],
                }
                return return_me

        # player is checkmated if we went to this step
        return_me["player_is_checkmated"] = True

        return return_me
