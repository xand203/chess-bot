import joblib #get trained model
from stockfish import Stockfish #chess ai
from chessboard_detection import ChessBoard_detector
from chess_bot import Chess_bot #class to manage the chess game
import time
import numpy as np
def main(suggestion_arrow = True):
    board_detector = ChessBoard_detector()

    #Find the borders of the chessboard and return first image 
    found,img = board_detector.find_chessboard()
    if not found: #If no chessboard found => stop program
        print("No board found!!")
        return

    bot = Chess_bot()
    if bot.find_color(img):
        print("We are white!")
        bot.execute_bestMove(board_detector.borders)
        #Update the chess board in bot to the new made move
        bot.turn(board_detector.get_chessboard())
    else:
        print("We are black!")
        #Wait for white to make his first move => execute_bestMove
        while True:
            if bot.white_move(board_detector.get_chessboard()):
                bot.execute_bestMove(board_detector.borders)
                break

    while True:
        if bot.turn(board_detector.get_chessboard()):
            if bot.execute_bestMove(board_detector.borders): break
            #Update the chess board image in bot to the new made move
            bot.turn(board_detector.get_chessboard(),True)






if __name__ == "__main__":
    main()


