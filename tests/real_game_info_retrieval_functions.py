import pgn


def get_real_game_chess_moves_history_from_pgn_file(file_path):
    """
    result structure:
        [
            # game 1
            [
                ["e3", "d5"],
                ["Nf3", "e5"],
                ...
            ],
            # game 2
            [
                ["e3", "d5"],
                ["Nf3", "e5"],
                ...
            ],
            ...
        ]
    """
    with open(file_path) as f:
        pgn_text = f.read()

    loaded_games = pgn.loads(pgn_text)  # Returns a list of PGNGame

    games_info = []

    # # breakpoint()
    for game in loaded_games:
        game_moves = []
        total_moves = 0

        for index, move in enumerate(game.moves):
            if index % 2 == 1:
                continue

            #####################################
            # temporary fix to not load moves after one
            # that we do not support yet
            if "=" in move or ("-" in move and move[0].isdigit()):
                break

            #####################################

            if total_moves % 2 == 0:
                game_moves.append([])

            game_moves[-1].append(move)
            total_moves += 1

        games_info.append(game_moves)

    return games_info
