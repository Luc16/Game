import pygame as pg
from dialog_box import DialogBox


class Tile:

    def __init__(self, screen_width, screen_height, grid, pos, color=(200, 200, 200)):
        self.rect = pg.Rect(pos, (screen_height / grid, screen_height / grid))
        self.color = color
        self.type = 0

    def get_type(self):
        return self.type

    def update_pos(self, movement):
        self.rect.y -= movement

    def update_color(self, color):
        self.color = color

    def update_type(self, color, type_num):
        self.color = color
        self.type = type_num

    def draw(self, screen, is_selected=False):
        edge = 2
        if is_selected:
            pg.draw.rect(screen, (0, 0, 0), self.rect)
            pg.draw.rect(screen, self.color,
                         (self.rect.x + edge, self.rect.y + edge, self.rect.width - 2 * edge,
                          self.rect.height - 2 * edge))
            return
        pg.draw.rect(screen, (0, 0, 0), self.rect)
        pg.draw.rect(screen, self.color,
                     (self.rect.x + edge, self.rect.y + edge, self.rect.width - 2 * edge, self.rect.height - 2 * edge))


class TileEditor:

    def __init__(self):
        self.running = True
        self.width, self.height = 1500, 1000
        self.screen = pg.display.set_mode((self.width, self.height))
        self.dialog_box = DialogBox(self.width, self.height, "Grid size (divisible by " + str(self.width) + ")")
        self.grid = 20
        self.types = [[(200, 200, 200), (150, 150, 150)],
                      [(255, 0, 0), (180, 0, 0)],
                      [(0, 0, 255), (0, 0, 180)]]
        self.square_side = 0
        self.sample_tiles = []
        self.filled_tiles = []
        self.selected_type = 0
        self.scrolling_down = False
        self.scrolling_up = False
        self.clicked = False
        self.on_screen = [0, 0]
        self.scroll = 0
        self.pos_mouse_var = (0, 0)
        self.num_tiles = 0
        self.max_scroll = 0
        self.tiles = []

    def run(self):
        self.dialog_box.run(self.screen)
        self.end_box()
        while self.running:
            pg.time.Clock().tick(60)
            self.handle_events()
            self.scroll_screen()
            self.draw()

    def end_box(self):
        answer = self.dialog_box.get_answers([int])[0]
        if answer is not None:
            self.grid = answer
        self.square_side = self.height / self.grid
        self.sample_tiles = [Tile(self.width, self.height, self.grid,
                                  ((idx + 1) * self.width / (len(self.types) + 1) - self.square_side / 2,
                                   self.height - self.square_side), color=typ[0])
                             for idx, typ in enumerate(self.types)]
        self.tiles = [[Tile(self.width, self.height, self.grid, (i * self.square_side, j * self.square_side))
                       for i in range(int(self.width/self.square_side))]
                      for j in range(self.grid - 1)]
        self.on_screen[1] = self.grid - 1
        self.max_scroll = self.on_screen[1]

    def create_new_line(self):
        self.tiles.append([Tile(self.width, self.height,
                                self.grid, (i * self.square_side, (self.grid - 1) * self.square_side))
                           for i in range(int(self.width/self.square_side))])

    def scroll_screen(self):
        if self.scroll >= self.square_side or self.scroll <= -self.square_side:
            self.on_screen[0] += int(self.scroll/self.square_side)
            self.on_screen[1] += int(self.scroll/self.square_side)
            if self.on_screen[1] > self.max_scroll:
                self.max_scroll = self.on_screen[1]
                self.create_new_line()
            for line in self.tiles:
                for tile in line:
                    tile.update_pos(self.scroll)
            self.scroll = 0
        if self.scrolling_down:
            self.scroll += self.square_side / 5
        elif self.scrolling_up:
            if self.on_screen[0] > 0:
                self.scroll -= self.square_side / 5

    def handle_mouse_click(self, event):
        self.clicked = True
        sample_pressed = False
        for idx, tile in enumerate(self.sample_tiles):
            if tile.rect.collidepoint(event.pos):
                self.selected_type = idx
                tile.update_color(self.types[idx][1])
                sample_pressed = True
        if sample_pressed:
            for idx, tile in enumerate(self.sample_tiles):
                if idx != self.selected_type:
                    tile.update_color(self.types[idx][0])
        for line in self.tiles:
            for tile in line:
                if tile.rect.collidepoint(event.pos):
                    tile.update_type(self.types[self.selected_type][0], self.selected_type)
                    self.filled_tiles.append(tile)

    def handle_mouse_up(self):
        self.clicked = False

    def handle_mouse_motion(self, event):
        if self.clicked:
            for line in self.tiles:
                for tile in line:
                    if tile.rect.collidepoint(event.pos):
                        tile.update_type(self.types[self.selected_type][0], self.selected_type)
                        self.filled_tiles.append(tile)

    def handle_scroll(self, event):
        if event.key == pg.K_DOWN:
            if self.scrolling_down:
                self.scroll = self.height / self.grid
            self.scrolling_down = not self.scrolling_down
        if event.key == pg.K_UP:
            if self.scrolling_up:
                if self.on_screen[0] > 0:
                    self.scroll = -self.height / self.grid
            self.scrolling_up = not self.scrolling_up

    def erase_all(self):
        for idx, line in enumerate(self.tiles):
            for tile in line:
                tile.update_type(self.types[0][0], 0)
                self.filled_tiles = []

    def save_to_file(self):
        file_name = DialogBox(self.width, self.height, "File name").run_and_return_answers(self.screen, [str])[0]
        file = open(file_name+".txt", 'w')
        for idx, line in enumerate(self.tiles):
            for tile in line:
                file.write(str(tile.get_type()))
            file.write('\n')
        self.running = False

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            elif event.type == pg.KEYDOWN:
                self.handle_scroll(event)
                if event.key == pg.K_r:
                    self.erase_all()
                if event.key == pg.K_RETURN:
                    self.save_to_file()
            elif event.type == pg.KEYUP:
                self.handle_scroll(event)
            if event.type == pg.MOUSEMOTION:
                self.handle_mouse_motion(event)
            if event.type == pg.MOUSEBUTTONDOWN:
                self.handle_mouse_click(event)
            if event.type == pg.MOUSEBUTTONUP:
                self.handle_mouse_up()

    def draw_grid(self):
        for line in self.tiles[self.on_screen[0]: self.on_screen[1]]:
            for tile in line:
                tile.draw(self.screen)

    def draw_tile_menu(self):
        for tile in self.sample_tiles:
            tile.draw(self.screen)

    def draw(self):
        self.screen.fill((200, 200, 200))
        self.draw_grid()
        self.draw_tile_menu()
        pg.display.flip()


if __name__ == '__main__':
    pg.init()
    TileEditor().run()
    pg.quit()
