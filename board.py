import os

from rich import print

from pieces import Bishop, King, Knight, Pawn, Queen, Rook, Piece

# from rich import Console


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
        self.positions_to_piece = {}
        self.killed_opponent_pieces = {1: [], 2: []}

        self._from_cell = None
        self._to_cell = None

        self._previous_move_cell_color = previous_move_cell_color

        self.errors_to_display = []

        self._initialize_pieces()

    def __repr__(self):
        return f"Board {self._cells}"

    def _add_temporary_error(self, error_text):
        self.errors_to_display.append(error_text)

    def _reset_errors(self):
        self.errors_to_display = []

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

    def _remove_piece_from_pieces(self, piece_to_kill, piece_owner_player):
        if piece_owner_player == 1:
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

    def draw(self, player_turn):
        """
        Draw all pieces where they are belonging to, with given params
        """
        self._clear_screen()
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
                if player_turn == 2:
                    print(f"[{self.p2_color}]⬤[/]", end="")
                else:
                    print(f" ", end="")

            if row_index == 7:
                if player_turn == 1:
                    print(f"[{self.p1_color}]⬤[/]", end="")
                else:
                    print(f" ", end="")

            # display killed pieces if any
            if row_index in (0, 7):
                # pieces that player 2 killed
                killed_pieces_to_draw = (
                    self.killed_opponent_pieces[2]
                    if row_index == 0
                    else self.killed_opponent_pieces[1]
                )

                # if row_index == 7 and killed_pieces_to_draw:
                #     breakpoint()

                if killed_pieces_to_draw:
                    # left padding
                    print(" " * 2, end="")

                    # killed pieces
                    for piece in killed_pieces_to_draw:
                        print(
                            f"[{piece.color} on {self._black_cell_color}]{piece.piece_icon}[/]",
                            end="",
                        )

            # display errors if any
            if 2 <= row_index <= 6 and len(self.errors_to_display) > 0:
                error_text = self.errors_to_display.pop()

                print(
                    # padding from board
                    " " * 5,
                    # actual error message
                    f"[red]{error_text}[/]",
                    end="",
                )

            # newline
            print()

        # draw column names
        print(f"[grey37] abcdefgh[/]")
        # draw row numbers

        # reset errors after every frame update
        self._reset_errors()

    def move_a_piece_if_possible_and_add_validation_errors_if_necessary(
        self, move_str, player_turn
    ):
        """'
        args:
            1. move_str - ex: "E2 E4"
            2. player_turn - 1 or 2, for player number

        if move is not possible, return False,
        otherwise change piece positions and return True
        """
        _from, _to = move_str.split()

        # if player_turn == 2:
        #     breakpoint()

        ### make a move only if space is empty for now
        ### and move player is trying to make starts from his/her piece
        ### later add other all sorts of necessary checks

        # player tries to move his/her piece
        if player_turn == 1:
            player_pieces = self.player_1_pieces
            opponent_pieces = self.player_2_pieces
        else:
            player_pieces = self.player_2_pieces
            opponent_pieces = self.player_1_pieces

        player_pieces_positions = {i.position for i in player_pieces}

        # do move checks
        if not _from in player_pieces_positions:
            self._add_temporary_error(f"Sorry, there is no your piece on cell {_from}")
            return False

        # if _to in self.all_piece_positions:
        #     self._add_temporary_error(f"Sorry, there is no other piece on cell {_to}")
        #     return False

        # if all previous checks are done
        # get piece
        piece = self.positions_to_pieces[_from]

        # can that piece make that move ?
        move_is_valid, killed_opponent_piece = piece.can_move_to(
            _to,
            player_pieces=player_pieces,
            opponent_pieces=opponent_pieces,
            positions_to_pieces=self.positions_to_pieces,
        )
        if move_is_valid:
            piece.position = _to
        else:
            self._add_temporary_error("Invalid move")
            return False

        # breakpoint()
        if killed_opponent_piece:
            print(f"Killing {killed_opponent_piece}")
            # we may also add and show score calculations like queen = 9 pawns, e.t.c
            # who is behinde and how e.t.c
            self.killed_opponent_pieces[player_turn].append(killed_opponent_piece)
            print(f"len(self.player_2_pieces")
            self._remove_piece_from_pieces(killed_opponent_piece, player_turn)
            print(f"len(self.player_2_pieces")

        self._to_cell = _to
        self._from_cell = _from

        return True
