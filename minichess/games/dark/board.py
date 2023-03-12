from minichess.resources import EMPTY_TILE, SPACE
from minichess.games.abstract.piece import PieceColor
from minichess.games.gardner.board import GardnerChessBoard

import numpy as np

class DarkChessBoard(GardnerChessBoard):

    def visibility_mask(self, color: PieceColor) -> np.array:
        '''
            Generate an array of 0s an 1s representing the tiles that `color` currently can see.
        '''
        vis_mask = np.zeros((self.height, self.width))

        for tile in self:
            if tile.occupied() and tile.peek().color == color:
                vis_mask[tile.peek().position] = 1

        for action in self.legal_actions_for_color(color):
            from_pos = action.from_pos
            to_pos = action.to_pos

            vis_mask[to_pos] = 1

        return vis_mask

    def state_vector(self) -> np.array:
        mask = np.expand_dims(self.visibility_mask(self.active_color), axis=2)
        return np.tile(mask, (1, 1, 12)) * super().state_vector()

    def no_fog_board(self):
        return super().__str__()

    def __str__(self):
        mask = self.visibility_mask(self.active_color)

        s = ''

        for row_idx, row in enumerate(self._board):
            for col_idx, col in enumerate(row):
                if mask[row_idx, col_idx] == 1:
                    s += str(col)
                else:
                    s += EMPTY_TILE
                s += SPACE
            s += '\n'

        return s
