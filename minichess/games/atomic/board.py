from minichess.utils import surrounding_pieces
from minichess.games.gardner.action import GardnerChessActionVisitor
from typing import List
from minichess.games.abstract.piece import PieceColor
from minichess.games.atomic.pieces import Pawn, Knight, Bishop, Rook, Queen, King
from minichess.games.abstract.action import AbstractActionFlags, AbstractChessAction
from minichess.games.gardner.board import GardnerChessBoard, BISHOP_VALUE, KNIGHT_VALUE, ROOK_VALUE, QUEEN_VALUE

class AtomicChessBoard(GardnerChessBoard):
    '''
        A rule variant of Gardner MiniChess where a capture removes the capturing piece, the captured piece, and all non-pawn pieces
        surrounding the captured piece are removed on capture (regardless of color).

        This implies that Kings cannot capture.
    '''
    def __init__(self):
        super().__init__()

        # this keeps track of pieces (and their locations) that are captured
        # by "collateral" captures at each step
        self.extra_capture_stack = []

    def push(self, action: AbstractChessAction, check_for_check=True):

        from_pos = action.from_pos
        to_pos = action.to_pos

        if check_for_check:
            checking_move, opp_cant_move = self._is_checking_action(action, self.active_color)

            if checking_move: action.modifier_flags.append(AbstractActionFlags.CHECK)
            if checking_move and opp_cant_move: action.modifier_flags.append(AbstractActionFlags.CHECKMATE)

        neighbors = []

        # either is a capture or isn't
        if AbstractActionFlags.CAPTURE in action.modifier_flags:

            # remove capturing piece
            self.get(from_pos).pop()

            # remove captured piece
            self.get(to_pos).pop()

            # get the neighbors of the captured piece
            neighbors = surrounding_pieces(to_pos, self, True)
            neighbors = [neighbor for neighbor in neighbors if type(neighbor[0]) not in [Pawn, type(None)]]

            # remove surrounding pieces
            for _, pos in neighbors:
                self.get(pos).pop()

        else: # otherwise, simply move
            agent = self.get(from_pos).pop()
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

        self.extra_capture_stack.append(neighbors)
        self.move_history.append(action)

        self.active_color = self.active_color.invert()

    def pop(self) -> AbstractChessAction:

        if len(self.move_history) == 0: return None

        action = self.move_history.pop()
        from_pos = action.from_pos
        to_pos = action.to_pos
        agent = action.agent
        captured_piece = action.captured_piece

        self.get(from_pos).pop()
        self.get(from_pos).push(agent)

        self.get(to_pos).pop()
        if captured_piece is not None: self.get(to_pos).push(captured_piece)

        # repopulate collaterally captured pieces
        neighbors = self.extra_capture_stack.pop()
        for piece,pos in neighbors:
            self.get(pos).push(piece)

        self.active_color = self.active_color.invert()

        return action

    def peek_extra_capture(self):
        return self.extra_capture_stack[-1] if len(self.extra_capture_stack) > 0 else None

    def _is_checking_action(self, action, color):
        '''
            Returns
            -------
            tuple of (bool, bool) where
            - the first item is True if this action puts the opponent in check, False otherwise.
            - the second item is True if this action puts the opponent in checkmate, False otherwise.
        '''
        if type(action.agent) == King: return False, len(self.legal_actions_for_color(color.invert(), filter_for_check=True)) == 0

        # simulate this move
        self.push(action, check_for_check=False)

        can_capture_king = False

        for possible_action in self.legal_actions_for_color(color, filter_for_check=False):
            self.push(possible_action, check_for_check=False)
            if type(possible_action.captured_piece) == King or King in [type(piece) for piece,_ in self.peek_extra_capture()]:
                can_capture_king = True
            self.pop()

        opponent_cannot_move_next = len(self.legal_actions_for_color(color.invert(), filter_for_check=True)) == 0

        self.pop() # undo our move

        return can_capture_king, opponent_cannot_move_next

    def _leads_to_check(self, action, color):
        '''
            Returns
            -------
            True if this action puts the player that made it in check, false otherwise.
        '''
        
        # simulate this move
        self.push(action, check_for_check=False)

        anti_color = color.invert()

        can_capture_king = False

        for possible_action in self.legal_actions_for_color(anti_color, filter_for_check=False):
            self.push(possible_action, check_for_check=False)
            if type(possible_action.captured_piece) == King or King in [type(piece) for piece,_ in self.peek_extra_capture()]:
                can_capture_king = True
            self.pop()

        self.pop() # undo our move

        return can_capture_king

    def legal_actions_for_color(self, color: PieceColor, filter_for_check=True) -> List[AbstractChessAction]:

        referee = GardnerChessActionVisitor()
        
        possible_actions = []

        for tile in self:
            piece = tile.peek()

            if piece is not None and piece.color == color:
                possible_actions.extend(referee.visit(piece, self))

        # filter for 1) kings can't capture 2) can't collateral own king
        possible_actions = [action for action in possible_actions if self._preserves_king(action, color) and
                                                                        (type(action.agent) != King or (type(action.agent) == King and AbstractActionFlags.CAPTURE not in action.modifier_flags))]

        # filter for checks
        if filter_for_check:
            possible_actions = [action for action in possible_actions if not self._leads_to_check(action, color)]

        return possible_actions

    def _preserves_king(self, action, color):
        self.push(action, check_for_check=False)

        preserves_king = self._contains_king(color)

        self.pop()

        return preserves_king

    def _contains_king(self, color):
        for tile in self:
            piece = tile.peek()
            if type(piece) == King and piece.color == color:
                return True
        return False
