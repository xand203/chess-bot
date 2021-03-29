import numpy as np
import cv2 #OpenCV
import pyautogui #Used to take screenshots and move the mouse
import random #Use the generate random numbers for processing time
import time #Used to time the executions
import mss #Used to get superfast screenshots
import os
import glob

class ChessBoard_detector:
    def __init__(self):
        self.sct = mss.mss()
    def save_tiles_from_chessboard(self,num,piece_set,theme,fen):
        '''Function to save every tile of the chessboard as png image ==> use to create dataset'''
        for x in range(2,9):
            fen = fen.replace(str(x),x*'1')

        board = fen.split('/')

        path = 'dataset/data'
        piece_path = os.path.join(path,piece_set)
        full_path = os.path.join(path,piece_set,theme)

        found,board_img = self.find_chessboard()
        if not found:return False

        if piece_set not in os.listdir(path):
            os.mkdir(piece_path)
            os.mkdir(full_path)
        elif theme not in os.listdir(piece_path):
            os.mkdir(full_path)


        #Resize the image of the board
        board_img = cv2.resize(board_img,(320,320))

        length = np.shape(board_img)[0]
        tile_size = length // 8

        for y in range(0,length,tile_size):
            for x in range(0,length,tile_size):
                cv2.imwrite(os.path.join(full_path,
                            f"{num}-{y//tile_size}_{x//tile_size}-{board[y//tile_size][x//tile_size]}.png"),
                            board_img[y:(y+tile_size),x:(x+tile_size)])
    def get_chessboard(self):
        img = np.array(np.array(self.sct.grab(self.monitor)))
        gray_img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        return gray_img[self.borders["minY"]:self.borders["maxY"],
                        self.borders["minX"]:self.borders["maxX"]]

    def find_chessboard(self):
        #We do a first classical screenshot to see the screen size:
        screenshot_shape = np.array(pyautogui.screenshot()).shape
        self.monitor = {'top': 0, 'left': 0, 'width': screenshot_shape[1], 'height': screenshot_shape[0]}
        img = np.array(np.array(self.sct.grab(self.monitor)))
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        gray = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
        is_found, current_chessboard_image,minX,minY,maxX,maxY,test_image = self.find_chessboard_from_image(img)
        self.borders = {
            "minY":minY,"minX":minX,"maxY":maxY,"maxX":maxX
        }
        return is_found, gray[minY:maxY,minX:maxX]

    def find_chessboard_from_image(self,img):
        #The algorithm here is much faster than the previous one:
        #1 Get the horizontal lines by convolving the image with [[-1,1]], get the indexes with the most start and end lines
        #2 Get the vertical lines by convolving the image with [[-1],[1]], get the indexes with the most start and end lines
        #3 Check if there is only one probable start and end for each dimension, and the board is squared
        #4 Resize the image to a std dimension to standardize the treatments

        #Converting the image in grayscale:
        image = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        found_board = False

        kernelH = np.array([[-1,1]])
        kernelV = np.array([[-1],[1]])

        #Récupération des lignes horizontales :
        lignesHorizontales = np.absolute(cv2.filter2D(image.astype('float'),-1,kernelV))
        ret,thresh1 = cv2.threshold(lignesHorizontales,30,255,cv2.THRESH_BINARY)

        kernelSmall = np.ones((1,3), np.uint8)
        kernelBig = np.ones((1,50), np.uint8)

        #Remove holes:
        imgH1 = cv2.dilate(thresh1, kernelSmall, iterations=1)
        imgH2 = cv2.erode(imgH1, kernelSmall, iterations=1)

        #Remove small lines
        imgH3 = cv2.erode(imgH2, kernelBig, iterations=1)
        imgH4 = cv2.dilate(imgH3, kernelBig, iterations=1)

        linesStarts = cv2.filter2D(imgH4,-1,kernelH)
        linesEnds = cv2.filter2D(imgH4,-1,-kernelH)

        lines = linesStarts.sum(axis=0)/255
        lineStart = 0
        nbLineStart = 0
        for idx, val in enumerate(lines):
            if val > 6:
                nbLineStart += 1
                lineStart = idx

        lines = linesEnds.sum(axis=0)/255
        lineEnd = 0
        nbLineEnd = 0
        for idx, val in enumerate(lines):
            if val > 6:
                nbLineEnd += 1
                lineEnd = idx

        #Récupération des lignes verticales:
        lignesVerticales = np.absolute(cv2.filter2D(image.astype('float'),-1,kernelH))
        ret,thresh1 = cv2.threshold(lignesVerticales,30,255,cv2.THRESH_BINARY)

        kernelSmall = np.ones((3,1), np.uint8)
        kernelBig = np.ones((50,1), np.uint8)

        #Remove holes:
        imgV1 = cv2.dilate(thresh1, kernelSmall, iterations=1)
        imgV2 = cv2.erode(imgV1, kernelSmall, iterations=1)

        #Remove small lines
        imgV3 = cv2.erode(imgV2, kernelBig, iterations=1)
        imgV4 = cv2.dilate(imgV3, kernelBig, iterations=1)

        columnStarts = cv2.filter2D(imgV4,-1,kernelV)
        columnEnds = cv2.filter2D(imgV4,-1,-kernelV)

        column = columnStarts.sum(axis=1)/255
        columnStart = 0
        nbColumnStart = 0
        for idx, val in enumerate(column):
            if val > 6:
                columnStart = idx
                nbColumnStart += 1

        column = columnEnds.sum(axis=1)/255
        columnEnd = 0
        nbColumnEnd = 0
        for idx, val in enumerate(column):
            if val > 6:
                columnEnd = idx
                nbColumnEnd += 1


        found_board = False
        if (nbLineStart == 1) and (nbLineEnd == 1) and (nbColumnStart == 1) and (nbColumnEnd == 1) :
            print("We found a board")
            if abs((columnEnd - columnStart) - (lineEnd - lineStart)) > 3:
                print ("However, the board is not a square")
            else:
                print(columnStart,columnEnd,lineStart,lineEnd)
                if (columnEnd - columnStart) % 8 == 1:
                    columnEnd -= 1
                if (columnEnd - columnStart) % 8 == 7:
                    columnEnd += 1
                if (lineEnd - lineStart) % 8 == 1:
                    lineStart += 1
                if (lineEnd - lineStart) % 8 == 7:
                    lineStart -= 1
                print(columnStart,columnEnd,lineStart,lineEnd)

                found_board = True
        else:
            print("We did not found the borders of the board")

        if found_board:
            print("Found chessboard sized:" , (columnEnd-columnStart),(lineEnd-lineStart)," x:",columnStart,columnEnd," y: ",lineStart,lineEnd)
            dim = (800, 800 ) # perform the actual resizing of the chessboard
            print(lineStart,lineEnd,columnStart,columnEnd)
            resizedChessBoard = cv2.resize(image[columnStart:columnEnd, lineStart:lineEnd], dim, interpolation = cv2.INTER_AREA)
            return True, resizedChessBoard , lineStart, columnStart  , lineEnd   , columnEnd  , resizedChessBoard 

        return False, image, 0, 0, 0, 0 , image

