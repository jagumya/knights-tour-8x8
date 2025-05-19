import random
import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

N = 8

moves = [(2, 1), (1, 2), (-1, 2), (-2, 1),
         (-2, -1), (-1, -2), (1, -2), (2, -1)]


def is_valid(x, y, board):
    return 0 <= x < N and 0 <= y < N and board[y][x] == -1


def onward_moves(x, y, board):
    return sum(is_valid(x + dx, y + dy, board) for dx, dy in moves)


def knight_tour(start_x, start_y, max_attempts=10):
    for attempt in range(1, max_attempts + 1):
        board = [[-1] * N for _ in range(N)]
        path = [(start_x, start_y)]
        board[start_y][start_x] = 0
        x, y = start_x, start_y

        for move_num in range(1, N * N):
            candidates = []
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if is_valid(nx, ny, board):
                    candidates.append((onward_moves(nx, ny, board), nx, ny))
            if not candidates:
                break

            min_deg = min(c[0] for c in candidates)
            choices = [(nx, ny) for deg, nx, ny in candidates if deg == min_deg]
            x, y = random.choice(choices)
            board[y][x] = move_num
            path.append((x, y))

        if len(path) == N * N:
            lx, ly = path[-1]
            if (start_x - lx, start_y - ly) in moves or (lx - start_x, ly - start_y) in moves:
                print(f"Knights tour found on attempt {attempt}")
                return path
    raise RuntimeError("Could not find a knight's tour")


class KnightTourApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Knight's Tour Visualizer")
        self.root.configure(bg="#1e1e1e")
        self.start_pos = None

        self.fig, self.ax = plt.subplots(figsize=(6, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack()
        self.canvas.mpl_connect("button_press_event", self.on_click)

        self.draw_board()

        panel = tk.Frame(self.root, bg="#1e1e1e")
        panel.pack(pady=10)
        tk.Button(panel, text="Start Tour", command=self.start_tour, bg="#2196F3", fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat", padx=10, pady=5).pack(side=tk.LEFT, padx=10)
        tk.Button(panel, text="Reset", command=self.reset_board, bg="#777", fg="white",
                  font=("Segoe UI", 10), relief="flat", padx=10, pady=5).pack(side=tk.LEFT)

        self.status_var = tk.StringVar()
        self.status_label = tk.Label(self.root, textvariable=self.status_var, font=("Segoe UI", 10), fg="white", bg="#1e1e1e")
        self.status_label.pack(pady=5)

    def draw_board(self):
        self.ax.clear()
        self.visited_patches = {}
        for i in range(N):
            for j in range(N):
                base_color = '#2b2b2b' if (i + j) % 2 == 0 else '#383838'
                self.ax.add_patch(plt.Rectangle((i, j), 1, 1, color=base_color))
        self.ax.set_xlim(0, N)
        self.ax.set_ylim(0, N)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax.set_title("Click a square to start", fontsize=13, fontweight='medium', color="white")
        self.canvas.draw()

    def on_click(self, event):
        if event.inaxes != self.ax:
            return
        x, y = int(event.xdata), int(event.ydata)
        self.start_pos = (x, y)
        self.draw_board()
        self.ax.add_patch(plt.Rectangle((x, y), 1, 1, facecolor='#aaaaaa', alpha=0.6))
        self.canvas.draw()

    def reset_board(self):
        self.start_pos = None
        self.status_var.set("")
        self.draw_board()

    def start_tour(self):
        if not self.start_pos:
            messagebox.showwarning("Select Start", "Please select a starting square by clicking on the board.")
            return

        try:
            path = knight_tour(*self.start_pos)
            self.animate_tour(path)
        except RuntimeError as e:
            messagebox.showerror("Tour Error", str(e))

    def animate_tour(self, path):
        xs, ys = [], []
        visited_squares = set()
        self.ax.clear()
        for i in range(N):
            for j in range(N):
                base_color = '#2b2b2b' if (i + j) % 2 == 0 else '#383838'
                self.ax.add_patch(plt.Rectangle((i, j), 1, 1, color=base_color))
        self.ax.set_xlim(0, N)
        self.ax.set_ylim(0, N)
        self.ax.set_xticks([])
        self.ax.set_yticks([])

        line, = self.ax.plot([], [], '-', lw=2.5, color='#00ACC1', alpha=0.9)
        dots, = self.ax.plot([], [], 'o', markersize=3, color='#FF4081', alpha=0.8)
        highlight = self.ax.add_patch(plt.Rectangle((0, 0), 1, 1, edgecolor='#80DEEA', fill=False, linewidth=1.8))

        def init():
            line.set_data([], [])
            dots.set_data([], [])
            highlight.set_xy((-1, -1))
            return line, dots, highlight

        def update(frame):
            x, y = path[frame]
            xs.append(x + 0.5)
            ys.append(y + 0.5)
            line.set_data(xs, ys)
            dots.set_data(xs, ys)
            highlight.set_xy((x, y))

            if (x, y) not in visited_squares:
                visited_patch = plt.Rectangle((x, y), 1, 1, facecolor='#4caf50', alpha=0.25)
                self.ax.add_patch(visited_patch)
                visited_squares.add((x, y))

            self.status_var.set(f"Progress: {frame + 1}/{N*N} ({(frame + 1) * 100 // (N*N)}%)")

            if frame + 1 == N * N:
                self.ax.add_patch(plt.Rectangle((x, y), 1, 1, fill=True, edgecolor='#FFD700', linewidth=2.5, alpha=0.4))
                self.ax.set_title("Knights Tour Complete!", fontsize=13, fontweight='medium', color="white")

            return line, dots, highlight

        ani = animation.FuncAnimation(
            self.fig, update, init_func=init,
            frames=len(path), interval=200,
            blit=True, repeat=False
        )
        self.canvas.draw()


if __name__ == '__main__':
    root = tk.Tk()
    app = KnightTourApp(root)
    root.mainloop()
