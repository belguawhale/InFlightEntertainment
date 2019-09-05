import os, sys, math, traceback, random
import pygame
from pygame.locals import *

pygame.init()

size = width, height = 800, 600

class Tank(pygame.sprite.Sprite):
    def __init__(self, image_file, keymap, dircolour=(255, 0, 0), colorkey=-1, speed=6, rotspeed=0.1, ammo=5, reload_delay=60*0.1):
        # keymap = [up, down, rotate left, rotate right, fire]
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image(image_file, colorkey)
        self.keymap = keymap
        self.dircolour = dircolour
        self.speed = speed
        self.rotspeed = rotspeed
        self.vel = [0, 0]
        self.direction = 0 # radians
        self.max_bullets = ammo
        self.reload_delay = reload_delay
        self.reload = 0

        self.bullets = []

        self.REVERSEMODIFIER = 0.6

        self.alive = True

    def move(self, x=None, y=None):
        if x is None or y is None:
            self.rect.move_ip(self.vel)
        else:
            self.rect.move_ip(x, y)

    def register_keys(self):
        keys = pygame.key.get_pressed()
        directions = [keys[x] for x in self.keymap]

        if self.alive:
            if directions[0]:
                self.vel = [self.speed * math.sin(self.direction), -self.speed * math.cos(self.direction)]
            elif directions[1]:
                self.vel = [self.REVERSEMODIFIER * -self.speed * math.sin(self.direction),
                            self.REVERSEMODIFIER * self.speed * math.cos(self.direction)]
            else:
                self.vel = [0, 0]

            if directions[2]:
                self.direction -= self.rotspeed
            elif directions[3]:
                self.direction += self.rotspeed
            
            if directions[4]: # fire!
                if self.reload == 0:
                    if len(self.bullets) < self.max_bullets:
                        self.reload = -1 # held key on last frame
                        self.bullets.append(Bullet(self.calc_direction_pos(*self.vel, multiplier=1.5), self.direction))
            elif self.reload == -1:
                # not holding the key anymore
                self.reload = self.reload_delay
        else:
            self.vel = [0, 0]

    def calc_direction_pos(self, offsetx=0, offsety=0, multiplier=1):
        radius = self.rect.size[0] / 2
        center = self.rect.center
        return (center[0] + offsetx + multiplier * radius * math.sin(self.direction),
                center[1] + offsety - multiplier * radius * math.cos(self.direction))

    def show_direction(self):
        indicator_pos = self.calc_direction_pos()
        pygame.draw.line(screen, self.dircolour, self.rect.center, indicator_pos, 5)
    
    def spawn(self):
        self.rect.center = (random.randrange(0, width), random.randrange(0, height))
        self.direction = random.random() * 2 * math.pi
        self.vel = [0, 0]
        self.bullets = []
        self.ammo = self.max_bullets
        self.alive = True

    def die(self):
        self.alive = False


class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, direction, image_file='bullet.png', colorkey=-1, speed=7, duration=60*10):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image(image_file, colorkey)
        self.rect.center = pos
        self.speed = speed
        self.vel = [0, 0]
        self.direction = direction
        self.duration = duration

    def calc_movement(self):
        self.vel = [self.speed * math.sin(self.direction), -self.speed * math.cos(self.direction)]

    def move(self, x=None, y=None):
        if x is None or y is None:
            self.rect.move_ip(self.vel)
        else:
            self.rect.move_ip(x, y)

black = 0, 0, 0

screen = pygame.display.set_mode(size)
pygame.display.set_caption("TankTrouble test")

def load_image(name, colorkey=None):
    fullname = os.path.join('assets', name)
    image = pygame.image.load(fullname)
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()

def load_sound(name):
    class NoneSound:
        def play(self): pass
    if not pygame.mixer:
        return NoneSound()
    fullname = os.path.join('data', name)
    sound = pygame.mixer.Sound(file=fullname)
    return sound

players = [Tank('circular belgua.png', [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_m], dircolour=(0, 255, 255)),
           Tank('circular beluga.png', [pygame.K_e, pygame.K_d, pygame.K_s, pygame.K_f, pygame.K_q])]


platforms = [pygame.Rect(150, 200, 75, 10), pygame.Rect(500, 300, 100, 10), pygame.Rect(600, 110, 10, 400),
             pygame.Rect(400, 210, 10, 100), pygame.Rect(475, 100, 125, 10), pygame.Rect(700, 110, 10, 490),
             pygame.Rect(200, 500, 50, 10), pygame.Rect(400, 400, 50, 10), pygame.Rect(400, 200, 100, 10),
             pygame.Rect(400, 100, 10, 10), pygame.Rect(350, 125, 10, 75)]

clock = pygame.time.Clock()

for player in players:
    player.spawn()


while 1:
    clock.tick(60)
    screen.fill(black)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                sys.exit()
            elif event.key == pygame.K_BACKSLASH:
                for player in players:
                    player.spawn()
            elif event.key == pygame.K_BACKQUOTE:
                text = ""
                while True:
                    text = input(">>> ")
                    if text in ('exit', 'exit()'):
                        break
                    try:
                        print(eval(text))
                    except SyntaxError:
                        try:
                            exec(text)
                        except:
                            traceback.print_exc()
                    except:
                        traceback.print_exc()

    for platform in platforms:
        pygame.draw.rect(screen, (255, 255, 255), platform)

    pygame.draw.rect(screen, (255, 255, 0), pygame.Rect(150, 200, 75, 10))

    for player in players:
        player.register_keys()
        player.move()
        for platform in platforms:
            player.move(0, -player.vel[1])
            if platform.colliderect(player.rect):
                if player.vel[0] > 0:
                    player.rect.right = platform.left
                    player.vel[0] = 0
                elif player.vel[0] < 0:
                    player.rect.left = platform.right
                    player.vel[0] = 0
            player.move(0, player.vel[1])
            if platform.colliderect(player.rect):
                if player.vel[1] > 0:
                    player.rect.bottom = platform.top
                    player.vel[1] = 0
                elif player.vel[1] < 0:
                    player.rect.top = platform.bottom
                    player.vel[1] = 0

        if player.rect.left < 0:
            player.rect.left = 0
            player.vel[0] = 0
        elif player.rect.right > width:
            player.rect.right = width
            player.vel[0] = 0
        if player.rect.top < 0:
            player.rect.top = 0
            player.vel[1] = 0
        elif player.rect.bottom > height:
            player.rect.bottom = height
            player.vel[1] = 0
        
        if player.alive:
            screen.blit(player.image, player.rect)
            player.show_direction()

    for player in players:
        if player.reload > 0:
            # if reloading and not holding key
            player.reload -= 1
        for bullet in player.bullets:
            bullet.duration -= 1
            if bullet.duration > 0:
                bullet.calc_movement()
                bullet.move()
                for platform in platforms:
                    bullet.move(0, -bullet.vel[1])
                    if platform.colliderect(bullet.rect):
                        if bullet.vel[0] > 0:
                            bullet.rect.right = platform.left
                            bullet.direction *= -1
                        elif bullet.vel[0] < 0:
                            bullet.rect.left = platform.right
                            bullet.direction *= -1
                    bullet.move(0, bullet.vel[1])
                    if platform.colliderect(bullet.rect):
                        if bullet.vel[1] > 0:
                            bullet.rect.bottom = platform.top
                            bullet.direction = math.pi - bullet.direction
                        elif bullet.vel[1] < 0:
                            bullet.rect.top = platform.bottom
                            bullet.direction = math.pi - bullet.direction
                
                for playertest in players:
                    if playertest.alive:
                        if bullet.rect.colliderect(playertest.rect):
                            playertest.die()
                            player.bullets.remove(bullet)
                        

                if bullet.rect.left < 0:
                    bullet.rect.left = 0
                    bullet.direction *= -1
                elif bullet.rect.right > width:
                    bullet.rect.right = width
                    bullet.direction *= -1
                if bullet.rect.top < 0:
                    bullet.rect.top = 0
                    bullet.direction = math.pi - bullet.direction
                elif bullet.rect.bottom > height:
                    bullet.rect.bottom = height
                    bullet.direction = math.pi - bullet.direction
            else:
                player.bullets.remove(bullet)
            
            screen.blit(bullet.image, bullet.rect)

    pygame.display.flip()
