from minichess.games.abstract.action import AbstractActionFlags, AbstractChessAction
from minichess.games.gardner.board import GardnerChessBoard, PAWN_VALUE, KNIGHT_VALUE, BISHOP_VALUE, ROOK_VALUE, QUEEN_VALUE, KING_VALUE
from minichess.games.rifle.pieces import *


class RifleChessBoard(GardnerChessBoard):
    ''' 
    A MiniChess variant where captures are made from range. That is, pieces do not move 
    to the spaces of pieces they capture, and a single capture necessitates a full turn.
    '''

    def push(self, action: AbstractChessAction, check_for_check=True):

        from_pos = action.from_pos
        to_pos = action.to_pos

        if check_for_check:
            checking_move, opp_cant_move = self._is_checking_action(action, self.active_color)

            if checking_move: action.modifier_flags.append(AbstractActionFlags.CHECK)
            if checking_move and opp_cant_move: action.modifier_flags.append(AbstractActionFlags.CHECKMATE)

        is_capture = AbstractActionFlags.CAPTURE in action.modifier_flags

        agent = self.get(from_pos).pop()

        if is_capture:
            # simply remove the piece
            self.get(to_pos).pop()

            self.get(from_pos).push(agent)
        else:
            # otherwise move piece from A to B
            self.get(to_pos).push(agent)

        # check for promotions
        if type(agent) == Pawn and agent.position[0] in [0, self.board_height - 1]:
            if AbstractActionFlags.PROMOTE_BISHOP in action.modifier_flags:
                self.get(to_pos).pop()
                self.get(to_pos).push(Bishop(agent.color, to_pos, BISHOP_VALUE))
            elif AbstractActionFlags.PROMOTE_KNIGHT in action.modifier_flags:
                self.get(to_pos).pop()
                self.get(to_pos).push(Knight(agent.color, to_pos, KNIGHT_VALUE))
            elif AbstractActionFlags.PROMOTE_ROOK in action.modifier_flags:
                self.get(to_pos).pop()
                self.get(to_pos).push(Rook(agent.color, to_pos, ROOK_VALUE))
            else:
                self.get(to_pos).pop()
                self.get(to_pos).push(Queen(agent.color, to_pos, QUEEN_VALUE))

        self.move_history.append(action)

        self.active_color = self.active_color.invert()