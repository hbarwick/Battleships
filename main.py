from pathlib import Path
import itertools
import sys
import random
import pygame
from pygame.locals import *

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (52, 140, 235)
RED = (230, 15, 11)
GREY = (107, 99, 99)

SHIPS = {"Battleship": [5, r".\Sprites\Battleship5.png"],
         "Cruiser": [4, r".\Sprites\Cruiser4.png"],
         "Submarine": [4, r".\Sprites\Submarine3.png"],
         "Rescue Ship": [3, r".\Sprites\RescueShip3.png"],
         "Destroyer": [2, r".\Sprites\Destroyer2.png"],
         "Aeroplane": [1, r".\Sprites\Plane1.png"]}

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
        cell_y = self.y_loc
        for col in range(self.num_rows):
            cell_x = self.x_loc
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
        print(f"Mouse click at {x}, {y}")

        for cell in self.cells:
            if cell.x_coord < x < cell.x_coord + cell.cell_width:
                if cell.y_coord < y < cell.y_coord + cell.cell_width:
                    print(cell.row, cell.column)
                    cell.change_colour()

    def check_ship(self, ship_endpoint, horizontal):
        for cell in self.cells:
            if cell.rect.collidepoint(ship_endpoint):
                if horizontal:
                    return cell.rect.midleft, cell.row, cell.column
                else:
                    return cell.rect.midtop, cell.row, cell.column

    def update_cells_with_ship(self, starting_x: int, starting_y: int, shipname: str, length: int, horizontal: bool):
        ship_coords = []
        for i in range(length):
            ship_coords.append((starting_x, starting_y))
            if horizontal:
                starting_x += 1
            else:
                starting_y += 1
        print(shipname, ship_coords)
        for cell in self.cells:
            cell_coords = (cell.row, cell.column)
            if cell_coords in ship_coords:
                cell.ship = shipname


class Cell:
    def __init__(self, x_coord: int, y_coord: int, cell_width: int, row: int, column: int):
        self.y_coord = y_coord
        self.x_coord = x_coord
        self.cell_width = cell_width
        self.row = row
        self.column = column
        self.rect = pygame.Rect(self.x_coord, self.y_coord,
                                self.cell_width - 3, self.cell_width - 3)  # -3 to stop cell fill overlap with border
        self.surface = pygame.Surface((self.cell_width - 4,
                                       self.cell_width - 4))  # -4 to stop cell surface overlapping with cell borders
        self.ship = None

    # TODO if change_colour is required need to find better way to ensure complete fill,
    # adding 3 pixels to the Cell rects caused bug on ship lock-in
    def change_colour(self):
        self.surface.fill(RED)
        window_surface.blit(self.surface, self.rect)
        pygame.display.flip()
        print(self.ship)


class Ship(pygame.sprite.Sprite):
    def __init__(self, name: str, length: int, image: Path, x=0, y=0, column=0, row=0, horizontal=True):
        super().__init__()
        self.horizontal = horizontal
        self.row = row
        self.column = column
        self.length = length
        self.name = name
        self.image = pygame.image.load(image)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.centery = y + 20

    def rotate(self, x, y):
        self.image = pygame.transform.rotate(self.image, 90)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.horizontal = not self.horizontal


class Button(pygame.sprite.Sprite):
    def __init__(self, name: str, image: Path, x, y):
        super().__init__()
        self.name = name
        self.image = pygame.image.load(image)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.centery = y + 20


class EnemyAi:
    def __init__(self, grid):
        self.grid = grid
        self.ships = [Ship(ship, SHIPS[ship][0], SHIPS[ship][1]) for ship in SHIPS]

    def print_ships(self):
        for ship in self.ships:
            print(ship.name)

    def randomise_ships(self):
        rows = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        columns = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        grid = itertools.product(rows, columns)
        available_cells = [cell for cell in grid]
        for ship in self.ships:
            ship_coordinates = self.randomize_ship_coordinates(columns, rows, ship, available_cells)
            available_cells = [cell for cell in available_cells if cell not in ship_coordinates]
        print(available_cells)

    def randomize_ship_coordinates(self, columns, rows, ship, available_cells):
        ship.horizontal = random.choice([True, False])
        ship_coordinates = []
        if ship.horizontal:
            ship.row = random.choice(rows)
            available_columns = columns[:-ship.length]
            ship.column = random.choice(available_columns)
            y = ship.row
            for i in range(ship.length):
                ship_coordinates.append((ship.column, y))
                y += 1
            print(ship.name, ship_coordinates)
        else:
            ship.column = random.choice(columns)
            available_rows = rows[:-ship.length]
            ship.row = random.choice(available_rows)
            x = ship.column
            for i in range(ship.length):
                ship_coordinates.append((x, ship.row))
                x += 1
            print(ship.name, ship_coordinates)
            if all(coord in available_cells for coord in ship_coordinates):
                return ship_coordinates
            else:
                return self.randomize_ship_coordinates(columns, rows, ship, available_cells)


def display_text():
    title_font = pygame.font.SysFont(None, 42)
    title_text = title_font.render("Battleships!", True, BLACK, GREY)
    title_text_rect = title_text.get_rect()
    title_text_rect.centerx = window_surface.get_rect().centerx
    title_text_rect.centery = 30

    grid_header_font = pygame.font.SysFont(None, 35)
    player_text = grid_header_font.render("Player Grid", True, BLACK, GREY)
    player_text_rect = player_text.get_rect()
    player_text_rect.centerx = 240
    player_text_rect.centery = 50

    enemy_text = grid_header_font.render("Enemy Grid", True, BLACK, GREY)
    enemy_text_rect = enemy_text.get_rect()
    enemy_text_rect.centerx = 920
    enemy_text_rect.centery = 50

    window_surface.blit(title_text, title_text_rect)
    window_surface.blit(player_text, player_text_rect)
    window_surface.blit(enemy_text, enemy_text_rect)


def create_ships(ship_list):
    """Creates the player's ship sprites from the SHIPS dict and draws to the area
    between the player and enemy grid"""
    ship_y = 100
    ship_x = 480
    for ship in SHIPS:
        path = Path(SHIPS[ship][1])
        name = ship
        length = SHIPS[ship][0]
        ship_list.add(Ship(name, length, path, ship_x, ship_y))
        ship_y += 40
    ship_list.draw(window_surface)


def refresh_screen(player_grid, enemy_grid, button_list, ship_list):
    window_surface.fill(GREY)
    window_surface.blit(player_grid.surface, player_grid.rect)
    window_surface.blit(enemy_grid.surface, enemy_grid.rect)
    display_text()
    button_list.update()
    button_list.draw(window_surface)
    ship_list.update()
    ship_list.draw(window_surface)
    pygame.display.update()


def set_up_player_ships(player_grid, enemy_grid, ship_list, button_list, clock):
    setting_up = True
    selected = None
    while setting_up:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                if selected is None:  # First click selects the ship and will start dragging
                    for i, ship in enumerate(ship_list):
                        if ship.rect.collidepoint(event.pos):
                            selected = i
                            print(ship.name)
                            shipmove_x = ship.rect.x - event.pos[0]
                            shipmove_y = ship.rect.y - event.pos[1]
                    for sprite in button_list.sprites():
                        if sprite.rect.collidepoint(event.pos):
                            # Detect if the Lock in button has been clicked
                            if sprite.name == "lock-in":
                                setting_up = lock_in_ships(player_grid, setting_up, ship_list)
                else:
                    for sprite in button_list.sprites():
                        if sprite.rect.collidepoint(event.pos):
                            if sprite.name == "rotate":
                                ships = ship_list.sprites()
                                ships[selected].rotate(event.pos[0], event.pos[1])
                                break  # break out of sprite checking loop to avoid selected=None if button pressed
                        else:
                            selected = None  # Second click puts the ship down

            elif event.type == pygame.MOUSEMOTION:
                if selected is not None:  # selected can be `0` so `is not None` is required
                    ships = ship_list.sprites()
                    ships[selected].rect.x = event.pos[0] + shipmove_x
                    ships[selected].rect.y = event.pos[1] + shipmove_y

        refresh_screen(player_grid, enemy_grid, button_list, ship_list)
        clock.tick(25)


def lock_in_ships(player_grid, setting_up, ship_list):
    print("locking in...")
    for ship in ship_list.sprites():
        if ship.horizontal:
            # Retrieve the details of the left/top cell the ship is on
            cell_details = player_grid.check_ship(ship.rect.midleft, True)
            if cell_details:
                ship.rect.midleft = cell_details[0]
                # Update all cells the ship falls on with the shipname
                player_grid.update_cells_with_ship(starting_x=cell_details[1],
                                                   starting_y=cell_details[2],
                                                   shipname=ship.name,
                                                   length=ship.length,
                                                   horizontal=True)
        else:
            cell_details = player_grid.check_ship(ship.rect.midtop, False)
            if cell_details:
                ship.rect.midtop = cell_details[0]
                player_grid.update_cells_with_ship(starting_x=cell_details[1],
                                                   starting_y=cell_details[2],
                                                   shipname=ship.name,
                                                   length=ship.length,
                                                   horizontal=False)

    # Count the total number of cells with a ship, compare with the sum of the lengths of ships in the input dict
    # This will ensure all ships are fully on grid, and none are overlapping
    ship_cell_total = len([cell.ship for cell in player_grid.cells if cell.ship is not None])
    ship_dict_total = sum([ship[0] for ship in SHIPS.values()])

    # End setup phase if ship check passes
    if ship_cell_total == ship_dict_total:
        setting_up = False
    else:
        # clear the ship attribute from all cells
        for cell in player_grid.cells:
            cell.ship = None
            # TODO flash message advising ship setup incorrect for lock in
    return setting_up


def main():
    # Set up and draw the player and enemy grids
    player_grid = Grid()
    enemy_grid = Grid(x_loc=720)
    player_grid.draw_grid()
    enemy_grid.draw_grid()
    player_grid.create_cells()
    enemy_grid.create_cells()

    # Create sprite list groups
    ship_list = pygame.sprite.Group()
    button_list = pygame.sprite.Group()
    create_ships(ship_list)

    # Create Buttons
    rotate_button = Button("rotate", Path(r".\sprites\Rotate_button.png"), 500, 380)
    lock_in_button = Button("lock-in", Path(r".\sprites\lock-in_button.png"), 500, 480)
    button_list.add(rotate_button)
    button_list.add(lock_in_button)

    enemy = EnemyAi(enemy_grid)
    enemy.print_ships()
    enemy.randomise_ships()

    # Main game loop

    clock = pygame.time.Clock()
    set_up_player_ships(player_grid, enemy_grid, ship_list, button_list, clock)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                if player_grid.rect.collidepoint(event.pos):
                    print("player grid clicked")
                    player_grid.get_cell()
                elif enemy_grid.rect.collidepoint(event.pos):
                    print("enemy grid clicked")
                    enemy_grid.get_cell()


if __name__ == '__main__':
    main()
