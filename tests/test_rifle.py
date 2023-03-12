from tests.test_gardner import TestGardner
from minichess.games.rifle.board import RifleChessBoard

import unittest

class TestRifle(TestGardner):
    def setUp(self) -> None:
        self.g = RifleChessBoard()

if __name__ == "__main__":
    unittest.main()