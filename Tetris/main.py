from settings import *
from tetris import Tetris, Text
import sys
import pathlib

class App:
    def __init__(self):
        pg.init()
        pg.display.set_caption('Tetris')
        self.screen = pg.display.set_mode(WIN_RES)
        self.clock = pg.time.Clock()
        self.set_timer()
        self.images = self.load_images()
        self.tetris = Tetris(self)
        self.text = Text(self)

    def load_images(self):
        files = [item for item in pathlib.Path(SPRITE_DIR_PATH).rglob('*.png')if item.is_file()]
        images = [pg.image.load(file).convert_alpha() for file in files]
        images = [pg.transform.scale(image,(TILE_SIZE, TILE_SIZE)) for image in images]
        return images

    def set_timer(self):
        self.user_event = pg.USEREVENT + 0
        self.fast_user_event = pg.USEREVENT + 1
        self.anim_trigger = False
        self.fast_anim_trigger = False
        pg.time.set_timer(self.user_event, ANIM_TIME_INTERVAL)
        pg.time.set_timer(self.fast_user_event, FAST_ANIM_TIME_INTERVAL)

    def update(self):
        self.tetris.update()
        self.clock.tick(FPS)

    def draw(self):
        self.screen.fill(color=BG_COLOR)
        self.screen.fill(color=FIELD_COLOR, rect=(0,0, *FIELD_RES))
        self.tetris.draw()
        self.text.draw()
        pg.display.flip()

    def check_events(self):
        self.anim_trigger = False
        self.fast_anim_trigger = False
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                pg.quit()
                sys.exit()
            elif event.type == pg.KEYDOWN or event.type == pg.KEYUP:
                if event.type == pg.KEYDOWN:
                    self.tetris.control(pressed_key=event.key)
                elif event.type == pg.KEYUP:
                    self.tetris.release_key(released_key=event.key)
            elif event.type == self.user_event:
                self.anim_trigger = True
            elif event.type == self.fast_user_event:
                self.fast_anim_trigger = True
    
    def get_player_name(self):
        font = pg.font.Font(None, 36)
        label_font = pg.font.Font(None, 30)
        input_box = pg.Rect(int(WIN_W * 0.4), int(WIN_H * 0.4), 200, 40)
        color_inactive = pg.Color('lightskyblue3')
        color = color_inactive
        player_name = ''
        active = True

        while active:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_RETURN:
                        active = False
                    elif event.key == pg.K_BACKSPACE:
                        player_name = player_name[:-1]
                    else:
                        player_name += event.unicode

            rect_Edge = pg.Rect(int(WIN_W * 0), int(WIN_H * 0.363), 850, 110)
            rect_back_text = pg.Rect(int(WIN_W * 0.4), int(WIN_H * 0.4), 200, 40)
            rect_back = pg.Rect(int(WIN_W * 0), int(WIN_H * 0.368), 850, 100)

            pg.draw.rect(self.screen, (0, 0, 0), rect_Edge)
            pg.draw.rect(self.screen, (150, 150, 150), rect_back)

            label_text = label_font.render("Digite seu nome:", True, pg.Color('white'))
            label_pos = (int(WIN_W * 0.4), int(WIN_H * 0.405) - 30)
            self.screen.blit(label_text, label_pos)
            txt_surface = font.render(player_name, True, color)
            width = max(200, txt_surface.get_width() + 10)
            input_box.w = width
            input_box.x = int(WIN_W * 0.3819) - (width - 200) // 2
            rect_back_text.w = width
            rect_back_text.x = int(WIN_W * 0.3819) - (width - 200) // 2

            pg.draw.rect(self.screen, (0, 0, 0), rect_back_text)
            self.screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
            pg.draw.rect(self.screen, color, input_box, 2)
            pg.display.flip()
            self.clock.tick(30)

        return player_name

    def run(self):
        while True:
            self.check_events()
            self.tetris.update_score_max()
            self.update()
            self.draw()

if __name__ == '__main__':
    app = App()
    app.run()

