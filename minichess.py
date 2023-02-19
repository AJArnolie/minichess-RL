'''
Minichess Implementation
'''

import constants
import numpy as np

# TODO: Maybe make the different variants Subclasses of this one?
# TODO: Represent pieces as characters or ints?
# TODO: Consider this implementation: https://github.com/mdhiebert/minichess/blob/main/minichess/games/gardner/pieces/knight.py

class Minichess:
    def __init__(self, board_size=(4, 5), variant="general", turn=0):
        self.board_size = board_size
        self.board = np.zeros(self.board_size)
        self.variant = variant
        self.turn = turn # Which player starts

def main():
    board = Minichess("Silverman4x5")
    print(board)

if __name__ == "__main__":
    main()
