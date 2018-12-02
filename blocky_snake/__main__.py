# -*- coding: utf-8 -*-

import time as _time
import contextlib as _ctx

import curses as _curses


class GameOver(Exception):
    pass


# milliseconds
render_interval = 16 / 1000.0
update_interval = 100 / 1000.0


world = {
    "moving_direction": "R",
    "window": {"height": 10, "width": 20, "x": 0, "y": 0},
    "cherry": {"pos": (10, 10)},
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
        pass

    def render(self, window, world):
        pass

    def update(self, world):
        pass


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

    def update(self, world):
        md = world["moving_direction"]
        last_pos = None
        for idx, part in enumerate(self.body):
            if idx == 0:
                last_pos = part
                if md == "D":
                    if part[0] < world["window"]["height"]:
                        self.body[0] = part[0] + 1, part[1]
                    else:
                        raise GameOver("Game Over")
                elif md == "U":
                    if part[0] > 1:
                        self.body[0] = part[0] - 1, part[1]
                    else:
                        raise GameOver("Game Over")
                elif md == "R":
                    if part[1] < world["window"]["width"]:
                        self.body[0] = part[0], part[1] + 1
                    else:
                        raise GameOver("Game Over")
                elif md == "L":
                    if part[1] > 1:
                        self.body[0] = part[0], part[1] - 1
                    else:
                        raise GameOver("Game Over")
                continue

            y, x = part
            self.body[idx] = last_pos
            last_pos = y, x


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
    with init_display(wincfg["height"] + 2 , wincfg["width"] + 2, wincfg["y"], wincfg["x"]) as (
        screen,
        window,
    ):
        while True:
            char = screen.getch()
            if char == ord("q") or char == 27:  # escape
                screen.clear()
                screen.addstr(10, 10, "Game exitte")
                screen.refresh()
                _time.sleep(2)
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
                screen.addstr(10, 10, "Game Over")
                screen.refresh()
                _time.sleep(2)
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
            )
        ]
    )


if __name__ == "__main__":
    # print("foo")
    release_the_snaken()
