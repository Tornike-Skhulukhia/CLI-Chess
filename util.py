import copy
from collections import Counter


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
    # # check if opponent has check
    # else:
    #     king_position = board_state.opponent_player_king.position
    #     opponent_pieces = board_state.current_player_pieces

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


def convert_basic_move_notation_to_chess_notation(
    basic_move_str, board_state_before_move
):
    '''
    Make small research, and if it is necessary for pawn killing other pieces to 
    write starting column even when can be uniquely identified without it, also modify logic
    here a bit to be consistent. Decoding from chess notation works without this change.
    '''
    """
    Ex:
        "G1 F3" --> "Nf3"
    """
    assert _is_chess_move_str(basic_move_str)

    from_cell, to_cell = basic_move_str.upper().split()

    # ex: N, Q, K, ""
    moving_piece = board_state_before_move.positions_to_pieces[from_cell]
    moving_piece_col, moving_piece_row = moving_piece.position
    piece_name_prefix = moving_piece.chess_notation_prefix

    # kill | x   # inacurate for an pasaunt
    # piece_being_killed = board_state_before_move.positions_to_pieces.get(to_cell)
    # vs approach N2
    # is it 100% correct? test
    piece_being_killed = moving_piece.get_possible_moves(board_state_before_move)[
        to_cell
    ]
    kill_prefix = "x" if piece_being_killed else ""

    # check | +
    board_after_move = board_state_before_move.get_deepcopy()
    copied_piece = board_after_move.positions_to_pieces[moving_piece.position]
    # copied_piece_being_killed =
    copied_piece_being_killed = (
        board_after_move.positions_to_pieces[piece_being_killed.position]
        if piece_being_killed
        else piece_being_killed
    )

    copied_piece.change_board_pieces_state_using_move(
        new_position=to_cell,
        board_state=board_after_move,
        killed_opponent_piece=copied_piece_being_killed,
    )

    check_suffix = (
        "+"
        if _player_has_check_in_position(
            board_state=board_after_move, check_for_current_player=1
        )
        else ""
    )

    ### if there are more than 1 same type of pieces
    ### that can move to new position
    all_pieces_of_this_type = moving_piece.get_all_pieces_of_this_type(
        board_state_before_move
    )
    clarification_prefix = ""

    if len(all_pieces_of_this_type) > 1:
        possible_moves_info = {
            piece: piece.get_possible_moves(board_state_before_move)
            for piece in all_pieces_of_this_type
        }

        pieces_that_can_move_to_new_position = [
            piece for piece, moves in possible_moves_info.items() if to_cell in moves
        ]

        if len(pieces_that_can_move_to_new_position) > 1:
            cols, rows = [], []

            for piece in pieces_that_can_move_to_new_position:
                cols.append(piece.position[0])
                rows.append(piece.position[1])

            # is adding column letter enough to make clear which one moved?
            # yes, if on given column only one such piece exists
            if cols.count(moving_piece_col) == 1:
                clarification_prefix = moving_piece_col

            # yes, if on given column only one such piece exists
            elif rows.count(moving_piece_row) == 1:
                clarification_prefix = moving_piece_row
            else:
                clarification_prefix = moving_piece.position

            clarification_prefix = clarification_prefix.lower()

    return f"{piece_name_prefix}{clarification_prefix}{kill_prefix}{to_cell.lower()}{check_suffix}"


def convert_chess_notation_to_basic_move_notation(
    chess_notation, board_state_before_move
):
    """
    Ex:
        "Nf3" --> "G1 F3"
    """
    # kills and checks signs do not change move at all
    chess_notation = chess_notation.replace("+", "").replace("x", "")
    move_to = chess_notation[-2:].upper()
    move_from_str = chess_notation[:-2]

    # what piece is moving?
    if move_from_str and move_from_str[0] in "RNBQK":
        # for pieces other than pawn
        piece_letter = move_from_str[0]
        move_from_str = move_from_str[1:]
    else:
        # for pawns
        piece_letter = ""


    # pieces of given type
    possible_move_initializer_pieces = (
        board_state_before_move.get_current_player_pieces_with_piece_prefix(
            piece_letter
        )
    )

    # leave ones that can move there
    pieces_that_can_move_there = [
        i
        for i in possible_move_initializer_pieces
        if move_to in i.get_possible_moves(board_state_before_move)
    ]
    
    if len(pieces_that_can_move_there) == 1:
        # for pawn we may have unnecessary more info here

        move_from = pieces_that_can_move_there[0].position
    else:
        # if more than 1 piece can move there,
        # we will have row, column or column&row prefixes to identify exact piece
        assert 1 <= len(move_from_str) <= 2

        # get row and column for all possibilities
        row, col = "", ""
        for i in move_from_str:
            if i.isdigit():
                assert i in "12345678"
                row = i
            else:
                assert i in "abcdefgh"
                col = i.upper()

        # we have column and row given - easy
        if row and col:
            move_from = board_state_before_move.positions_to_pieces[
                f"{col}{row}"
            ].position
        else:
            # we have only row
            if row:
                pieces = [i for i in pieces_that_can_move_there if i.position[1] == row]
            # we have only column
            else:
                pieces = [i for i in pieces_that_can_move_there if i.position[0] == col]

            assert len(pieces) == 1
            move_from = pieces[0].position

    return f"{move_from} {move_to}"
