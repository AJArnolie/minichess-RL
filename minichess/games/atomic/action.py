from minichess.games.atomic.pieces.multipiece import MultiPiece
from minichess.utils import surrounding_pieces
import numpy as np
from minichess.games.atomic.board import AtomicChessBoard
from minichess.games.gardner.action_reference import ID_TO_ACTION
from typing import List
from minichess.games.abstract.action import AbstractActionFlags, AbstractChessAction, visitor
from minichess.games.abstract.piece import AbstractChessPiece, PieceColor
from minichess.games.gardner.action import GardnerChessAction, GardnerChessActionVisitor
from minichess.games.atomic.pieces import Pawn, Knight, Bishop, Rook, Queen, King


class AtomicChessAction(GardnerChessAction):
    '''
        A variant of chess where, on capture, all non-pawn pieces
        surrounding the captured piece are also removed.
    '''
    pass