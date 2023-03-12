from typing import List
from minichess.games.abstract.piece import AbstractChessPiece, PieceColor
import numpy as np

class MultiPiece(AbstractChessPiece):
    '''
        A piece that keeps track of itself and 8 other non-pawn pieces surrounding it (up to 9 in total).

        This piece keeps track of its pieces with a queue. First in, first out.
    '''
    def __init__(self, pieces: List[AbstractChessPiece], position: tuple, value: int) -> None:
        super().__init__(PieceColor.WHITE, position, value)
        self.pieces = pieces

    def _onehot(self):
        return np.array([-1, 0, -1, 0, -1, 0])

    def push(self, piece):
        self.pieces.append(piece)

    def pop(self):
        return self.pieces.pop(0)

    @property
    def captured_piece(self):
        assert len(self) == 9, 'Cannot call captured_piece() mid-construction.'
        return self.pieces[4]

    def __len__(self):
        return len(self.pieces)

    def __iter__(self):
        for piece in self.pieces:
            yield piece

    def __str__(self):
        return '*'