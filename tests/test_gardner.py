from minichess.games.abstract.piece import PieceColor
from minichess.games.gardner.pieces import Pawn, King, Rook, Queen
import unittest
from minichess.games.gardner.board import GardnerChessBoard

import numpy as np

GENERIC_PAWN_WHITE = Pawn(PieceColor.WHITE, (-1, -1), 100)
GENERIC_PAWN_BLACK = Pawn(PieceColor.BLACK, (-1, -1), 100)
GENERIC_KING_WHITE = King(PieceColor.WHITE, (-1, -1), 6000)
GENERIC_KING_BLACK = King(PieceColor.BLACK, (-1, -1), 6000)
GENERIC_ROOK_BLACK = Rook(PieceColor.BLACK, (-1, -1), 550)
GENERIC_QUEEN_BLACK = Queen(PieceColor.BLACK, (-1, -1), 800)

class TestGardner(unittest.TestCase):
    def setUp(self):
        self.g = GardnerChessBoard()

    def test_wipe_board(self):
        self.g.wipe_board()

        assert self.g.is_empty() == True, 'Expected board to be empty after wiping, but was not.'
        assert np.all(self.g.state_vector() == 0), 'Expected state vector of empty board to be all zero.'

        self.g.get((2,2)).push(GENERIC_PAWN_WHITE)

        assert self.g.is_empty() == False, 'Expected board to not be empty after placing piece, but it was.'
        assert np.any(self.g.state_vector() != 0), 'Expected state vector of nonempty board to not be zero.'

    def test_decode(self):
        vec = self.g.state_vector()

        decoded = GardnerChessBoard.from_vector(vec)

        assert str(decoded) == str(self.g), "Expected equal strings. Got:\n{}\n{}".format(str(decoded), str(self.g))

    def test_canonical_str(self):
        assert str(self.g) == self.g.canonical_str(), 'Expected initial board and initial canonical board to be identical'
        self.g.active_color = PieceColor.BLACK
        expected_canon_str = '''♚ ♛ ♝ ♞ ♜
♟ ♟ ♟ ♟ ♟
⭘ ⭘ ⭘ ⭘ ⭘
♙ ♙ ♙ ♙ ♙
♔ ♕ ♗ ♘ ♖
'''
        assert expected_canon_str == self.g.canonical_str(), 'Expected initial board and initial canonical board to be identical when active color artificially set to black. Expected:\n{}\nGot:\n{}'.format(expected_canon_str, self.g.canonical_str())


    def test_king_actions_alone(self):
        self.g.wipe_board()

        self.g.get((2, 2)).push(GENERIC_KING_WHITE)

        print('Testing on board...')
        print(self.g)
        print('')

        actions = self.g.legal_actions_for_color(PieceColor.WHITE)

        actions = set(actions)

        assert len(actions) == 8, 'Expected possible king actions on empty board to be set of length 8 but had length {}. Actions are:\n{}'.format(len(actions), '\n'.join([str(s) for s in actions]))

    def test_king_actions_could_have_check(self):
        
        self.g.wipe_board()

        self.g.get((0, 3)).push(GENERIC_KING_WHITE)

        self.g.get((2, 4)).push(GENERIC_ROOK_BLACK)
        self.g.get((3, 3)).push(GENERIC_KING_BLACK)

        print('Testing on board...')
        print(self.g)
        print('')

        actions = self.g.legal_actions_for_color(PieceColor.BLACK)

        actions = set(actions)
        
        assert len(actions) == 15, 'Expected possible actions for black to be set of length 15 but had length {}. Actions are:\n{}'.format(len(actions), '\n'.join([str(s) for s in actions]))

        actions = self.g.legal_actions_for_color(PieceColor.WHITE)

        actions = set(actions)
        
        assert len(actions) == 3, 'Expected possible actions for white to be set of length 3 but had length {} Actions are:\n{}'.format(len(actions), '\n'.join([str(s) for s in actions]))

    def test_complex_king_in_check(self):

        self.g.wipe_board()

        self.g.get((0, 3)).push(GENERIC_ROOK_BLACK)
        self.g.get((0, 4)).push(GENERIC_KING_BLACK)
        self.g.get((1, 0)).push(GENERIC_PAWN_BLACK)
        self.g.get((1, 4)).push(GENERIC_PAWN_BLACK)
        self.g.get((2, 3)).push(GENERIC_PAWN_BLACK)
        self.g.get((3, 1)).push(GENERIC_QUEEN_BLACK)

        self.g.get((2, 4)).push(GENERIC_PAWN_WHITE)
        self.g.get((4, 4)).push(GENERIC_KING_WHITE)

        print('Testing on board...')
        print(self.g)
        print('')

        white_legal_actions = self.g.legal_actions_for_color(PieceColor.WHITE)

        assert len(white_legal_actions) != 0, 'Expected white to be able to make a legal move, got legal move list of length {}'.format(len(white_legal_actions))

if __name__ == "__main__":
    unittest.main()