'''

'''

from game import Game


game = Game(
    # p1_color="dark_red",
    # p2_color="green1",
    # black_cell_color="dark_blue",
    # white_cell_color="orange",
    # previous_move_cell_color="blue",
    debug_mode=True,
)


#########################################################################
# get specific starting position from chess notation moves of some game
#########################################################################
moves = [
    # ["d4", "Nf6"],  # 1
    # ["c4", "e6"],  # 2
    # ["Nf3", "b6"],  # 3
    # ["g3", "Bb7"],  # 4
    # ["Bg2", "Bb4+"],  # 5
    # ["Bd2", "c5"],  # 6
    # ["Bxb4", "cxb4"],  # 7
    # ["O-O", "O-O"],  # 8
    # ["Nbd2", "a5"],  # 9
    # ["Re1", "d6"],
    # ["e4", "Nfd7"],
    # ["Qe2", "e5"],
    # ["Rad1", "Nc6"],
    # ["Nf1", "Qf6"],
    # ["Ne3", "Nxd4"],
    # ["Nxd4", "exd4"],
    # ["e5", "Qxe5"],
    # ["Bxb7", "Ra7"],
    # ["Qg4", "Nf6"],
    # ["Qxd4", "Rxb7"],
    # ["Qxd6", "Qxb2"],
    # ["Rd2", "Qc3"],
    # ["Nd1", "Re8"],
    # ["Rxe8+", "Nxe8"],
    # ["Nxc3", "1-0"],
]
# [:6]


game.board.apply_chess_notation_moves(moves)

game.play()
