import sys
from .Player import Player
sys.path.append('../')
from referee import update_board_history

class AlphaBetaPlayer(Player):
    def __init__(self, stone, name, depth):
        self.depth = depth
        super().__init__(stone, name)

    def register(self):
        if self.receive_flag or self.register_flag:
            return self.go_crazy()
        self.register_flag = True
        return "no name"

    def receive_stones(self, stone):
        self.receive_flag = True
        self.stone = stone

    def go_crazy(self):
        self.crazy_flag = True
        return crazy

    def end_game(self):
        self.receive_flag = False
        return "OK"

    def make_a_move(self, boards):
        return (self.ab_minimax(0, self.depth, True, NEG_INF, POS_INF, boards))[1]

    def heuristic(self, curr_board):
        return board(curr_board).calculate_score()[self.stone]

    def ab_minimax(self, depth, max_depth, is_maximizer, alpha, beta, boards):
        curr_board = boards[0]
        if is_maximizer:
            legal_moves = get_legal_moves(boards, self.stone)
        else:
            legal_moves = get_legal_moves(boards, get_opponent_stone(self.stone))

        if (depth == max_depth) or (len(legal_moves) == 0):
            return [self.heuristic(curr_board), "hello"]  # heuristic for game evaluation
        updated_board = curr_board
        if is_maximizer:
            max_eval = [alpha, None]
            for move in legal_moves:
                if move != "pass":
                    updated_board = board(curr_board).place(self.stone, move)
                updated_history = update_board_history(updated_board, boards)
                result = self.ab_minimax(depth + 1, max_depth, not is_maximizer, alpha, beta, updated_history)
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
                    updated_board = board(curr_board).place(self.stone, move)
                updated_history = update_board_history(updated_board, boards)
                result = self.ab_minimax(depth + 1, max_depth, not is_maximizer, alpha, beta, updated_history)
                result[1] = move
                min_eval = min(min_eval, result, key=lambda x: x[0])
                beta = min(beta, result[0])
                if beta <= alpha:
                    break
            return min_eval
