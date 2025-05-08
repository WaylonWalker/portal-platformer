from pydantic import BaseModel
from typing import TYPE_CHECKING, List, Any

if TYPE_CHECKING:
    from typing import List


class MenuItem(BaseModel):
    text: str
    game: Any

    @property
    def height(self):
        return self.game.font.size(self.text)[1]


class Menu(BaseModel):
    items: List[MenuItem]
    game: Any
    selected: int = 0

    def move_down(self):
        self.selected = (self.selected + 1) % len(self.items)

    def move_up(self):
        self.selected = (self.selected - 1) % len(self.items)

    @property
    def height(self):
        return sum([item.height for item in self.items])

    @property
    def width(self):
        return max([len(item.text) for item in self.items])

    def draw(self):
        y = (self.game.screen.get_height() - self.height) // 2
        x = (self.game.screen.get_width() - self.width) // 2

        for i, item in enumerate(self.items):
            if i == self.selected:
                color = "red"
            else:
                color = "white"
            item_surf = self.game.font.render(item.text, True, color)
            self.game.screen.blit(item_surf, (x, y))
            y += item.height
