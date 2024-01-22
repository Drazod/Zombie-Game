import pygame
import random
from collections import namedtuple
import time
import math

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
pygame.transform.scale(zombie_image, (20,20))
zombie_rect = zombie_image.get_rect()

target = pygame.image.load('target.png')
pygame.transform.scale(target, (5, 5))
pygame.Surface.set_colorkey(target, [255, 255, 255])
print(target)

class Zombie:
    def __init__(self, screen_width, screen_height):
        self.image = zombie_image
        self.rect = self.image.get_rect()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.reset()

    def reset(self):
        self.alive = True
        self.rect.x = random.randint(0, self.screen_width - self.rect.width)
        self.rect.y = random.randint(0, self.screen_height - self.rect.height)
        self.target_corner = random.choice([(0, 0), (self.screen_width, 0), (0, self.screen_height),
                                            (self.screen_width, self.screen_height)])

    def move(self, speed):
        if self.alive:
            angle = math.atan2(self.target_corner[1] - self.rect.centery, self.target_corner[0] - self.rect.centerx)
            dx = speed * math.cos(angle)
            dy = speed * math.sin(angle)
            self.rect.x += dx
            self.rect.y += dy

            if (
                (dx > 0 and self.rect.x > self.target_corner[0])
                or (dx < 0 and self.rect.x < self.target_corner[0])
                or (dy > 0 and self.rect.y > self.target_corner[1])
                or (dy < 0 and self.rect.y < self.target_corner[1])
            ):
                self.reset()

class SnakeGame:
    def __init__(self, w=640, h=480):
        self.w = w
        self.h = h
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Zombie')
        self.clock = pygame.time.Clock()
        self.mouse_position = pygame.mouse.get_pos()
        self.gameover = False
        self.starter = False
        self.zombies = []
        self.zombie_speed = 5
        self.hit = 0
        self.miss = 0
        self.click = False
        self.click_Pos = (-1, -1)
        self.game_time = 60
        self.starter_time = 3
        self.spawn_interval = 2000  # Spawn a new zombie every 5 seconds
        self.last_spawn_time = pygame.time.get_ticks()
        self._load_resources()

    def _load_resources(self):
        self.background_image = pygame.image.load('grayard.png')

    def draw_text(self, text, font, text_col, x, y):
        img = font.render(text, True, text_col)
        self.display.blit(img, (x, y))

    def ClickZombie(self, zombies):
        for zombie in zombies:
            if zombie.alive and zombie.rect.collidepoint(self.click_Pos):
                hit.play()
                zombie.alive = False
                return True
        return False

    def _place_zombie(self):
        now = pygame.time.get_ticks()
        if now - self.last_spawn_time >= self.spawn_interval:
            new_zombie = Zombie(self.w, self.h)
            self.zombies.append(new_zombie)
            self.last_spawn_time = now

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
                halloween.play(loops=-1, maxtime=1000 * (self.game_time - 1))

            if self.starter:
                if self.game_time > 0:
                    pygame.mouse.set_visible(False)
                    self.mouse_position = pygame.mouse.get_pos()
                    self._place_zombie()

                    for zombie in self.zombies:
                        zombie.move(self.zombie_speed)

                    if self.click:
                        self.click_Pos = pygame.mouse.get_pos()
                        if not self.ClickZombie(self.zombies):
                            print("Missed zombie!")
                            self.miss += 1
                        else:
                            self.hit +=1
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
            self.draw_text("Game starts in " + str(self.starter_time), font, WHITE, int(self.w / 2 - 100),
                           int(self.h / 2))
            pygame.display.flip()
            time.sleep(1)
            if self.starter_time == 0:
                self.starter = True
        else:
            if not self.gameover:
                for zombie in self.zombies:
                    if zombie.alive:
                        self.display.blit(zombie.image, zombie.rect)
                self.draw_text("Score: " + str(self.hit) + '-' + str(self.miss), font, WHITE, 0, 0)
                self.draw_text("Time: " + str(self.game_time), font, WHITE, self.w - 100, 0)
                self.display.blit(target, (self.mouse_position[0] - 40, self.mouse_position[1] - 40))
                pygame.display.flip()
            else:
                self.draw_text("GAME OVER!", font, WHITE, int(self.w / 2 - 75), int(self.h / 2))
                pygame.display.flip()


if __name__ == '__main__':
    game = SnakeGame()
    game.play_step()
    pygame.quit()
