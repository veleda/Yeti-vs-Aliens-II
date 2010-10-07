#!/usr/bin/env python
# vi: set et:ts=4:sw=4
import pygame
import sys
import os
import dircache

def customlevel(edit):
    subdir = ""
    print dircache.listdir('levels')
       
def menumain(screen):
    buttons = ["New game", "Custom Level", "Level Editor", "Quit."]
    button_height = 37
    menu_margin = 30

    bgcolor = 255, 255, 255
    fgcolor = 0, 0, 0

    framerate = 20


    menuhover = -1

    font = pygame.font.SysFont("Bitstream Vera Sans", 24)

    pygame.time.set_timer(pygame.VIDEOEXPOSE, 1000 / framerate)

    labels = []
    for button in buttons:
        labels.append(font.render(button, 1, fgcolor))

    while True:
        event = pygame.event.wait()

        if event.type == pygame.VIDEOEXPOSE:
            screen.fill(bgcolor)

            for i in range(len(labels)):
                screen.blit(labels[i], (menu_margin, i * button_height + menu_margin))
            if menuhover != -1:
                rect = labels[menuhover].get_rect()
                rect[0] += menu_margin - 4
                rect[1] += menu_margin + menuhover * button_height - 3
                rect[2] += 8
                rect[3] += 6
                pygame.draw.rect(screen, (255,0,0), rect, 3)

            pygame.display.update()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                sys.exit(0)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            for i in range(len(labels)):
                rect = labels[i].get_rect()
                if (event.pos[0] < rect[2] + menu_margin and event.pos[0] > menu_margin and event.pos[1] > menu_margin + i*button_height and event.pos[1] < menu_margin + (i+1)*button_height):
                    if i == 0:
                        return (0, "levels/campaigns/default/level1")
                    elif i == 1:
                        return customlevel(0)
                    elif i == 2:
                        return customlevel(1)
                    elif i == 3:
                        sys.exit(0)
                
        elif event.type == pygame.MOUSEMOTION:
            menuhover = -1
            for i in range(len(labels)):
                rect = labels[i].get_rect()
                if (event.pos[0] < rect[2] + menu_margin and event.pos[0] > menu_margin and event.pos[1] > menu_margin + i*button_height and event.pos[1] < menu_margin + (i+1)*button_height):
                    menuhover = i
if (__name__ == '__main__'):
    import os
    import sys
    import pygame
    pygame.init()
    window_width = 640
    window_height = 480
    screen = pygame.display.set_mode((window_width, window_height))
    menumain(screen)
