#!/usr/bin/env python
# vi: set et:ts=4:sw=4

import os
import sys

import pygame

framerate = 60

tile_width = 32
tile_height = 32

window_width = 640
window_height = 480
editor_width = 4 * tile_width

class Camera:
    x = 0

class Player:
    agility = 9
    airborne = True
    jumptime = -1
    maxjumptime = 8
    speed = 4

    x = 40
    y = 400

    vx = 0
    vy = 0

    w = 32
    h = 43

    rimage = pygame.image.load("gfx/sprites/yeti.png")
    limage = pygame.transform.flip(rimage, True, False)
    image = rimage

def load_tiles(filename):
    tile_image = pygame.image.load(filename)

    tiles = []
    for y in range(tile_image.get_rect()[3] // tile_height):
        tiles.append(tile_image.subsurface(0, y * tile_height, tile_width, tile_height))

    return tiles

def play(level, window, tiles, editing=False):
    layernames, tilemap = level
    level_width = len(tilemap[0]) * tile_width

    layers = []
    for layername in layernames:
        if layername:
            layers.append(pygame.image.load("gfx/layers/%s" % layername))
            layers[-1].set_colorkey((255, 0, 255))
        else:
            layers.append(None)

    current_tile = 0
    g = .5

    camera = Camera()
    player = Player()

    screen_height = window_height
    if editing:
        screen_width = window_width - editor_width
        screen = window.subsurface((editor_width, 0, screen_width, screen_height))
    else:
        screen_width = window_width
        screen = window.subsurface((0, 0, screen_width, screen_height))

    while True:
        event = pygame.event.wait()

        if event.type == pygame.VIDEOEXPOSE:
            # Check if the player is falling onto a platform.
            # x and y are measured in tiles.

            # Check if the tiles covered by the player are filled in.
            if player.vy > 0:
                y = int((player.y + player.h + player.vy) // tile_height)

                for x in range(player.x // tile_width, (player.x + player.w - 1) // tile_width + 1):
                    if y in range(len(tilemap)) and tilemap[y][x]:
                        if player.airborne and player.jumptime > 0:
                            player.y -= 1
                            player.vy = -player.agility
                            player.airborne = True
                        else:
                            player.y = tile_height * y - player.h - g
                            player.vy = 0
                            player.airborne = False

            elif player.vy < 0:
                # Find the height of the tiles over the player's head.
                y = int(player.y // tile_height)

                for x in range(player.x // tile_width, (player.x + player.w - 1) // tile_width + 1):
                    if y in range(len(tilemap)) and tilemap[y][x]:
                        # If falling, stop the player from falling through.
                        player.y = y * tile_height + player.h - g
                        player.vy = 0

            # Stop player if trying to walk into a wall.
            if player.vx > 0:
                x = (player.x + player.w) // tile_width

                for y in range(int(player.y // tile_height), int((player.y + player.h) // tile_height + 1)):
                    if y in range(len(tilemap)) and tilemap[y][x]:
                        player.x -= player.vx
                        break

            elif player.vx < 0:
                x = (player.x + player.w - 1) // tile_width - 1

                for y in range(int(player.y // tile_height), int((player.y + player.h) // tile_height + 1)):
                    if y in range(len(tilemap)) and tilemap[y][x]:
                        player.x -= player.vx
                        break

            # Move the player.
            if player.jumptime > -1:
                player.jumptime -= 1

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
                    x = -camera.x // (1 << i)
                    screen.blit(layers[i], (x, 0))

            # Draw the tiles of the level.
            for y in range(len(tilemap)):
                for x in range(len(tilemap[y])):
                    if tilemap[y][x]:
                        screen.blit(tiles[tilemap[y][x]], (x * tile_width - camera.x, y * tile_height))

            # Draw player.
            #pygame.draw.rect(screen, mgcolor, (player.x, player.y, player.w, player.h))
            if player.vx < 0:
                player.image = player.limage
            elif player.vx > 0:
                player.image = player.rimage

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

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                player.vx -= player.speed

            elif event.key == pygame.K_RIGHT:
                player.vx += player.speed

            elif event.key == pygame.K_UP:
                if player.airborne:
                    if player.jumptime < 0:
                        player.jumptime = player.maxjumptime
                else:
                    player.y -= 1
                    player.vy = -player.agility
                    player.airborne = True

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

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                player.vx += player.speed

            elif event.key == pygame.K_RIGHT:
                player.vx -= player.speed

            elif event.key == pygame.K_UP:
                player.jumptime = -1
                if player.vy < 0:
                    player.vy += player.agility / 2

        elif editing and event.type == pygame.MOUSEBUTTONDOWN:
            if event.pos[0] > editor_width:
                x = (event.pos[0] - editor_width + camera.x) // tile_width
                y = event.pos[1] // tile_height
                if event.button == 1:
                    tilemap[y][x] = current_tile
                elif event.button == 3:
                    tilemap[y][x] = 0

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

        elif editing and event.type == pygame.MOUSEMOTION:
            if event.pos[0] > editor_width:
                x = (event.pos[0] - editor_width + camera.x) // tile_width
                y = event.pos[1] // tile_height
                if event.buttons[0]:
                    tilemap[y][x] = current_tile
                elif event.buttons[2]:
                    tilemap[y][x] = 0

    return level

def main():
    editing = "-e" in sys.argv

    level_filename = sys.argv[-1]

    if len(sys.argv) > 1 and os.path.isfile(level_filename):
        level = eval(open(level_filename).read())
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

    # Short buffer for low latency.
    pygame.mixer.pre_init(buffer=512)

    pygame.init()
    pygame.time.set_timer(pygame.VIDEOEXPOSE, 1000 / framerate)
    window = pygame.display.set_mode((window_width, window_height))

    play(level, window, load_tiles("gfx/tiles.png"), editing=editing)

    if editing:
        f = open(level_filename, "w")
        f.write(repr(level))
        f.close()

if __name__ == "__main__":
    main()
