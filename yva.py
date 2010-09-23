#!/usr/bin/env python

import sys

import pygame

g = 1

tile_width = 32
tile_height = 32

levelfilename = "levelt"
level = map(list, open(levelfilename).read().split("\n")[:-1])

class Player:
    agility = 17
    speed = 3
    score = 0
    x = 240
    y = 340
    vx = 0
    vy = 0
    w = 30
    h = 80

# Colors.
bgcolor = 0, 127, 0
fgcolor = 255, 255, 255
mgcolor = 255, 127, 0

# Screen surface and size.
size = screen_width, screen_height = 640, 480
screen = pygame.display.set_mode(size)

heaven = pygame.image.load("heaven.png")

# Game objects.
player = Player()

# Short buffer for low latency.
pygame.mixer.pre_init(buffer=512)

# Initialize all pygame submodules.
pygame.init()

# Generate display update request at the framerate.
framerate = 60 # Frames per second.
pygame.time.set_timer(pygame.VIDEOEXPOSE, 1000 / framerate)

# Load sound effects.
#bip = pygame.mixer.Sound("bip.wav")
#bop = pygame.mixer.Sound("bop.wav")
#end = pygame.mixer.Sound("end.wav")

while True:
    # Wait until event arrives.
    event = pygame.event.wait()

    # If we should update the screen...
    if event.type == pygame.VIDEOEXPOSE:
        # Move the player.
        player.vy += g
        player.x += player.vx
        player.y += player.vy

        if player.y >= screen_height - player.h:
            player.y = screen_height - player.h
            player.vy = 0

        # Draw objects to back buffer.
        #screen.fill(bgcolor)
        screen.blit(heaven, (0, 0))

        for y in range(len(level)):
            for x in range(len(level[y])):
                if level[y][x] == "x":
                    pygame.draw.rect(screen, mgcolor, (x * tile_width, y * tile_height, tile_width, tile_height))

        pygame.draw.rect(screen, fgcolor, (player.x, player.y, player.w, player.h))

        # Swap front and back buffers.
        pygame.display.update()

    # If a key is pressed...
    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_LEFT:
            player.vx += -player.speed

        elif event.key == pygame.K_RIGHT:
            player.vx += player.speed

        elif event.key == pygame.K_UP:
            if player.y == 400:
                player.y -= 1
                player.vy = -player.agility

        elif event.key == 27:
            break

    # If a key is released...
    elif event.type == pygame.KEYUP:
        if event.key == pygame.K_LEFT:
            player.vx -= -player.speed

        elif event.key == pygame.K_RIGHT:
            player.vx -= player.speed
