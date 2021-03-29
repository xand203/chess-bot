from stockfish import Stockfish #Chess ai
import joblib
import numpy as np
import cv2
import pyautogui #control chess game
import chess #library to manage chess board

class Chess_bot:
    def __init__(self):
        self.stockfish = Stockfish("./stockfish")
        self.knn_clf = joblib.load("train/model.pkl")

        #The board size. Should be 320 because thats what the model has been trained on
        self.board_size = 320

        self.checking = False
        self.bot_turn = True

    def find_color(self,img):
        tiles = self.get_tiles(img)

        #White if pawn at a2 is white else black
        self.white = self.knn_clf.predict([tiles[48]])[0] == 'P'

        self.board = chess.Board()

        #Set last board positions as a black board
        black_start = cv2.imread("black_board.png",cv2.IMREAD_GRAYSCALE)
        self.last_positions = self.knn_clf.predict(
            self.get_tiles(black_start)
        ).reshape(8,8)

        self.last_img = img

        return self.white

    def get_tiles(self,img):
        #Resize the image of the board
        board_img = cv2.resize(img,(self.board_size,self.board_size))

        tile_size = self.board_size // 8

        #initialize tiles array with 8 rows and columns
        tiles = list()

        for y in range(0,self.board_size,tile_size):
            for x in range(0,self.board_size,tile_size):
                tiles.append(board_img[y:y+tile_size,x:x+tile_size].flatten())

        return np.array(tiles)

    def turn(self,img,bot_move=False):
        """Return True if it's bot turn to make a move else False"""

        #If the new predicted board is different ==> new move is being made, wait till completion.
        if not np.array_equal(self.last_img,img):
            self.checking = True
            self.last_img = img
            return False
        elif self.checking: #If images are equal and move has been made
            self.checking = False

            #Get new board layout
            tiles = self.get_tiles(img)
            board_pred = self.knn_clf.predict(tiles).reshape(8,8)

            if np.array_equal(board_pred,self.last_positions):
                return False

            if not self.move(board_pred):
                self.last_positions = board_pred
                return False
            self.last_positions = board_pred

            print(self.board)
            return True
        else:
            return False
    def white_move(self,img):
        tiles = self.get_tiles(img)
        board_pred = self.knn_clf.predict(tiles).reshape(8,8)
        if not np.array_equal(self.last_positions,board_pred):
            if not self.move(board_pred):return False
            self.last_positions = board_pred

            return True

    def move(self,new_pos):
        from_moves = []
        to_moves = []
        vals = {0:"a",1:"b",2:"c",3:"d",4:"e",5:"f",6:"g",7:"h"}

        #Black and white have opposite coordinates
        Y_mod = 8 if self.white else -1
        X_mod = 7 if not self.white else 0

        for y in range(8):
            for x in range(8):
                if new_pos[y,x] != self.last_positions[y,x]:
                    pos = f"{vals[abs(x-X_mod)]}{abs(Y_mod-y)}"
                    from_moves.append(pos) if new_pos[y,x] == '1' \
                        else to_moves.append(pos)

        if len(to_moves) > 1 and len(to_moves) < 3:
            try:
                self.board.push_san("O-O")
            except ValueError:
                self.board.push_san("O-O-O")
            return True

        for from_move in from_moves:
            for to_move in to_moves:
                move = chess.Move.from_uci(f"{from_move}{to_move}")
                if move in self.board.legal_moves:
                    self.board.push(move)
                    return True

        print("Can't find any legal move")
        return False


    def execute_bestMove(self,borders):
        self.stockfish.set_fen_position(self.board.fen())

        #Get the best move from current position on a time constraint
        #Change it if you want the bot to play faster
        best_move = self.stockfish.get_best_move_time(750)
        print(f"Best move {'for opponent' if not self.bot_turn else ''} is: {best_move}")

        #Stop the program if its checkmate
        if best_move == None:
            print("We won!!")
            return True

        #Get best_move start position [X,Y]
        from_pos = self.get_pos(best_move[:2],borders)
        #Get best_move end position [X,Y]
        to_pos = self.get_pos(best_move[2:],borders)

        #Drag the piece using the positions
        pyautogui.moveTo(from_pos[0], from_pos[1], 0.01)
        pyautogui.dragTo(from_pos[0], from_pos[1] + 1, button="left", duration=0.01) #This small click is used to get the focus back on the browser window
        pyautogui.dragTo(to_pos[0],to_pos[1], button=f"{'left' if self.bot_turn else 'right'}", duration=0.3)
        pyautogui.moveTo(2,2,0.01)

        self.bot_turn = not self.bot_turn


    def get_pos(self,tile,borders):
        """Get the position from the uci format position"""
        tile_size = (borders["maxX"] - borders["minX"]) // 8
        vals = {"a":0,"b":1,"c":2,"d":3,"e":4,"f":5,"g":6,"h":7}

        #Black and white have opposite coordinates
        Y_mod = -8 if self.white else -1
        X_mod = 7 if not self.white else 0

        x,y = abs(X_mod - vals[tile[0]]),abs(Y_mod + int(tile[1]))

        Xpos = x * tile_size + tile_size//2 + borders['minX']
        Ypos = y * tile_size + tile_size//2 + borders['minY']

        return [Xpos,Ypos]




