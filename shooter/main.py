from random import randint
from pygame import *

lost = 0
number = 0
killed_monsters = 0
missed_monsters = 0

image_background = "galaxy.jpg"
image_hero = "rocket.png"
image_enemy = "ufo.png"
image_bullet = "bullet.png"
image_super_bullet = "superbullet.png"
image_restart = "restart.png"  # Added line

font.init()
font1 = font.Font(None, 36)

window_width = 700
window_height = 500

window = display.set_mode((window_width, window_height))
display.set_caption("Shooter")

FPS = 30
clock = time.Clock()

mixer.init()
mixer.music.load("space.ogg")
mixer.music.play()

background = transform.scale(image.load(image_background), (window_width, window_height))


class GameSprite(sprite.Sprite):
    def __init__(self, sprite_image, sprite_position_x, sprite_position_y, sprite_width, sprite_height, sprite_speed):
        super().__init__()
        self.image = transform.scale(image.load(sprite_image), (sprite_width, sprite_height))
        self.rect = self.image.get_rect()
        self.rect.x = sprite_position_x
        self.rect.y = sprite_position_y
        self.width = sprite_width
        self.height = sprite_height
        self.speed = sprite_speed

    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))


class Bullet(GameSprite):
    def update(self):
        self.rect.y -= self.speed
        if self.rect.y < 0:
            self.kill()


bullets = sprite.Group()


class SuperBullet(GameSprite):
    def update(self):
        self.rect.y -= self.speed
        if self.rect.y < 0:
            self.kill()


super_bullets = sprite.Group()


class Player(GameSprite):
    def __init__(self, sprite_image, sprite_position_x, sprite_position_y, sprite_width, sprite_height, sprite_speed,
                 super_bullet_cooldown):
        super().__init__(sprite_image, sprite_position_x, sprite_position_y, sprite_width, sprite_height, sprite_speed)
        self.super_bullet_cooldown = super_bullet_cooldown
        self.last_super_bullet_time = time.get_ticks()

    def update(self):
        keys = key.get_pressed()
        if keys[K_RIGHT] and self.rect.x < window_width - 100:
            self.rect.x += self.speed
        if keys[K_LEFT] and self.rect.x > 20:
            self.rect.x -= self.speed
        if keys[K_UP] and self.rect.y > window_height - 200:
            self.rect.y -= self.speed
        if keys[K_DOWN] and self.rect.y < window_height - 100:
            self.rect.y += self.speed
        if keys[K_SPACE]:
            self.fire()
        if keys[K_b]:
            self.fire_super_bullet()

    def fire(self):
        bullet = Bullet(image_bullet, self.rect.x + self.width // 2, self.rect.y, 10, 30, 15)
        bullets.add(bullet)

    def fire_super_bullet(self):
        current_time = time.get_ticks()
        if current_time - self.last_super_bullet_time >= self.super_bullet_cooldown:
            super_bullet = SuperBullet(image_super_bullet, self.rect.x + self.width // 2, self.rect.y, 20, 60, 10)
            super_bullets.add(super_bullet)
            self.last_super_bullet_time = current_time


player = Player(image_hero, window_width / 2, window_height - 100, 75, 75, 20, 5000)


class Enemy(GameSprite):
    def update(self):
        self.rect.y += self.speed
        global lost
        if self.rect.y > window_height:
            self.rect.x = randint(50, window_width - 80)
            self.rect.y = 0
            lost += 1


monsters = sprite.Group()

run = True
finish = False
bullet_cooldown = 500
monster_spawn_cooldown = 5000
last_monster_spawn_time = time.get_ticks()
bullet_delay = 500
last_bullet_time = time.get_ticks()

while run:
    current_time = time.get_ticks()

    for e in event.get():
        if e.type == QUIT:
            run = False

    if not finish:

        window.blit(background, (0, 0))
        text_win = font1.render("Рахунок: " + str(number), 1, (255, 255, 255))
        window.blit(text_win, (10, 20))
        text_lose = font1.render("Пропущено: " + str(lost), 1, (255, 255, 255))
        window.blit(text_lose, (10, 50))

        player.reset()
        monsters.draw(window)
        bullets.draw(window)
        super_bullets.draw(window)

        monsters.update()
        player.update()
        bullets.update()
        super_bullets.update()

        if bullet_cooldown <= 0:
            keys = key.get_pressed()
            if keys[K_SPACE]:
                if current_time - last_bullet_time >= bullet_delay:
                    player.fire()
                    last_bullet_time = current_time
            elif keys[K_b]:
                player.fire_super_bullet()

        if current_time - last_monster_spawn_time >= monster_spawn_cooldown:
            for i in range(5):
                monster = Enemy(image_enemy, randint(50, window_width - 80), 0, 60, 60, randint(1, 4))
                monsters.add(monster)
            last_monster_spawn_time = current_time

        hits_bullets = sprite.groupcollide(monsters, bullets, True, True)
        hits_super_bullets = sprite.groupcollide(monsters, super_bullets, True, True)
        number += len(hits_bullets) + len(hits_super_bullets)

        if hits_bullets or hits_super_bullets:
            killed_monsters += 1

        missed_monsters += lost
        lost = 0

        if sprite.spritecollide(player, monsters, True):
            finish = True
            lose_text = font1.render("Гра завершена. Корабель зіткнувся з монстром. Рахунок: " + str(number), 1, (255, 255, 255))
            window.blit(lose_text, (window_width // 2 - 300, window_height // 2 - 50))

        if killed_monsters >= 1000:
            finish = True
            win_text = font1.render("Ви перемогли! Рахунок: " + str(number), 1, (255, 255, 255))
            window.blit(win_text, (window_width // 2 - 150, window_height // 2 - 50))

        if missed_monsters >= 3:
            finish = True
            lose_text = font1.render("Гра завершена. Ви пропустили 3 монстрів. Рахунок: " + str(number), 1, (255, 255, 255))
            window.blit(lose_text, (window_width // 2 - 250, window_height // 2 - 50))
            print("Монстрів вбито:", killed_monsters)

        # Draw restart button
        restart_button = transform.scale(image.load(image_restart), (50, 50))
        window.blit(restart_button, (window_width - 70, 10))

        # Check if the restart button is clicked
        mouse_x, mouse_y = mouse.get_pos()
        mouse_click = mouse.get_pressed()

        if window_width - 70 <= mouse_x <= window_width - 20 and 10 <= mouse_y <= 60:
            if mouse_click[0] == 1 and finish:
                finish = False
                number = 0
                killed_monsters = 0
                missed_monsters = 0

        keys = key.get_pressed()
        if finish and keys[K_r]:
            finish = False
            number = 0
            killed_monsters = 0
            missed_monsters = 0

        display.update()
        clock.tick(FPS)

        bullet_cooldown -= clock.get_rawtime()
