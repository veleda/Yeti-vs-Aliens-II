#!/usr/bin/env python
# vi: set et:ts=4:sw=4

import os
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
    rimage = pygame.image.load("gfx/sprites/yeti.png")
    limage = pygame.transform.flip(rimage, True, False)
    image = rimage

draw_tile = lambda color, x, y: pygame.draw.rect(screen, color,
        (x * tile_width, y * tile_height, tile_width, tile_height))

# Check for editing mode.
editing = "-e" in sys.argv

# Gravity.
g = .8

# Screen size.
screen_width = 640
screen_height = 480

# Tiles.
tile_width = 32
tile_height = 32
tile_image = pygame.image.load("gfx/tiles.png")

tiles = []
for y in range(tile_image.get_rect()[3] // tile_height):
    tiles.append(tile_image.subsurface(0, y * tile_height, tile_width, tile_height))

current_tile = 0

# Level.
level_filename = sys.argv[-1]

if len(sys.argv) > 1 and os.path.isfile(level_filename):
    layernames, tilemap = level = eval(open(level_filename).read())
else:
    if not editing:
        if len(sys.argv) == 2:
            print "Level \"%s\" does not exist. Try creating a level using the editor option (-e)." % level_filename
        print "Usage: %s [-e] level" % sys.argv[0]
        sys.exit(1)

    layernames = [None, None,
            "mountains_1.png", None,
            "mountains_2.png", None,
            "mountains_3.png", None,
            None, None, "heaven.png"]

    tilemap = []
    for i in range(14):
        tilemap.append([0 for i in range(3 * screen_width // tile_width)])
    tilemap.append([1 for i in range(3 * screen_width // tile_width)])

    level = layernames, tilemap

level_width = len(tilemap[0]) * tile_width

# Layers.
layers = []
for layername in layernames:
    if layername:
        layers.append(pygame.image.load("gfx/layers/%s" % layername))
    else:
        layers.append(None)

# Colors.
bgcolor = 0, 127, 0
fgcolor = 255, 255, 255
hgcolor = 255, 0, 0
mgcolor = 255, 127, 0

# Screen surface and size.
editor_width = 4 * tile_width

if editing:
    window_width = screen_width + editor_width
else:
    window_width = screen_width

window_height = screen_height

window = pygame.display.set_mode((window_width, window_height))

if editing:
    screen = window.subsurface((editor_width, 0, screen_width, screen_height))
else:
    screen = window.subsurface((0, 0, screen_width, screen_height))

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
            y = int((player.y + player.h + player.vy) // tile_height)

            for x in range(player.x // tile_width, (player.x + player.w - 1) // tile_width + 1):
                if y in range(len(tilemap)) and tilemap[y][x]:
                    player.can_jump = True

                    # If falling, stop the player from falling through.
                    player.y = tile_height * y - player.h - g
                    player.vy = 0

                #draw_tile(fgcolor, x, y)
        elif player.vy < 0:
            # Find the height of the tiles over the player's head.
            y = int(player.y // tile_height)

            for x in range(player.x // tile_width, (player.x + player.w - 1) // tile_width + 1):
                if y in range(len(tilemap)) and tilemap[y][x]:
                    # If falling, stop the player from falling through.
                    player.y = y * tile_height + player.h - g
                    player.vy = 0

                #draw_tile(fgcolor, x, y)

        # Stop player if trying to walk into a wall.
        if player.vx > 0:
            x = (player.x + player.w) // tile_width

            for y in range(int(player.y // tile_height), int((player.y + player.h) // tile_height + 1)):
                if y in range(len(tilemap)) and tilemap[y][x]:
                    player.x -= player.vx
                    break

                #draw_tile(hgcolor, x, y)

        elif player.vx < 0:
            x = (player.x + player.w - 1) // tile_width - 1

            for y in range(int(player.y // tile_height), int((player.y + player.h) // tile_height + 1)):
                if y in range(len(tilemap)) and tilemap[y][x]:
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

        # Draw layers.
        for i in range(len(layers) - 1, -1, -1):
            if layers[i]:
                screen.blit(layers[i], (0 - camera.x // 2 ** i, 0))

        # Draw the tiles of the level.
        for y in range(len(tilemap)):
            for x in range(len(tilemap[y])):
                if tilemap[y][x]:
                    screen.blit(tiles[tilemap[y][x]], (x * tile_width - camera.x, y * tile_height))

        # Draw player.
        #pygame.draw.rect(screen, mgcolor, (player.x, player.y, player.w, player.h))
        screen.blit(player.image, (player.x - camera.x, player.y, player.w, player.h))

        # Draw editor widgets.
        if editing:
            x, y = 0, 0
            for tile in tiles:
                window.blit(tile, (x, y))
                if x + 2 * tile_width > editor_width:
                    x = 0
                    y += tile_height
                else:
                    x += tile_width

        # Swap front and back buffers.
        pygame.display.update()

    # If a key is pressed...
    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_LEFT:
            player.vx -= player.speed
            player.image = player.limage

        elif event.key == pygame.K_RIGHT:
            player.vx += player.speed
            player.image = player.rimage

        elif event.key == pygame.K_UP:
            if player.can_jump:
                player.y -= 1
                player.vy = -player.agility

            player.can_jump = False

        elif event.key == 27:
            break

        if editing:
            if event.key in (pygame.K_PLUS, pygame.K_KP_PLUS):
                for row in tilemap:
                    row.append(0)
                    level_width = len(tilemap[0]) * tile_width

            elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                for row in tilemap:
                    row.pop()
                    level_width = len(tilemap[0]) * tile_width

    # If a key is released...
    elif event.type == pygame.KEYUP:
        if event.key == pygame.K_LEFT:
            player.vx += player.speed

        elif event.key == pygame.K_RIGHT:
            player.vx -= player.speed

        elif event.key == pygame.K_UP:
            if player.vy < 0:
                player.vy += player.agility

    # If a mouse button is clicked...
    elif editing and event.type == pygame.MOUSEBUTTONDOWN:
        if event.pos[0] > editor_width:
            x = (event.pos[0] - editor_width + camera.x) // tile_width
            y = event.pos[1] // tile_height
            tilemap[y][x] = current_tile

        else:
            x, y = 0, 0
            for i in range(len(tiles)):
                if event.pos[0] in range(x, x + tile_width) and event.pos[1] in range(y, y + tile_height):
                    current_tile = i
                    break

                if x + 2 * tile_width > editor_width:
                    x = 0
                    y += tile_height
                else:
                    x += tile_width

    # If a mouse button is held down...
    elif editing and event.type == pygame.MOUSEMOTION:
        if event.buttons[0] and event.pos[0] > editor_width:
            x = (event.pos[0] - editor_width + camera.x) // tile_width
            y = event.pos[1] // tile_height
            tilemap[y][x] = current_tile

if editing:
    f = open(level_filename, "w")
    f.write(repr(level))
    f.close()
