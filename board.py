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

        self._from_cell = None
        self._to_cell = None

        self._previous_move_cell_color = previous_move_cell_color

        self._initialize_pieces()

    def __repr__(self):
        return f"Board {self._cells}"

    def _initialize_pieces(self):
        """
        Create all pieces as they should be when game starts
        and assign them to current board object.
        """

        print("Pieces are going to be Ready!!!")

        col_1, col_2 = self.p1_color, self.p2_color

        pieces_1 = [
            Rook(color=col_1, position="A1"),
            Knight(color=col_1, position="B1"),
            Bishop(color=col_1, position="F1"),
            Queen(color=col_1, position="D1"),
            King(color=col_1, position="E1"),
            Bishop(color=col_1, position="C1"),
            Knight(color=col_1, position="G1"),
            Rook(color=col_1, position="H1"),
            Pawn(color=col_1, position="A2"),
            Pawn(color=col_1, position="B2"),
            Pawn(color=col_1, position="C2"),
            Pawn(color=col_1, position="D2"),
            Pawn(color=col_1, position="E2"),
            Pawn(color=col_1, position="F2"),
            Pawn(color=col_1, position="G2"),
            Pawn(color=col_1, position="H2"),
        ]

        pieces_2 = [
            Rook(color=col_2, position="A8"),
            Knight(color=col_2, position="B8"),
            Bishop(color=col_2, position="F8"),
            Queen(color=col_2, position="D8"),
            King(color=col_2, position="E8"),
            Bishop(color=col_2, position="C8"),
            Knight(color=col_2, position="G8"),
            Rook(color=col_2, position="H8"),
            Pawn(color=col_2, position="A7"),
            Pawn(color=col_2, position="B7"),
            Pawn(color=col_2, position="C7"),
            Pawn(color=col_2, position="D7"),
            Pawn(color=col_2, position="E7"),
            Pawn(color=col_2, position="F7"),
            Pawn(color=col_2, position="G7"),
            Pawn(color=col_2, position="H7"),
        ]

        self.player_1_pieces = pieces_1
        self.player_2_pieces = pieces_2

        print("Pieces Ready!!!")

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

            # player 2 must move
            if row_index == 0 and player_turn == 2:
                print(f"[{self.p2_color}]⬤[/]", end="")
            elif row_index == 7 and player_turn == 1:
                print(f"[{self.p1_color}]⬤[/]", end="")

            # newline
            print()

        # draw column names
        print(f"[grey37] abcdefgh[/]")
        # draw row numbers

    def move_a_piece_if_possible(self, move_str, player_turn):
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
        player_pieces = (
            self.player_1_pieces if player_turn == 1 else self.player_2_pieces
        )
        player_pieces_positions = {i.position for i in player_pieces}

        # do move checks
        if not _from in player_pieces_positions:
            print("Sorry, there is no your piece on cell", _from)
            input("Press enter when you are ready to try again")
            return False

        if _to in self.all_piece_positions:
            print("Sorry, there is a piece on cell", _to)
            input("Press enter when you are ready to try again")
            return False

        # if all previous checks are done
        # get piece
        piece = self.positions_to_pieces[_from]

        # make a move
        piece.position = _to

        self._from_cell = _from
        self._to_cell = _to

        return True

