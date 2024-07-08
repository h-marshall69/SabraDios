import pygame
import math

# Configuraciones del juego
WIDTH = 1366
HEIGHT = 768
FPS = 60

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

class Bullet:
    def __init__(self, x, y, direction, speed=10, color=WHITE, damage=50):
        self.image = pygame.Surface((10, 10))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = speed
        self.direction = direction
        self.damage = damage

    def update(self):
        self.rect.x += self.speed * self.direction[0]
        self.rect.y += self.speed * self.direction[1]

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Boss:
    def __init__(self):
        self.image = pygame.Surface((200, 200))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.speed = 2
        self.detection_radius = 500
        self.horizontal = 0
        self.vertical = 0
        self.life = 2500
        self.max_life = self.life
        self.damage = 20
        self.bullets = []
        self.shoot_cooldown = 0
        self.active = False

    def update(self, player_rect):
        distance_x = player_rect.centerx - self.rect.centerx
        distance_y = player_rect.centery - self.rect.centery
        distance = math.sqrt(distance_x**2 + distance_y**2)
        
        if distance <= self.detection_radius:
            self.active = True
            if distance != 0:
                self.horizontal = distance_x / distance
                self.vertical = distance_y / distance
            self.rect.x += self.speed * self.horizontal
            self.rect.y += self.speed * self.vertical
        else:
            self.active = False
            self.horizontal = 0
            self.vertical = 0

        if self.active:
            self.shoot_cooldown -= 1
            if self.shoot_cooldown <= 0:
                self.shoot_pattern()
                self.shoot_cooldown = FPS

        for bullet in self.bullets:
            bullet.update()

    def shoot_pattern(self):
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (0.707, 0.707), (-0.707, 0.707), (0.707, -0.707), (-0.707, -0.707)]
        for direction in directions:
            bullet = Bullet(self.rect.centerx, self.rect.centery, direction, color=RED, damage=self.damage)
            self.bullets.append(bullet)

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 0, 0), self.rect.center, self.detection_radius, 1)
        screen.blit(self.image, self.rect)
        for bullet in self.bullets:
            bullet.draw(screen)
        self.draw_health_bar(screen)

    def draw_health_bar(self, screen):
        bar_width = 200
        bar_height = 20
        fill = (self.life / self.max_life) * bar_width
        outline_rect = pygame.Rect(WIDTH - bar_width - 10, 10, bar_width, bar_height)
        fill_rect = pygame.Rect(WIDTH - bar_width - 10, 10, fill, bar_height)
        pygame.draw.rect(screen, RED, fill_rect)
        pygame.draw.rect(screen, WHITE, outline_rect, 2)

class Player:
    def __init__(self):
        self.image = pygame.Surface((50, 50))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.center = (600, 600)
        self.speed = 5
        self.horizontal = 0
        self.vertical = 0
        self.life = 200
        self.max_life = self.life
        self.damage = 50
        self.bullets = []
        self.shooting = False

    def handle_keys(self):
        keys = pygame.key.get_pressed()
        self.horizontal = keys[pygame.K_d] - keys[pygame.K_a]
        self.vertical = keys[pygame.K_s] - keys[pygame.K_w]

        if self.horizontal != 0 or self.vertical != 0:
            magnitude = math.sqrt(self.horizontal ** 2 + self.vertical ** 2)
            self.horizontal /= magnitude
            self.vertical /= magnitude

    def handle_mouse(self):
        mouse_pressed = pygame.mouse.get_pressed()
        if mouse_pressed[0] and not self.shooting:
            self.shooting = True
            mouse_pos = pygame.mouse.get_pos()
            direction = (mouse_pos[0] - self.rect.centerx, mouse_pos[1] - self.rect.centery)
            magnitude = math.sqrt(direction[0] ** 2 + direction[1] ** 2)
            if magnitude != 0:
                direction = (direction[0] / magnitude, direction[1] / magnitude)
            bullet = Bullet(self.rect.centerx, self.rect.centery, direction, damage=self.damage)
            self.bullets.append(bullet)
        elif not mouse_pressed[0]:
            self.shooting = False

    def update(self):
        self.rect.x += self.speed * self.horizontal
        self.rect.y += self.speed * self.vertical
        for bullet in self.bullets:
            bullet.update()

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        for bullet in self.bullets:
            bullet.draw(screen)
        self.draw_health_bar(screen)

    def draw_health_bar(self, screen):
        bar_width = 200
        bar_height = 20
        fill = (self.life / self.max_life) * bar_width
        outline_rect = pygame.Rect(10, 10, bar_width, bar_height)
        fill_rect = pygame.Rect(10, 10, fill, bar_height)
        pygame.draw.rect(screen, WHITE, fill_rect)
        pygame.draw.rect(screen, WHITE, outline_rect, 2)

class Menu:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.font = pygame.font.Font(None, 74)
        self.options = ["Play", "Quit"]
        self.selected = 0

    def display_menu(self):
        self.screen.fill(BLACK)
        for i, option in enumerate(self.options):
            color = WHITE if i == self.selected else RED
            text = self.font.render(option, True, color)
            rect = text.get_rect()
            rect.center = (WIDTH // 2, HEIGHT // 2 + i * 100)
            self.screen.blit(text, rect)
        pygame.display.flip()

    def run(self):
        while True:
            self.display_menu()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game.running = False
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.selected = (self.selected - 1) % len(self.options)
                    elif event.key == pygame.K_DOWN:
                        self.selected = (self.selected + 1) % len(self.options)
                    elif event.key == pygame.K_RETURN:
                        if self.selected == 0:
                            self.game.playing = True
                            return
                        elif self.selected == 1:
                            self.game.running = False
                            return

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Souls-Like")
        self.clock = pygame.time.Clock()
        self.player = Player()
        self.boss = Boss()
        self.menu = Menu(self)
        self.running = True
        self.playing = False

    def run(self):
        while self.running:
            if self.playing:
                self.game_loop()
            else:
                self.menu.run()
        pygame.quit()

    def game_loop(self):
        while self.playing:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        self.reset_game()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.playing = False

    def update(self):
        self.player.handle_keys()
        self.player.handle_mouse()
        self.player.update()
        self.boss.update(self.player.rect)
        self.check_collisions()

    def draw(self):
        self.screen.fill(BLACK)
        self.player.draw(self.screen)
        self.boss.draw(self.screen)
        pygame.display.flip()

    def check_collisions(self):
        for bullet in self.player.bullets:
            if self.boss.rect.colliderect(bullet.rect):
                self.boss.life -= bullet.damage
                self.player.bullets.remove(bullet)
                if self.boss.life <= 0:
                    self.boss_destroy()

        for bullet in self.boss.bullets:
            if self.player.rect.colliderect(bullet.rect):
                self.player.life -= bullet.damage
                self.boss.bullets.remove(bullet)
                if self.player.life <= 0:
                    self.player_destroy()

    def boss_destroy(self):
        print("Boss destruido!")
        self.playing = False

    def player_destroy(self):
        print("Player destruido!")
        self.playing = False

    def reset_game(self):
        self.player = Player()
        self.boss = Boss()

if __name__ == "__main__":
    game = Game()
    game.run()
