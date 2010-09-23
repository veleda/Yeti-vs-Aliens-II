#!/usr/bin/env python
# vi: set et:ts=4:sw=4

import sys

import pygame

class Player:
    agility = 20
    can_jump = True
    speed = 5
    score = 0
    x = 240
    y = 340
    vx = 0
    vy = 0
    w = 30
    h = 80

draw_tile = lambda color, x, y: pygame.draw.rect(screen, color,
        (x * tile_width, y * tile_height, tile_width, tile_height))

# Gravity.
g = 1

tile = pygame.image.load("tile.png")
tile_width = 32
tile_height = 32

levelfilename = "levelt"
level = map(list, open(levelfilename).read().split("\n")[:-1])

# Colors.
bgcolor = 0, 127, 0
fgcolor = 255, 255, 255
hgcolor = 255, 0, 0
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
        # Draw objects to back buffer.
        screen.blit(heaven, (0, 0))

        # Check if the player is falling onto a platform.
        # x and y are measured in tiles.

        # Find the height of the tiles under the player's feet.
        y = (player.y + player.h) // tile_height

        # Check if the tiles covered by the player are filled in.
        for x in range(player.x // tile_width, (player.x + player.w) // tile_height + 1):
            if level[y][x] == "x":
                player.can_jump = True

                # If falling, stop the player from falling through.
                if player.vy > 0:
                    player.y = tile_height * y - player.h - g
                    player.vy = 0

            draw_tile(hgcolor, x, y)

        # Move the player.
        player.vy += g
        player.x += player.vx
        player.y += player.vy

        # Draw the tiles of the level. Just rectangles for now.
        for y in range(len(level)):
            for x in range(len(level[y])):
                if level[y][x] == "x":
                    screen.blit(tile, (x * tile_width, y * tile_height))

        # Draw player. Just a rectangle for now.
        pygame.draw.rect(screen, fgcolor, (player.x, player.y, player.w, player.h))

        # Swap front and back buffers.
        pygame.display.update()

    # If a key is pressed...
    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_LEFT:
            player.vx -= player.speed

        elif event.key == pygame.K_RIGHT:
            player.vx += player.speed

        elif event.key == pygame.K_UP:
            if player.can_jump:
                player.y -= 1
                player.vy = -player.agility

            player.can_jump = False

        elif event.key == 27:
            break

    # If a key is released...
    elif event.type == pygame.KEYUP:
        if event.key == pygame.K_LEFT:
            player.vx += player.speed

        elif event.key == pygame.K_RIGHT:
            player.vx -= player.speed

        elif event.key == pygame.K_UP:
            player.vy += player.agility
