import pygame as pg
from dialog_box import DialogBox


class Tile:

    def __init__(self, screen_width, screen_height, grid, idx=None):
        self.rect = pg.Rect(screen_width*0.1, screen_height*0.8, screen_width/grid, screen_height/grid)
        self.idx = idx

    def draw(self, screen, is_selected=False):
        edge = 2
        if is_selected:
            pg.draw.rect(screen, (0, 0, 0), self.rect)
            pg.draw.rect(screen, (180, 0, 0),
                         (self.rect.x + edge, self.rect.y + edge, self.rect.width - 2*edge, self.rect.height - 2*edge))
            return
        pg.draw.rect(screen, (0, 0, 0), self.rect)
        pg.draw.rect(screen, (255, 0, 0),
                     (self.rect.x + edge, self.rect.y + edge, self.rect.width - 2*edge, self.rect.height - 2*edge))


class TileEditor:

    def __init__(self):
        self.running = True
        self.width, self.height = 1000, 1000
        self.screen = pg.display.set_mode((self.width, self.height))
        self.dialog_box = DialogBox(self.width, self.height, "Grid size (divisible by "+str(self.width)+")")
        self.grid = 20
        self.scrolling_down = False
        self.scrolling_up = False
        self.scroll = 0
        self.sample_tile = None
        self.created = False
        self.pos_mouse_var = (0, 0)
        self.selected_tile = None
        self.num_tiles = 0
        self.tiles = []
        self.max_scroll = 0

    def run(self):
        while self.running:
            pg.time.Clock().tick(60)
            self.handle_events()
            self.run_actions()
            self.draw()

    def run_actions(self):
        square_side = self.height/self.grid
        if self.scroll >= square_side or self.scroll <= -square_side:
            self.max_scroll += self.scroll
            if self.max_scroll > 0:
                self.max_scroll = 0
            else:
                for idx, tile in enumerate(self.tiles):
                    if idx != self.selected_tile:
                        tile.rect.y -= self.scroll
            self.scroll = 0
            print(self.max_scroll)
        if self.scrolling_down:
            self.scroll += square_side/10
        elif self.scrolling_up:
            self.scroll -= square_side/10

    def update_tile_pos(self, event):
        self.pos_mouse_var = [-self.pos_mouse_var[x] + event.pos[x] for x in range(2)]
        if self.selected_tile is not None:
            tile = self.tiles[self.selected_tile]
            tile.rect.x += self.pos_mouse_var[0]
            tile.rect.y += self.pos_mouse_var[1]
        self.pos_mouse_var = event.pos

    def fit_to_grid(self, tile_axis):
        square_size = self.width / self.grid
        margin = tile_axis % square_size
        if margin != 0:
            if margin > square_size / 2:
                return square_size - margin
            else:
                return -margin
        return 0

    def colliding_with_other_tiles(self):
        for tile in self.tiles:
            if tile != self.tiles[self.selected_tile]:
                if self.tiles[self.selected_tile].rect.colliderect(tile.rect):
                    return True
        return False

    def handle_mouse_click(self, event):
        if self.sample_tile.rect.collidepoint(event.pos) and not self.created:
            self.sample_tile.selected = True
            self.created = True
            self.tiles.append(Tile(self.width, self.height, self.grid, self.num_tiles))
            self.num_tiles += 1
        if self.selected_tile is None:
            for tile in self.tiles:
                if tile.rect.collidepoint(event.pos):
                    self.selected_tile = tile.idx

    def handle_mouse_up(self):
        self.sample_tile.selected = False
        self.created = False
        if self.selected_tile is not None:
            tile = self.tiles[self.selected_tile]
            tile.rect.x += self.fit_to_grid(tile.rect.x)
            tile.rect.y += self.fit_to_grid(tile.rect.y)
            if not self.colliding_with_other_tiles():
                if tile.rect.colliderect(self.sample_tile.rect):
                    del self.tiles[self.selected_tile]
                    self.num_tiles -= 1
                self.selected_tile = None

    def text_box_end(self, event):
        grid = self.dialog_box.handle_text_box_return(event)
        if grid[0] is not None:
            try:
                self.grid = int(grid[0])
            except ValueError:
                pass
            self.sample_tile = Tile(self.width, self.height, self.grid)

    def handle_scroll(self, event):
        if event.key == pg.K_DOWN:
            if self.scrolling_down:
                self.scroll = self.height / self.grid
            self.scrolling_down = not self.scrolling_down
        if event.key == pg.K_UP:
            if self.scrolling_up:
                self.scroll = -self.height / self.grid
            self.scrolling_up = not self.scrolling_up

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            elif event.type == pg.KEYDOWN:
                if self.dialog_box.active:
                    self.dialog_box.handle_text_box_text(event)
                    self.text_box_end(event)
                else:
                    if not self.dialog_box.active:
                        self.handle_scroll(event)
            elif event.type == pg.KEYUP:
                self.handle_scroll(event)
            if event.type == pg.MOUSEMOTION:
                self.update_tile_pos(event)
            if event.type == pg.MOUSEBUTTONDOWN:
                if self.dialog_box.active:
                    self.dialog_box.handle_text_box_mouse(event)
                else:
                    self.handle_mouse_click(event)
            if event.type == pg.MOUSEBUTTONUP:
                if not self.dialog_box.active:
                    self.handle_mouse_up()

    def draw_grid(self):
        for dot in range(-1, self.grid + 1):
            pg.draw.line(self.screen, (0, 0, 0),
                         (dot*self.width/self.grid, 0),
                         (dot*self.width/self.grid, self.height))
            pg.draw.line(self.screen, (0, 0, 0),
                         (0, dot * self.height/self.grid),
                         (self.width, dot * self.height/self.grid))

    def draw(self):
        self.screen.fill((200, 200, 200))
        if self.dialog_box.active:
            self.dialog_box.draw_text_box(self.screen)
        else:
            self.draw_grid()
            self.sample_tile.draw(self.screen)
            for idx, tile in enumerate(self.tiles):
                if idx != self.selected_tile:
                    tile.draw(self.screen)
            if self.selected_tile is not None:
                self.tiles[self.selected_tile].draw(self.screen, True)
        pg.display.flip()


if __name__ == '__main__':
    pg.init()
    TileEditor().run()
    pg.quit()
