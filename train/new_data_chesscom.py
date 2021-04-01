import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from selenium import webdriver
from generate_fen import *
from chessboard_detection import ChessBoard_detector
import time

if __name__ == "__main__":
    driver = webdriver.Firefox()
    board_detector = ChessBoard_detector()
    driver.get("https://www.chess.com/analysis")
    board_detector.find_chessboard()

    theme = input("Board theme: ")
    piece_set = input("Piece set: ")
    for x in range(5):
        driver.get("https://www.chess.com/analysis")
        fen = generate()
        print(f"fen: {fen}")
        input("Waiting...")
        board_detector.save_tiles_from_chessboard(x,piece_set,theme,fen)
