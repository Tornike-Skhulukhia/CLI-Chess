import copy


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


def _get_copied_hypothetical_board_state_if_this_move_happens(
    current_board, piece, new_position, killed_opponent_piece
):
    # in this hypothetical new state
    copied_board_state = copy.deepcopy(current_board)

    copied_piece = copied_board_state.positions_to_pieces[piece.position]

    copied_killed_opponent_piece = (
        copied_board_state.positions_to_pieces[killed_opponent_piece.position]
        if killed_opponent_piece is not None
        else None
    )

    copied_piece.make_a_move(
        new_position=new_position,
        killed_opponent_piece=copied_killed_opponent_piece,
        board_state=copied_board_state,
    )

    return copied_board_state


def convert_basic_move_notation_to_chess_notation(
    basic_move_str, board_state_before_move
):
    """
    Ex:
        "G1 F3" --> "Nf3"
    """
    from_cell, to_cell = basic_move_str.upper().split()

    # ex: N, Q, K, ""
    moving_piece = board_state_before_move.positions_to_pieces[from_cell]
    piece_name_prefix = moving_piece.chess_notation_prefix

    # kill | x   # inacurate for an pasaunt
    piece_being_killed = board_state_before_move.positions_to_pieces.get(to_cell)
    kill_prefix = "x" if piece_being_killed else ""

    # check | +
    board_after_move = _get_copied_hypothetical_board_state_if_this_move_happens(
        current_board=board_state_before_move,
        piece=moving_piece,
        new_position=to_cell,
        killed_opponent_piece=piece_being_killed,
    )
    board_after_move._swap_player_turn()
    check_suffix = (
        "+"
        if _player_has_check_in_position(
            board_state=board_after_move, check_for_current_player=1
        )
        else ""
    )

    # if not clear where move starts, we also need these
    from_col_letter_prefix = ""
    from_row_num_prefix = ""

    return f"{piece_name_prefix}{kill_prefix}{to_cell.lower()}{check_suffix}"
