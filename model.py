from math import sin, cos, pi, atan2, hypot
import random

class Gem(object):
    # position
    # radius
    # levels
    pass

class Base(object):
    # position
    # radius
    # levels
    pass

class Bot(object):
    def __init__(self, position, target):
        self.position = position
        self.target = target
        self.padding = 0.333
        self.speed = 2.0

class Grid(object):
    def __init__(self, size):
        self.size = size
        self.walls = set()
        self.clear_caches()
    @property
    def width(self):
        return self.size[0]
    @property
    def height(self):
        return self.size[1]
    def clear_caches(self):
        self.neighbors = {}
        self.distances = {}
    def add_wall(self, point):
        if not self.inside(point):
            return
        self.walls.add(point)
        self.clear_caches()
    def toggle_wall(self, point):
        if not self.inside(point):
            return
        if point in self.walls:
            self.walls.remove(point)
        else:
            self.walls.add(point)
        self.clear_caches()
    def has_wall(self, point):
        return point in self.walls
    def inside(self, point):
        x, y = point
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return False
        return True
    def empty(self, point):
        return self.inside(point) and not self.has_wall(point)
    def random_empty(self, jitter=False):
        while True:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if not self.has_wall((x, y)):
                if jitter:
                    x += random.random() * 0.5 - 0.25
                    y += random.random() * 0.5 - 0.25
                return (x, y)
    def compute_neighbors(self, point):
        result = []
        if not self.empty(point):
            return result
        x, y = point
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            other = (x + dx, y + dy)
            if self.empty(other):
                result.append(other)
        for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            other = (x + dx, y + dy)
            a = (x + dx, y)
            b = (x, y + dy)
            if self.empty(other) and self.empty(a) and self.empty(b):
                result.append(other)
        return result
    def compute_distances(self, start):
        distance = {}
        distance[start] = 0
        queue = [start]
        while queue:
            point = queue.pop(0)
            for other in self.get_neighbors(point):
                if other not in distance:
                    queue.append(other)
                    distance[other] = distance[point] + 1
        return distance
    def get_neighbors(self, point):
        if point not in self.neighbors:
            self.neighbors[point] = self.compute_neighbors(point)
        return self.neighbors[point]
    def get_distance(self, a, b):
        if b not in self.distances:
            self.distances[b] = self.compute_distances(b)
        return self.distances[b].get(a, -1)
    def get_neighbor(self, a, b):
        return min(self.get_neighbors(a),
            key=lambda x: self.get_distance(x, b))
    def get_angle(self, a, b):
        try:
            n = self.get_neighbor((int(round(a[0])), int(round(a[1]))), b)
            return atan2(n[1] - a[1], n[0] - a[0])
        except Exception:
            return 0 # TODO

class Model(object):
    def __init__(self):
        self.grid = Grid((16, 16))
        for i in range(50):
            self.grid.toggle_wall(self.grid.random_empty())
        self.reset()
    def reset(self):
        self.bots = self.create_bots(100)
    def update(self, t, dt):
        m = 1
        for i in range(m):
            self.update_bots(dt / m)
    def create_bots(self, count):
        result = []
        for i in range(count):
            position = self.grid.random_empty(True)
            target = self.grid.random_empty()
            bot = Bot(position, target)
            result.append(bot)
        return result
    def update_bot(self, bot):
        px, py = bot.position
        angle = self.grid.get_angle(bot.position, bot.target)
        dx = cos(angle)
        dy = sin(angle)
        for other in self.bots:
            if other == bot:
                continue
            x, y = other.position
            ox = abs(px - x)
            oy = abs(py - y)
            if ox > 5 or oy > 5:
                continue
            d = hypot(ox, oy) ** 2
            d = max(d, 0.001)
            p = other.padding ** 2
            angle = atan2(py - y, px - x)
            dx += cos(angle) / d * p
            dy += sin(angle) / d * p
        angle = atan2(dy, dx)
        magnitude = hypot(dx, dy)
        return angle, magnitude
    def update_bots(self, dt):
        data = [self.update_bot(bot) for bot in self.bots]
        for bot, (angle, magnitude) in zip(self.bots, data):
            speed = min(1, 0.2 + magnitude * 0.8)
            dx = cos(angle) * dt * bot.speed * speed
            dy = sin(angle) * dt * bot.speed * speed
            px, py = bot.position
            tx, ty = bot.target
            bot.position = (px + dx, py + dy)
            if hypot(px - tx, py - ty) < 0.5:
                bot.target = self.grid.random_empty()
        pad = 0.2
        for bot in self.bots:
            x, y = bot.position
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                px = int(round(x + dx * pad))
                py = int(round(y + dy * pad))
                if not self.grid.empty((px, py)):
                    if dx:
                        x = px - (0.5 + pad) * dx
                    if dy:
                        y = py - (0.5 + pad) * dy
            bot.position = (x, y)
