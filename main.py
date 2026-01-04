import pygame
import math
import random

# Game setup
pygame.init()
pygame.mixer.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SPEED = 7
PLAYER_JUMP = -17
PLAYER_GRAVITY = 0.8
SHOOT_DELAY = 400
GRAVITY_PARTICLE = 0.2
BULLET_SPEED = 12
PLATFORM_SPEED_X = 2
PLATFORM_SPEED_Y = 4
COLOR_VICTORY = (50, 200, 50)
COLOR_GAME_OVER = (50, 0, 0)
VOL_SHOOT = 0.4
VOL_JUMP = 0.5
VOL_HIT = 0.6
VOL_COIN = 0.6
VOL_MUSIC = 0.2
MAP_LENGTH = 10000
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Sky wars version 1.67")
clock = pygame.time.Clock()
running = True


# All fonts and their sizes
title_font = pygame.font.SysFont("freesansbold.ttf", 80)
menu_font = pygame.font.SysFont("freesansbold.ttf", 40)
ui_font = pygame.font.SysFont("freesansbold.ttf", 24)
ammo_font = pygame.font.SysFont("freesansbold.ttf", 30)


def load_sound(name):
    """
    Loads a sound file
    and returns a pygame Sound object.
    """
    sound = pygame.mixer.Sound(name)
    return sound


# Sound effects
shoot_sound = load_sound("shoot.wav")
jump_sound = load_sound("jump.wav")
hit_sound = load_sound("hit.wav")
win_sound = load_sound("win.mp3")
lose_sound = load_sound("lose.mp3")
coin_sound = load_sound("coin.wav")
# Volume
shoot_sound.set_volume(VOL_SHOOT)
jump_sound.set_volume(VOL_JUMP)
hit_sound.set_volume(VOL_HIT)
coin_sound.set_volume(VOL_COIN)

# Music in game
pygame.mixer.music.load("music.mp3")
pygame.mixer.music.set_volume(VOL_MUSIC)
pygame.mixer.music.play(-1)


def load_image(name, scale_size=None):
    """
    Function to load all images
    and its size
    """
    image = pygame.image.load(name)
    image = image.convert_alpha()
    if scale_size:
        image = pygame.transform.scale(image, scale_size)
    return image


# Background image, flipped to make smooth transition
bg_img = load_image("background.png", (SCREEN_WIDTH, SCREEN_HEIGHT))
bg_img_flipped = pygame.transform.flip(bg_img, True, False)
bg_width = bg_img.get_width()
# All images for bullet, oponnents and hero
player_img = load_image("hero.png", (50, 60))
enemy_img = load_image("enemy.png", (50, 40))
fly_img = load_image("enemy2.png", (50, 40))
flag_img = load_image("flag.png", (50, 60))
platform_texture = load_image("pixel.png")
bullet_img = load_image("bullet.png", (60, 30))
coin_img = load_image("coin.png", (40, 40))

# Classes


class Particle(pygame.sprite.Sprite):
    """
    Class to make effect when collecting coins
    or killing enemies
    """
    def __init__(self, x, y, color):
        """
        Random size of every particle
        and random velocity
        """
        super().__init__()
        size = random.randint(3, 6)
        self.image = pygame.Surface((size, size))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))

        self.vx = random.uniform(-5, 5)
        self.vy = random.uniform(-5, 5)
        self.gravity = GRAVITY_PARTICLE  # To make particles fall down
        self.life = random.randint(20, 40)  # Random time for every particle

    def update(self):
        """
        This function controls how particles move
        """
        self.vx *= 0.95
        self.vy += self.gravity
        self.rect.x += self.vx
        self.rect.y += self.vy
        self.life -= 1
        if self.life <= 0:
            self.kill()


class Platform(pygame.sprite.Sprite):
    """
    Represents a static map element
    """
    def __init__(self, x, y, width, height):
        """
        Creating platform
        """
        super().__init__()
        self.image = pygame.transform.scale(platform_texture, (width, height))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class MovingPlatform_x(Platform):
    """
    Platoform moving horizontally
    """
    def __init__(self, x, y, width, height, range_dist=100, speed=PLATFORM_SPEED_X):
        """
        Function which define platform move
        """
        super().__init__(x, y, width, height)
        self.start_x = x
        self.range_dist = range_dist
        self.move_speed = speed
        self.direction = 1

    def update(self):
        """
        Handles platform movement and directional switching.
        """
        self.rect.x += self.move_speed * self.direction
        if self.rect.x > self.start_x + self.range_dist:
            self.direction = -1
        elif self.rect.x < self.start_x:
            self.direction = 1


class MovingPlatform_y(Platform):
    """
    Platoform moving vertically
    """
    def __init__(self, x, y, width, height, range_dist=100, speed=PLATFORM_SPEED_Y):
        """
        Function which define platform move
        """
        super().__init__(x, y, width, height)
        self.start_y = y
        self.range_dist = range_dist
        self.move_speed = speed
        self.direction = 1

    def update(self):
        """
        Handles platform movement and directional switching.
        """
        self.rect.y += self.move_speed * self.direction
        if self.rect.y > self.start_y + self.range_dist:
            self.direction = -1
        elif self.rect.y < self.start_y:
            self.direction = 1


class Coin(pygame.sprite.Sprite):
    """
    Class which defines coin as a objects possible to collect
    """
    def __init__(self, x, y):
        """
        Coin creating
        """
        super().__init__()
        self.image = coin_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.start_y = y
        self.timer = 0

    def update(self):
        """
        Animation for coin
        """
        self.timer += 0.1
        self.rect.y = self.start_y + math.sin(self.timer) * 5


class Bullet(pygame.sprite.Sprite):
    """
    Class for bullets which our hero is using to kill enemies
    """
    def __init__(self, x, y, direction):
        """
        Creating bullet
        """
        super().__init__()
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = BULLET_SPEED * direction
        if direction == -1:  # Flip bullet sprite if the player is facing left.
            self.image = pygame.transform.flip(bullet_img, True, False)

    def update(self):
        """
        Removing bullets when they are too far behind the map
        """
        self.rect.x += self.speed
        if self.rect.x < -100 or self.rect.x > MAP_LENGTH + 1000:
            self.kill()


class Player(pygame.sprite.Sprite):
    """
    Class for our hero
    """
    def __init__(self, platforms_group, bullets_group):
        """
        Hero creating
        """
        super().__init__()
        self.image_right = player_img
        self.image_left = pygame.transform.flip(player_img, True, False)
        self.image = self.image_right
        self.rect = self.image.get_rect()
        self.rect.inflate_ip(-15, 0)
        self.platforms = platforms_group
        self.bullets = bullets_group

        # Setup of hero
        self.start_pos = (100, 400)
        self.rect.x = self.start_pos[0]
        self.rect.y = self.start_pos[1]
        self.speed = PLAYER_SPEED
        self.on_ground = False
        self.velocity_y = 0
        self.facing_right = True

        self.last_shot_time = pygame.time.get_ticks()
        self.ammo = 1

    def shoot(self):
        """
        Function for shooting
        """
        now = pygame.time.get_ticks()
        if now - self.last_shot_time > SHOOT_DELAY:  # Delay for shooting
            if self.ammo > 0:
                self.last_shot_time = now
                self.ammo -= 1
                if self.facing_right:
                    direction = 1
                else:
                    direction = -1
                bullet = Bullet(self.rect.centerx, self.rect.centery, direction)
                all_sprites.add(bullet)
                self.bullets.add(bullet)
                shoot_sound.play()

    def update(self):
        """
        Controls for main character
        """
        keys = pygame.key.get_pressed()
        dx = 0
        if keys[pygame.K_LEFT]:
            dx = -self.speed
            self.image = self.image_left
            self.facing_right = False
        if keys[pygame.K_RIGHT]:
            dx = self.speed
            self.image = self.image_right
            self.facing_right = True
        if keys[pygame.K_SPACE]:
            self.shoot()
        if keys[pygame.K_UP] and self.on_ground:
            self.velocity_y = PLAYER_JUMP
            self.on_ground = False
            jump_sound.play()

        # Rules for horizontal movement
        self.rect.x += dx
        hits = pygame.sprite.spritecollide(self, self.platforms, False)
        for platform in hits:
            if self.rect.bottom <= platform.rect.top + 15:
                continue

            if dx > 0:
                self.rect.right = platform.rect.left
            if dx < 0:
                self.rect.left = platform.rect.right

        # Rules for vertical movement
        self.velocity_y += PLAYER_GRAVITY
        self.rect.y += self.velocity_y
        self.on_ground = False

        hits = pygame.sprite.spritecollide(self, self.platforms, False)

        if not hits and self.velocity_y >= 0:
            check_rect = self.rect.move(0, 15)
            for platform in self.platforms:
                if check_rect.colliderect(platform.rect):
                    hits = [platform]
                    break
        # Settings for moving platforms
        for platform in hits:
            if self.velocity_y > 0:
                self.rect.bottom = platform.rect.top
                self.velocity_y = 0
                self.on_ground = True
                if isinstance(platform, MovingPlatform_x):
                    self.rect.x += platform.move_speed * platform.direction
            elif self.velocity_y < 0:
                self.rect.top = platform.rect.bottom
                self.velocity_y = 0
        # Invisible barriers
        if self.rect.x < 0:
            self.rect.x = 0
        if self.rect.x > MAP_LENGTH + 200:
            self.rect.x = MAP_LENGTH + 200


class Enemy(pygame.sprite.Sprite):
    """
    Class for basic opponents
    """
    def __init__(self, x, y, distance, speed=2):
        """
        Creating basic opponents
        """
        super().__init__()
        self.image = enemy_img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.bottom = y
        self.start_x = x
        self.max_dist = distance
        self.direction = 1
        self.speed = speed

    def update(self):
        """
        Updating their movements
        """
        self.rect.x += self.speed * self.direction
        if self.rect.x > self.start_x + self.max_dist:
            self.direction = -1
            self.image = pygame.transform.flip(enemy_img, True, False)
        elif self.rect.x < self.start_x:
            self.direction = 1
            self.image = enemy_img


class FlyEnemy(pygame.sprite.Sprite):
    """
    Class for fly enemy
    """
    def __init__(self, x, y, target_player, speed_multiplier=1.0):
        """
        Creating fly enemy and its movement
        """
        super().__init__()
        self.image = fly_img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.player = target_player
        self.base_speed = 1.5 * speed_multiplier
        self.true_x = float(x)
        self.true_y = float(y)

    def update(self):
        """
        Defining what is goal of these flies
        """
        dx = self.player.rect.centerx - self.rect.centerx
        dy = self.player.rect.centery - self.rect.centery
        distance = math.sqrt(dx**2 + dy**2)
        # Showing when flies starting to move
        if distance < 1000 and distance != 0:
            dx = dx / distance
            dy = dy / distance
            self.true_x += dx * self.base_speed
            self.true_y += dy * self.base_speed

        self.rect.x = int(self.true_x)
        self.rect.y = int(self.true_y)
        # Flipping fly if needed
        if dx > 0:
            self.image = pygame.transform.flip(fly_img, True, False)
        else:
            self.image = fly_img


class Flag(pygame.sprite.Sprite):
    """
    Class for flag - our main goal
    """
    def __init__(self, x, y):
        """
        Creating flag
        """
        super().__init__()
        self.image = flag_img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.bottom = y


# All actors and objects
all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()
enemies = pygame.sprite.Group()
goals = pygame.sprite.Group()
bullets = pygame.sprite.Group()
coins = pygame.sprite.Group()
particles = pygame.sprite.Group()

player = None
scroll_x = 0
game_state = "MENU"


def create_particles(x, y, color, amount=10):
    """
    Creating explosions
    """
    for _ in range(amount):
        p = Particle(x, y, color)
        all_sprites.add(p)
        particles.add(p)


def init_level():
    """
    Creating level
    """
    global player, scroll_x, game_state

    if not pygame.mixer.music.get_busy():
        pygame.mixer.music.play(-1)

    all_sprites.empty()
    platforms.empty()
    enemies.empty()
    goals.empty()
    bullets.empty()
    coins.empty()
    particles.empty()

    scroll_x = 0
    # Setting current game state
    game_state = "GAME"
    # Creating map by using all platforms
    level_layout = [
        (0, 500, 800, 50),
        (900, 400, 200, 30),
        (1200, 300, 200, 30),
        (1500, 200, 300, 30),
        (2500, 250, 150, 30),
        (2850, 200, 50, 20),
        (3100, 150, 50, 20),
        (2800, 400, 500, 50),
        (3250, 100, 50, 300),
        (3400, 400, 800, 30),
        (4300, 300, 200, 30),
        (4330, 500, 50, 30),
        (4600, 500, 600, 50),
        (5300, 450, 50, 15),
        (5550, 350, 50, 15),
        (5800, 250, 50, 15),
        (6050, 150, 400, 30),
        (6600, 350, 150, 30),
        (6900, 500, 200, 50),
        (7200, 400, 25, 10),
        (7450, 300, 25, 10),
        (7700, 200, 25, 10),
        (7900, 300, 15, 5),
        (8100, 350, 150, 30),
        (8400, 500, 600, 50),
        (9100, 400, 200, 30),
        (9700, 200, 500, 50)
    ]
    # Adding platform to the map
    for p in level_layout:
        plat = Platform(p[0], p[1], p[2], p[3])
        platforms.add(plat)
        all_sprites.add(plat)
    # Creating horizontal platform
    moving_plat_x = MovingPlatform_x(1900, 350, 150, 30, range_dist=300, speed=2)
    platforms.add(moving_plat_x)
    all_sprites.add(moving_plat_x)
    # Creating horizontal platform
    moving_plat_y = MovingPlatform_y(9400, 250, 150, 30, range_dist=150, speed=4)
    platforms.add(moving_plat_y)
    all_sprites.add(moving_plat_y)

    player = Player(platforms, bullets)
    all_sprites.add(player)
    # Creating enemies and their location
    enemies_data = [
        (1550, 200, 200, 2),
        (2850, 400, 300, 3),
        (3500, 400, 600, 4),
        (4650, 500, 500, 2),
        (6100, 150, 300, 3),
        (8500, 500, 400, 2),
    ]
    # Adding enemies to the level
    for e_data in enemies_data:
        e = Enemy(e_data[0], e_data[1], e_data[2], e_data[3])
        enemies.add(e)
        all_sprites.add(e)
    # Two different type of flies one slow and second one fast
    slow_fly = FlyEnemy(5500, 200, player, speed_multiplier=1.2)
    enemies.add(slow_fly)
    all_sprites.add(slow_fly)

    boss_fly = FlyEnemy(9600, 100, player, speed_multiplier=3.5)
    enemies.add(boss_fly)
    all_sprites.add(boss_fly)
    # All coins / ammo
    coins_data = [
        (950, 350), (1650, 150), (3200, 350),
        (3800, 350), (4350, 450), (5825, 200),
        (6250, 100), (7215, 350), (9200, 350),
    ]
    # Adding coins to the map
    for c_pos in coins_data:
        c = Coin(c_pos[0], c_pos[1])
        coins.add(c)
        all_sprites.add(c)
    # Goal coordinate
    win_flag = Flag(10000, 200)
    goals.add(win_flag)
    all_sprites.add(win_flag)


def draw_centered_text(text, font, color, y_offset=0):
    """
    Function to simplify creating text
    """
    surface = font.render(text, True, color)
    rect = surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + y_offset))
    return surface, rect


def draw_menu():
    """
    Function with main menu
    """
    screen.fill("skyblue")
    title_text, title_rect = draw_centered_text("Sky wars", title_font, "white", -150)
    shadow_text, shadow_rect = draw_centered_text("Sky wars", title_font, "black", -145)  # Shadow effect
    screen.blit(shadow_text, shadow_rect)
    screen.blit(title_text, title_rect)
    start_text, start_rect = draw_centered_text("Press SPACE to Start", menu_font, "black", 0)
    screen.blit(start_text, start_rect)
    set_text, set_rect = draw_centered_text("Settings:", menu_font, "black", 50)
    screen.blit(set_text, set_rect)
    set1_text, set1_rect = draw_centered_text("Arrows: Move", ui_font, "black", 90)
    screen.blit(set1_text, set1_rect)
    set2_text, set2_rect = draw_centered_text("Space: Shoot", ui_font, "black", 130)
    screen.blit(set2_text, set2_rect)
    info_text, info_rect = draw_centered_text("Collect coins for ammo!", ui_font, "red", 200)
    screen.blit(info_text, info_rect)


def draw_ui_game():
    """
    Information in game about ammo and settings
    """
    ammo_text = ammo_font.render(f"AMMO: {player.ammo}", True, "black")
    screen.blit(ammo_text, (20, 20))
    help_text = ui_font.render("Arrows: Move | Space: Shoot", True, (50, 50, 50))
    screen.blit(help_text, (20, 55))


def draw_win_screen():
    """
    Win screen
    """
    screen.fill(COLOR_VICTORY)
    t, r = draw_centered_text("VICTORY!", title_font, "gold", -50)
    s, sr = draw_centered_text("Press SPACE to Play Again", menu_font, "white", 50)
    screen.blit(t, r)
    screen.blit(s, sr)


def draw_lose_screen():
    """
    Lose screen
    """
    screen.fill(COLOR_GAME_OVER)
    t, r = draw_centered_text("GAME OVER", title_font, "red", -50)
    s, sr = draw_centered_text("Press SPACE to Restart", menu_font, "white", 50)
    screen.blit(t, r)
    screen.blit(s, sr)


def main():
    """
    Main loop
    """
    global running, scroll_x, game_state
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if game_state == "MENU":
            draw_menu()
            keys = pygame.key.get_pressed()  # Start option
            if keys[pygame.K_SPACE]:
                init_level()

        elif game_state == "GAME":
            all_sprites.update()
            # Following camera
            target_scroll = player.rect.x - 300
            scroll_x += (target_scroll - scroll_x) * 0.1
            if scroll_x < 0:
                scroll_x = 0
            if scroll_x > MAP_LENGTH - 400:
                scroll_x = MAP_LENGTH - 400

            # Bullets and effects
            hits = pygame.sprite.groupcollide(bullets, enemies, True, False)
            for bullet, hit_enemies in hits.items():
                for enemy in hit_enemies:
                    if -100 < enemy.rect.x - scroll_x < SCREEN_WIDTH + 100:
                        # Killing effect
                        create_particles(enemy.rect.centerx, enemy.rect.centery, "green", 15)
                        enemy.kill()
                        hit_sound.play()

            # Collecting coins
            collected_coins = pygame.sprite.spritecollide(player, coins, True)
            for coin in collected_coins:
                # Collecting effect
                create_particles(coin.rect.centerx, coin.rect.centery, "gold", 10)
                player.ammo += 1
                coin_sound.play()

            if pygame.sprite.spritecollide(player, enemies, False):
                pygame.mixer.music.stop()
                lose_sound.play()
                game_state = "LOSE"

            if player.rect.y > SCREEN_HEIGHT:
                pygame.mixer.music.stop()
                lose_sound.play()
                game_state = "LOSE"

            if pygame.sprite.spritecollide(player, goals, False):
                pygame.mixer.music.stop()
                win_sound.play()
                game_state = "WIN"

            screen.fill("skyblue")
            start_tile = int(scroll_x) // bg_width
            for i in range(start_tile - 1, start_tile + 3):
                pos_x = i * bg_width - int(scroll_x)
                screen.blit(bg_img if i % 2 == 0 else bg_img_flipped, (pos_x, 0))

            # Creating all actors
            for sprite in all_sprites:
                screen.blit(sprite.image, (sprite.rect.x - int(scroll_x), sprite.rect.y))

            draw_ui_game()

        elif game_state == "WIN":
            draw_win_screen()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                init_level()

        elif game_state == "LOSE":
            draw_lose_screen()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                init_level()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
