from game import Game

game = Game(
    # p1_color="dark_red",
    # p2_color="green1",
    # black_cell_color="dark_blue",
    # white_cell_color="orange",
    # previous_move_cell_color="blue",
)
#########################################################################
# get specific starting position from chess notation moves of some game
#########################################################################
moves = [
    ["d4", "Nf6"],
    ["c4", "e6"],
    ["Nf3", "b6"],
    ["g3", "Bb7"],
    ["Bg2", "Bb4+"],
    ["Bd2", "c5"],
    ["Bxb4", "cxb4"],
    ["O-O", "O-O"],
    ["Nbd2", "a5"],
    ["Re1", "d6"],
    ["e4", "Nfd7"],
    ["Qe2", "e5"],
    ["Rad1", "Nc6"],
    ["Nf1", "Qf6"],
    ["Ne3", "Nxd4"],
    ["Nxd4", "exd4"],
    ["e5", "Qxe5"],
    ["Bxb7", "Ra7"],
    ["Qg4", "Nf6"],
    ["Qxd4", "Rxb7"],
    ["Qxd6", "Qxb2"],
    ["Rd2", "Qc3"],
    ["Nd1", "Re8"],
    ["Rxe8+", "Nxe8"],
    ["Nxc3", "1-0"],
][:1]

game.board.apply_chess_notation_moves(moves)

# make sure state is recovered and no errors appeared during it
# this will make sure that lots of functions work correctly in real game


###############
game.play()
