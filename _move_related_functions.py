def _is_chess_cell_coord(coord_str):
    """
    ex:
        E2 - True
        T8 - False
    """
    res = False

    try:
        if all(
            [
                len(coord_str) == 2,
                coord_str[0] in "ABCDEFGH",
                coord_str[1] in "12345678",
            ]
        ):
            res = True

    except Exception:
        pass

    return res


def _is_chess_basic_move_str(move):
    """
    Just validate that move has proper format, not any logic yet

    Format:
        "E2 E4" - case insensitive
    """
    if not isinstance(move, str):
        return False

    move = move.upper()

    # special cases for castling
    if move in ("O-O", "O-O-O"):
        return True

    parts = move.split()

    try:
        assert len(parts) == 2
        return _is_chess_cell_coord(parts[0]) and _is_chess_cell_coord(parts[1])
    except Exception:
        return False


def _is_chess_notation_move_str(move):
    """
    This does not need to be perfect, just good enough, as only used for real game notations.

    We can refine it later if necessary.
    """

    try:
        assert len(move) >= 2

        # special cases for castling
        if move in ("O-O", "O-O-O"):
            return True

        assert " " not in move

        assert all([i in "abcdefgh12345678xKQNBR+x" for i in move])

        # check can only be at the end
        if move.count("+") > 0:
            assert move.endswith("+")
            move = move[:-1]

        # kills
        if move.count("x") > 0:
            # max 1 kill sign
            assert move.count("x") == 1
            # but not at the start(even for pawn, first will be column if killing something)
            assert not move.startswith("x")

            move = move.replace("x", "")

        # digits
        digits_count = len([i for i in move if i.isdigit()])
        assert 1 <= digits_count <= 2

        assert move[-1].isdigit()

        if digits_count == 2:
            assert move[-3].isdigit()

        # if piece prefix is here
        if any([i for i in move if i in "KQNBR"]):
            # it must be first letter
            assert move[0] in "KQNBR"
            # and the only one
            assert len([i for i in move if i in "KQNBR"]) == 1

        return True
    except AssertionError:
        return False


# next move calculation helpers, without validation
def _top_left_coords(from_cell) -> str:
    col, row = from_cell

    return chr(ord(col) - 1) + str(int(row) + 1)


def _top_right_coords(from_cell) -> str:
    col, row = from_cell
    return chr(ord(col) + 1) + str(int(row) + 1)


def _top_coords(from_cell) -> str:
    col, row = from_cell
    return col + str(int(row) + 1)


def _left_coords(from_cell) -> str:
    col, row = from_cell
    return chr(ord(col) - 1) + row


def _right_coords(from_cell) -> str:
    col, row = from_cell
    return chr(ord(col) + 1) + row


def _bottom_left_coords(from_cell) -> str:
    col, row = from_cell
    return chr(ord(col) - 1) + str(int(row) - 1)


def _bottom_right_coords(from_cell) -> str:
    col, row = from_cell
    return chr(ord(col) + 1) + str(int(row) - 1)


def _bottom_coords(from_cell) -> str:
    col, row = from_cell
    return col + str(int(row) - 1)


def _get_linearly_distant_cells_from_piece_position(
    piece, positions_to_pieces, linearity_functions
):
    """
    ex, lets say we got cell E4 and 2 linearity functions and 4 functions
    that get next cells based on top, bottom, left and right positions of current
    cells respectively, then this function will try to follow from
    given position cell to given function-orienting cells until it can and
    return resulting cells to opposite player pieces dictionary that will be useful
    in outer functions that decide where the piece can move.

    We plan to use this function with diagonal functions for Bishop, with straight functions
    for Rook and with linear and straight functions for Queen.

    Having it written one place is better than having in multiple places, also its usage will be
    super easy from callers.
    """
    # possible_moves_to_killed_pieces = []
    possible_moves_info = []

    # useful, as we can not kill our piece here, but we defend them, so their King cant kill them
    current_player_cells_that_are_defended_by_this_piece = []

    for func_to_apply in linearity_functions:
        curr_cell = func_to_apply(piece.position)

        for _ in range(7):
            if not _is_chess_cell_coord(curr_cell):
                break

            # some piece found there
            if curr_cell in positions_to_pieces:
                # it is not our piece
                if positions_to_pieces[curr_cell].player_number != piece.player_number:

                    possible_moves_info.append(
                        {
                            "new_position": curr_cell,
                            "killed_opponent_piece_position": positions_to_pieces[
                                curr_cell
                            ].position,
                        }
                    )

                # defending our piece
                else:
                    current_player_cells_that_are_defended_by_this_piece.append(
                        positions_to_pieces[curr_cell]
                    )
                break
            else:
                possible_moves_info.append(
                    {"new_position": curr_cell, "killed_opponent_piece_position": None}
                )

            curr_cell = func_to_apply(curr_cell)

    return (
        current_player_cells_that_are_defended_by_this_piece,
        possible_moves_info,
    )
