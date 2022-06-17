from _move_related_functions import _is_chess_basic_move_str


def convert_basic_move_notation_to_chess_notation(
    basic_move_str, board_state_before_move
):
    """
    Ex:
        "G1 F3" --> "Nf3"
    """
    assert _is_chess_basic_move_str(basic_move_str)

    # special case - short or long castle
    if basic_move_str in ("O-O", "O-O-O"):
        return basic_move_str

    from_cell, to_cell = basic_move_str.upper().split()

    # ex: N, Q, K, ""
    (
        move_info,
        moving_piece,
        _from,
        _to,
    ) = board_state_before_move.get_move_info_if_it_is_valid_move_str(basic_move_str)
    try:
        assert bool(move_info)
    except:
        breakpoint()

    moving_piece_col, moving_piece_row = moving_piece.position
    piece_name_prefix = moving_piece.chess_notation_prefix

    # kill | x   # inacurate for an pasaunt ?
    piece_being_killed = move_info.get("killed_opponent_piece_position")

    kill_prefix = "x" if piece_being_killed else ""

    # check | +
    board_after_move = board_state_before_move.get_deepcopy()
    copied_piece = board_after_move.positions_to_pieces[moving_piece.position]

    copied_piece.apply_move_info_to_board(
        board_state=board_after_move,
        move_info=move_info,
    )

    check_suffix = "+" if board_after_move._player_has_check_in_position() else ""

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
            piece
            for piece, moves_infos in possible_moves_info.items()
            if to_cell in [i["new_position"] for i in moves_infos]
        ]

        assert len(pieces_that_can_move_to_new_position) > 0

        if len(pieces_that_can_move_to_new_position) > 1:
            cols, rows = [], []

            for piece in pieces_that_can_move_to_new_position:
                cols.append(piece.position[0])
                rows.append(piece.position[1])

            # is adding column letter enough to make clear which one moved?
            # yes, if on given column only one such piece exists
            if cols.count(moving_piece_col) == 1:
                clarification_prefix = moving_piece_col

            # yes, if on given row only one such piece exists
            elif rows.count(moving_piece_row) == 1:
                clarification_prefix = moving_piece_row
            else:
                clarification_prefix = moving_piece.position

            clarification_prefix = clarification_prefix.lower()

        elif kill_prefix and piece_name_prefix == "":
            # for pawns, if they kill other pieces, add starting column
            # (even though not always necessary to know from which piece it was killed)
            clarification_prefix = moving_piece_col.lower()

    return f"{piece_name_prefix}{clarification_prefix}{kill_prefix}{to_cell.lower()}{check_suffix}"


def convert_chess_notation_to_basic_move_notation(
    chess_notation, board_state_before_move
):
    """
    Ex:
        "Nf3" --> "G1 F3"
    """
    # special case - short or long castle
    if chess_notation in ("O-O", "O-O-O"):
        return chess_notation

    chess_notation_bak = chess_notation

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
        if move_to
        in [i["new_position"] for i in i.get_possible_moves(board_state_before_move)]
    ]

    if len(pieces_that_can_move_there) == 0:
        raise ValueError(
            f"Move {chess_notation_bak} does not seem valid/possible on current board"
        )

    elif len(pieces_that_can_move_there) == 1:
        # for pawn we may have unnecessary more info here

        move_from = pieces_that_can_move_there[0].position
    else:
        # if more than 1 piece can move there,
        # we will have row, column or column&row prefixes to identify exact piece
        if not 1 <= len(move_from_str) <= 2:
            raise ValueError(
                f"Can not uniquely identify which piece to use for given move {chess_notation_bak}"
            )

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
