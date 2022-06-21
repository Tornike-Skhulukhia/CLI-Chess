"""
After starting player_1.py file, run this file to connect to the created game and make it start.

If connection does not work, please read player_1.py file comments 
where it is explained how to set HOST and PORT correctly.

Also make sure that firewall or other similar software is not blocking connections to given ports.
"""

from config import HOST, PORT
from multiplayer_game import Game

# start hosting game to given host & port
game = Game()

# # # you can also load games from Chess notation text
# # # for example, to apply some moves to current initial board state,
# # you can do something like this
# game.board.apply_chess_notation_moves(
#     [
#         ["d3", "d5"],
#         ["Bf4", "Bg4"],
#         ["Nc3", "Nf6"],
#         ["Qd2", "e6"],
#         ["e3", "Bb4"],
#     ]
# )


game.connect_to_hosted_game(HOST, PORT)
