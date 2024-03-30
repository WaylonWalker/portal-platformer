from portal_platformer.game import Game
import sys


def main():
    if "--debug" in sys.argv:
        game = Game(debug=True)
    else:
        game = Game()
    game.run()
