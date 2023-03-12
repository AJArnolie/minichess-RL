from minichess.utils import numpy_softmax
import numpy as np
from minichess.players.abstract import Player
from minichess.games.gardner.action import GardnerChessAction

class RandomPlayer(Player):
    def __init__(self, num_states=1225):
        super().__init__(num_states)

    def propose_action(self, board, color, action_mask):

        action_weights = np.random.rand(self.action_space_size)

        legal_actions = action_weights * action_mask

        if np.all(legal_actions == 0): return False, None

        renormalized = numpy_softmax(legal_actions)

        idx = np.argmax(renormalized)

        action_vector = np.zeros(self.action_space_size)
        action_vector[idx] = 1

        action = GardnerChessAction.decode(action_vector, board)

        return True, action