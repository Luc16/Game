import pygame as pg


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
        self.grid = 10
        self.sample_tile = Tile(self.width, self.height, self.grid)
        self.created = False
        self.pos_mouse_var = (0, 0)
        self.selected_tile = None
        self.num_tiles = 0
        self.tiles = []

    def run(self):
        while self.running:
            self.handle_events()
            self.draw()

    def run_actions(self):
        for tile in self.tiles:
            tile.update()

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

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            if event.type == pg.MOUSEMOTION:
                self.update_tile_pos(event)
            if event.type == pg.MOUSEBUTTONDOWN:
                self.handle_mouse_click(event)
            if event.type == pg.MOUSEBUTTONUP:
                self.handle_mouse_up()

    def draw_grid(self):
        for dot in range(self.grid):
            pg.draw.line(self.screen, (0, 0, 0), (dot*self.width/self.grid, 0),
                         (dot*self.width/self.grid, self.height))
            pg.draw.line(self.screen, (0, 0, 0), (0, dot * self.height / self.grid),
                         (self.width, dot * self.height / self.grid))

    def draw(self):
        self.screen.fill((200, 200, 200))
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
