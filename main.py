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
DARK_GREY = (41, 41, 46)
DARK_BLUE = (14, 19, 156)

SHIPS = {"Battleship": [5, r".\Sprites\Battleship5.png"],
         "Cruiser": [4, r".\Sprites\Cruiser4.png"],
         "Submarine": [4, r".\Sprites\Submarine3.png"],
         "Rescue Ship": [3, r".\Sprites\RescueShip3.png"],
         "Destroyer": [2, r".\Sprites\Destroyer2.png"],
         "Aeroplane": [1, r".\Sprites\Plane1.png"]}

pygame.init()
window_surface = pygame.display.set_mode((1160, 580), 0, 32)


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
        for cell in self.cells:
            if cell.x_coord < x < cell.x_coord + cell.cell_width:
                if cell.y_coord < y < cell.y_coord + cell.cell_width:
                    return cell

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
        for cell in self.cells:
            cell_coords = (cell.row, cell.column)
            if cell_coords in ship_coords:
                cell.ship = shipname

    def return_cell(self, coordinates: tuple):
        for cell in self.cells:
            if cell.column == coordinates[0]:
                if cell.row == coordinates[1]:
                    return cell


class Cell:
    def __init__(self, x_coord: int, y_coord: int, cell_width: int, row: int, column: int):
        self.y_coord = y_coord
        self.x_coord = x_coord
        self.cell_width = cell_width
        self.row = row
        self.column = column
        self.rect = pygame.Rect(self.x_coord, self.y_coord,
                                self.cell_width, self.cell_width)
        self.surface = pygame.Surface((self.cell_width,
                                       self.cell_width))
        self.ship = None
        self.is_clicked = False

    def cell_clicked(self):
        self.surface.fill(RED)
        window_surface.blit(self.surface, self.rect)
        pygame.display.flip()
        self.is_clicked = True
        return self.rect.center, self.ship


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


class CellHit(pygame.sprite.Sprite):
    def __init__(self, image: Path, rect_center):
        super().__init__()
        self.image = pygame.image.load(image)
        self.rect = self.image.get_rect()
        self.rect.center = (rect_center[0] + 1, rect_center[1] + 1)


class EnemyAi:
    def __init__(self, grid):
        self.grid = grid
        self.ships = [Ship(ship, SHIPS[ship][0], SHIPS[ship][1]) for ship in SHIPS]
        self.ship_hit = None
        self.second_hit = None
        self.tested_no_hit = None
        self.tested_no_hit_2 = None
        self.available_cells = self.populate_available_cells()

    def populate_available_cells(self):
        rows = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        columns = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        grid = itertools.product(rows, columns)
        return [cell for cell in grid]

    def reset_hit_logs(self):
        self.ship_hit = None
        self.second_hit = None
        self.tested_no_hit = None
        self.tested_no_hit_2 = None

    def randomise_ships(self):
        """Creates a list to reflect coordinates of a 10x10 grid, then adds each of the ships in turn to
        self.grid, removing the coordinates from the list so they cannot be used again."""
        rows = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        columns = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        ship_coord_mapping = {}
        grid = itertools.product(rows, columns)
        available_cells = [cell for cell in grid]
        for ship in self.ships:
            ship_coordinates = self.randomize_ship_coordinates(columns, rows, ship, available_cells)
            cells_minus_ship = [cell for cell in available_cells if cell not in ship_coordinates]
            ship_coord_mapping[ship.name] = ship_coordinates
            available_cells = cells_minus_ship
            self.grid.update_cells_with_ship(starting_x=ship.column,
                                             starting_y=ship.row,
                                             shipname=ship.name,
                                             length=ship.length,
                                             horizontal=ship.horizontal)

    def randomize_ship_coordinates(self, columns, rows, ship, available_cells) -> list:
        """Produces a list of randomized ship coordinates for randomize_ships() to populate to the cells.
        Checks that all coordinate pairs are in available_cells, and if not calls recursively until valid
        Coordinate list is created."""
        ship.horizontal = random.choice([True, False])
        ship_coordinates = []
        if ship.horizontal:
            ship.row = random.choice(rows)  # choose any y coordinate
            available_columns = columns[:-ship.length]  # x coordinate only those which can contain ship's length
            ship.column = random.choice(available_columns)
            x = ship.column
            for i in range(ship.length):
                ship_coordinates.append((x, ship.row))
                x += 1
        else:
            ship.column = random.choice(columns)
            available_rows = rows[:-ship.length]
            ship.row = random.choice(available_rows)
            y = ship.row
            for i in range(ship.length):
                ship_coordinates.append((ship.column, y))
                y += 1
        if all(coord in available_cells for coord in ship_coordinates):
            return ship_coordinates
        else:
            #  If any ship in a cell already taken, re-call the function to try again
            return self.randomize_ship_coordinates(columns, rows, ship, available_cells)

    def random_pick(self):
        return random.choice(self.available_cells)

    def enemy_turn(self):
        print("---Starting attributes---")
        print(f"Ship Hit = {self.ship_hit}")
        print(f"Second Hit = {self.second_hit}")
        print(f"Tested no hit = {self.tested_no_hit}")
        print(f"Tested no hit2= {self.tested_no_hit_2}")
        if not self.ship_hit:
            pick = self.random_pick()
        elif self.tested_no_hit_2:  # If there has been 2 miss set second_hit back to none to go back to original targets
            self.second_hit = None
            print("Resetting second hit")
            return self.pick_target_after_first_hit()
        elif self.ship_hit and not self.second_hit:
            pick = self.pick_target_after_first_hit()
        elif self.ship_hit and self.second_hit:
            pick = self.pick_target_after_second_hit(1)
        else:
            print("no move in ai")
            pick = self.random_pick()
        self.available_cells.remove(pick)
        return pick

    def pick_target_after_first_hit(self):
        next_targets = [(self.ship_hit[0] + 1, self.ship_hit[1]),
                        (self.ship_hit[0] - 1, self.ship_hit[1]),
                        (self.ship_hit[0], self.ship_hit[1] + 1),
                        (self.ship_hit[0], self.ship_hit[1] - 1)]
        next_targets_verified = [cell for cell in next_targets if cell in self.available_cells]
        pick = random.choice(next_targets_verified)
        return pick

    def pick_target_after_second_hit(self, check_distance):
        if self.ship_hit[0] == self.second_hit[0]:
            next_targets = [(self.ship_hit[0], (max(self.ship_hit[1], self.second_hit[1]) + check_distance)),
                            (self.ship_hit[0], (min(self.ship_hit[1], self.second_hit[1]) - check_distance))]
            next_targets_verified = [cell for cell in next_targets if cell in self.available_cells]
            if next_targets_verified:
                return random.choice(next_targets_verified)
            else:
                if self.tested_no_hit_2:
                    self.second_hit = None
                    return self.enemy_turn()
                else:
                    check_distance += 1
                    return self.pick_target_after_second_hit(check_distance)
        else:
            next_targets = [(max(self.ship_hit[0], self.second_hit[0] + check_distance), self.ship_hit[1]),
                            (min(self.ship_hit[0], self.second_hit[0] - check_distance), self.ship_hit[1])]
            next_targets_verified = [cell for cell in next_targets if cell in self.available_cells]
            if next_targets_verified:
                return random.choice(next_targets_verified)
            else:
                if self.tested_no_hit_2:
                    self.second_hit = None
                    return self.enemy_turn()
                else:
                    check_distance += 1
                    return self.pick_target_after_second_hit(check_distance)


def display_permanent_text():
    title_font = pygame.font.Font(r".\fonts\INVASION2000.TTF", 60)
    title_text = title_font.render("Battleships!", True, BLACK, None)
    title_text_rect = title_text.get_rect()
    title_text_rect.centerx = window_surface.get_rect().centerx
    title_text_rect.centery = 30

    grid_header_font = pygame.font.Font(r".\fonts\ARCADECLASSIC.TTF", 35)
    player_text = grid_header_font.render("Player Grid", True, BLACK, None)
    player_text_rect = player_text.get_rect()
    player_text_rect.centerx = 240
    player_text_rect.centery = 60

    enemy_text = grid_header_font.render("Enemy Grid", True, BLACK, None)
    enemy_text_rect = enemy_text.get_rect()
    enemy_text_rect.centerx = 920
    enemy_text_rect.centery = 60

    window_surface.blit(title_text, title_text_rect)
    window_surface.blit(player_text, player_text_rect)
    window_surface.blit(enemy_text, enemy_text_rect)


def display_instruction(text, colour=WHITE):
    """Displays instruction line at the bottom of the screen, pass 'text' to display"""
    instruction_font = pygame.font.SysFont(None, 42)
    instruction_text = instruction_font.render(text, True, colour, GREY)
    instruction_text_rect = instruction_text.get_rect()
    instruction_text_rect.centerx = 580
    instruction_text_rect.centery = 530
    window_surface.blit(instruction_text, instruction_text_rect)


def create_ships(ship_list):
    """Creates the player's ship sprites from the SHIPS dict and draws to the area
    between the player and enemy grid"""
    ship_y = 70
    ship_x = 480
    for ship in SHIPS:
        path = Path(SHIPS[ship][1])
        name = ship
        length = SHIPS[ship][0]
        ship_list.add(Ship(name, length, path, ship_x, ship_y))
        ship_y += 40
    ship_list.draw(window_surface)


def refresh_screen(player_grid, enemy_grid, button_list, ship_list, instruction_text, hit_list, instruction_colour=WHITE):
    """Updates each graphical element to the main display"""
    window_surface.fill(GREY)
    draw_lines()
    window_surface.blit(player_grid.surface, player_grid.rect)
    window_surface.blit(enemy_grid.surface, enemy_grid.rect)
    display_permanent_text()
    display_instruction(instruction_text, instruction_colour)
    button_list.update()
    button_list.draw(window_surface)
    ship_list.update()
    ship_list.draw(window_surface)
    hit_list.update()
    hit_list.draw(window_surface)
    pygame.display.update()


def set_up_player_ships(player_grid, enemy_grid, ship_list, button_list, clock, hit_list):
    """Game loop for the ship setup phase of the game"""
    setting_up = True
    selected = None
    instruction_text = "Move the ships to the player grid, then press 'Lock-in ships'"
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
                            shipmove_x = ship.rect.x - event.pos[0]
                            shipmove_y = ship.rect.y - event.pos[1]
                    for sprite in button_list.sprites():
                        if sprite.rect.collidepoint(event.pos):
                            # Detect if the Lock in button has been clicked
                            if sprite.name == "lock-in":
                                setting_up, instruction_text = lock_in_ships(player_grid, setting_up, ship_list)
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

        refresh_screen(player_grid, enemy_grid, button_list, ship_list, instruction_text, hit_list)
        clock.tick(25)


def play_sound(type):
    if type == "hit":
        explosion = random.choice([r".\sounds\boom1.mp3", r".\sounds\boom2.mp3", r".\sounds\boom3.mp3"])
        explosion_sound = pygame.mixer.Sound(explosion)
        pygame.mixer.Sound.play(explosion_sound)
    elif type == "miss":
        splash = random.choice([r".\sounds\splash1.mp3", r".\sounds\splash2.mp3", r".\sounds\splash3.mp3"])
        splash_sound = pygame.mixer.Sound(splash)
        pygame.mixer.Sound.play(splash_sound)
    elif type == "sink":
        splash_sound = pygame.mixer.Sound(r".\sounds\sink.mp3")
        pygame.mixer.Sound.play(splash_sound)


def lock_in_ships(player_grid, setting_up, ship_list):
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
        instruction_text = "Ships locked in!"
    else:
        # clear the ship attribute from all cells
        for cell in player_grid.cells:
            cell.ship = None
            instruction_text = "Make sure all ships are fully on the grid and not overlapping!"
    return setting_up, instruction_text


def check_for_win(grid):
    for cell in grid.cells:
        if cell.ship is not None:
            return False
    return True


def game_over():
    print("Game Over")

def draw_lines():
    pygame.draw.line(window_surface, DARK_GREY, (10, 10), (1150, 10))
    pygame.draw.line(window_surface, DARK_GREY, (1150, 10), (1150, 570))
    pygame.draw.line(window_surface, DARK_GREY, (1150, 570), (10, 570))
    pygame.draw.line(window_surface, DARK_GREY, (10, 10), (10, 570))

def main():
    pygame.mixer.music.load(r".\sounds\valkyries.mid")
    pygame.mixer.music.play()
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
    hit_list = pygame.sprite.Group()
    create_ships(ship_list)

    # Create Buttons
    rotate_button = Button("rotate", Path(r".\sprites\Rotate_button.png"), 500, 330)
    lock_in_button = Button("lock-in", Path(r".\sprites\lock-in_button.png"), 500, 420)
    button_list.add(rotate_button)
    button_list.add(lock_in_button)

    enemy = EnemyAi(enemy_grid)
    enemy.randomise_ships()

    # Main game loop

    clock = pygame.time.Clock()
    set_up_player_ships(player_grid, enemy_grid, ship_list, button_list, clock, hit_list)
    button_list.empty()
    instruction_text = "Ships locked in!"
    refresh_screen(player_grid, enemy_grid, button_list, ship_list, instruction_text, hit_list)
    pygame.time.wait(1000)

    playing = True
    while playing:
        player_turn = True
        instruction_text = "Your go. Choose enemy cell to target."
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                if enemy_grid.rect.collidepoint(event.pos):
                    # Check the cell clicked on to see if it had been clicked before
                    cell = None
                    while not cell:
                        cell = enemy_grid.get_cell()
                    print(cell)
                    if not cell.is_clicked:
                        cell_rect_center, cell_ship = cell.cell_clicked()
                        if cell_ship:  # ship name will be returned if there is a hit
                            hit_list.add(CellHit(Path(r".\sprites\hit.png"), cell_rect_center))
                            play_sound("hit")
                            instruction_text = f"You hit the enemy's {cell_ship}!"
                            for ship in enemy.ships:
                                if ship.name == cell.ship:
                                    cell.ship = None
                                    ship.length -= 1
                                    if ship.length == 0:
                                        instruction_text = f"You sunk the enemy's {cell_ship}!"
                                        play_sound("sink")
                                        refresh_screen(player_grid, enemy_grid, button_list, ship_list,
                                                       instruction_text, hit_list, instruction_colour=RED)
                                        pygame.time.wait(2000)
                                        if check_for_win(enemy_grid):
                                            instruction_text = "You sunk all the enemy's ships. You win!"
                                            game_over()
                        else:
                            hit_list.add(CellHit(Path(r".\sprites\miss.png"), cell_rect_center))
                            play_sound("miss")
                            instruction_text = "Miss!"

                        refresh_screen(player_grid, enemy_grid, button_list, ship_list, instruction_text, hit_list)
                        pygame.time.wait(1000)

                        enemy_hit = enemy.enemy_turn()
                        cell = player_grid.return_cell(enemy_hit)
                        cell_rect_center, cell_ship = cell.cell_clicked()
                        if cell_ship:  # ship name will be returned if there is a hit
                            hit_list.add(CellHit(Path(r".\sprites\hit.png"), cell_rect_center))
                            if not enemy.ship_hit:
                                print("if not enemy.ship_hit:")
                                enemy.ship_hit = enemy_hit
                            elif enemy.ship_hit:
                                print("elif enemy.ship_hit:")
                                enemy.second_hit = enemy_hit
                            play_sound("hit")
                            instruction_text = f"Enemy attacked, {cell_rect_center}. They hit your {cell_ship}!"
                            for ship in ship_list:
                                if ship.name == cell.ship:
                                    cell.ship = None
                                    ship.length -= 1
                                    if ship.length == 0:
                                        instruction_text = f"Enemy sunk your {cell_ship}!"
                                        play_sound("sink")
                                        enemy.reset_hit_logs()
                                        refresh_screen(player_grid, enemy_grid, button_list, ship_list,
                                                       instruction_text, hit_list, instruction_colour=RED)
                                        pygame.time.wait(2000)
                                        if check_for_win(player_grid):
                                            instruction_text = "Enemy sunk all your ships. You lose!"
                                            game_over()
                        else:
                            hit_list.add(CellHit(Path(r".\sprites\miss.png"), cell_rect_center))
                            play_sound("miss")
                            instruction_text = f"Enemy attacked, {enemy_hit}. They missed!"
                            print(f"Enemy hit = {enemy_hit}")
                            if enemy.ship_hit and enemy.second_hit:
                                if not enemy.tested_no_hit:
                                    print("if not enemy.tested_no_hit:")
                                    # record the miss if 2 hits are logged
                                    enemy.tested_no_hit = enemy_hit
                                else:
                                    print("else: enemy.tested_no_hit_2 = enemy_hit")
                                    # if a miss again after a miss already logged, this means the enemy is not
                                    # correctly tracking a ship (eg if 2 ships next to each other)
                                    # set tested_no_hit_2 to break out of the recursion to avoid crash
                                    enemy.tested_no_hit_2 = enemy_hit

                        refresh_screen(player_grid, enemy_grid, button_list, ship_list, instruction_text, hit_list)
                        pygame.time.wait(1000)

        refresh_screen(player_grid, enemy_grid, button_list, ship_list, instruction_text, hit_list)


if __name__ == '__main__':
    main()

# TODO game over and play again
# TODO start screen
# TODO improve look of game
