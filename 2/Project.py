import pygame
from math import sin, cos, pi
from random import randint

pygame.init()
size = width, height = 800, 600
Run = True
screen = pygame.display.set_mode(size)
pygame.display.flip()


score = 1
Start_Resolution = 5
Start_Max_Distance = 1000


def tofpifagor(a, b):
    return (a * a + b * b) ** 0.5


class Rectangle:
    def __init__(self, x=0, y=0, w=0, h=0):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.t = "rect"  # type of special shape

    def xother(self, other):
        if other.type == "rect":
            if other.x <= self.x + self.w and self.x <= other.x + other.w:
                return other.y <= self.y + self.h and self.y <= other.y + other.h

        if other.type == "circle":
            return self.topoint(other.x, other.y) <= other.r

    def topoint(self, x, y):
        a = 0
        b = 0
        if x < self.x:
            a = self.x - x
        if x > self.x + self.w:
            a = x - self.x - self.w

        if y < self.y:
            b = self.y - y
        if y > self.y + self.h:
            b = y - self.y - self.h

        return tofpifagor(a, b)


class Circle:
    def __init__(self, x=0, y=0, r=0):
        self.type = "circle"
        self.x = x
        self.y = y
        self.r = r

    def xother(self, other):
        if other.type == "circle":
            return tofpifagor(self.x - other.x, self.y - other.y) <= (self.r + other.r)

        if other.type == "rect":
            return other.xother(self)

    def topoint(self, x, y):
        return tofpifagor(x - self.x, y - self.y) - self.r


class Map:
    def __init__(self):
        self.mp = []

    def push(self, shape):
        self.mp += [shape]

    def getmindistance(self, x, y, mxd):
        d = mxd
        for i in self.mp:
            d = min(d, i.topoint(x, y))
        return d

    def xother(self, shape):
        for i in self.mp:
            if i.xother(shape):
                return True
        return False


mp = Map()  # Map initialization


def ray(a, bx, by, mxd, massive):
    fd = 0
    dx = cos(a)
    dy = sin(a)
    x = bx
    y = by
    ind = 0
    while fd < mxd:
        ind = 0
        d = min(mxd, massive[ind].topoint(x, y))
        for i in range(1, len(massive)):
            nd = massive[i].topoint(x, y)
            if nd < d:
                d = nd
                ind = i
        x += dx * d
        y += dy * d
        fd += d
        if d < 1:
            break
    return [fd, x, y, ind]


class Weapon:
    def __init__(self, damage, time, shootcount=1, randomsdvig=0, countofbullets=0):
        self.d = damage
        self.t = time
        self.b = countofbullets
        self.sh = shootcount, randomsdvig

    def getangels(self):
        if self.b <= 0:
            return []
        ans = []
        for i in range(self.sh[0]):
            ans += [randint(-self.sh[1], -self.sh[1]) * pi / 1000.0]
        self.b -= len(ans)
        return ans


class Entity(Circle):
    def __init__(self, x=0, y=0, r=0):
        super().__init__(x, y, r)
        self.hp = 100


class Enemy(Entity):
    def __init__(self, x=0, y=0, r=10):
        super().__init__(x, y, r)
        self.dx = 0
        self.dy = 0
        self.speed = 0.01

    def upd(self, px, py, time):

        global mp

        d = tofpifagor(self.x - px, self.y - py)
        self.dx = (px - self.x) / d * self.speed
        self.dy = (py - self.y) / d * self.speed

        self.x += self.dx * time
        self.y += self.dy * time


ens = [Enemy(-100, -100)]


class Player(Entity):
    def __init__(self, x=20, y=20, r=10):

        global Start_Max_Distance

        super().__init__(x, y, r)
        self.dfw = 0
        self.dleft = 0
        self.a = 0
        self.press = {}
        for i in ['w', 'a', 's', 'd', 'j', 'i', 'l']:
            self.press[i] = False
        self.speed = 0.1
        self.aspeed = 0.005
        self.mxd = Start_Max_Distance
        self.ts = []
        self.wpns = [
            Weapon(34, 200, 1, 1, 100000)
        ]
        self.chwp = 0
        self.time = 0

    def draw(self, resolution):

        global screen, width, height, mp, ens, score

        rc = width // resolution
        self.ts = []
        d = []
        ms = mp.mp + ens
        for i in range(rc):
            d += [ray(self.a + (i - rc / 2) / rc / 2 * pi, self.x, self.y, self.mxd, ms)]
            d[i][0] = min(max(self.r, d[i][0]), self.mxd)
        for i in range(rc):
            if d[i][0] >= self.mxd - 20:
                continue
            d[i][0] *= cos((rc / 2 - i) * pi / 2 / rc)
            ps = height * 20 / d[i][0] / 2  # / (cos((i - width / 2) / width * pi / 4) ** 4)

            col = min(255, ps / 600 * 255 + 30)

            col = (col,) * 3

            if d[i][3] >= len(mp.mp):
                col = col[0], 0, 0

                if ens[d[i][3] - len(mp.mp)].speed > Enemy().speed:
                    col = col[0], 0, col[0]

                if ens[d[i][3] - len(mp.mp)].speed < Enemy().speed:
                    col = col[0], col[0], 0

            pygame.draw.rect(screen, col,
                             (i * resolution, height / 2 - ps, resolution, ps * 2))

        text = pygame.font.Font(None, 25).render(f"Score: {score}", True, (255,) * 3)
        screen.blit(text, (width - 175, 25))

        text = pygame.font.Font(None, 25).render(f"Bullets {self.wpns[self.chwp].b}", True, (255,) * 3)
        screen.blit(text, (width - 175, 75))

    def control(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_d:
                self.press['d'] = True
            if e.key == pygame.K_a:
                self.press['a'] = True
            if e.key == pygame.K_w:
                self.press['w'] = True
            if e.key == pygame.K_s:
                self.press['s'] = True
            if e.key == pygame.K_j:
                self.press['j'] = True
            if e.key == pygame.K_l:
                self.press['l'] = True
            if e.key == pygame.K_i:
                self.press['i'] = True
        if e.type == pygame.KEYUP:
            if e.key == pygame.K_d:
                self.press['d'] = False
            if e.key == pygame.K_a:
                self.press['a'] = False
            if e.key == pygame.K_w:
                self.press['w'] = False
            if e.key == pygame.K_s:
                self.press['s'] = False
            if e.key == pygame.K_j:
                self.press['j'] = False
            if e.key == pygame.K_l:
                self.press['l'] = False
            if e.key == pygame.K_i:
                self.press['i'] = False

    def upd(self, time):

        global mp, ens

        # key updates
        self.a += (self.press['l'] - self.press['j']) * time * self.aspeed
        self.dfw = (self.press['w'] - self.press['s']) * self.speed
        self.dleft = (self.press['d'] - self.press['a']) * self.speed

        n = self.x
        self.x += self.dfw * time * cos(self.a)
        self.x += self.dleft * time * cos(self.a + pi / 2)
        if mp.xother(self):
            self.x = n
        n = self.y
        self.y += self.dfw * time * sin(self.a)
        self.y += self.dleft * time * sin(self.a + pi / 2)
        if mp.xother(self):
            self.y = n

        self.time += time
        if self.press['i'] and self.time >= 0:
            self.time = -self.wpns[self.chwp].t
            for i in self.wpns[self.chwp].getangels():
                t = ray(self.a + i, self.x, self.y, self.mxd, ens + mp.mp)[3]
                if t < len(ens):
                    self.hp += 10
                    ens[t].hp -= self.wpns[self.chwp].d

# vars section


p = Player(20, 20)
mp.push(Rectangle(100, 100, 100, 100))
mp.push(Circle(100, 100, 10))
#


class Game:
    def __init__(self):
        pass

    def draw(self):
        pass

    def logic(self, time):
        pass

    def control(self, e):
        pass


class Zombie(Game):
    def __init__(self):

        global Start_Resolution

        self.respawn = [0, 2000]
        self.resolution = Start_Resolution
        self.wall_creation = 25

    def draw(self):

        global p, screen

        screen.fill((0, 0, 0))
        p.draw(self.resolution)

        cross = 10
        pygame.draw.line(screen, (255,) * 3,
                         (width / 2 - cross, height / 2),
                         (width / 2 + cross, height / 2))
        pygame.draw.line(screen, (255,) * 3,
                         (width / 2, height / 2 - cross),
                         (width / 2, height / 2 + cross))

        pygame.display.flip()

    def logic(self, time):

        global p, ens, score, choosen_game

        p.upd(time)
        for i in range(len(ens) - 1, -1, -1):
            ens[i].upd(p.x, p.y, time)

            if ens[i].hp <= 0:
                ens.pop(i)
                score += 1
                continue

            if ens[i].topoint(p.x, p.y) < p.r + ens[i].r:
                ens = []
                p.__init__()
                score = 0
                choosen_game = 1
                break

        self.respawn[0] += time

        if self.respawn[0] > self.respawn[1]:

            self.respawn[0] -= self.respawn[1]

            ens += [Enemy(p.x + cos(p.a + pi) * randint(100, 200), p.y + sin(p.a + pi) * randint(100, 200))]

            if score >= self.wall_creation:
                ens[-1] = Enemy(p.x + cos(p.a + pi) * randint(100, 200), p.y + sin(p.a + pi) * randint(500, 2000))
                ens[-1].hp *= 10
                ens[-1].speed *= 0.01
                ens[-1].r *= 10
                score += 1
                self.wall_creation += 25

            elif score % 5 == 0:
                ens[-1].hp *= 3
                ens[-1].speed *= 3

    def control(self, e):

        global Run, p, choosen_game

        if e.type == pygame.QUIT:
            Run = False
        p.control(e)
        if e.type == pygame.KEYDOWN:
            self.resolution += (int(e.key == pygame.K_LEFT) - int(e.key == pygame.K_RIGHT)) * 3

            if self.resolution < 1:
                self.resolution = 1

            if self.resolution > width:
                self.resolution = width

            if e.key == pygame.K_ESCAPE:
                choosen_game = 0


class Menu(Game):
    def __init__(self):
        self.games = ['Zombie', 'Options', 'Exit']
        self.c = 0

    def draw(self):

        global screen

        screen.fill((0, 0, 255))

        for i in range(len(self.games)):
            text = pygame.font.Font(None, 50).render(self.games[i], True, (255, 255, 255 * (self.c != i)))
            screen.blit(text, (75, 25 + i * 50))

        pygame.display.flip()

    def control(self, e):

        global Run, choosen_game

        if e.type == pygame.QUIT:
            Run = False
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_w:
                self.c -= 1
                self.c %= len(self.games)
            if e.key == pygame.K_s:
                self.c += 1
                self.c %= len(self.games)
            if e.key == pygame.K_RETURN:
                if self.games[self.c] == 'Exit':
                    Run = 0
                    return
                choosen_game = self.c + 2


class GameOver(Game):
    def control(self, e):

        global Run, choosen_game

        if e.type == pygame.QUIT:
            Run = False

        if e.type == pygame.KEYDOWN:
            choosen_game = 0
            return

    def draw(self):

        global screen, width, height

        screen.fill((0, 0, 255))

        text = pygame.font.Font(None, 50).render("Game over", True, (255, 255, 255))
        screen.blit(text, (width // 2 - text.get_width() // 2, height // 3))

        text = pygame.font.Font(None, 50).render("Press any button to go to menu", True, (255, 255, 255))
        screen.blit(text, (width // 2 - text.get_width() // 2, height // 2.5))

        pygame.display.flip()


class Options(Game):
    def __init__(self):

        global Start_Resolution

        super().__init__()
        self.options = ["Resolution", "Ray distance", "Exit"]
        self.par = [[Start_Resolution, 5, 1, 800], [Start_Max_Distance, 100, 500, 2000], ['']]
        self.c = 0

    def draw(self):

        global screen

        screen.fill((0, 0, 255))
        for i in range(len(self.options)):
            text = pygame.font.Font(None, 50).render(
                self.options[i] + f" {self.par[i][0]}", True, (255, 255, 255 * (i != self.c)))
            screen.blit(text, (100, 100 + i * 100))

        pygame.display.flip()

    def control(self, e):

        global Run, choosen_game, games, p

        if e.type == pygame.QUIT:
            Run = False
        if e.type == pygame.KEYDOWN:

            if e.key == pygame.K_w:
                self.c -= 1
                self.c %= len(self.options)

            if e.key == pygame.K_s:
                self.c += 1
                self.c %= len(self.options)

            if e.key == pygame.K_RETURN:
                if self.options[self.c] == 'Exit':
                    choosen_game = 0

            if e.key == pygame.K_d:
                if self.options[self.c] == 'Exit':
                    return
                self.par[self.c][0] += self.par[self.c][1]
                self.par[self.c][0] = min(max(self.par[self.c][0], self.par[self.c][2]), self.par[self.c][3])

            if e.key == pygame.K_a:
                if self.options[self.c] == 'Exit':
                    return
                self.par[self.c][0] -= self.par[self.c][1]
                self.par[self.c][0] = min(max(self.par[self.c][0], self.par[self.c][2]), self.par[self.c][3])

            games[2].resolution = self.par[0][0]
            p.mxd = self.par[1][0]


clock = pygame.time.Clock()

mn = 100

games = [Menu(), GameOver(), Zombie(), Options()]
choosen_game = 0

while Run:
    screen.fill((0, 0, 0))
    for event in pygame.event.get():
        games[choosen_game].control(event)
    games[choosen_game].draw()
    time1 = clock.tick()
    games[choosen_game].logic(time1)

pygame.quit()
