#!/usr/bin/env python
# vi: set et:ts=4:sw=4

import sys

import pygame

class Camera:
    x = 0

class Player:
    agility = 12
    can_jump = True
    speed = 4
    score = 0
    x = 40
    y = 400
    vx = 0
    vy = 0
    w = 32
    h = 43
    image = pygame.image.load("yeti.png")

draw_tile = lambda color, x, y: pygame.draw.rect(screen, color,
        (x * tile_width, y * tile_height, tile_width, tile_height))

# Gravity.
g = 1

# Tiles.
tile = pygame.image.load("tile.png")
tile_width = 32
tile_height = 32

# Level.
level_filename = "levelp"
level = map(list, open(level_filename).read().split("\n")[:-1])
level_width = len(level[0]) * tile_width

# Colors.
bgcolor = 0, 127, 0
fgcolor = 255, 255, 255
hgcolor = 255, 0, 0
mgcolor = 255, 127, 0

# Screen surface and size.
size = screen_width, screen_height = 640, 480
screen = pygame.display.set_mode(size)

# Background.
heaven = pygame.image.load("heaven.png")

# Middleground.
mountains = pygame.image.load("mountains.png")

# Game objects.
camera = Camera()
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
        # Check if the player is falling onto a platform.
        # x and y are measured in tiles.

        # Check if the tiles covered by the player are filled in.
        if player.vy > 0:
            # Find the height of the tiles under the player's feet.
            y = (player.y + player.h) // tile_height

            for x in range(player.x // tile_width, (player.x + player.w - 1) // tile_width + 1):
                if y in range(len(level)) and level[y][x] == "x":
                    player.can_jump = True

                    # If falling, stop the player from falling through.
                    player.y = tile_height * y - player.h - g
                    player.vy = 0

                #draw_tile(fgcolor, x, y)
        elif player.vy < 0:
            # Find the height of the tiles over the player's head.
            y = player.y // tile_height

            for x in range(player.x // tile_width, (player.x + player.w - 1) // tile_width + 1):
                if y in range(len(level)) and level[y][x] == "x":
                    player.can_jump = True

                    # If falling, stop the player from falling through.
                    player.y = y * tile_height + player.h - g
                    player.vy = 0

                #draw_tile(fgcolor, x, y)

        # Stop player if trying to walk into a wall.
        if player.vx > 0:
            x = (player.x + player.w) // tile_width

            for y in range(player.y // tile_height, (player.y + player.h) // tile_height + 1):
                if y in range(len(level)) and level[y][x] == "x":
                    player.x -= player.vx
                    break

                #draw_tile(hgcolor, x, y)

        elif player.vx < 0:
            x = (player.x + player.w - 1) // tile_width - 1

            for y in range(player.y // tile_height, (player.y + player.h) // tile_height + 1):
                if y in range(len(level)) and level[y][x] == "x":
                    player.x -= player.vx
                    break

                #draw_tile(hgcolor, x, y)

        # Move the player.
        if player.vx < tile_height // 2:
            player.vy += g

        player.x += player.vx
        player.y += player.vy

        # Stop game if player falls out of the screen.
        if player.y > screen_height:
            break

        # Position camera.
        if player.x < screen_width // 2:
            camera.x = 0
        elif player.x > level_width - screen_width // 2:
            camera.x = level_width - screen_width
        else:
            camera.x = player.x - screen_width // 2

        # Draw background.
        screen.blit(heaven, (0 - camera.x // 32, 0))

        # Draw middleground.
        screen.blit(mountains, (0 - camera.x // 8, 0))

        # Draw the tiles of the level.
        for y in range(len(level)):
            for x in range(len(level[y])):
                if level[y][x] == "x":
                    screen.blit(tile, (x * tile_width - camera.x, y * tile_height))

        # Draw player.
        #pygame.draw.rect(screen, mgcolor, (player.x, player.y, player.w, player.h))
        screen.blit(player.image, (player.x - camera.x, player.y, player.w, player.h))

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
