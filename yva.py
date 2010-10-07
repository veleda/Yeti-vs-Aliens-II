#!/usr/bin/env python
# vi: set et:ts=4:sw=4

import os
import sys

import pygame

class Decal:
    def __init__(self, stagetime, x, y, sprites):
        self.alpha = 255
        self.x = x
        self.y = y
        self.stagetime = stagetime
        self.cstage = 0
        self.maxstage = len(sprites)*stagetime-1
        self.sprite = sprites

    def nstage(self):
        self.cstage += 1

class Camera:
    x = 0
    y = 0

class Baddie:
    dead = False

    vy = 0

    w = 32
    h = 32

    def __init__(self, kind, x, y, right):
        self.kind, self.x, self.y, self.right = kind, x, y, right

        self.speed = kind.speed
        self.w = kind.w
        self.h = kind.h
        self.rimage = kind.image
        self.limage = pygame.transform.flip(kind.image, True, False)

        if right:
            self.vx = self.speed
            self.image = self.rimage
        else:
            self.vx = -self.speed
            self.image = self.limage

    def __repr__(self):
        return "Baddie(%s, %d, %d, %s)" % (self.kind, self.x, self.y, self.right)

class Kind:
    def __init__(self, speed, w, h, spritename):
        self.speed, self.w, self.h, self.spritename = speed, w, h, spritename
        imagepath = os.path.join("gfx", "characters", spritename)
        self.image = pygame.image.load(imagepath)
        self.image.set_colorkey((255, 0, 255))

    def __repr__(self):
        return "Kind(%d, %d, %d, \"%s\")" % (self.speed, self.w, self.h, self.spritename)

class Player:
    agility = 10
    airborne = True
    dead = False
    jumptime = -1
    maxjumptime = 8
    speed = 4
    right = True

    life = 5
    heart = pygame.image.load("gfx/items/heart.png")
    heart.set_colorkey((255, 0, 255))

    vx = 0
    vy = 0

    w = 32
    h = 43

    rimage = pygame.image.load("gfx/characters/yeti.png")
    limage = pygame.transform.flip(rimage, True, False)
    image = rimage

    def __init__(self, x, y):
        self.x, self.y = x, y

rpunch = [pygame.image.load("gfx/decals/punch.png")]
lpunch = [pygame.transform.flip(rpunch[0], True, False)]

decals = []

layers_dir = ["gfx", "layers"]
tiles_path = os.path.join("gfx", "tiles.png")

framerate = 60

tile_width = 32
tile_height = 32

window_width = 640
window_height = 480
editor_width = 4 * tile_width

kinds = [Kind(2, 32, 32, "skier.png"),
         Kind(1, 32, 32, "blob.png"),
         Kind(4, 64, 64, "alien.png")]


def load_layers(layernames):
    layers = []
    for layername in layernames:
        if layername:
            filename = os.path.join(*(layers_dir + [layername]))
            layers.append(pygame.image.load(filename))
            layers[-1].set_colorkey((255, 0, 255))
        else:
            layers.append(None)

    return layers

def load_tiles(tiles_path):
    tile_image = pygame.image.load(tiles_path)

    tiles = []
    for y in range(tile_image.get_rect()[3] // tile_height):
        tiles.append(tile_image.subsurface(0, y * tile_height, tile_width, tile_height))
        tiles[-1].set_colorkey((255, 0, 255))

    return tiles

def play(level, window, tiles, editing=False):
    layernames, tilemap, spikytiles, baddies = level
    level_width = len(tilemap[0]) * tile_width
    level_height = len(tilemap) * tile_height

    layers = load_layers(layernames)

    current_baddie = None
    current_kind = 0
    current_tiles = [1, 0]
    g = .6

    camera = Camera()
    player = Player(4 * tile_width, 4 * tile_height)

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
            if not player.dead:
                if player.vy > 0:
                    y = int((player.y + player.h + player.vy) // tile_height)

                    for x in range(player.x // tile_width, (player.x + player.w - 1) // tile_width + 1):
                        if y in range(len(tilemap)) and tilemap[y][x]:
                            if tilemap[y][x] in spikytiles:
                                player.life -= 1
                                player.y -= 1
                                player.vy = -player.agility
                                player. airborne = True

                            else:
                                if player.airborne and player.jumptime > 0:
                                    player.y -= 1
                                    player.vy = -player.agility
                                    player.airborne = True
                                else:
                                    player.y = tile_height * y - player.h - g
                                    player.vy = 0
                                    player.airborne = False

                            break

                        else:
                            if not editing:
                                for baddie in baddies:
                                    if baddie.y // tile_height == y and x in range(baddie.x // tile_width,
                                            (baddie.x + baddie.w) // tile_width) and not baddie.dead:
                                        baddie.dead = True
                                        player.y -= 1
                                        player.vy = -player.agility
                                        player.airborne = True
                                        break

                else:
                    y = int(player.y // tile_height)

                    for x in range(player.x // tile_width, (player.x + player.w - 1) // tile_width + 1):
                        if y in range(len(tilemap)) and tilemap[y][x]:
                            if tilemap[y][x] in spikytiles:
                                player.life -= 1

                            player.y = y * tile_height + player.h - g
                            player.vy = 0
                            break

                        else:
                            if not editing:
                                for baddie in baddies:
                                    if baddie.y // tile_height == y and x in range(baddie.x // tile_width,
                                            (baddie.x + baddie.w) // tile_width) and not baddie.dead:
                                        player.life -= 1
                                        baddie.dead = True
                                        break

                if player.vx > 0:
                    x = (player.x + player.w) // tile_width

                    for y in range(int(player.y // tile_height), int((player.y + player.h) // tile_height + 1)):
                        if y in range(len(tilemap)) and tilemap[y][x]:
                            if tilemap[y][x] in spikytiles:
                                player.life -= 1
                                player.x -= tile_height // 2
                            else:
                                player.x -= player.vx

                            break

                elif player.vx < 0:
                    x = (player.x + player.w - 1) // tile_width - 1

                    for y in range(int(player.y // tile_height), int((player.y + player.h) // tile_height + 1)):
                        if y in range(len(tilemap)) and tilemap[y][x]:
                            if tilemap[y][x] in spikytiles:
                                player.life -= 1
                                player.x += tile_height // 2
                            else:
                                player.x -= player.vx

                            break

                if not editing:
                    for x in (player.x + player.w - 1) // tile_width - 1, (player.x + player.w) // tile_width:
                        for y in range(int(player.y // tile_height), int((player.y + player.h) // tile_height + 1)):
                            for baddie in baddies:
                                if baddie.y // tile_height == y and x in range(baddie.x // tile_width,
                                        (baddie.x + baddie.w) // tile_width) and not baddie.dead:
                                    player.life -= 1
                                    baddie.dead = True
                                    break

            # Move the player.
            if player.jumptime > -1:
                player.jumptime -= 1

            if player.vx < tile_height // 2:
                player.vy += g

            player.x += player.vx
            player.y += player.vy

            if editing:
                player.life = 9

            if player.life < 1:
                player.dead = True

            if player.y > level_height:
                break

            if not editing:
                for baddie in baddies:
                    if not baddie.dead:
                        if baddie.vy > 0:
                            y = int((baddie.y + baddie.h + baddie.vy) // tile_height)

                            for x in range(baddie.x // tile_width, (baddie.x + baddie.w - 1) // tile_width + 1):
                                if y in range(len(tilemap)) and tilemap[y][x]:
                                    baddie.y = tile_height * y - baddie.h - g
                                    baddie.vy = 0
                                    break

                        if baddie.vx > 0:
                            x = (baddie.x + baddie.w) // tile_width

                            for y in range(int(baddie.y // tile_height), int((baddie.y + baddie.h) // tile_height + 1)):
                                if y in range(len(tilemap)) and tilemap[y][x]:
                                    baddie.vx = -baddie.speed
                                    baddie.image = baddie.limage
                                    break

                        elif baddie.vx < 0:
                            x = (baddie.x + baddie.w - 1) // tile_width - 1

                            for y in range(int(baddie.y // tile_height), int((baddie.y + baddie.h) // tile_height + 1)):
                                if y in range(len(tilemap)) and tilemap[y][x]:
                                    baddie.vx = baddie.speed
                                    baddie.image = baddie.rimage
                                    break

                    if baddie.vx < tile_height // 2:
                        baddie.vy += g

                    baddie.x += baddie.vx
                    baddie.y += baddie.vy

            # Position camera.
            if player.x < screen_width // 2:
                camera.x = 0
            elif player.x > level_width - screen_width // 2:
                camera.x = level_width - screen_width
            else:
                camera.x = player.x - screen_width // 2

            if player.y < screen_height // 2:
                camera.y = 0
            elif player.y > level_height - screen_height // 2:
                camera.y = level_height - screen_height
            else:
                camera.y = player.y - screen_height // 2

            # Draw layers.
            for i in range(len(layers) - 1, -1, -1):
                if layers[i]:
                    x = -camera.x // (1 << i)
                    screen.blit(layers[i], (x, 0))

            # Draw the tiles of the level.
            for y in range(len(tilemap)):
                for x in range(len(tilemap[y])):
                    if tilemap[y][x]:
                        screen.blit(tiles[tilemap[y][x]], (x * tile_width - camera.x, y * tile_height - camera.y))

            for baddie in baddies:
                screen.blit(baddie.image, (baddie.x - camera.x, baddie.y - camera.y, baddie.w, baddie.h))

            if player.vx < 0:
                player.right = False
                player.image = player.limage
            elif player.vx > 0:
                player.right = True
                player.image = player.rimage

            screen.blit(player.image, (player.x - camera.x, player.y - camera.y, player.w, player.h))

            for i in range(player.life):
                screen.blit(player.heart, ((tile_width * 3 / 4) * i, 0, tile_width, tile_height))

            for decal in decals:
                screen.blit(decal.sprite[decal.cstage//decal.stagetime], (decal.x-camera.x, decal.y - camera.y))

            for decal in decals:
                decal.nstage()
                if (decal.cstage > decal.maxstage):
                    decals.remove(decal)

            # Draw editor widgets.
            if editing:
                pygame.draw.rect(window, (63, 63, 63), (0, 0, editor_width, window_height))
                window.blit(tiles[current_tiles[0]], ((editor_width - tile_width) // 4, tile_height / 2))
                window.blit(tiles[current_tiles[1]], ((editor_width - tile_width) // 4 * 3, tile_height / 2))

                x, y = -tile_width, 2 * tile_height
                for tile in tiles:
                    if x + 2 * tile_width > editor_width:
                        x = 0
                        y += tile_height
                    else:
                        x += tile_width

                    window.blit(tile, (x, y))
                
                x = (editor_width - kinds[current_kind].w) // 2
                y += 2 * tile_height
                window.blit(kinds[current_kind].image, (x, y))

                x = 0
                y += 2 * tile_height
                for kind in kinds:
                    window.blit(kind.image, (x, y))

                    if x + 3 * tile_width > editor_width:
                        x = 0
                        y += 2 * tile_height
                    else:
                        x += 2 * tile_width

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

            elif event.key == pygame.K_F2 and editing:
                x, y = pygame.mouse.get_pos()

                if x > editor_width:
                    baddies.append(Baddie(kinds[current_kind], (x + camera.x - editor_width) // tile_width * tile_width, (y + camera.y) // tile_height * tile_height, True))

            elif event.key == pygame.K_LCTRL:
                if player.right:
                    offset = 48
                    decals.append(Decal(10, player.x+48, player.y, rpunch))
                else:
                    decals.append(Decal(10, player.x-48, player.y, lpunch))
                    offset = -48-player.w

                for x in (player.x + player.w - 1+offset) // tile_width - 1, (player.x + player.w+offset) // tile_width:
                    for y in range(int(player.y // tile_height), int((player.y + player.h) // tile_height + 1)):
                        for baddie in baddies:
                            if baddie.y // tile_height == y and x in range(baddie.x // tile_width,
                                    (baddie.x + baddie.w) // tile_width) and not baddie.dead:
                                baddie.dead = True

            elif event.key == 27:
                break

            if editing:
                if event.key == pygame.K_END:
                    for row in tilemap:
                        row.append(0)

                    level_width = len(tilemap[0]) * tile_width

                elif event.key == pygame.K_HOME:
                    for row in tilemap:
                        row.pop()

                    level_width = len(tilemap[0]) * tile_width

                elif event.key == pygame.K_PAGEUP:
                    tilemap.insert(0, [0 for i in range(len(tilemap[0]))])
                    level_height = len(tilemap) * tile_width
                    player.y += tile_height
                    for baddie in baddies:
                        baddie.y += tile_height

                elif event.key == pygame.K_PAGEDOWN:
                    tilemap.pop(0)
                    level_height = len(tilemap) * tile_width
                    player.y -= tile_height
                    for baddie in baddies:
                        baddie.y -= tile_height

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
                x = int(event.pos[0] - editor_width + camera.x) // tile_width
                y = int(event.pos[1] + camera.y) // tile_height

                if event.button == 1:
                    for baddie in baddies:
                        if x == baddie.x // tile_width and y == baddie.y // tile_height:
                            current_baddie = baddie
                            break

                    else:
                        tilemap[y][x] = current_tiles[0]

                elif event.button == 2:
                    for baddie in baddies:
                        if x == baddie.x // tile_width and y == baddie.y // tile_height:
                            if baddie.vx > 0:
                                baddie.vx = -baddie.speed
                                baddie.image = baddie.limage
                            else:
                                baddie.vx = +baddie.speed
                                baddie.image = baddie.rimage

                elif event.button == 3:
                    for baddie in baddies:
                        if x == baddie.x // tile_width and y == baddie.y // tile_height:
                            current_baddie = baddie
                            baddies.remove(baddie)
                            break

                    else:
                        tilemap[y][x] = current_tiles[1]

            else:
                x, y = 0, 2 * tile_height
                for i in range(len(tiles)):
                    if event.pos[0] in range(x, x + tile_width) and event.pos[1] in range(y, y + tile_height):
                        if event.button == 1:
                            current_tiles[0] = i
                        elif event.button == 3:
                            current_tiles[1] = i

                        break

                    if x + 2 * tile_width > editor_width:
                        x = 0
                        y += tile_height
                    else:
                        x += tile_width

                x = 0
                y += 4 * tile_height
                for i in range(len(kinds)):
                    if event.pos[0] in range(x, x + 2 * tile_width) and event.pos[1] in range(y, y +  2 * tile_height):
                        current_kind = i

                    if x + 3 * tile_width > editor_width:
                        x = 0
                        y += 2 * tile_height
                    else:
                        x += 2 * tile_width

        elif editing and event.type == pygame.MOUSEBUTTONUP:
            current_baddie = None

        elif editing and event.type == pygame.MOUSEMOTION:
            if event.pos[0] > editor_width:
                x = int(event.pos[0] - editor_width + camera.x) // tile_width
                y = int(event.pos[1] + camera.y) // tile_height
                if event.buttons[0]:
                    if current_baddie:
                        current_baddie.x = x * tile_width
                        current_baddie.y = y * tile_height
                    else:
                        tilemap[y][x] = current_tiles[0]

                elif event.buttons[2]:
                    tilemap[y][x] = current_tiles[1]

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
                "mountains_1.png", "clouds_1.png",
                "mountains_2.png", "clouds_2.png",
                "mountains_3.png", "clouds_3.png",
                None, None, "heaven.png"]

        tilemap = []
        for i in range(14):
            tilemap.append([0 for i in range(3 * window_width // tile_width)])
        tilemap.append([2 for i in range(3 * window_width // tile_width)])

        spikytiles = [4, 5]

        baddies = []

        level = layernames, tilemap, spikytiles, baddies

    # Short buffer for low latency.
    try:
        pygame.mixer.pre_init(buffer=512)
    except:
        pass

    pygame.init()
    pygame.time.set_timer(pygame.VIDEOEXPOSE, 1000 / framerate)
    window = pygame.display.set_mode((window_width, window_height))

    tiles = load_tiles(tiles_path)
    play(level, window, tiles, editing=editing)

    if editing:
        f = open(level_filename, "w")
        f.write(repr(level))
        f.close()

if __name__ == "__main__":
    main()
