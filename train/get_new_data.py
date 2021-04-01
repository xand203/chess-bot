from selenium import webdriver
import mss
from train.generate_fen import *
from chessboard_detection import ChessBoard_detector
import time

if __name__ == "__main__":
    driver = webdriver.Firefox()
    board_detector = ChessBoard_detector()
    while True:
        driver.get("https://lichess.org/editor")
        theme = input("Board theme: ")
        piece_set = input("Piece set: ")
        for x in range(11):
            fen = generate()
            driver.get(f"https://lichess.org/editor/{fen}")
            board_detector.save_tiles_from_chessboard(x,piece_set,theme,fen)

    driver.close()

