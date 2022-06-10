import abc


class Piece(metaclass=abc.ABCMeta):
    def __init__(self, color, name, piece_icon, position, player_number):
        self.color = color
        self.name = name
        self.player_number = player_number
        self.piece_icon = piece_icon
        self._position = position

    def __repr__(self):
        return (
            f"""{self.color} {self.piece_icon} on """
            f"""{self.position} ({self.index_based_position})""".title()
        )

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, position):

        # basic check that position is not outside of board
        try:
            assert position and position[0] in "ABCDEFGH" and position[1] in "12345678"
        except Exception:
            raise ValueError("Please use correct position from Range A1 to H8")

        self._position = position

    @staticmethod
    def index_based_position_to_position(index_based_position):
        row_number = 8 - index_based_position[0]
        col_letter = "ABCDEFGH"[index_based_position[1]]

        return f"{col_letter}{row_number}"

    @staticmethod
    def position_to_index_based_position(position):
        index_based_position = (
            # row index
            8 - int(position[1]),
            # column index
            {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5, "G": 6, "H": 7}[
                position[0]
            ],
        )

        return index_based_position

    @property
    def index_based_position(self):
        """
        ex:
            get "A1" like current piece position and return {"column_index": 0, "row_index": 7}.

            explanation:
                A is translated to row number 7, and 1 translated into column 0

                Columns start from top to bottom as board is drawn from top to bottom.
        """
        result = self.position_to_index_based_position(self.position)

        return result

    # @abc.abstractmethod
    # def can_move_to(
    #     self, new_position, player_pieces, opponent_pieces, positions_to_pieces
    # ):
    #     """
    #     Move object to new location if
    #     combination of pieces on board allows it
    #     """
    #     raise NotImplementedError

    def can_move_to(
        self, new_position, player_pieces, opponent_pieces, positions_to_pieces
    ):
        # is move valid for this piece
        can_move_there = True
        killed_opponent_piece = None

        # will opponent piece be killed with this move?
        if (
            new_position in positions_to_pieces
            and positions_to_pieces[new_position].player_number
            != player_pieces[0].player_number
        ):
            killed_opponent_piece = positions_to_pieces[new_position]

        return can_move_there, killed_opponent_piece


class King(Piece):
    def __init__(self, color, position, player_number):
        super().__init__(
            color=color,
            name="king",
            piece_icon="♚",
            position=position,
            player_number=player_number,
        )

    # def can_move_to(
    #     self, new_position, player_pieces, opponent_pieces, positions_to_pieces
    # ):
    #     return


class Queen(Piece):
    def __init__(self, color, position, player_number):
        super().__init__(
            color=color,
            name="queen",
            piece_icon="♛",
            position=position,
            player_number=player_number,
        )

    # def can_move_to(
    #     self, new_position, player_pieces, opponent_pieces, positions_to_pieces
    # ):
    #     return


class Rook(Piece):
    def __init__(self, color, position, player_number):
        super().__init__(
            color=color,
            name="rook",
            piece_icon="♜",
            position=position,
            player_number=player_number,
        )

    # def can_move_to(
    #     self, new_position, player_pieces, opponent_pieces, positions_to_pieces
    # ):
    #     return


class Bishop(Piece):
    def __init__(self, color, position, player_number):
        super().__init__(
            color=color,
            name="bishop",
            piece_icon="♝",
            position=position,
            player_number=player_number,
        )

    # def can_move_to(
    #     self, new_position, player_pieces, opponent_pieces, positions_to_pieces
    # ):
    #     return


class Knight(Piece):
    def __init__(self, color, position, player_number):
        super().__init__(
            color=color,
            name="knight",
            piece_icon="♞",
            position=position,
            player_number=player_number,
        )

    # def can_move_to(
    #     self, new_position, player_pieces, opponent_pieces, positions_to_pieces
    # ):
    #     return


class Pawn(Piece):
    def __init__(self, color, position, player_number):
        super().__init__(
            color=color,
            name="pawn",
            piece_icon="♟",
            position=position,
            player_number=player_number,
        )
