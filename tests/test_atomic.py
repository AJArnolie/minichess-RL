from minichess.games.abstract.board import AbstractBoardStatus
from minichess.games.abstract.action import AbstractActionFlags
import unittest
from minichess.games.abstract.piece import PieceColor
from minichess.games.atomic.pieces import Pawn, Knight, Bishop, Rook, Queen, King
from tests.test_gardner import TestGardner
from minichess.games.atomic.board import AtomicChessBoard
from minichess.games.atomic.action import AtomicChessAction


class TestAtomic(TestGardner):
    def setUp(self) -> None:
        self.g = AtomicChessBoard()

    def test_pawn_capture_no_pawns(self) -> None:
        self.g.wipe_board()

        for i in range(1, 4):
            for j in range(1,4):
                self.g.get((i,j)).push(Rook(PieceColor.BLACK, (i,j), 100))

        self.g.get((3,3)).push(Pawn(PieceColor.WHITE, (3,3), 100))

        print('Testing on board...')
        print(self.g)
        print('')

        self.g.push(AtomicChessAction(self.g.get((3,3)).peek(), (3,3), (2,2), self.g.get((2,2)).peek(), modifier_flags=[AbstractActionFlags.CAPTURE]))

        assert self.g.is_empty(), 'Expected empty graph but got:\n{}'.format(self.g)

    def test_pawn_capture_all_pawns(self) -> None:
        self.g.wipe_board()

        for i in range(1, 4):
            for j in range(1,4):
                self.g.get((i,j)).push(Pawn(PieceColor.BLACK, (i,j), 100))

        self.g.get((3,3)).push(Pawn(PieceColor.WHITE, (3,3), 100))

        print('Testing on board...')
        print(self.g)
        print('')

        self.g.push(AtomicChessAction(self.g.get((3,3)).peek(), (3,3), (2,2), self.g.get((2,2)).peek(), modifier_flags=[AbstractActionFlags.CAPTURE]))

        assert not self.g.is_empty(), 'Expected nonempty graph but got g.isempty == True'
        assert self.g.get((2,2)).peek() == self.g.get((3,3)).peek() == None, 'Expected capturing and captured piece to be removed from board.'

    def test_check(self) -> None:
        '''
        ⭘ ⭘ ♜ ♛ ♚
        ♟ ♟ ♟ ♞ ♟
        ♙ ⭘ ♙ ⭘ ♕
        ⭘ ⭘ ⭘ ♙ ⭘
        ⭘ ⭘ ⭘ ⭘ ♔
        '''
        self.g.wipe_board()

        self.g.get((0,2)).push(Rook(PieceColor.BLACK, (-1, -1), 1))
        self.g.get((0,3)).push(Queen(PieceColor.BLACK, (-1, -1), 1))
        self.g.get((0,4)).push(King(PieceColor.BLACK, (-1, -1), 1))
        self.g.get((1,0)).push(Pawn(PieceColor.BLACK, (-1, -1), 1))
        self.g.get((1,1)).push(Pawn(PieceColor.BLACK, (-1, -1), 1))
        self.g.get((1,2)).push(Pawn(PieceColor.BLACK, (-1, -1), 1))
        self.g.get((1,3)).push(Knight(PieceColor.BLACK, (-1, -1), 1))
        self.g.get((1,4)).push(Pawn(PieceColor.BLACK, (-1, -1), 1))
        self.g.get((2,0)).push(Pawn(PieceColor.WHITE, (-1, -1), 1))
        self.g.get((2,2)).push(Pawn(PieceColor.WHITE, (-1, -1), 1))
        self.g.get((2,4)).push(Queen(PieceColor.WHITE, (-1, -1), 1))
        self.g.get((3,3)).push(Pawn(PieceColor.WHITE, (-1, -1), 1))
        self.g.get((4,4)).push(King(PieceColor.WHITE, (-1, -1), 1))

        print('Testing on board...')
        print(self.g)
        print('')

        assert self.g.status == AbstractBoardStatus.WHITE_WIN, 'Expected white win over checkmate, but got {} for board:\n{}'.format(self.g.status_for_color(PieceColor.BLACK), self.g)

    def test_king_cant_check(self) -> None:
        self.g.wipe_board()

        self.g.get((1,2)).push(King(PieceColor.BLACK, (-1, -1), 1))
        self.g.get((2,2)).push(Pawn(PieceColor.BLACK, (-1, -1), 1))

        self.g.get((4,2)).push(King(PieceColor.WHITE, (-1, -1), 1))

        print('Testing on board...')
        print(self.g)
        print('')

        test_action = AtomicChessAction(self.g.get((4,2)).peek(), (4,2), (3,2), None)
        assert not self.g._is_checking_action(test_action, PieceColor.WHITE), 'King cannot capture, so King cannot check (or checkmate)!'

if __name__ == "__main__":
    unittest.main()