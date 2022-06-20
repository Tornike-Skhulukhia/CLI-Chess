'''
Run this file from 1-st computer
'''
import socket
from config import HOST, PORT
from multiplayer_game import Game


# start hosting game to given host & port
Game().start_game_hosting(HOST, PORT)
