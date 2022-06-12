def _is_chess_cell_coord(coord_str):
    """
    ex:
        E2 - True
        T8 - False
    """
    try:
        if all(
            [
                len(coord_str) == 2,
                coord_str[0] in "ABCDEFGH",
                coord_str[1] in "12345678",
            ]
        ):
            return True

    except Exception:
        return False


def _is_chess_move_str(move):
    """
    Just validate that move has proper format, not any logic yet

    Format:
        "E2 E4" - not case sensitive
    """
    move = move.upper().strip()
    parts = move.split()

    print(f"Checking move {move}")

    try:
        assert len(parts) == 2
        return _is_chess_cell_coord(parts[0]) and _is_chess_cell_coord(parts[1])
    except Exception:
        return False


def _player_has_check_in_position(check_for_current_player, board_state):

    # check if current player has check
    if check_for_current_player:
        king_position = board_state.current_player_king.position
        opponent_pieces = board_state.opponent_player_pieces
    # check if opponent has check
    else:
        king_position = board_state.opponent_player_king.position
        opponent_pieces = board_state.current_player_pieces

    # get all possible killing moves that opponent pieces can make
    # for pawns, we care only about killing cells here, as they can't push King forward :-)
    cells_on_which_opponent_can_kill_piece = set()

    for piece in opponent_pieces:
        cells = piece.get_all_possible_cells_where_this_piece_can_kill(
            positions_to_pieces=board_state.positions_to_pieces,
        )
        # print(piece, cells)
        # if piece.piece_name == "queen":
        #     print("==================")
        #     print("==================")
        #     print("==================")
        #     breakpoint()
        cells_on_which_opponent_can_kill_piece.update(cells)

    has_check = king_position in cells_on_which_opponent_can_kill_piece

    return has_check


# next move calculation helpers, without validation
def _top_left_coords(from_cell) -> str:
    """
    input ex:
        E2 or D1 or C4 ...
    output ex:
        f3 or g4 or b6 ...

    no validation if cell is real chess cell or not
    """
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


def get_linearly_distant_cells_from_piece_position(
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
    possible_moves_to_killed_pieces = {}

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
                    possible_moves_to_killed_pieces[curr_cell] = positions_to_pieces[
                        curr_cell
                    ]

                # defending our piece
                else:
                    current_player_cells_that_are_defended_by_this_piece.append(
                        positions_to_pieces[curr_cell]
                    )
                break
            else:
                possible_moves_to_killed_pieces[curr_cell] = None

            curr_cell = func_to_apply(curr_cell)

    return (
        current_player_cells_that_are_defended_by_this_piece,
        possible_moves_to_killed_pieces,
    )
