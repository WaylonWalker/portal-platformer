import sys

from portal_platformer.game import Game


def main():
    args = {}
    if "--debug" in sys.argv:
        args["debug"] = True
    if "--fullscreen" in sys.argv:
        args["fullscreen"] = True

    game = Game(**args)
    game.run()
