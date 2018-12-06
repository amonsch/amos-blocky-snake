# -*- coding: utf-8 -*-

import time as _time
import contextlib as _ctx
import random as _random
import curses as _curses


class GameOver(Exception):
    pass


# milliseconds
render_interval = 16 / 1000.0
update_interval = 100 / 1000.0


world = {
    "moving_direction": "R",
    "window": {"height": 30, "width": 60, "x": 0, "y": 0},
    "cherry": {"pos": None},
}


@_ctx.contextmanager
def init_display(height, width, y, x):
    screen = _curses.initscr()
    _curses.noecho()
    _curses.cbreak()
    _curses.curs_set(0)
    screen.nodelay(True)
    screen.keypad(True)
    window = _curses.newwin(height, width, y, x)
    yield screen, window
    _curses.endwin()


class Cherry:
    def __init__(self):
        self.pos = None

    def render(self, window, world):
        if self.pos:
            window.addstr(self.pos[0], self.pos[1], "X")

    def update(self, world):
        if not world["cherry"]["pos"]:
            w = world["window"]["width"]
            h = world["window"]["height"]
            self.pos = _random.randint(1, h - 1), _random.randint(1, w - 1)
            world["cherry"]["pos"] = self.pos


class Frame:
    def __init__(self, height, width, y, x):
        self.pos = x, y
        self.width = width
        self.height = height

    def render(self, window, world):
        for y in range(self.height + 1):
            window.addstr(y, 0, "#")
            window.addstr(y, self.width + 1, "#")

        for x in range(self.width + 1):
            window.addstr(0, x, "#")
            window.addstr(self.height + 1, x, "#")

    def update(self, world):
        pass


class Snake:
    def __init__(self):
        self.body = [(1, 3), (1, 2), (1, 1), (1, 0)]

    def render(self, window, world):
        for (idx, part) in enumerate(self.body):
            y, x = part
            if idx == 0:
                window.addstr(y, x, "o")
            else:
                window.addstr(y, x, "=")

    def _out_of_bounds_check(self, direction, world):
        head = self.body[0]
        if (
            head[0] > world["window"]["height"]
            or head[0] < 1
            or head[1] > world["window"]["width"]
            or head[1] < 1
        ):
            raise GameOver("Game Over")

    def _snake_bites_itself_check(self):
        if self.body[0] in self.body[1:]:
            raise GameOver("Game Over")

    def _invert_direction(self, current_direction):
        if current_direction == "U":
            direction = "D"
        elif current_direction == "D":
            direction = "U"
        elif current_direction == "R":
            direction = "L"
        elif current_direction == "L":
            direction = "R"
        return direction

    def update(self, world):
        md = world["moving_direction"]

        last_pos = None
        for idx, part in enumerate(self.body):
            if idx == 0:
                last_pos = part
                if md == "D":
                    self.body[0] = part[0] + 1, part[1]
                elif md == "U":
                    self.body[0] = part[0] - 1, part[1]
                elif md == "R":
                    self.body[0] = part[0], part[1] + 1
                elif md == "L":
                    self.body[0] = part[0], part[1] - 1
                self._out_of_bounds_check(md, world)

                if self.body[0] == self.body[1]:
                    self.body[0] = last_pos
                    world["moving_direction"] = self._invert_direction(md)
                    self.update(world)

                self._snake_bites_itself_check()
                continue

            y, x = part
            self.body[idx] = last_pos
            last_pos = y, x

        # Does the head has the same pos as the cherry?
        # if so, erase cherry pos in world and grow snake
        if self.body[0] == world["cherry"]["pos"]:
            self.body.append(last_pos)
            world["cherry"]["pos"] = None


def render(window, components):
    window.clear()
    for comp in components:
        comp.render(window, world)
    window.refresh()


def update(world, components):
    for comp in components:
        comp.update(world)


def game_loop(components):
    last_rendered = _time.time()
    last_updated = _time.time()

    wincfg = world["window"]
    with init_display(
        wincfg["height"] + 2, wincfg["width"] + 2, wincfg["y"], wincfg["x"]
    ) as (screen, window):
        while True:
            char = screen.getch()
            if char == ord("q") or char == 27:  # escape
                screen.clear()
                screen.addstr(
                    world["window"]["height"] // 2,
                    world["window"]["width"] // 2,
                    "Game exitted!",
                )
                screen.refresh()
                _time.sleep(1)
                break
            elif char == _curses.KEY_LEFT:
                world["moving_direction"] = "L"
            elif char == _curses.KEY_RIGHT:
                world["moving_direction"] = "R"
            elif char == _curses.KEY_UP:
                world["moving_direction"] = "U"
            elif char == _curses.KEY_DOWN:
                world["moving_direction"] = "D"

            if _time.time() >= (last_rendered + render_interval):
                render(window, components)
                last_rendered = _time.time()

            try:
                if _time.time() >= (last_updated + update_interval):
                    update(world, components)
                    last_updated = _time.time()
            except GameOver:
                screen.clear()
                screen.addstr(
                    world["window"]["height"] // 2,
                    world["window"]["width"] // 2,
                    "Game Over!",
                )
                screen.refresh()
                _time.sleep(1)
                break


def release_the_snaken():
    game_loop(
        [
            Snake(),
            Cherry(),
            Frame(
                world["window"]["height"],
                world["window"]["width"],
                world["window"]["y"],
                world["window"]["x"],
            ),
        ]
    )


if __name__ == "__main__":
    release_the_snaken()
