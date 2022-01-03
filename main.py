import sys
import pygame
from pygame.locals import *

pygame.init()

window_surface = pygame.display.set_mode((480, 480), 0, 32)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (52, 140, 235)
RED = (230, 15, 11)
GREY = (107, 99, 99)

title_font = pygame.font.SysFont(None, 42)
text = title_font.render("Battleships!", True, BLACK, GREY)

text_rect = text.get_rect()
text_rect.centerx = window_surface.get_rect().centerx
text_rect.centery = 20

window_surface.fill(GREY)

pygame.draw.polygon(window_surface, BLUE, ((40, 40), (440, 40), (440, 440), (40, 440)))

x = 40
y = 40

for i in range(11):
    pygame.draw.line(window_surface, BLACK, (x, 40), (x, 440), 4)
    pygame.draw.line(window_surface, BLACK, (40, y), (440, y), 4)
    x += 40
    y += 40

window_surface.blit(text, text_rect)

pygame.display.update()

def main():
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()



if __name__ == '__main__':
    main()

