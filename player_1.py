"""
Run this file from 1-st computer to start the game.

After successfully starting it, you will see prompt asking
you to connect to this game from the second player, after which the game starts.

. If you are just playing with functionality from the same PC,
use "localhost" as HOST and any available port for PORT when running this script
and the same values in player_2.py file.

. If you want to play with other person(2 player chess), set HOST to "" in this file and 
PORT to some available port number. After this, on the second computer, 
run player_2.py file with HOST value of your local/external IP address where this(player_1.py) 
script is started and same PORT. 
"""

from config import HOST, PORT
from multiplayer_game import Game

# start hosting game to given host & port.
# you can start Game here without any parameters and play it with default styling
# but if you want, there are some modifications possible as seen next

game = Game(
    # uncomment if you want to play with colors. This changes will be applied only to current player screen,
    # player_2 can do similar changes for itself. Warning: Some colors may not work in some Terminals
    p1_color="dark_red",  # what color to use for first(usually white) player
    p2_color="purple4",  # what color to use for second(usually black) player
    black_cell_color="grey58",  # black background cell color
    white_cell_color="grey37",  # white background cell colors can also be modified
    previous_move_cell_color="yellow",  # previous move color
    debug_mode=1,  # set to 0 or False if do not want to see moves history and other debug info
)

# # you can also load games from Chess notation text
# # for example, to apply some moves to current initial board state,
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

# of course, if applying previous moves and playing with other player,
# make sure they also do the same thing, otherwise your board states will not match
# so game will not be correctly playable

game.start_game_hosting(HOST, PORT)

# link to all available colors https://rich.readthedocs.io/en/stable/appendix/colors.html
