# Chess Bot

A chess bot for chess websites like chess.com, liechess, ... that uses machine learning to recognize game board
instead of using html elements. With this method, website changes won't affect the program and almost every site should work.

## Tabe of contents

- [General info](#general-info)
- [Setup](#setup)
- [Train Model](#train-model)
- [Extra Notes](#extra-notes)

## General info

The program takes screenshot, detects the board, devides it into tiles and predicts each piece using the KNN algoritm.
Then it calculates the best move using the popular [Stockfish Engine](https://github.com/official-stockfish/Stockfish)

> Not performance heavy. I programmed this on a 10 year old laptop.

> The model reaches a 100% accuracy. Trained on the most popular board themes and piece sets of liechess and chess.com.
> You can easily train the model with different piecesets or themes if it performs badly. Check this section: [Train Model](#train-model)

## Setup

Download the right [stockfish file](https://stockfishchess.org/download/) for your os and rename it to stockfish:
Move it into the main directory of this project.

Running this project through a virtual environment is recommended.

Install necessary libraries and run project:

```
$ pip3 install -r requirements.txt
$ python3 main.py

```

## Train Model

- Add data to train/data.
  1. Get some screenshots from random boards.
  2. Save every tile with a piece as an image. Size should be 40\*40 in grayscale.
  3. Name each image file to its corresponding piece. Look into the data directory to see how each file should be named
     and organised. 1 stands for empy tile.

> get_new_data.py in train might be helpfull.

- Install jupyter and sklearn using pip and run the notebook in the train directory.

## Extra Notes

- Don't move the mouse when bot is playing.
- Chessboard should be easily recognized on screen.

**Feel free to open an issue if something is not working properly.**
