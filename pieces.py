import abc
import copy
from util import (
    _bottom_coords,
    _bottom_left_coords,
    _bottom_right_coords,
    _current_player_has_check_in_position,
    _is_chess_cell_coord,
    _left_coords,
    _right_coords,
    _top_coords,
    _top_left_coords,
    _top_right_coords,
    get_lineraly_distant_cells_from_position,
)


class Piece(metaclass=abc.ABCMeta):
    def __init__(self, color, name, piece_icon, position, player_number):
        self.color = color
        self.name = name
        self.player_number = player_number
        self.piece_icon = piece_icon
        self._position = position
        self.moves_count = 0

    def __repr__(self):
        return (
            f"""{self.color} {self.piece_icon} on """
            f"""{self.position} {self.index_based_position}""".title()
        )

    def increase_moves_count(self):
        self.moves_count += 1

    @property
    def position(self):
        return self._position

    @property
    def current_row(self) -> int:
        """
        ex: for E2 --> 2
        """
        return int(self.position[1])

    @property
    def current_col(self) -> str:
        """
        ex: for E2 --> E
        """
        return int(self.position[1])

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
    def get_all_possible_moves_and_killed_pieces_if_moved(
        self, player_turn, positions_to_pieces
    ):
        raise NotImplementedError

    def can_move_to(self, new_position, board_state):
        """
        Todo: also add error messages for invalid moves, explaining why it is not possible - good for debugging/fixing and user/s
        """
        killed_opponent_piece = None
        can_move_there = False

        # todo: make sure if we have check and are moving cases work as expected...

        # according to rules can piece move there ?
        _possible_moves = self.get_all_possible_moves_and_killed_pieces_if_moved(
            board_state._player_turn, board_state.positions_to_pieces
        )

        # filter out not on board moves
        possible_moves = {
            i: j for i, j in _possible_moves.items() if _is_chess_cell_coord(i)
        }

        print(f"{possible_moves=}")

        if new_position in possible_moves:
            # and no check after moving there will be present for current player
            copied_board_state = copy.deepcopy(board_state)
            copied_board_state.positions_to_pieces[
                self.position
            ].position = new_position

            if not _current_player_has_check_in_position(self, copied_board_state):
                killed_opponent_piece = possible_moves[new_position]
                can_move_there = True

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

    def get_all_possible_moves_and_killed_pieces_if_moved(
        self,
        player_turn,
        positions_to_pieces,
    ):

        return get_lineraly_distant_cells_from_position(
            position=self.position,
            positions_to_pieces=positions_to_pieces,
            player_turn=player_turn,
            linearity_functions=[
                # bishop-like moves
                _top_left_coords,
                _top_right_coords,
                _bottom_left_coords,
                _bottom_right_coords,
                # rook-like moves
                _top_coords,
                _bottom_coords,
                _left_coords,
                _right_coords,
            ],
        )


class Rook(Piece):
    def __init__(self, color, position, player_number):
        super().__init__(
            color=color,
            name="rook",
            piece_icon="♜",
            position=position,
            player_number=player_number,
        )

    def get_all_possible_moves_and_killed_pieces_if_moved(
        self,
        player_turn,
        positions_to_pieces,
    ):
        return get_lineraly_distant_cells_from_position(
            position=self.position,
            positions_to_pieces=positions_to_pieces,
            player_turn=player_turn,
            linearity_functions=[
                _top_coords,
                _bottom_coords,
                _left_coords,
                _right_coords,
            ],
        )


class Bishop(Piece):
    def __init__(self, color, position, player_number):
        super().__init__(
            color=color,
            name="bishop",
            piece_icon="♝",
            position=position,
            player_number=player_number,
        )

    def get_all_possible_moves_and_killed_pieces_if_moved(
        self,
        player_turn,
        positions_to_pieces,
    ):

        return get_lineraly_distant_cells_from_position(
            position=self.position,
            positions_to_pieces=positions_to_pieces,
            player_turn=player_turn,
            linearity_functions=[
                _top_left_coords,
                _top_right_coords,
                _bottom_left_coords,
                _bottom_right_coords,
            ],
        )


class Knight(Piece):
    def __init__(self, color, position, player_number):
        super().__init__(
            color=color,
            name="knight",
            piece_icon="♞",
            position=position,
            player_number=player_number,
        )

    def get_all_possible_moves_and_killed_pieces_if_moved(
        self,
        player_turn,
        positions_to_pieces,
    ):
        possible_moves_to_killed_pieces = {}
        possible_moves = []

        _pos = self.position
        _top = _top_coords(_pos)
        _bottom = _bottom_coords(_pos)
        _left = _left_coords(_pos)
        _right = _right_coords(_pos)

        # get all possible places, performance is not issue for now
        possible_moves = [
            # top
            _top_left_coords(_top),
            _top_right_coords(_top),
            # bottom
            _bottom_left_coords(_bottom),
            _bottom_right_coords(_bottom),
            # left
            _top_left_coords(_left),
            _bottom_left_coords(_left),
            # right
            _top_right_coords(_right),
            _bottom_right_coords(_right),
        ]

        for move in possible_moves:
            # empty destination cell
            if move not in positions_to_pieces:
                possible_moves_to_killed_pieces[move] = None

            # opponent piece on cell
            elif positions_to_pieces[move].player_number != player_turn:
                possible_moves_to_killed_pieces[move] = positions_to_pieces[move]

        return possible_moves_to_killed_pieces


class Pawn(Piece):
    def __init__(self, color, position, player_number):
        super().__init__(
            color=color,
            name="pawn",
            piece_icon="♟",
            position=position,
            player_number=player_number,
        )

    def get_all_possible_moves_and_killed_pieces_if_moved(
        self,
        player_turn,
        positions_to_pieces,
    ):
        possible_moves_to_killed_pieces = {}

        # 1 up | no kill
        top_cell = (
            _top_coords(self.position)
            if player_turn == 1
            else _bottom_coords(self.position)
        )

        if top_cell not in positions_to_pieces:
            possible_moves_to_killed_pieces[top_cell] = None

            # 2 up | no kill
            if self.moves_count == 0:
                top_top_cell = (
                    _top_coords(top_cell)
                    if player_turn == 1
                    else _bottom_coords(top_cell)
                )

                if top_top_cell not in positions_to_pieces:
                    possible_moves_to_killed_pieces[top_top_cell] = None

        # up left | kill
        top_left = (
            _top_left_coords(self.position)
            if player_turn == 1
            else _bottom_right_coords(self.position)
        )
        if (
            positions_to_pieces.get(top_left)
            and positions_to_pieces.get(top_left).player_number != player_turn
        ):
            possible_moves_to_killed_pieces[top_left] = positions_to_pieces[top_left]

        # up right | kill
        top_right = (
            _top_right_coords(self.position)
            if player_turn == 1
            else _bottom_left_coords(self.position)
        )
        if (
            positions_to_pieces.get(top_right)
            and positions_to_pieces.get(top_right).player_number != player_turn
        ):
            possible_moves_to_killed_pieces[top_right] = positions_to_pieces[top_right]

        ### TO-BE-IMPLEMENTED
        # exchange pawn to queen if at the end of opposite side
        # En passant
        ### end TO-BE-IMPLEMENTED

        return possible_moves_to_killed_pieces
