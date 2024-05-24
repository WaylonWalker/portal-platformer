import sys

from portal_platformer.game import Game


def main():
    # use argparse instead
    # args = {}
    # if "--debug" in sys.argv:
    #     args["debug"] = True
    # if "--fullscreen" in sys.argv:
    #     args["fullscreen"] = True

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--fullscreen", action="store_true")
    parser.add_argument("--width", type=int, default=1920)
    parser.add_argument("--height", type=int, default=1080)
    args = vars(parser.parse_args())

    game = Game(**args)
    game.run()
