import numpy as np

def numpy_softmax(x):
    ''' Basic numpy implementation of softmax over a 1-D vector. '''
    return np.exp(x) / sum(np.exp(x))

def numpy_scaled_softmax(x, scale):
    return np.exp(scale * x) / sum(np.exp(scale * x))

def surrounding_pieces(pos_tup, board, return_pos=False):
    row,col = pos_tup
    pieces = []
    for i in range(row - 1, row + 2):
        for j in range(col - 1, col + 2):
            cur_pos = (i,j)
            if 0 <= i < board.getHeight() and 0 <= j < board.getWidth():
                piece = board.get(cur_pos).peek()
            else:
                piece = None

            if return_pos:
                pieces.append((piece, cur_pos))
            else:
                pieces.append(piece)
    return pieces