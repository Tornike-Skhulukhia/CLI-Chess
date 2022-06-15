"""
Not implemented:
    . king castling
    . an passant
    . exchanging pawn to queen or other pieces when in the end...
Bugs
    . 
"""


import copy
import os

from rich import print

from pieces import Bishop, King, Knight, Pawn, Piece, Queen, Rook
from util import (  # _get_copied_hypothetical_board_state_if_this_move_happens,; _is_chess_cell_coord,
    _player_has_check_in_position,
    convert_basic_move_notation_to_chess_notation,
    convert_chess_notation_to_basic_move_notation,
)


NO_YOUR_PIECE_ON_CELL_ERROR_FORMAT_TEXT = "Sorry, there is no your piece on cell {}"
INVALID_MOVE_ERROR_TEXT = "Invalid move"


class Board:
    def __init__(
        self,
        p1_color,
        p2_color,
        black_cell_color,
        white_cell_color,
        previous_move_cell_color,
    ):
        self.p1_color = p1_color
        self.p2_color = p2_color

        self._black_cell_color = black_cell_color
        self._white_cell_color = white_cell_color

        # also needed
        self.player_1_pieces = []
        self.player_2_pieces = []
        # self.positions_to_pieces = {}
        self.killed_opponent_pieces = {1: [], 2: []}

        self._from_cell = None
        self._to_cell = None

        self._previous_move_cell_color = previous_move_cell_color

        self.errors_to_display = []

        self._player_turn = 1

        self.total_moves_count = 0
        self.moves = []
        self.chess_notation_moves = []

        self._initialize_pieces()

    def __repr__(self):
        self.draw(debug_mode=1)

        return f"<Board object>"

    def apply_chess_notation_moves(self, moves_list):
        """
               Get list of moves written in chess notation like this:

        # link for this specific game example - https://www.chess.com/games/view/15792867

        [
            ['d4', 'Nf6'],
            ['c4', 'e6'],
            ['Nf3', 'b6'],
            ['g3', 'Bb7'],
            ['Bg2', 'Bb4+'],
            ['Bd2', 'c5'],
            ['Bxb4', 'cxb4'],
            ['O-O', 'O-O'],
            ['Nbd2', 'a5'],
            ['Re1', 'd6'],
            ['e4', 'Nfd7'],
            ['Qe2', 'e5'],
            ['Rad1', 'Nc6'],
            ['Nf1', 'Qf6'],
            ['Ne3', 'Nxd4'],
            ['Nxd4', 'exd4'],
            ['e5', 'Qxe5'],
            ['Bxb7', 'Ra7'],
            ['Qg4', 'Nf6'],
            ['Qxd4', 'Rxb7'],
            ['Qxd6', 'Qxb2'],
            ['Rd2', 'Qc3'],
            ['Nd1', 'Re8'],
            ['Rxe8+', 'Nxe8'],
            ['Nxc3', '1-0']
        ]

        apply these moves to our board and return the resulting board configuration object.

        currently checks and other warnings/errors are not rendered at all, but validations are still in place,
        so for example if last position after these moves causes check, player will not be able to play
        something that does not stop king from checking, so just the errors are not visible(we may change that if needed)
        """
        for moves in moves_list:
            for move in moves:



                basic_move = convert_chess_notation_to_basic_move_notation(move, self)

                from_cell, to_cell = basic_move.split()
                piece = self.positions_to_pieces[from_cell]

                print(f"Checking chess notation move {move} --> {basic_move}")

                self.update_moves_history(
                    last_move_from=from_cell, last_move_to=to_cell
                )

                piece.change_board_pieces_state_using_move(
                    new_position=to_cell,
                    killed_opponent_piece=piece.get_possible_moves(board_state=self)[
                        to_cell
                    ],
                    board_state=self,
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

    def update_moves_history(self, last_move_from, last_move_to):
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
        basic_move_str = f"{last_move_from} {last_move_to}"
        self.moves[-1].append(basic_move_str)

        # for chess notation history
        chess_notation_move = convert_basic_move_notation_to_chess_notation(
            basic_move_str=basic_move_str.lower(),
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

        print("Pieces are going to be Ready!!!")

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

        print("Pieces Ready!!!")

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

    @property
    def all_piece_positions(self):
        all_piece_positions = list(self.positions_to_pieces.keys())

        return all_piece_positions

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

    def move_a_piece_if_possible_and_add_validation_errors_if_necessary(self, move_str):
        """'
        args:
            1. move_str - ex: "E2 E4"

        if move is not possible, return False,
        otherwise change piece positions and return True
        """
        _from, _to = move_str.split()

        ### make a move only if space is empty for now
        ### and move player is trying to make starts from his/her piece
        ### later add other all sorts of necessary checks

        player_pieces_positions = {i.position for i in self.current_player_pieces}

        # do move checks
        if not _from in player_pieces_positions:
            self._add_temporary_error(
                NO_YOUR_PIECE_ON_CELL_ERROR_FORMAT_TEXT.format(_from)
            )
            return False

        # if all previous checks are done
        # get piece
        piece = self.positions_to_pieces[_from]

        # can that piece make that move ?
        possible_moves = piece.get_possible_moves(board_state=self)

        if not _to in possible_moves:
            self._add_temporary_error(INVALID_MOVE_ERROR_TEXT)
            return False

        killed_opponent_piece = possible_moves[_to]

        print(f"{killed_opponent_piece=}")

        # run it before making actual changes as current notations translations implementation
        # needs board state info before making actual move on board itself
        # as conversions that happen, make decisions based on current board state, not after move
        self.update_moves_history(last_move_from=_from, last_move_to=_to)

        piece.change_board_pieces_state_using_move(
            new_position=_to,
            board_state=self,
            killed_opponent_piece=killed_opponent_piece,
        )

        return True

    def get_current_player_troubles(self):
        return_me = {
            "player_is_checked": False,
            "player_is_checkmated": False,
            "move_that_makes_check_disappear": {},
        }

        # no check -> no checkmate, easy
        if not _player_has_check_in_position(
            check_for_current_player=True, board_state=self
        ):
            # no troubles
            return return_me

        return_me["player_is_checked"] = True

        for piece in self.current_player_pieces:
            possible_moves = piece.get_possible_moves(board_state=self)

            if len(possible_moves) > 0:
                return_me["move_that_makes_check_disappear"] = {
                    "piece": piece,
                    "new_position": list(possible_moves.keys())[0],
                }
                return return_me

        # player is checkmated if we went to this step
        return_me["player_is_checkmated"] = True

        return return_me
