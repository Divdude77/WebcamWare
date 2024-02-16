import pygame
from sys import exit

from cv import *
from menus import *
from games import *
from components import *

pygame.init()
WINDOW_WIDTH = 1080
WINDOW_HEIGHT = 720
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("WebcamWare")
pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 3)
clock = pygame.time.Clock()

# menu = HomeMenu(screen)
# menu = HoleInTheWall(screen, 10)
menu = GameRunner(screen)
# menu = GameOverMenu(screen)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        else:
            new_menu = menu.handle_event(event)
            if new_menu:
                menu = new_menu

    new_menu = menu.draw()
    if new_menu:
        menu = new_menu

    pygame.display.update()
    clock.tick(60)
