import pygame
import random
import math
import scipy.spatial

# Configuraciones del juego
WIDTH = 800
HEIGHT = 600
FPS = 60
NUM_CELLS = 10
MIN_ROOM_SIZE = 20

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

class Rectangle:
    def __init__(self, width, height, x, y):
        self.width = width
        self.height = height
        self.image = pygame.Surface((width, height))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
    
    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Dungeon:
    def __init__(self, num_cells):
        self.cells = []
        self.rooms = []
        self.corridors = []
        self.num_cells = num_cells
        self.radius = num_cells * 2

    def generate_cells(self):
        for _ in range(self.num_cells):
            width = random.randint(MIN_ROOM_SIZE, MIN_ROOM_SIZE * 3)
            height = random.randint(MIN_ROOM_SIZE, MIN_ROOM_SIZE * 3)
            x = random.randint(0, WIDTH - width)
            y = random.randint(0, HEIGHT - height)
            self.cells.append(Rectangle(width, height, x, y))

    def separate_cells(self):
        for _ in range(1000):  # Iterar para mejorar la separación
            collision = False
            for i, cell in enumerate(self.cells):
                for j, other in enumerate(self.cells):
                    if i != j and cell.rect.colliderect(other.rect):
                        collision = True
                        dx = (cell.rect.centerx - other.rect.centerx) / 10
                        dy = (cell.rect.centery - other.rect.centery) / 10
                        cell.rect.x += dx
                        cell.rect.y += dy
                        other.rect.x -= dx
                        other.rect.y -= dy
            if not collision:
                break

    def identify_rooms(self):
        for cell in self.cells:
            if cell.width >= MIN_ROOM_SIZE and cell.height >= MIN_ROOM_SIZE:
                self.rooms.append(cell)

    def connect_rooms(self):
        points = [(room.rect.centerx, room.rect.centery) for room in self.rooms]
        tri = scipy.spatial.Delaunay(points)
        edges = set()
        for simplex in tri.simplices:
            for i in range(3):
                edge = sorted((simplex[i], simplex[(i + 1) % 3]))
                edges.add(tuple(edge))
        mst = self.minimum_spanning_tree(points, edges)
        self.corridors = mst

    def minimum_spanning_tree(self, points, edges):
        parent = list(range(len(points)))

        def find(u):
            if parent[u] != u:
                parent[u] = find(parent[u])
            return parent[u]

        def union(u, v):
            pu = find(u)
            pv = find(v)
            parent[pu] = pv

        sorted_edges = sorted(edges, key=lambda edge: math.dist(points[edge[0]], points[edge[1]]))
        mst = []
        for u, v in sorted_edges:
            if find(u) != find(v):
                union(u, v)
                mst.append((points[u], points[v]))
        return mst

class Game:
    def __init__(self):
        self.pygame = pygame
        self.pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.pygame.display.set_caption('Procedural Dungeon Generation')
        self.clock = pygame.time.Clock()
        self.running = True
        self.dungeon = Dungeon(NUM_CELLS)
        self.dungeon.generate_cells()
        self.dungeon.separate_cells()
        self.dungeon.identify_rooms()
        self.dungeon.connect_rooms()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def run(self):
        while self.running:
            self.handle_events()
            self.screen.fill(BLACK)
            
            for rect in self.dungeon.cells:
                rect.draw(self.screen)
            for room in self.dungeon.rooms:
                pygame.draw.rect(self.screen, BLUE, room.rect, 2)
            for corridor in self.dungeon.corridors:
                pygame.draw.line(self.screen, GREEN, corridor[0], corridor[1], 2)

            self.pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()
