import pygame, sys, random
from pygame import Vector2 as vector

# initialize pygame
pygame.init()

# Set display surface and set caption
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 200 

display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Dinosaur Game")

# Define classes
class Player(pygame.sprite.Sprite):
    """A class to represent the player"""
    def __init__(self, x, y, enemy_group, floor_group):
        """Initializes the player"""
        super().__init__()

        # All possible sprites for the player to have 
        self.sprites = [
            pygame.image.load("assets/images/DinosaurStatic.png"), # 0
            pygame.image.load("assets/images/DinosaurRun1.png"),   # 1 
            pygame.image.load("assets/images/DinosaurRun2.png"),   # 2  
            pygame.image.load("assets/images/DinosaurJump.png"),   # 3  
            pygame.image.load("assets/images/DinosaurDuck1.png"),  # 4 
            pygame.image.load("assets/images/DinosaurDuck2.png"),  # 5
            pygame.image.load("assets/images/DinosaurDie.png")     # 6
            ]


        # This pevents the player from jumping when they press space to reset the game
        self.space_was_to_reset = False

        # Scales down all of the images to be 32 by 32 opposed to larger
        self.sprites = [pygame.transform.scale(sprite, (56, 62)) for sprite in self.sprites]

        # The ducking sprites will need special scalings
        self.sprites[4] = pygame.transform.scale(self.sprites[4], (86, 42))
        self.sprites[5] = pygame.transform.scale(self.sprites[5], (86, 42))

        # Is used to check if the player has died or is on the ground
        self.enemy_group = enemy_group
        self.floor_group = floor_group

        # Boolean values used to dictate the seelct sprites the player is going ot use 
        self.is_static = False 
        self.is_running = True  
        self.is_jumping = False 
        self.is_ducking = False 

        # Kinematics vectors (first value is x, the second value is y)
        self.position = vector(x, y)
        self.vertical_velocity = 0
        self.last_vertical_velocity = 0
        self.acceleration = 0

        # Kinematics constnats
        self.VERTICAL_ACCELERATION = 2 # Gravity
        self.VERTICAL_JUMP_SPEED = 25 # Determines how high the dinosaur can jump

        # Positions the player, starting with the static sprite on the screen
        self.current_sprite = 1 
        self.image = self.sprites[self.current_sprite]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = self.position

        self.game_over = False 

    def update(self):
        """Flips between the player's sprites as necessary"""
        if self.game_over:
            self.image = self.sprites[self.current_sprite]


        if not self.game_over or self.is_ducking:
            # See if the player wants to jump
            self.acceleration = self.VERTICAL_ACCELERATION

            # Store the previous vertical velocity value so that the player does not do anything weird while in mid air
            self.last_vertical_velocity = self.vertical_velocity

            # Calculate new kinematics values
            self.vertical_velocity += self.acceleration 


            self.position.y += self.vertical_velocity + 0.5*self.acceleration

            # Check for collisions with the floor
            collided_platforms = pygame.sprite.spritecollide(self, self.floor_group, False) 
            if collided_platforms:
                if self.vertical_velocity > 0:
                    self.position.y = collided_platforms[0].rect.top + 20 
                    self.vertical_velocity = 0

        if not self.game_over:

            # See how the player is moving 
            self.check_status()

            if self.is_running:
                if self.current_sprite > 2:
                    self.current_sprite = 1 
                else:
                    self.current_sprite += 0.5 

            elif self.is_jumping:
                self.current_sprite = 3

            elif self.is_ducking:
                self.current_sprite += 1
                if self.current_sprite < 4 or self.current_sprite > 5:
                    self.current_sprite = 4

            # Check if the player wants to jump (cannot do this in the event loop because the player must jump multiple times if the space bar is held down)
            self.jump()
        # Set the image to the correct sprite
        self.image = self.sprites[int(self.current_sprite)]

        # Set the rect size appropriately
        self.rect.size = self.image.get_rect().size

        # Update new rects based on kinematic caclulations
        self.rect.bottomleft = self.position


    def jump(self):
        """Allows the player to jump"""
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_SPACE] or keys[pygame.K_UP]:
            if pygame.sprite.spritecollide(self, self.floor_group, False):
                self.vertical_velocity = -1*self.VERTICAL_JUMP_SPEED

    def check_status(self):
        if self.vertical_velocity != 0 and self.last_vertical_velocity != 0:
            self.is_jumping = True
            self.is_running = False
            self.is_ducking = False

        if self.vertical_velocity == 0 and self.last_vertical_velocity == 0:
            self.is_running = True
            self.is_ducking = False
            self.is_jumping = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_DOWN] and self.vertical_velocity == 0 and self.last_vertical_velocity == 0: 
            self.is_ducking = True
            self.is_jumping = False
            self.is_running = False  

class Floor(pygame.sprite.Sprite):
    """A class to represent the floor that the player and enemies are on"""
    def __init__(self, x, y, velocity):
        """Initializes the floor"""
        super().__init__()
        self.game_over = False 

        self.image = pygame.transform.scale(pygame.image.load("assets/images/Floor.png"), (1200, 12))
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (x, y)
        self.floor_can_be_added = True 
        
        self.velocity = int(velocity) 

        floor_group.add(self)

    def update(self):
        """Moves the floor of the game"""

        if self.game_over:
            return

        if self.floor_can_be_added and (WINDOW_WIDTH - self.rect.right) > 0:
            Floor(self.rect.bottomright[0] - 10,  self.rect.bottomright[1], self.velocity)
            self.floor_can_be_added = False

        if self.rect.right < 0:
            self.kill()

        self.rect.left -= int(self.velocity)


class Cactus(pygame.sprite.Sprite):
    """A class to represent cactuses that the player must jump over"""
    def __init__(self, velocity):
        super().__init__()
        self.game_over = False

        available_cactuses = [
            pygame.image.load("assets/images/SingularCactus.png"),
            pygame.image.load("assets/images/DoubleCactus.png"),
            pygame.image.load("assets/images/ClusterCactus.png")
        ]


        self.image = random.choice(available_cactuses)

        self.image_size = random.choice([32, 64])

        self.image = pygame.transform.scale(self.image, (self.image_size, self.image_size))
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (WINDOW_WIDTH + 50, floor.rect.topleft[1]+20)

        # Velocity should be the same as the floor
        self.velocity = int(velocity)

    def update(self):

        if self.game_over:
            return 

        self.rect.left -= self.velocity

        if self.rect.right < 0:
            self.kill()


class Ptyrodactyl(pygame.sprite.Sprite):
    """A class to represent ptyrodactyls that act as barriers for the player"""
    def __init__(self, velocity):
        """Initializes the ptyrodactyl"""
        super().__init__()
        self.game_over = False

        self.sprites = [
            pygame.transform.scale(pygame.image.load("assets/images/Ptyrodactyl1.png"), (60, 36)), 
            pygame.transform.scale(pygame.image.load("assets/images/Ptyrodactyl2.png"), (60, 28))
            ]

        self.heights = [
            floor.rect.topleft[1],
            115,
            140
        ]

        self.flying_height = random.choice(self.heights)

        self.current_image = 0
        self.velocity = int(velocity)

        self.image = self.sprites[self.current_image]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (WINDOW_WIDTH + 50, self.flying_height)


    def update(self):
        """Moves the ptyrodactly and flaps its wings"""

        if self.game_over:
            return

        self.current_image += 1
        if self.current_image > 1:
            self.current_image = 0

        self.rect.left -= int(self.velocity)
        if self.rect.right < 0:
            self.kill()

        self.image = self.sprites[self.current_image]

class ResetButton(pygame.sprite.Sprite):
    """A class to represent the reset button on the game over screen"""
    def __init__(self, button_group):
        """Initializes the reset button"""
        super().__init__()
        self.image = pygame.image.load("assets/images/ResetButton.png")
        self.rect = self.image.get_rect()
        self.rect.center = (WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 30)

        button_group.add(self)

    

class Game:
    """A class to help organize and  manage gameplay"""
    def __init__(self, enemy_group, floor_group, player): # Will need a cloud group later on 
        """Initializes the game"""
        # Groups and player sprite
        self.enemy_group = enemy_group
        self.floor_group = floor_group
        self.player = player

        # Set game values
        self.points = 0
        self.highest_score = 0

        self.enemy_threshold = 100 

        self.game_over = False

        self.reset_button = None # Will later be used

        # These will be used to flash the point number every 100 points
        self.last_hundred = 0
        self.reached_hundred_more = False
        self.flash_num = 0
        self.last_interval_of_five = 0
        self.score_on = False

        # Velocity for the cactus
        self.enemy_velocity = 8 
        # Set font
        self.font = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 14)

    def update(self):
        """updates the game"""
        if self.reached_hundred_more == True:
            self.flash_num += 1
            if self.flash_num > 35:
                self.reached_hundred_more = False
                self.flash_num = 0
                self.last_interval_of_five = 0

            if self.flash_num - 5  == self.last_interval_of_five:
                self.last_interval_of_five = self.flash_num
                
                if self.score_on:
                    self.score_on = False
                else:
                    self.score_on = True 

        self.check_speed_increase()

        if self.points != 0 and int(self.points) - 100 == self.last_hundred: # Remember to set back to 100
            self.last_hundred = int(self.points)
            self.reached_hundred_more = True

        if self.game_over:
            return

        # Increment the number of points
        if not self.reached_hundred_more:
            self.points += 0.2 # Represent this as an integer when displaying it to the screen 

        self.generate_enemies()
        self.check_collisions()

    def check_collisions(self):
       if pygame.sprite.spritecollide(player, enemy_group, False):
           self.update_highest_score()
           self.player.current_sprite = -1
           self.signal_game_over(True)


    def draw(self):
        """Draws the player's scores"""
        if self.game_over:
            game_over_text = pygame.image.load("assets/images/GameOver.png")
            game_over_rect = game_over_text.get_rect()
            game_over_rect.center = (WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 30)

            display_surface.blit(game_over_text, game_over_rect)

        score = self.font.render("0"*(6-len(list(str(int(self.points))))) + str(int(self.points)), True, (10, 10, 10))
        score_rect = score.get_rect()

        if not self.game_over:
            with open("highest_score.txt") as f:
                self.highest_score = int(f.read())
                if len(list(f)) == 0:
                    highest_score = 0
                else:
                    highest_score = f.read()  
        highest_score = self.font.render("HI " + "0"*(6-len(list(str(int(self.highest_score))))) + str(int(self.highest_score)), True, (10, 10, 10))
        highest_score_rect = highest_score.get_rect()


        highest_score_rect.topright = (WINDOW_WIDTH - 90, 10)


        score_rect.topright = (WINDOW_WIDTH, 10)

        if not self.reached_hundred_more or self.score_on: 
            display_surface.blit(score, score_rect)

        if self.highest_score > 0:
            display_surface.blit(highest_score, highest_score_rect)

    def generate_enemies(self):
        # Choose whether enemy is going to be ptyrodactyl or cactus
        for enemy in self.enemy_group:
            if enemy.rect.x > self.enemy_threshold:
                return

        if self.points > 500:
            enemy = random.choice([1, 2])
            if enemy == 1:
                enemy_group.add(Ptyrodactyl(self.enemy_velocity))
            else:
                enemy_group.add(Cactus(self.enemy_velocity))
        else:
            enemy_group.add(Cactus(self.enemy_velocity))

    def reset_game(self):
        self.points = 0
        self.enemy_group.empty()
        self.player.position = vector(90, 198)
        self.reached_hundred_more = False

        # Reset velocities
        self.enemy_velocity = 8 
        for floor in self.floor_group:
            floor.velocity = 8 

        for enemy in self.enemy_group:
            enemy.velocity = 8 


    def signal_game_over(self, boolean): 
        if boolean:
            self.reset_button = ResetButton(button_group)
        else:
            button_group.empty()
            self.reset_button = None
            

        self.game_over = boolean 
        self.player.game_over = boolean 
        
        for floor in floor_group:
            floor.game_over = boolean 

        for enemy in enemy_group:
            enemy.game_over = boolean

        for cloud in cloud_group:
            cloud.game_over = boolean 

    def update_highest_score(self):
        """Updates the highest score for the game"""
        with open("highest_score.txt", "r+") as f:
            f.seek(0) 
            score = int(f.readline()) 
            if score == 0 or score < self.points:
                f.seek(0)
                f.write(str(int(self.points)))
                f.truncate()

    def check_speed_increase(self):
        # Display the values
        if int(self.points - 100) == self.last_hundred:
            self.enemy_velocity += 0.5 
            # Increase the floor's velocity
            for floor in self.floor_group:
                floor.velocity += 0.5  

            for enemy in self.enemy_group:
                enemy.velocity += 0.5


class Cloud(pygame.sprite.Sprite):
    """A class to0 represent the clouds in the game"""
    def __init__(self, cloud_group):
        super().__init__()
        self.starting_x = WINDOW_WIDTH + 1
        
        self.image = pygame.image.load("assets/images/Cloud.png")
        self.rect = self.image.get_rect()
        self.heights = [

            20,
            50,
            70,
        ]

        self.game_over = False 

        self.rect.topleft = (self.starting_x, random.choice(self.heights))
        self.velocity = 2
        self.cloud_group = cloud_group

        self.threshold = 301

    def update(self):
        if not self.game_over:
            self.rect.left -= self.velocity

            if self.rect.left == self.threshold:
                self.cloud_group.add(Cloud(self.cloud_group))

            if self.rect.right < 0:
                self.kill()

    
# Set FPS and clock
FPS = 60
clock = pygame.time.Clock()

button_group = pygame.sprite.Group()

floor_group = pygame.sprite.Group()
floor = Floor(90, WINDOW_HEIGHT - 10, 8)

cloud_group = pygame.sprite.Group()
cloud = Cloud(cloud_group)
cloud_group.add(cloud)

enemy_group = pygame.sprite.Group()

player = Player(floor.rect.topleft[0], floor.rect.topleft[1]+20, enemy_group, floor_group)
player_group = pygame.sprite.Group()
player_group.add(player)

enemy_group = pygame.sprite.Group()

game = Game(enemy_group, floor_group, player)

# Main game loop
while True:
    for event in pygame.event.get():
        # Check if the user wants to quit
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if game.game_over and event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
            player.space_was_to_reset = True
            game.signal_game_over(False)
            game.reset_game()

        if event.type == pygame.MOUSEBUTTONUP and game.reset_button:
            if game.reset_button.rect.collidepoint(event.pos):
                game.signal_game_over(False)
                game.reset_game()

    # Fill the display
    display_surface.fill((255, 255, 255))

    # Draw and update the sprite groups
    button_group.draw(display_surface)

    floor_group.draw(display_surface)
    floor_group.update()

    cloud_group.draw(display_surface)
    cloud_group.update()

    enemy_group.draw(display_surface)
    enemy_group.update()

    game.update()
    game.draw()

    player_group.update()
    player_group.draw(display_surface)

    # Update display and tick the clock
    pygame.display.update()
    clock.tick(FPS)