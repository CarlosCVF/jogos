from settings import *
from tetromino import Tetromino
import pygame.freetype as ft
import pygame as pg
import sqlite3

class Text:
    def __init__(self,app):
        self.app = app
        self.font = pg.font.Font(None, 80)
    def draw(self):
        text_surface = self.font.render('Tetris', True, pg.Color('white'))
        self.app.screen.blit(text_surface, (int(WIN_W * 0.595), int(WIN_H * 0.02)))

        text_surface = self.font.render('Next', True, pg.Color('white'))
        self.app.screen.blit(text_surface, (int(WIN_W * 0.595), int(WIN_H * 0.215)))

        text_surface = self.font.render('Score:', True, pg.Color('white'))
        self.app.screen.blit(text_surface, (int(WIN_W * 0.595), int(WIN_H * 0.64)))

        text_surface = self.font.render(f'{self.app.tetris.score}', True, pg.Color('white'))
        self.app.screen.blit(text_surface, (int(WIN_W * 0.595), int(WIN_H * 0.7)))
        
        text_surface = self.font.render('Score Max.', True, pg.Color('white'))
        self.app.screen.blit(text_surface, (int(WIN_W * 0.595), int(WIN_H * 0.8)))

        text_surface = self.font.render(f'{self.app.tetris.scoreMax}', True, pg.Color('white'))
        self.app.screen.blit(text_surface, (int(WIN_W * 0.595), int(WIN_H * 0.9)))
        

class Tetris:
    def __init__(self,app):
        self.app = app
        self.sprite_group = pg.sprite.Group()
        self.field_array = self.get_field_array()
        self.tetromino = Tetromino(self)
        self.next_tetromino = Tetromino(self,current=False)
        self.speed_up = False

        self.score = 0
        self.high_scores = []
        self.full_lines = 0
        self.points_per_lines = {0: 0, 1: 100, 2: 300, 3: 500, 4: 1000}
        self.points_threshold = 200  # Pontuação necessária para aumentar a velocidade
        self.speed_multiplier = 1000

    def update_score_max(self):
        conn = sqlite3.connect('Tetris.db')
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(score) FROM scores")
        self.scoreMax = cursor.fetchone()[0]
        cursor.close()

    def save_score(self,player_name):
        conn = sqlite3.connect('Tetris.db')
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS scores (name TEXT, score INTEGER)")
        cursor.execute("INSERT INTO scores VALUES (?, ?)", (player_name, self.score))
        conn.commit()
        cursor.close()

    def get_score(self):
        self.score += self.points_per_lines[self.full_lines]
        self.full_lines = 0
        if self.score >= self.points_threshold:  # Verifica se a pontuação atingiu o limite
            self.increase_speed()

    def increase_speed(self):
        ANIM_TIME_INTERVAL += self.speed_multiplier

    def check_full_lines(self):
        row = FIELD_H - 1
        for y in range(FIELD_H - 1, -1, -1):
            if sum(map(bool, self.field_array[y])) < FIELD_W:
                for x in range(FIELD_W):
                    self.field_array[row][x] = self.field_array[y][x]
                    if self.field_array[y][x]:
                        self.field_array[row][x].pos = vec(x, row)

                row -= 1
            else:
                for block in self.field_array[y]:
                    if block:
                        block.kill()
                        block.alive = False

                self.full_lines += 1

        for y in range(row, -1, -1):
            for x in range(FIELD_W):
                self.field_array[y][x] = None
    
    def put_tetromino_blocks_in_array(self):
        for block in self.tetromino.blocks:
            x,y = int(block.pos.x), int(block.pos.y)
            self.field_array[y][x] = block

    def get_field_array(self):
        return [[0 for x in range(FIELD_W)]for y in range(FIELD_H)]

    def is_game_over(self):
        if self.tetromino.blocks[0].pos.y == INIT_POS_OFFSET[1]:
            pg.time.wait(300)
            return True

    def check_tetromino_landing(self):
        if self.tetromino.landing:
            if self.is_game_over():
                player_name = self.app.get_player_name()
                self.save_score(player_name)
                self.__init__(self.app)
            else:
                self.speed_up = False
                self.put_tetromino_blocks_in_array()
                self.next_tetromino.current = True
                self.tetromino = self.next_tetromino
                self.next_tetromino = Tetromino(self, current=False)

    def control(self,pressed_key):
        if pressed_key == pg.K_LEFT:
            self.tetromino.move(direction='left')
        elif pressed_key == pg.K_RIGHT:
            self.tetromino.move(direction='right')
        elif pressed_key == pg.K_UP:
            self.tetromino.rotate()
        elif pressed_key == pg.K_DOWN:
            self.speed_up = True

    def release_key(self, released_key):
        if released_key == pg.K_DOWN:
            self.speed_up = False


    def draw_grid(self):
        for x in range(FIELD_W):
            for y in range(FIELD_H):
                pg.draw.rect(self.app.screen, 'black' ,(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE,TILE_SIZE),1)

    def update(self):
        trigger = [self.app.anim_trigger, self.app.fast_anim_trigger][self.speed_up]
        if trigger:
            self.check_full_lines()
            self.tetromino.update()
            self.check_tetromino_landing()
            self.get_score()
        self.sprite_group.update()

    def draw(self):
        self.draw_grid()
        self.sprite_group.draw(self.app.screen)