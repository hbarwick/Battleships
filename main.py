from pathlib import Path
import sys
import pygame
from pygame.locals import *

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (52, 140, 235)
RED = (230, 15, 11)
GREY = (107, 99, 99)

SHIPS = {"Battleship": [5, ".\Sprites\Battleship5.png"],
         "Cruiser": [4, ".\Sprites\Cruiser4.png"],
         "Submarine": [3, ".\Sprites\Submarine3.png"],
         "Rescue Ship": [3, ".\Sprites\RescueShip3.png"],
         "Destroyer": [2, ".\Sprites\Destroyer2.png"],
         "Aeroplane": [1, ".\Sprites\Plane1.png"]}


pygame.init()
window_surface = pygame.display.set_mode((1160, 560), 0, 32)


class Grid:
    def __init__(self, num_rows=10,
                 num_cols=10,
                 cell_width=40,
                 grid_size=402,  # 2 extra pixels to allow line width not to be cut off
                 y_loc=80,
                 x_loc=40):
        self.y_loc = y_loc
        self.x_loc = x_loc
        self.grid_size = grid_size
        self.cell_width = cell_width
        self.num_cols = num_cols
        self.num_rows = num_rows
        self.rect = pygame.Rect(self.x_loc, self.y_loc, self.grid_size, self.grid_size)
        self.surface = pygame.Surface((self.grid_size, self.grid_size))
        self.cells = []

    def draw_grid(self):
        self.surface.fill(BLUE)
        grid_x = 0
        grid_y = 0
        for i in range(self.num_cols + 1):
            pygame.draw.line(self.surface, BLACK, (grid_x, 0), (grid_x, self.grid_size), 4)
            pygame.draw.line(self.surface, BLACK, (0, grid_y), (self.grid_size, grid_y), 4)
            grid_x += self.cell_width
            grid_y += self.cell_width

    def create_cells(self):
        cell_y = 0
        for col in range(self.num_rows):
            cell_x = 0
            for row in range(self.num_cols):
                self.cells.append(Cell(x_coord=cell_x,
                                       y_coord=cell_y,
                                       cell_width=self.cell_width,
                                       row=row,
                                       column=col))
                cell_x += self.cell_width
            cell_y += self.cell_width

    def get_cell(self):
        x, y = pygame.mouse.get_pos()
        gridx = x - self.x_loc
        gridy = y - self.y_loc
        print(f"Mouse click at {x}, {y}")

        for cell in self.cells:
            if cell.x_coord < gridx < cell.x_coord + cell.cell_width:
                if cell.y_coord < gridy < cell.y_coord + cell.cell_width:
                    print(cell.row, cell.column)
                    cell.change_colour()

    def add_ships(self):
        pass


class Cell:
    def __init__(self, x_coord: int, y_coord: int, cell_width: int, row: int, column: int):
        self.y_coord = y_coord
        self.x_coord = x_coord
        self.cell_width = cell_width
        self.row = row
        self.column = column
        self.rect = pygame.Rect(self.x_coord + 43, self.y_coord + 83,
                                self.cell_width - 3, self.cell_width - 3)  # -3 to stop cell fill overlap with border
        self.surface = pygame.Surface((self.cell_width - 4,
                                       self.cell_width - 4))  # -4 to stop cell surface overlapping with cell borders

    def change_colour(self):
        self.surface.fill(RED)
        window_surface.blit(self.surface, self.rect)
        pygame.display.flip()


class Ship(pygame.sprite.Sprite):
    def __init__(self, name: str, length: int, image: Path, x, y):
        super().__init__()
        self.length = length
        self.name = name
        self.image = pygame.image.load(image)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.centery = y + 20

    def rotate(self):
        self.image = pygame.transform.rotate(self.image, 270)



def main():
    title_font = pygame.font.SysFont(None, 42)
    text = title_font.render("Battleships!", True, BLACK, GREY)
    text_rect = text.get_rect()
    text_rect.centerx = window_surface.get_rect().centerx
    text_rect.centery = 20


    window_surface.fill(GREY)
    window_surface.blit(text, text_rect)
    pygame.display.update()

    player_grid = Grid()
    enemy_grid = Grid(x_loc=720)
    player_grid.draw_grid()
    enemy_grid.draw_grid()
    player_grid.create_cells()

    ship_list = pygame.sprite.Group()
    ship_y = 160
    ship_x = 480
    for ship in SHIPS:
        path = Path(SHIPS[ship][1])
        name = ship
        length = SHIPS[ship][0]
        ship_list.add(Ship(name, length, path, ship_x, ship_y))
        ship_y += 40
    ship_list.draw(window_surface)
    window_surface.blit(player_grid.surface, player_grid.rect)
    window_surface.blit(enemy_grid.surface, enemy_grid.rect)
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                player_grid.get_cell()


if __name__ == '__main__':
    main()
