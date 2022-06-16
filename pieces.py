import abc
from _move_related_functions import (
    _bottom_coords,
    _bottom_left_coords,
    _bottom_right_coords,
    _is_chess_cell_coord,
    _left_coords,
    _right_coords,
    _top_coords,
    _top_left_coords,
    _top_right_coords,
    _get_linearly_distant_cells_from_piece_position,
)


class Piece(metaclass=abc.ABCMeta):
    """
    Chess piece superclass for subclasses like Pawn, Queen, King e.t.c
    """

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
        self.increase_moves_count()

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

    def get_all_possible_cells_where_this_piece_can_kill(self, board_state):

        # try:
        (defended_cells, moves_info,) = self.get_technically_valid_moves_info_for_piece(
            board_state,
            return_defended_cells=True,
            return_only_places_where_piece_can_directly_kill=True,
        )
        # except:
        #     breakpoint()

        # pawns can only kill where they defend
        if self.piece_name == "pawn":
            return defended_cells

        defended_cells.extend([i["new_position"] for i in moves_info])

        # clean defended_cells as they may have offboard values
        defended_cells = [i for i in defended_cells if _is_chess_cell_coord(i)]

        return defended_cells

    def get_possible_moves(self, board_state):
        _possible_moves = self.get_technically_valid_moves_info_for_piece(board_state)

        possible_moves = [
            i for i in _possible_moves if _is_chess_cell_coord(i["new_position"])
        ]

        valid_possible_moves = []

        for move_info in possible_moves:

            copied_board_state = board_state.get_deepcopy()
            copied_piece = copied_board_state.positions_to_pieces[self.position]

            # apply move itself
            copied_piece.apply_move_info_to_board(
                board_state=copied_board_state,
                move_info=move_info,
                swap_player_turn=False,
            )

            if not copied_board_state._player_has_check_in_position():
                valid_possible_moves.append(move_info)

        return valid_possible_moves

    def apply_move_info_to_board(
        self,
        board_state,
        move_info,
        swap_player_turn=True,
    ):
        """
        Execute given move_info instructions to make a move on board.

        Usually it means moving a piece and killing other piece if necessary, but in case of
        castling, we here will also get additional info about rook that needs to be also moved
        when doing castle operation with king so we also handle that.
        """

        if move_info["killed_opponent_piece_position"]:
            killed_opponent_piece = board_state.positions_to_pieces[
                move_info["killed_opponent_piece_position"]
            ]

            board_state.kill_piece(killed_opponent_piece)

        self.position = move_info["new_position"]

        # also handle rooks in case of castling
        if move_info.get("additional_movements"):
            _from, _to = (
                move_info["additional_movements"]["from"],
                move_info["additional_movements"]["to"],
            )

            rook = board_state.positions_to_pieces[_from]
            rook.position = _to

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

    def get_technically_valid_moves_info_for_piece(
        self,
        board_state,
        return_defended_cells=False,
        return_only_places_where_piece_can_directly_kill=False,
    ):
        # use second argument to avoid recursion limit.
        # we do not need to know if opponent king have check, when checking where it kills
        # so, for example, it can kill place where our king wants to move
        # but this case is losing for ourselves, so here case no problem should arise
        assert return_only_places_where_piece_can_directly_kill == return_defended_cells

        positions_to_pieces = board_state.positions_to_pieces

        possible_moves_info = []
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
                possible_moves_info.append(
                    {
                        "new_position": move,
                        "killed_opponent_piece_position": None,
                    }
                )

            # opponent piece on cell
            elif positions_to_pieces[move].player_number != self.player_number:
                possible_moves_info.append(
                    {
                        "new_position": move,
                        "killed_opponent_piece_position": positions_to_pieces[
                            move
                        ].position,
                    }
                )
            # our piece on cell
            else:
                defended_cells.append(move)

        # is castling possible ?
        if not return_only_places_where_piece_can_directly_kill:
            for castling_case, castle_notation in {
                "short": "O-O",
                "long": "O-O-O",
            }.items():

                rook_info = board_state._get_player_rook_info_if_possible_to_do_castling_with_it(
                    castling_case
                )

                king_info = board_state._get_player_king_info_if_possible_to_do_castling_with_it(
                    castling_case
                )

                if bool(rook_info) and bool(king_info):
                    old_rook_pos, new_rook_pos = rook_info
                    new_king_pos = king_info

                    possible_moves_info.append(
                        {
                            "new_position": new_king_pos,
                            "killed_opponent_piece_position": None,
                            "additional_movements": {
                                "from": old_rook_pos,
                                "to": new_rook_pos,
                            },
                            "castle_notation": castle_notation,
                        }
                    )

        if return_defended_cells:
            return defended_cells, possible_moves_info

        return possible_moves_info


class Queen(Piece):
    def __init__(self, color, position, player_number):
        super().__init__(
            color=color,
            name="queen",
            piece_icon="♛",
            position=position,
            player_number=player_number,
        )

    def get_technically_valid_moves_info_for_piece(
        self,
        board_state,
        return_defended_cells=False,
        return_only_places_where_piece_can_directly_kill=False,
    ):
        positions_to_pieces = board_state.positions_to_pieces

        defended_cells, info = _get_linearly_distant_cells_from_piece_position(
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

    def get_technically_valid_moves_info_for_piece(
        self,
        board_state,
        return_defended_cells=False,
        return_only_places_where_piece_can_directly_kill=False,
    ):
        positions_to_pieces = board_state.positions_to_pieces

        defended_cells, info = _get_linearly_distant_cells_from_piece_position(
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

    def get_technically_valid_moves_info_for_piece(
        self,
        board_state,
        return_defended_cells=False,
        return_only_places_where_piece_can_directly_kill=False,
    ):
        positions_to_pieces = board_state.positions_to_pieces

        defended_cells, info = _get_linearly_distant_cells_from_piece_position(
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

    def get_technically_valid_moves_info_for_piece(
        self,
        board_state,
        return_defended_cells=False,
        return_only_places_where_piece_can_directly_kill=False,
    ):
        positions_to_pieces = board_state.positions_to_pieces

        # possible_moves_to_killed_pieces = {}
        possible_moves_info = []
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
                possible_moves_info.append(
                    {
                        "new_position": move,
                        "killed_opponent_piece_position": None,
                    }
                )

            # opponent piece on cell
            elif positions_to_pieces[move].player_number != self.player_number:
                possible_moves_info.append(
                    {
                        "new_position": move,
                        "killed_opponent_piece_position": positions_to_pieces[
                            move
                        ].position,
                    }
                )
            # our piece
            else:
                defended_cells.append(move)

        if return_defended_cells:
            return defended_cells, possible_moves_info

        return possible_moves_info


class Pawn(Piece):
    def __init__(self, color, position, player_number):
        super().__init__(
            color=color,
            name="pawn",
            piece_icon="♟",
            position=position,
            player_number=player_number,
        )

    def get_technically_valid_moves_info_for_piece(
        self,
        board_state,
        return_defended_cells=False,
        return_only_places_where_piece_can_directly_kill=False,
    ):
        positions_to_pieces = board_state.positions_to_pieces

        # possible_moves_to_killed_pieces = {}
        possible_moves_info = []
        defended_cells = []

        # 1 up | no kill
        top_cell = (
            _top_coords(self.position)
            if self.player_number == 1
            else _bottom_coords(self.position)
        )

        if top_cell not in positions_to_pieces:
            possible_moves_info.append(
                {
                    "new_position": top_cell,
                    "killed_opponent_piece_position": None,
                }
            )

            # 2 up | no kill
            if self.moves_count == 0:
                top_top_cell = (
                    _top_coords(top_cell)
                    if self.player_number == 1
                    else _bottom_coords(top_cell)
                )

                if top_top_cell not in positions_to_pieces:
                    possible_moves_info.append(
                        {
                            "new_position": top_top_cell,
                            "killed_opponent_piece_position": None,
                        }
                    )

        # up left | kill
        top_left = (
            _top_left_coords(self.position)
            if self.player_number == 1
            else _bottom_right_coords(self.position)
        )

        if top_left in positions_to_pieces:
            # opponent piece there
            if positions_to_pieces[top_left].player_number != self.player_number:
                possible_moves_info.append(
                    {
                        "new_position": top_left,
                        "killed_opponent_piece_position": positions_to_pieces[
                            top_left
                        ].position,
                    }
                )

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
                # possible_moves_to_killed_pieces[top_right] = positions_to_pieces[
                #     top_right
                # ]

                possible_moves_info.append(
                    {
                        "new_position": top_right,
                        "killed_opponent_piece_position": positions_to_pieces[
                            top_right
                        ].position,
                    }
                )
            # our piece there
            else:
                defended_cells.append(top_right)

        ### An passant
        if board_state.total_moves_count > 0:
            opponents_last_moves = []

            for two_player_moves in board_state.moves:
                try:
                    if board_state._player_turn == 1:
                        opponents_last_moves.append(two_player_moves[1])
                    else:
                        opponents_last_moves.append(two_player_moves[0])
                except IndexError:
                    pass

            opponents_last_move = opponents_last_moves[-1]

            # for basic moves, we will hav space
            if " " in opponents_last_move:
                last_move_from, last_move_to = opponents_last_move.split()
            else:
                # for other moves we do not care about an pasants
                last_move_from, last_move_to = "", ""

        # check for white player
        if self.player_number == 1:
            # whites can do it only from 5-th row
            if self.position[-1] == "5":

                # left an passant check
                left_cell = _left_coords(self.position)
                if last_move_to == left_cell:

                    if last_move_to in board_state.positions_to_pieces:
                        last_moved_piece = board_state.positions_to_pieces[last_move_to]

                        if (
                            last_moved_piece.piece_name == "pawn"
                            and last_moved_piece.moves_count == 1
                        ):
                            possible_moves_info.append(
                                {
                                    "new_position": _top_coords(left_cell),
                                    "killed_opponent_piece_position": left_cell,
                                }
                            )

                # right an passant check
                right_cell = _right_coords(self.position)
                if last_move_to == right_cell:

                    if last_move_to in board_state.positions_to_pieces:

                        last_moved_piece = board_state.positions_to_pieces[last_move_to]

                        if (
                            last_moved_piece.piece_name == "pawn"
                            and last_moved_piece.moves_count == 1
                        ):
                            possible_moves_info.append(
                                {
                                    "new_position": _top_coords(right_cell),
                                    "killed_opponent_piece_position": right_cell,
                                }
                            )

        elif self.player_number == 2:
            # blacks can do it only from 4-th row
            if self.position[-1] == "4":

                # left from whites perspective an passant check
                left_cell = _left_coords(self.position)
                if last_move_to == left_cell:
                    if last_move_to in board_state.positions_to_pieces:

                        last_moved_piece = board_state.positions_to_pieces[last_move_to]

                        if (
                            last_moved_piece.piece_name == "pawn"
                            and last_moved_piece.moves_count == 1
                        ):
                            possible_moves_info.append(
                                {
                                    "new_position": _bottom_coords(left_cell),
                                    "killed_opponent_piece_position": left_cell,
                                }
                            )

                # right from whites perspective an passant check
                right_cell = _right_coords(self.position)
                if last_move_to == right_cell:

                    if last_move_to in board_state.positions_to_pieces:
                        last_moved_piece = board_state.positions_to_pieces[last_move_to]

                        if (
                            last_moved_piece.piece_name == "pawn"
                            and last_moved_piece.moves_count == 1
                        ):
                            possible_moves_info.append(
                                {
                                    "new_position": _bottom_coords(right_cell),
                                    "killed_opponent_piece_position": right_cell,
                                }
                            )

        ### TO-BE-IMPLEMENTED
        # exchange pawn to queen if at the end of opposite side
        ### end TO-BE-IMPLEMENTED

        if return_defended_cells:
            return defended_cells, possible_moves_info

        return possible_moves_info
