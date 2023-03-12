from minichess.games.gardner.action import GardnerChessAction, GardnerChessActionVisitor
from minichess.games.abstract.piece import AbstractChessPiece, PieceColor
from minichess.games.abstract.action import AbstractActionFlags, AbstractChessAction, visitor
from minichess.games.rifle.pieces import Pawn

from typing import List

class RifleChessAction(GardnerChessAction):

    def __init__(self, agent: AbstractChessPiece, from_pos: tuple, to_pos: tuple, captured_piece: AbstractChessPiece = None, modifier_flags: List[AbstractActionFlags] = None):
        super().__init__(agent, from_pos, to_pos, captured_piece, modifier_flags)

class RifleChessActionVisitor(GardnerChessActionVisitor):
    '''
        All standard chess rules, though pawns cannot underpromote via 
        capture (since in Rifle Chess, we do not occupy the tile of captured 
        pieces post-capture)
    '''

    def _pawn_move_helper(self, piece: Pawn, board, new_position: tuple, is_capture) -> List[AbstractChessAction]:
        '''
            Helper function for pawn moves.
        '''
        possible_moves = []

        if board.is_valid_position(new_position):

            if (is_capture and board.get(new_position).capturable(piece.color)) or not (is_capture or board.get(new_position).occupied()):

                # check if this is last row
                if new_position[0] in [0, 4]: # if yes, we must promote

                    if not is_capture:
                        for flag in [AbstractActionFlags.PROMOTE_QUEEN, AbstractActionFlags.PROMOTE_KNIGHT,
                                        AbstractActionFlags.PROMOTE_BISHOP, AbstractActionFlags.PROMOTE_ROOK]:

                            possible_moves.append(
                                GardnerChessAction(
                                    piece,
                                    piece.position,
                                    new_position,
                                    board.get(new_position).peek() if is_capture else None,
                                    [flag]
                                )
                            )
                    else:
                        possible_moves.append(
                                GardnerChessAction(
                                    piece,
                                    piece.position,
                                    new_position,
                                    board.get(new_position).peek() if is_capture else None,
                                    [AbstractActionFlags.CAPTURE]
                                )
                            )

                else: # if no, just normal move
                    possible_moves.append(
                        GardnerChessAction(
                            piece,
                            piece.position,
                            new_position,
                            board.get(new_position).peek() if is_capture else None,
                            [AbstractActionFlags.CAPTURE] if is_capture else []
                        )
                    )

        return possible_moves