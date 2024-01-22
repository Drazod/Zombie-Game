import pygame
import random
from collections import namedtuple
import time

pygame.init()
font = pygame.font.Font('arial.ttf', 25)

Point = namedtuple('Point', 'x, y')

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

clock = pygame.mixer.Sound('./music/clock-ticking-60-second-countdown-118231.mp3')
halloween = pygame.mixer.Sound('./music/organ-interrupt-brolefilmer-122454.mp3')
gameover = pygame.mixer.Sound('./music/violin-lose-1-175615.mp3')
hit = pygame.mixer.Sound('./music/hq-explosion-6288.mp3')
hit.set_volume(0.3)
BLOCK_SIZE = 20
SPEED = 20
last_count = pygame.time.get_ticks()
zombie_image = pygame.image.load('zombie_stand.png')
zombie_rect = zombie_image.get_rect()

class SnakeGame:
    def __init__(self, w=640, h=480):
        self.w = w
        self.h = h
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Zombie')
        self.clock = pygame.time.Clock()
        self.gameover = False
        self.starter = False
        self.zombies = []
        self.zombie_speed = 8
        self.zombie_direction = random.choice(['up', 'down', 'left', 'right'])
        self.hit = 0
        self.miss = 0
        self.zombie = None
        self.click = False
        self.click_Pos = (-1, -1)
        self.game_time = 60
        self.starter_time = 3
        self._load_resources()
        self._place_zombie()

    def _load_resources(self):
        self.background_image = pygame.image.load('grayard.png')

    def draw_text(self, text, font, text_col, x, y):
        img = font.render(text, True, text_col)
        self.display.blit(img, (x, y))

    def ClickZombie(self, clickable_area):
        if clickable_area.collidepoint(self.click_Pos):
            hit.play()
            return True

    def _place_zombie(self):
        x = random.randint(0, (self.w - zombie_rect.width) // zombie_rect.width) * zombie_rect.width
        y = random.randint(0, (self.h - zombie_rect.height) // zombie_rect.height) * zombie_rect.height
        self.zombie = pygame.Rect(x - zombie_rect.width / 2, y - zombie_rect.height / 2,
                                   zombie_rect.width, zombie_rect.height)
        self.zombies.append(self.zombie)

    def countdown(self):
        global last_count
        now = pygame.time.get_ticks()
        if now - last_count >= 1000:
            self.game_time -= 1
            last_count = now

    def play_step(self):
        clock.play(maxtime=3000)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w:
                        pygame.mixer.music.fadeout(1000)
                    if event.key == pygame.K_e:
                        pygame.mixer.music.play(-1)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.click = True
            if self.starter_time == 0:
                halloween.play(loops=-1,maxtime=1000*(self.game_time-1))
            if self.starter:
                if self.game_time > 0:
                    for zombie in self.zombies:
                        if self.zombie_direction == 'up':
                            zombie.y -= self.zombie_speed
                        elif self.zombie_direction == 'down':
                            zombie.y += self.zombie_speed
                        elif self.zombie_direction == 'left':
                            zombie.x -= self.zombie_speed
                        elif self.zombie_direction == 'right':
                            zombie.x += self.zombie_speed

                    if random.random() < 0.02:
                        self.zombie_direction = random.choice(['up', 'down', 'left', 'right'])

                    if self.zombie.x + BLOCK_SIZE < 0 or self.zombie.x > self.w or \
                       self.zombie.y + BLOCK_SIZE < 0 or self.zombie.y > self.h:
                        print("Zombie went out of bounds!")
                        self._place_zombie()

                    if self.click:
                        self.click_Pos = pygame.mouse.get_pos()
                        clickable_area = self._update_ui()
                        if self.ClickZombie(clickable_area):
                            print("Zombie clicked!")
                            self.hit += 1
                            self._place_zombie()
                        else:
                            print("Missed zombie!")
                            self.miss += 1
                            self._place_zombie()
                        self.click = False

                else:
                    self.gameover = True
                    self.draw_text("GAME OVER!", font, WHITE, int(self.w / 2 - 100), int(self.h / 2 + 50))
                self.countdown()
                if self.game_time == 0:
                    gameover.play(maxtime=3000)
            self._update_ui()
            self.clock.tick(SPEED)

    def _update_ui(self):
        self.display.blit(self.background_image, (0, 0))
        self.starter_time -= 1
        if not self.starter:
            self.draw_text("Game starts in " + str(self.starter_time), font, WHITE, int(self.w / 2 - 100), int(self.h / 2))
            pygame.display.flip()
            time.sleep(1)
            if self.starter_time == 0:
                self.starter = True
        else:
            if not self.gameover:
                zombie_rect.center = (self.zombie.x, self.zombie.y)
                self.display.blit(zombie_image, zombie_rect)
                clickable_area = pygame.Rect(self.zombie.x - zombie_rect.width / 2, self.zombie.y - zombie_rect.height / 2,
                                             zombie_rect.width, zombie_rect.height)

                self.draw_text("Score: " + str(self.hit) + '-' + str(self.miss), font, WHITE, 0, 0)
                self.draw_text("Time: " + str(self.game_time), font, WHITE, self.w - 100, 0)
                pygame.display.flip()
                return clickable_area
            else:
                self.draw_text("GAME OVER!", font, WHITE, int(self.w / 2 - 75), int(self.h / 2))
                pygame.display.flip()


if __name__ == '__main__':
    game = SnakeGame()
    game_over, score = game.play_step()
    pygame.quit()
