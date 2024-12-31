import pygame
import sys
from queue import PriorityQueue

# Initialize Pygame
pygame.init()

# Constants
WIDTH = 800
HEIGHT = 600
RADIUS = 25  # Increased node size
FONT_SIZE = 28  # Increased font size
EDGE_THICKNESS = 3  # Added edge thickness
PATH_THICKNESS = 6  # Added path thickness

# Enhanced color scheme
NODE_COLOR = (41, 128, 185)  # Prettier blue
NODE_BORDER_COLOR = (25, 79, 114)  # Darker blue for node border
EDGE_COLOR = (189, 195, 199)  # Light gray
PATH_COLOR = (231, 76, 60)  # Coral red
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
TEXT_COLOR = (44, 62, 80)  # Dark blue-gray
ACTIVE_COLOR = (52, 152, 219)  # Bright blue
INFO_BG_COLOR = (236, 240, 241)  # Light gray
WEIGHT_BG_COLOR = (255, 255, 255, 180)  # Semi-transparent white

# Improved node positions for better layout
nodes = {
    'A': (150, 150),
    'B': (350, 150),
    'C': (150, 350),
    'D': (550, 150),
    'E': (550, 350),
    'F': (750, 150)
}

edges = {
    ('A', 'B'): 7, ('A', 'C'): 12,
    ('B', 'C'): 2, ('B', 'D'): 9,
    ('C', 'E'): 10, ('D', 'E'): 4,
    ('D', 'F'): 1, ('E', 'F'): 5
}

class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = BLACK
        self.text = text
        self.font = pygame.font.Font(None, FONT_SIZE)
        self.txt_surface = self.font.render(text, True, self.color)
        self.active = False
        self.width = w
        self.height = h

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
                return None
            else:
                self.active = False
                return None

        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    temp = self.text
                    self.text = ''
                    self.txt_surface = self.font.render(self.text, True, self.color)
                    return temp
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                    self.txt_surface = self.font.render(self.text, True, self.color)
                else:
                    key_char = event.unicode.upper()
                    if key_char in 'ABCDEF' and len(self.text) < 1:
                        self.text = key_char
                        self.txt_surface = self.font.render(self.text, True, self.color)
                return self.text
        return None

    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, self.rect)
        border_color = ACTIVE_COLOR if self.active else BLACK
        pygame.draw.rect(screen, border_color, self.rect, 2)
        screen.blit(self.txt_surface, (self.rect.x + 10, self.rect.y + 5))

def dijkstra(graph, start, end):
    pq = PriorityQueue()
    distances = {node: float('inf') for node in graph}
    distances[start] = 0
    pq.put((0, start))
    previous = {node: None for node in graph}
    
    while not pq.empty():
        current_distance, current_node = pq.get()
        
        if current_node == end:
            break
        
        for neighbor, weight in graph[current_node].items():
            distance = current_distance + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous[neighbor] = current_node
                pq.put((distance, neighbor))
    
    path = []
    current = end
    while current is not None:
        path.append(current)
        current = previous[current]
    path.reverse()
    return path, distances[end]

def draw_weight_label(screen, weight, x, y):
    font = pygame.font.Font(None, FONT_SIZE)
    text = font.render(str(weight), True, TEXT_COLOR)
    text_rect = text.get_rect(center=(x, y))
    
    padding = 4
    bg_rect = pygame.Rect(text_rect.x - padding, text_rect.y - padding,
                         text_rect.width + 2*padding, text_rect.height + 2*padding)
    bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
    pygame.draw.rect(bg_surface, WEIGHT_BG_COLOR, bg_surface.get_rect())
    screen.blit(bg_surface, bg_rect)
    screen.blit(text, text_rect)

def draw_graph(screen):
    screen.fill(WHITE)
    
    # Draw edges with weights
    for (node1, node2), weight in edges.items():
        x1, y1 = nodes[node1]
        x2, y2 = nodes[node2]
        
        pygame.draw.line(screen, EDGE_COLOR, (x1, y1), (x2, y2), EDGE_THICKNESS)
        
        mid_x = (x1 + x2) // 2
        mid_y = (y1 + y2) // 2
        draw_weight_label(screen, weight, mid_x, mid_y)
    
    # Draw nodes with border
    for node, (x, y) in nodes.items():
        pygame.draw.circle(screen, NODE_BORDER_COLOR, (x, y), RADIUS + 2)
        pygame.draw.circle(screen, NODE_COLOR, (x, y), RADIUS)
        font = pygame.font.Font(None, FONT_SIZE)
        text = font.render(node, True, WHITE)
        text_rect = text.get_rect(center=(x, y))
        screen.blit(text, text_rect)

def draw_path(screen, path):
    if not path:
        return
    for i in range(len(path) - 1):
        x1, y1 = nodes[path[i]]
        x2, y2 = nodes[path[i + 1]]
        pygame.draw.line(screen, PATH_COLOR, (x1, y1), (x2, y2), PATH_THICKNESS)

def draw_info_panel(screen, start_box, end_box, path=None, distance=None):
    panel_height = 120
    info_rect = pygame.Rect(10, HEIGHT - panel_height - 10, WIDTH - 20, panel_height)
    pygame.draw.rect(screen, INFO_BG_COLOR, info_rect)
    pygame.draw.rect(screen, BLACK, info_rect, 2)

    font = pygame.font.Font(None, FONT_SIZE)
    y_start = HEIGHT - panel_height + 10
    line_height = 30
    
    start_text = font.render("Start node (A-F):", True, TEXT_COLOR)
    screen.blit(start_text, (20, y_start))
    start_box.rect.y = y_start
    start_box.draw(screen)
    
    end_text = font.render("End node (A-F):", True, TEXT_COLOR)
    screen.blit(end_text, (20, y_start + line_height))
    end_box.rect.y = y_start + line_height
    end_box.draw(screen)

    if path and distance is not None:
        path_text = f"Shortest path: {' -> '.join(path)} with distance {distance}"
        max_width = WIDTH - 40
        if font.size(path_text)[0] > max_width:
            path_text = f"Path: {' -> '.join(path)}"
            distance_text = f"Distance: {distance}"
            path_surface = font.render(path_text, True, TEXT_COLOR)
            distance_surface = font.render(distance_text, True, TEXT_COLOR)
            screen.blit(path_surface, (20, y_start + line_height * 2))
            screen.blit(distance_surface, (20, y_start + line_height * 3))
        else:
            path_surface = font.render(path_text, True, TEXT_COLOR)
            screen.blit(path_surface, (20, y_start + line_height * 2))

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Dijkstra's Algorithm Visualizer")
    clock = pygame.time.Clock()
    
    start_box = InputBox(200, HEIGHT - 85, 40, 30)
    end_box = InputBox(200, HEIGHT - 50, 40, 30)
    
    graph = {node: {} for node in nodes}
    for (node1, node2), weight in edges.items():
        graph[node1][node2] = weight
        graph[node2][node1] = weight
    
    path = None
    distance = None
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            start_result = start_box.handle_event(event)
            end_result = end_box.handle_event(event)
            
            if start_result and end_result and start_result in nodes and end_result in nodes:
                path, distance = dijkstra(graph, start_result, end_result)
            elif start_result and end_box.text in nodes:
                path, distance = dijkstra(graph, start_result, end_box.text)
            elif start_box.text in nodes and end_result:
                path, distance = dijkstra(graph, start_box.text, end_result)
        
        draw_graph(screen)
        if path:
            draw_path(screen, path)
        draw_info_panel(screen, start_box, end_box, path, distance)
        
        pygame.display.flip()
        clock.tick(30)
    
    pygame.quit()

if __name__ == "__main__":
    main()

    
