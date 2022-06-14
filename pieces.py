import abc
import copy
from util import (
    _bottom_coords,
    _bottom_left_coords,
    _bottom_right_coords,
    _player_has_check_in_position,
    _is_chess_cell_coord,
    _left_coords,
    _right_coords,
    _top_coords,
    _top_left_coords,
    _top_right_coords,
    get_linearly_distant_cells_from_piece_position,
    # _get_copied_hypothetical_board_state_if_this_move_happens,
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
        return f"Player {self.player_number} {self.piece_name.capitalize()} on {self.position}".title()

    def increase_moves_count(self):
        self.moves_count += 1

    @property
    def piece_name(self):
        return type(self).__name__.lower()

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

    @property
    def chess_notation_prefix(self):
        # no prefix for Pawns
        if self.piece_name == "pawn":
            return ""

        # Knight has N as first letter, not K
        if self.piece_name == "knight":
            return "N"

        # all others use uppercased first letter
        return self.piece_name[0].upper()

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

    def get_all_pieces_of_this_type(self, board_state):
        all_pieces = []

        for piece in board_state.positions_to_pieces.values():
            if (
                self.player_number == piece.player_number
                and self.piece_name == piece.piece_name
            ):
                all_pieces.append(piece)

        return all_pieces

    def get_all_possible_cells_where_this_piece_can_kill(self, positions_to_pieces):
        (
            defended_cells,
            moving_cells,
        ) = self.get_all_possible_moves_and_killed_pieces_if_moved(
            positions_to_pieces,
            return_defended_cells=True,
        )

        # pawns can only kill where they defend
        if self.piece_name == "pawn":
            return defended_cells

        defended_cells.extend(list(moving_cells.keys()))

        # clean defended_cells as they may have offboard values
        defended_cells = [i for i in defended_cells if _is_chess_cell_coord(i)]

        return defended_cells

    def get_possible_moves(self, board_state):
        _possible_moves = self.get_all_possible_moves_and_killed_pieces_if_moved(
            board_state.positions_to_pieces
        )

        possible_moves = {
            i: j for i, j in _possible_moves.items() if _is_chess_cell_coord(i)
        }

        valid_possible_moves = {}

        for new_position, killed_opponent_piece in possible_moves.items():

            copied_board_state = board_state.get_deepcopy()
            copied_board_state.positions_to_pieces[
                self.position
            ].change_board_pieces_state_using_move(
                new_position=new_position,
                board_state=copied_board_state,
                killed_opponent_piece=killed_opponent_piece,
                swap_player_turn=False,
            )

            if not _player_has_check_in_position(
                check_for_current_player=True,
                board_state=copied_board_state,
            ):
                valid_possible_moves[new_position] = killed_opponent_piece

        return valid_possible_moves

    def change_board_pieces_state_using_move(
        self,
        new_position,
        board_state,
        killed_opponent_piece,
        swap_player_turn=True,
    ):
        """
        move current piece in given technically valid new location and kill any piece required
        """
        # # will error if no valid move is passed in this function
        # killed_opponent_piece = self.get_possible_moves(board_state)[new_position]

        if killed_opponent_piece:
            board_state.kill_piece(killed_opponent_piece)

        self.position = new_position
        self.increase_moves_count()

        if swap_player_turn:
            board_state._swap_player_turn()


class King(Piece):
    def __init__(self, color, position, player_number):
        super().__init__(
            color=color,
            name="king",
            piece_icon="♚",
            position=position,
            player_number=player_number,
        )

    def get_all_possible_moves_and_killed_pieces_if_moved(
        self,
        positions_to_pieces,
        return_defended_cells=False,
    ):
        possible_moves_to_killed_pieces = {}
        defended_cells = []
        possible_moves = []

        _pos = self.position

        # get all possible places, performance is not issue for now
        possible_moves = [
            _top_coords(_pos),
            _bottom_coords(_pos),
            _left_coords(_pos),
            _right_coords(_pos),
            _top_left_coords(_pos),
            _top_right_coords(_pos),
            _bottom_left_coords(_pos),
            _bottom_right_coords(_pos),
        ]

        for move in possible_moves:
            # empty destination cell
            if move not in positions_to_pieces:
                possible_moves_to_killed_pieces[move] = None

            # opponent piece on cell
            elif positions_to_pieces[move].player_number != self.player_number:
                possible_moves_to_killed_pieces[move] = positions_to_pieces[move]
            # our piece on cell
            else:
                defended_cells.append(move)

        if return_defended_cells:
            return defended_cells, possible_moves_to_killed_pieces

        return possible_moves_to_killed_pieces


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
        positions_to_pieces,
        return_defended_cells=False,
    ):

        defended_cells, info = get_linearly_distant_cells_from_piece_position(
            piece=self,
            positions_to_pieces=positions_to_pieces,
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

        if return_defended_cells:
            return defended_cells, info

        return info


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
        positions_to_pieces,
        return_defended_cells=False,
    ):

        defended_cells, info = get_linearly_distant_cells_from_piece_position(
            piece=self,
            positions_to_pieces=positions_to_pieces,
            linearity_functions=[
                _top_coords,
                _bottom_coords,
                _left_coords,
                _right_coords,
            ],
        )

        if return_defended_cells:
            return defended_cells, info

        return info


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
        positions_to_pieces,
        return_defended_cells=False,
    ):

        defended_cells, info = get_linearly_distant_cells_from_piece_position(
            piece=self,
            positions_to_pieces=positions_to_pieces,
            linearity_functions=[
                _top_left_coords,
                _top_right_coords,
                _bottom_left_coords,
                _bottom_right_coords,
            ],
        )

        if return_defended_cells:
            return defended_cells, info

        return info


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
        positions_to_pieces,
        return_defended_cells=False,
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

        defended_cells = []

        for move in possible_moves:
            # empty destination cell
            if move not in positions_to_pieces:
                possible_moves_to_killed_pieces[move] = None

            # opponent piece on cell
            elif positions_to_pieces[move].player_number != self.player_number:
                possible_moves_to_killed_pieces[move] = positions_to_pieces[move]
            # our piece
            else:
                defended_cells.append(move)

        if return_defended_cells:
            return defended_cells, possible_moves_to_killed_pieces

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
        positions_to_pieces,
        return_defended_cells=False,
    ):
        possible_moves_to_killed_pieces = {}
        defended_cells = []

        # 1 up | no kill
        top_cell = (
            _top_coords(self.position)
            if self.player_number == 1
            else _bottom_coords(self.position)
        )

        if top_cell not in positions_to_pieces:
            possible_moves_to_killed_pieces[top_cell] = None

            # 2 up | no kill
            if self.moves_count == 0:
                top_top_cell = (
                    _top_coords(top_cell)
                    if self.player_number == 1
                    else _bottom_coords(top_cell)
                )

                if top_top_cell not in positions_to_pieces:
                    possible_moves_to_killed_pieces[top_top_cell] = None

        # up left | kill
        top_left = (
            _top_left_coords(self.position)
            if self.player_number == 1
            else _bottom_right_coords(self.position)
        )

        if top_left in positions_to_pieces:
            # opponent piece there
            if positions_to_pieces[top_left].player_number != self.player_number:
                possible_moves_to_killed_pieces[top_left] = positions_to_pieces[
                    top_left
                ]
            # our piece there
            else:
                defended_cells.append(top_left)

        # up right | kill
        top_right = (
            _top_right_coords(self.position)
            if self.player_number == 1
            else _bottom_left_coords(self.position)
        )

        if top_right in positions_to_pieces:
            # opponent piece there
            if positions_to_pieces[top_right].player_number != self.player_number:
                possible_moves_to_killed_pieces[top_right] = positions_to_pieces[
                    top_right
                ]
            # our piece there
            else:
                defended_cells.append(top_right)

        ### TO-BE-IMPLEMENTED
        # exchange pawn to queen if at the end of opposite side
        # En passant
        ### end TO-BE-IMPLEMENTED

        if return_defended_cells:
            return defended_cells, possible_moves_to_killed_pieces

        return possible_moves_to_killed_pieces
