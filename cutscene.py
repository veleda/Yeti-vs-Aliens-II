#!/usr/bin/env python
# vi: set et:ts=4:sw=4

import pygame

def cutscene(window, bgfile, fgfile, musicfile, textfile, textcolor=(255, 255, 255), volume=.25):
    scroll_speed = .7
    scroll = 0

    font_name = "fonts/alien.ttf"
    text_height = 28
    line_height = 1.1 * text_height

    x = 80

    bgimage = pygame.image.load(bgfile)
    fgimage = pygame.image.load(fgfile)
    fgimage.set_colorkey((255, 0, 255))
    text = open(textfile).read().split("\n")[1:]

    pygame.mixer.music.load(musicfile)
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.play()

    font = pygame.font.Font(font_name, text_height)
    lines = [font.render(line, True, textcolor) for line in text]

    while True:
        event = pygame.event.wait()

        if event.type == pygame.VIDEOEXPOSE:
            window.blit(bgimage, (0, 0))

            for i in range(len(lines)):
                y = i * line_height - scroll
                window.blit(lines[i], (x, y))

            window.blit(fgimage, (0, 0))
            
            pygame.display.update()

            scroll += scroll_speed

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                break

if __name__ == "__main__":
    framerate = 60

    window_width, window_height = 640, 480

    pygame.init()
    pygame.time.set_timer(pygame.VIDEOEXPOSE, 1000 / framerate)
    window = pygame.display.set_mode((window_width, window_height))

    cutscene(window, "cutscenes/credits/bg.png", "cutscenes/credits/fg.png", "art/music/Yetis theme 1.mp3", "cutscenes/credits/text")
