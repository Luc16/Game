import pygame as pg


class Text:

    def __init__(self, text, x, y):
        self.title = text
        self.y = y
        self.x = x
        self.answer = ""
        self.text_color = (255, 255, 255)
        self.rect_color = pg.Color('gray15')
        self.rect = pg.Rect(x, y, 140, 32)
        self.activated = False


class DialogBox:
    
    def __init__(self, screen_width, screen_height, *argv):
        self.text_box = pg.Surface((500, 300))
        self.x, self.y = screen_width/2-self.text_box.get_width()/2, screen_height/2-self.text_box.get_height()/2
        self.font = pg.font.SysFont('Arial', 32)
        self.texts = []
        for idx, arg in enumerate(argv, 1):
            y_pos = self.y-16+idx*self.text_box.get_height()/(len(argv)+1) if len(argv) < 4 \
                else self.y-32+1.2*idx*self.text_box.get_height()/(len(argv)+1)
            self.texts.append(Text(arg,
                                   self.x+self.text_box.get_width()/4,
                                   y_pos))

    def run(self, screen, func=None, arg=None):
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return
                elif event.type == pg.MOUSEBUTTONDOWN:
                    self.handle_text_box_mouse(event)
                elif event.type == pg.KEYDOWN:
                    if self.handle_text_box_return(event):
                        if func is not None:
                            return func(arg)
                        return
                    self.handle_text_box_text(event)
            self.draw_text_box(screen)

    def get_answers(self, var_types):
        answers = []
        for idx, text in enumerate(self.texts):
            if var_types[idx] == str:
                answers.append(text.answer)
            else:
                try:
                    v = var_types[idx](text.answer)
                    answers.append(v)
                except ValueError:
                    pass
        if answers:
            return answers
        return [None]

    def run_and_return_answers(self, screen, var_types):
        return self.run(screen, func=self.get_answers, arg=var_types)

    def handle_text_box_mouse(self, event):
        for idx, text in enumerate(self.texts):
            if text.rect.collidepoint(event.pos):
                text.rect_color = pg.Color('lightskyblue3')
                text.activated = True
            else:
                text.activated = False
                text.rect_color = pg.Color('gray15')

    def handle_text_box_text(self, event):
        for text in self.texts:
            if text.activated:
                if event.key == pg.K_BACKSPACE:
                    text.answer = text.answer[:-1]
                else:
                    text.answer += event.unicode

    @staticmethod
    def handle_text_box_return(event):
        if event.key == pg.K_RETURN:
            return True
        return False

    def draw_text_box(self, screen):
        screen.fill((200, 200, 200))
        self.text_box.fill((20, 20, 20))
        screen.blit(self.text_box, (self.x, self.y))
        for idx, text in enumerate(self.texts):
            screen.blit(self.font.render(text.title+':', True, text.text_color), (text.x-50, text.y-34))
            txt = self.font.render(text.answer, True, (255, 255, 255))
            text.rect.width = max(txt.get_width(), 140)
            pg.draw.rect(screen, text.rect_color, text.rect, 2)
            screen.blit(txt, (text.rect.x + 2, text.rect.y + 2))
        pg.display.flip()


if __name__ == '__main__':
    running = True
    pg.init()
    display = pg.display.set_mode((1000, 1000))
    box = DialogBox(1000, 1000, "title 1", "title 2")
    box.run(display)
    print(box.get_answers([int, int]))
    pg.quit()
