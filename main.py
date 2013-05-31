import sys
from math import sin, cos, radians
from random import randint
import pygame

class Game:
    def __init__(self):
	pygame.init()
	# set up screen
	self.width, self.height = 600, 600
	self.screen = pygame.display.set_mode((self.width, self.height))
	pygame.display.set_caption("Hitch A Ride v0.42c - Cardboard")
	# set up sprite group and add sprites
	self.player = Player(self.height)
	self.cannon = Cannon(self.height)
	self.iid = Iid()
	# set up clock
	self.clock = pygame.time.Clock()
	self.fps = 60
	# colors
	self.color_bg = (16,16,16)
	# gameover overlays
	self.gameover = "no"
	self.gameover_win = pygame.transform.scale(pygame.image.load("win.png"), (self.width, self.height))
	self.gameover_lose = pygame.transform.scale(pygame.image.load("lose.png"), (self.width, self.height))
	# events
	self.NOT_RESCUED = pygame.USEREVENT
	self.RESCUED = pygame.USEREVENT+1
	# audio
	self.sound_dead = pygame.mixer.Sound("death.wav")
	self.sound_dead.set_volume(0.3)
	self.sound_launch = pygame.mixer.Sound("launch.wav")
	self.sound_launch.set_volume(0.5)
	self.sound_restart = pygame.mixer.Sound("restart.wav")
	self.sound_restart.set_volume(0.2)
	self.sound_rescued = pygame.mixer.Sound("rescued.wav")
	self.sound_rescued.set_volume(0.2)
	self.sound_iid = pygame.mixer.Sound("iid.wav")
	self.sound_win = pygame.mixer.Sound("win.wav")
	self.sound_win.set_volume(0.3)
	self.sound_lose = pygame.mixer.Sound("lose.wav")
	self.sound_lose.set_volume(0.3)
	pygame.mixer.music.load("music.wav")
	pygame.mixer.music.play(-1)

    def run(self):
	running = True
	while running == True:
	    # get change in ms since last tick (and tick the clock as well)
	    dt = self.clock.tick(self.fps)
	    # keypress events
	    for event in pygame.event.get():
		if event.type == pygame.QUIT:
		    pygame.quit()
		    sys.exit()
		if event.type == pygame.KEYDOWN:
		    # quit game
		    if event.key == pygame.K_ESCAPE:
			pygame.quit()
			sys.exit()
		    if event.key == pygame.K_RETURN:
			# clear overlay
			self.gameover = "no"
			# re-add sprites
			self.player = Player(self.height)
			self.cannon = Cannon(self.height)
			self.iid = Iid()
			# play sound
			self.sound_restart.play()
		if event.type == pygame.KEYUP:
		    # launch player!
		    if event.key == pygame.K_SPACE and self.cannon.fired == False:
			self.player.launch(self.cannon.speed_fire, self.cannon.rotation)
			self.sound_launch.play()
			self.cannon.fired = True
		if event.type == self.NOT_RESCUED: 
		    self.sound_lose.play()
		    self.player.dead = True
		    self.gameover = "lose"
		    pygame.time.set_timer(self.NOT_RESCUED, 0)
		if event.type == self.RESCUED:
		    self.sound_win.play()
		    self.gameover = "win"
		    pygame.time.set_timer(self.RESCUED, 0)
	    # launch the ship (after the player finishes moving)
	    if self.player.done_moving:
		self.iid.launched = True
	    # update everything
	    self.cannon.update(dt, self.screen, self)
	    self.player.update(dt, self.screen, self)
	    self.iid.update(dt, self.screen, self)
	    # draw everything
	    self.screen.fill(self.color_bg)
	    self.cannon.draw(self.screen)
	    self.player.draw(self.screen)
	    self.iid.draw(self.screen)
	    self.draw()
	    pygame.display.update()

    def draw(self):
	if self.gameover == "win":
	    self.screen.blit(self.gameover_win, (0,0))
	if self.gameover == "lose":
	    self.screen.blit(self.gameover_lose, (0,0))
	else:
	    pass

class Player(pygame.sprite.Sprite):
    def __init__(self, scrHeight):
	super(Player, self).__init__()
	# load image, set starting pos, etc.
	self.image_default = pygame.image.load("player.png")
	self.image = self.image_default
	self.image_dead = pygame.image.load("player_dead.png")
	self.width, self.height = 42, 42
	self.rect = pygame.Rect(0, 0, self.width, self.height)
	self.rect.topleft = (0, scrHeight - self.height)
	# other player things
	self.draw_me = False
	self.dead = False
	self.rescued = 0
	self.launched = False
	self.done_moving = False
	self.angle = 0
	self.speed = 0
	self.speed_rotate = 0.02
	self.rotation = randint(0, 360)
	self.slow_speed = 500.0 # speed at which player slows down (low # = slows faster)
	self.xvel = 0
	self.yvel = 0
	self.lr = 1 # 1 if moving right, -1 if moving left
	self.ud = -1 # 1 if moving down, -1 if moving up

    def update(self, dt, screen, game):
	# still moving
	if self.speed > 0.0:
	    self.speed -= dt / self.slow_speed 
	else:
	    self.speed = 0
	if self.launched and self.speed == 0:
	    self.done_moving = True
	# check for collisions and adjust velocity accordingly
	if self.rect.x < 0 or self.rect.x > (game.width - self.width):
	    self.lr *= -1
	if self.rect.y < 0 or self.rect.y > (game.height - self.height):
	    self.ud *= -1
	# calculate velocities
	xvel = abs( self.speed * cos(self.angle) )
	yvel = abs( self.speed * sin(self.angle) )
	# move player
	self.rect.x += self.lr * xvel
	self.rect.y += self.ud * yvel
	# check if dead
	self.die()
	# rotate forever
	self.rotation += dt * self.speed_rotate
	self.image = pygame.transform.rotate(self.image, self.rotation)

    def launch(self, launch_speed, launch_angle):
	self.draw_me = True
	self.launched = True
	self.speed = launch_speed
	self.angle = launch_angle

    def die(self):
	# ending animation/cutscene thing when you die
	if self.dead:
	    self.image = self.image_dead
	else:
	    self.image = self.image_default

    def reset(self, scrHeight):
	self.__init__(scrHeight)

    def draw(self, screen):
	if self.draw_me:
	    screen.blit(self.image, self.rect)


class Cannon(pygame.sprite.Sprite):
    def __init__(self, scrHeight):
	super(Cannon, self).__init__()
	# image and rect
	self.image_default = pygame.image.load("cannon.png")
	self.image = self.image_default
	self.width, self.height = 42, 42
	self.rect = pygame.Rect(0, 0, self.width, self.height)
	self.rect.topleft = (-10, scrHeight - self.height+10)
	# cannon can only be fired once per game
	self.draw_me = True
	self.fired = False
	self.rotation = 0
	self.speed_rotate = 0.1 # speed cannon rotates at
	self.speed_fire = 10 # current speed player will be launched at

    def update(self, dt, screen, game):
	# cannon rotation
	if self.rotation > 90:
	    self.speed_rotate *= -1 # reverse rotation when angle outside (0,90)
	    self.rotation = 90
	if self.rotation < 0:
	    self.speed_rotate *= -1
	    self.rotation = 0
	self.rotation += dt * self.speed_rotate
	self.image = pygame.transform.scale(pygame.transform.rotate(self.image_default, self.rotation), (self.width, self.height))

    def reset(self, scrHeight):
	self.__init__(scrHeight)

    def draw(self, screen):
	if self.draw_me:
	    screen.blit(self.image, self.rect)


class Iid(pygame.sprite.Sprite):
    def __init__(self):
	super(Iid, self).__init__()
	# image and rect
	self.image_default = pygame.image.load("iid.png")
	self.image = self.image_default
	self.width, self.height = 600, 600
	self.rect = pygame.Rect(0, 0, self.width, self.height)
	self.rect.center = (-self.width, -self.height)
	# other variables
	self.draw_me = True
	self.z = 300 # distance from plane of the monitor
	self.speed = 0.1
	self.launched = False
	self.pos = (-1, -1)
	self.collision_point = 50 # z-coordinate where collision is checked

    def update(self, dt, screen, game):
	# the ship has begun to fly (player has launched and has stopped moving)
	if self.launched:
	    size = int(self.width * self.z/100)
	    # generate random coordinates if not done so already
	    if self.pos == (-1, -1): 
		game.sound_iid.play()
		self.pos = (randint(10, game.width-10), randint(10, game.height-10))
		self.image = pygame.transform.scale(self.image_default, (size, size)) 
	    if self.z <= self.collision_point:
		if self.rect.colliderect(game.player):
		    game.player.draw_me = False
		    game.player.rescued = 1
		    game.sound_rescued.play()
		    pygame.time.set_timer(game.RESCUED, 1000)
	    if size <= 0:
		if game.player.rescued == 0:
		    game.sound_dead.play()
		    pygame.time.set_timer(game.NOT_RESCUED, 1000)
		    game.player.rescued = -1
		self.draw_me = False
		return

	    self.z -= dt * self.speed
	    self.image = pygame.transform.scale(self.image_default, (size, size))
	    self.rect = self.image.get_rect()
	    self.rect.center = self.pos
    def reset(self):
	self.__init__()

    def draw(self, screen):
	if self.draw_me:
	    screen.blit(self.image, self.rect)



if __name__ == '__main__':
    game = Game()
    game.run()
