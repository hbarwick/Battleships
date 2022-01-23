import itertools

class Grid:
    def __init__(self, num_rows=10,
                 num_cols=10,
                 cell_width=40,
                 grid_size=402, #  2 extra pixels to allow line width not to be cut off
                 x_loc=40,
                 y_loc=40):
        self.y_loc = y_loc
        self.x_loc = x_loc
        self.grid_size = grid_size
        self.cell_width = cell_width
        self.num_cols = num_cols
        self.num_rows = num_rows
        self.cells = []


    def create_cells(self):
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                print(row, col)

class Cell:
    def __init__(self, x_coord, y_coord, cell_width, row, column):
        self.y_coord = y_coord
        self.x_coord = x_coord
        self.cell_width = cell_width
        self.row = row
        self.column = column

grid = Grid()
grid.create_cells()