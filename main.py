import pygame
import math

# Configuraciones del juego
WIDTH = 800
HEIGHT = 600
FPS = 60

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

class Bullet:
    def __init__(self, x, y, direction, speed=10, color=WHITE):
        self.image = pygame.Surface((10, 10))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = speed
        self.direction = direction

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
        self.detection_radius = 300
        self.horizontal = 0
        self.vertical = 0
        self.life = 2500
        self.damage = 50
        self.bullets = []
        self.shoot_cooldown = 0
        self.active = False

    def update(self, player_rect):
        # Calcular la distancia al jugador
        distance_x = player_rect.centerx - self.rect.centerx
        distance_y = player_rect.centery - self.rect.centery
        distance = math.sqrt(distance_x**2 + distance_y**2)
        
        # Verificar si el jugador está dentro del radio de detección
        if distance <= self.detection_radius:
            self.active = True
            # Normalizar la dirección hacia el jugador
            if distance != 0:
                self.horizontal = distance_x / distance
                self.vertical = distance_y / distance
            # Mover hacia el jugador
            self.rect.x += self.speed * self.horizontal
            self.rect.y += self.speed * self.vertical
        else:
            self.active = False
            self.horizontal = 0
            self.vertical = 0

        if self.active:
            # Disparar proyectiles en patrones
            self.shoot_cooldown -= 1
            if self.shoot_cooldown <= 0:
                self.shoot_pattern()
                self.shoot_cooldown = FPS

        # Actualizar los proyectiles
        for bullet in self.bullets:
            bullet.update()

    def shoot_pattern(self):
        # Disparar en 8 direcciones (arriba, abajo, izquierda, derecha y diagonales)
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (0.707, 0.707), (-0.707, 0.707), (0.707, -0.707), (-0.707, -0.707)]
        for direction in directions:
            bullet = Bullet(self.rect.centerx, self.rect.centery, direction, color=RED)
            self.bullets.append(bullet)

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 0, 0), self.rect.center, self.detection_radius, 1)
        screen.blit(self.image, self.rect)
        for bullet in self.bullets:
            bullet.draw(screen)

class Player:
    def __init__(self):
        self.image = pygame.Surface((50, 50))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.speed = 5
        self.horizontal = 0
        self.vertical = 0
        self.life = 200
        self.damage = 100
        self.bullets = []
        self.shooting = False

    def handle_keys(self):
        keys = pygame.key.get_pressed()
        self.horizontal = keys[pygame.K_d] - keys[pygame.K_a]
        self.vertical = keys[pygame.K_s] - keys[pygame.K_w]

        # Normalizar el movimiento
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
            bullet = Bullet(self.rect.centerx, self.rect.centery, direction)
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

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Souls-Like")
        self.clock = pygame.time.Clock()
        self.player = Player()
        self.boss = Boss()
        self.running = True

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        self.player.handle_keys()
        self.player.handle_mouse()
        self.player.update()
        self.boss.update(self.player.rect)

    def draw(self):
        self.screen.fill(BLACK)
        self.player.draw(self.screen)
        self.boss.draw(self.screen)
        pygame.display.flip()

if __name__ == "__main__":
    game = Game()
    game.run()
