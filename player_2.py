"""
Run this file from 2-nd computer
"""
import socket
from config import HOST, PORT
from multiplayer_game import Game

# start hosting game to given host & port
game = Game().connect_to_hosted_game(HOST, PORT)
