from pydantic import BaseModel
import pygame
from typing import TYPE_CHECKING, List, Any

if TYPE_CHECKING:
    from typing import List


class MenuItem(BaseModel):
    text: str
    game: Any
    action: Any
    margin_bottom: int = 0

    @property
    def height(self):
        return self.game.font.size(self.text)[1] + self.margin_bottom

    # def action(self):
    #     print("action")
    #     pass


class Menu(BaseModel):
    items: List[MenuItem]
    game: Any
    selected: int = 0
    selected_color: str = "red"

    def move_down(self):
        self.selected = (self.selected + 1) % len(self.items)
        if self.items[self.selected].action is None:
            self.move_down()

    def move_up(self):
        self.selected = (self.selected - 1) % len(self.items)
        if self.items[self.selected].action is None:
            self.move_up()

    @property
    def height(self):
        return sum([item.height for item in self.items])

    @property
    def width(self):
        return max([len(item.text) for item in self.items])

    def select(self):
        print("taking action")
        self.selected_color = "blue"
        self.draw()
        pygame.display.flip()
        self.items[self.selected].action()
        self.selected_color = "red"

    def draw(self):
        y = (self.game.screen.get_height() - self.height) // 2
        x = (self.game.screen.get_width() - self.width) // 2
        if self.items[self.selected].action is None:
            self.move_down()

        for i, item in enumerate(self.items):
            if i == self.selected:
                color = self.selected_color
            else:
                color = "white"
            item_surf = self.game.font.render(item.text, True, color)
            self.game.screen.blit(item_surf, (x, y))
            y += item.height
