from .Player import Player
import sys
from matplotlib import pyplot as plt
from matplotlib.widgets import TextBox
sys.path.append('../')
from const import *
from utils import *
from board import make_point, board, get_board_length, make_empty_board, parse_point
from tests.test_boards import *


class GuiPlayer(Player):
    def __init__(self):
        self.name_from_user()
        super().__init__(name=self.name)
        self.register_flag = False
        self.receive_flag = False
        self.crazy_flag = False
        self.next_move = None
        self.next_move_flag = False

    def register(self):
        if self.receive_flag or self.register_flag:
            self.go_crazy()
        else:
            self.register_flag = True
        return self.name

    def receive_stones(self, stone):
        print("gui 33", stone)
        if is_stone(stone):
            self.receive_flag = True
            self.stone = stone
        else:
            return self.go_crazy()

    def end_game(self):
        # display game over to player
        plt.text(0.08, 0.5, "GAME OVER", size=50, bbox=dict(facecolor='red', alpha=0.5))
        plt.xticks([])
        plt.yticks([])
        plt.show()
        # reset flags for next game
        self.receive_flag = False
        # acknowledge that game over msg was received
        return "OK"

    def name_from_user(self):
        def submit(text):
            plt.close()
            self.name = text

        axbox = plt.axes([0.1, 0.05, 0.8, 0.075])
        text_box = TextBox(axbox, 'Name: ', initial="")
        text_box.on_submit(submit)
        plt.show()

    def display(self, curr_board):
        # create a 8" x 8" board
        fig = plt.figure(figsize=[8, 8])
        fig.patch.set_facecolor((1, 1, .8))
        ax = fig.add_subplot(111)

        #fig.suptitle(self.player1.name + " (black)" + " vs. " + self.player2.name + " (white)", fontsize=16)

        # draw the grid
        for x in range(maxIntersection):
            ax.plot([x, x], [0, maxIntersection - 1], 'k')
        for y in range(maxIntersection):
            ax.plot([0, maxIntersection - 1], [y, y], 'k')

        # scale the axis area to fill the whole figure
        ax.set_position([0, 0, 1, 1])

        # get rid of axes and everything (the figure background will show through)
        ax.set_axis_off()

        # scale the plot area conveniently (the board is in 0,0..18,18)
        ax.set_xlim(-1, maxIntersection)
        ax.set_ylim(-1, maxIntersection)

        fig.canvas.mpl_connect('button_press_event', self.onclick)

        # draw Go stones at (10,10) and (13,16)
        for p in curr_board.get_points(black):
            xy = parse_point(p)
            ax.plot(xy[1], maxIntersection - 1 - xy[0], 'o', markersize=25, markeredgecolor=(.5, .5, .5),
                    markerfacecolor='k', markeredgewidth=2)
        for p in curr_board.get_points(white):
            xy = parse_point(p)
            ax.plot(xy[1], maxIntersection - 1 - xy[0], 'o', markersize=25, markeredgecolor=(0, 0, 0),
                    markerfacecolor='w', markeredgewidth=2)

        plt.show()

    def point_from_click_data(self, xdata, ydata):
        x = int(round(xdata))
        y = maxIntersection - 1 - int(round(ydata))
        return x, y

    def onclick(self, event):
        plt.close()
        x, y = self.point_from_click_data(event.xdata, event.ydata)
        self.next_move = make_point(x, y)
        self.next_move_flag = True

    def make_a_move(self, boards):
        self.display(board(boards[0]))
        if self.next_move_flag:
            self.next_move_flag = False
            return self.next_move
        return "pass"


def main():
    print(GuiPlayer().make_a_move(board_history1))



if __name__ == "__main__":
    main()