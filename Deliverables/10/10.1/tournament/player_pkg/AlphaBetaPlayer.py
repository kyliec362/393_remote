import sys
from .Player import Player
sys.path.append('../')
from const import *
from utils import *
from rule_checker import rule_checker, get_opponent_stone, get_legal_moves
from board import make_point, board, get_board_length, make_empty_board, parse_point


class AlphaBetaPlayer(Player):
    def __init__(self, depth="1"):
        self.depth = depth
        super().__init__()

    def register(self):
        if self.receive_flag or self.register_flag:
            self.go_crazy()
        else:
            self.register_flag = True
        return self.name

    def receive_stones(self, stone):
        if not is_stone(stone):
            self.go_crazy()
        if self.receive_flag or not self.register_flag:
            self.go_crazy()
        self.receive_flag = True
        self.stone = stone

    def go_crazy(self):
        self.crazy_flag = True
        return crazy

    def end_game(self):
        self.receive_flag = False
        return "OK"

    def make_a_move(self, boards):
        if self.crazy_flag:
            return crazy
        if self.register_flag and self.receive_flag:
            import copy
            move = self.ab_minimax(0, self.depth, True, NEG_INF, POS_INF, copy.deepcopy(boards), self.stone)
            return move[1]
        return crazy

    def heuristic(self, curr_board, stone):
        return board(curr_board).calculate_score()[stone]

    def ab_minimax(self, depth, max_depth, is_maximizer, alpha, beta, boards, stone):
        curr_board = boards[0]
        if is_maximizer:
            legal_moves = get_legal_moves(boards, stone)
        else:
            legal_moves = get_legal_moves(boards, get_opponent_stone(stone))
        if (depth == max_depth) or (len(legal_moves) == 0):
            return [self.heuristic(curr_board, stone), "hello"]  # heuristic for game evaluation
        updated_board = curr_board
        if is_maximizer:
            max_eval = [alpha, None]
            for move in legal_moves:
                if move != "pass":
                    updated_board = board(curr_board).place(stone, move)
                updated_history = update_board_history(updated_board, boards)
                result = self.ab_minimax(depth + 1, max_depth, not is_maximizer, alpha, beta, updated_history, get_opponent_stone(stone))
                result[1] = move
                max_eval = max(max_eval, result, key=lambda x: x[0])
                alpha = max(alpha, result[0])
                if beta <= alpha:
                    break
            return max_eval

        else:
            min_eval = [beta, None]
            for move in legal_moves:
                if move != "pass":
                    updated_board = board(curr_board).place(stone, move)
                updated_history = update_board_history(updated_board, boards)
                result = self.ab_minimax(depth + 1, max_depth, not is_maximizer, alpha, beta, updated_history, get_opponent_stone(stone))
                result[1] = move
                min_eval = min(min_eval, result, key=lambda x: x[0])
                beta = min(beta, result[0])
                if beta <= alpha:
                    break
            return min_eval
