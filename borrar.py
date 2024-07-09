import pygame
import random
import math
from scipy.spatial import Delaunay
import networkx as nx

# Configuraciones del juego
WIDTH = 800
HEIGHT = 600
FPS = 60
NUM_CELLS = 150
MIN_ROOM_SIZE = 20

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

class Rectangle:
    def __init__(self, width, height, x, y):
        self.width = width
        self.height = height
        self.image = pygame.Surface((width, height))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
    
    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Test:
    def __init__(self):
        self.pygame = pygame
        self.pygame.init()
        
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.pygame.display.set_caption('Procedural Dungeon Generation')
        
        self.clock = pygame.time.Clock()
        self.running = True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def draw_line(self, x1, y1, x2, y2):
        pygame.draw.line(self.screen, RED, (x1, y1), (x2, y2), 1)

    def generate_cells(self, num_cells):
        cells = []
        radius = num_cells * 2
        for i in range(num_cells):
            while True:
                width = int(random.paretovariate(2) * 10)
                height = int(random.paretovariate(2) * 10)
                angle = random.uniform(0, 2 * math.pi)
                r = random.uniform(0, radius)
                x = int(WIDTH / 2 + r * math.cos(angle))
                y = int(HEIGHT / 2 + r * math.sin(angle))

                if math.sqrt((x - WIDTH // 2) ** 2 + (y - HEIGHT // 2) ** 2) <= radius:
                    cells.append(Rectangle(width, height, x, y))
                    break
        return cells

    def separate_cells(self, cells):
        for i in range(1000):  # Iterar para mejorar la separación
            collision = False
            for i, cell in enumerate(cells):
                for j, other in enumerate(cells):
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

    def create_rooms_and_corridors(self, cells):
        rooms = [cell for cell in cells if cell.width >= MIN_ROOM_SIZE and cell.height >= MIN_ROOM_SIZE]
        points = [(cell.rect.centerx, cell.rect.centery) for cell in rooms]
        tri = Delaunay(points)
        edges = set()
        for simplex in tri.simplices:
            for i in range(3):
                for j in range(i+1, 3):
                    edge = (simplex[i], simplex[j])
                    edges.add(edge)

        graph = nx.Graph()
        graph.add_edges_from(edges)
        mst = nx.minimum_spanning_tree(graph)
        extra_edges = random.sample(graph.edges - mst.edges, int(0.15 * len(graph.edges)))
        mst.add_edges_from(extra_edges)

        corridors = []
        for edge in mst.edges:
            start, end = points[edge[0]], points[edge[1]]
            corridors.append((start, end))
        return rooms, corridors

    def run(self):
        cells = self.generate_cells(NUM_CELLS)
        self.separate_cells(cells)
        rooms, corridors = self.create_rooms_and_corridors(cells)

        while self.running:
            self.handle_events()
            self.screen.fill(BLACK)
            
            for rect in cells:
                rect.draw(self.screen)
            for room in rooms:
                pygame.draw.rect(self.screen, GREEN, room.rect, 2)
            for corridor in corridors:
                pygame.draw.line(self.screen, RED, corridor[0], corridor[1], 2)

            self.pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()

if __name__ == '__main__':
    game = Test()
    game.run()
