import pygame
import sys
import random
import asyncio

#status

# Screen dimensions (These need to be *outside* the functions)
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):
        super().__init__()
        
        image1 = pygame.image.load("graphics/Fly/Fly1.png").convert_alpha()
        image2 = pygame.image.load("graphics/Fly/Fly2.png").convert_alpha()
        
        # Resize images to 50x50
        image1 = pygame.transform.scale(image1, (60, 50))
        image2 = pygame.transform.scale(image2, (60, 50))
        
        self.images = [image1, image2]
        self.current_image = 0
        self.image = self.images[self.current_image]
        
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        
        #self.image = pygame.Surface((width, height))
        self.speed = speed
        self.last_image_change = pygame.time.get_ticks()  # Initialize last_image_change
        self.image_change_delay = 100  # Initialize image_change_delay  <--- THIS WAS MISSING

    def update(self):
        # Store the current position
        current_x = self.rect.x
        current_y = self.rect.y
        
        # Move the obstacle
        current_x -= self.speed
        
        # Reset position if off screen
        if current_x + self.rect.width < 0:
            current_x = WIDTH
            current_y = random.randint(0, HEIGHT - self.rect.height)
        
        # Handle animation
        current_time = pygame.time.get_ticks()
        if current_time - self.last_image_change > self.image_change_delay:
            self.current_image = (self.current_image + 1) % len(self.images)
            self.image = self.images[self.current_image]
            # Get new rect but maintain position
            self.rect = self.image.get_rect()
            self.rect.x = current_x
            self.rect.y = current_y
            self.last_image_change = current_time
        else:
            # Update position without changing rect
            self.rect.x = current_x
            self.rect.y = current_y

def create_obstacles(num_obstacles, speed):  # Corrected function
    obstacles = pygame.sprite.Group()
    spacing = WIDTH // num_obstacles

    for i in range(num_obstacles):
        x = WIDTH + i * spacing
        y = random.randint(0, HEIGHT - 50)
        obstacle = Obstacle(x, y, speed)
        obstacles.add(obstacle)
    return obstacles


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        #self.image = pygame.Surface((width, height))
        #self.image.fill(BLACK)
        self.image = pygame.image.load("graphics/Player/player_stand.png")
        self.image = pygame.transform.scale(self.image, (50, 50))
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.gravity = 0.2
        self.gravity_direction = 1
        self.velocity_y = 0

    def update(self):
        self.velocity_y += self.gravity * self.gravity_direction
        self.rect.y += self.velocity_y

        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
            self.velocity_y = 0

        elif self.rect.top < 0:
            self.rect.top = 0
            self.velocity_y = 0

    def reverse_gravity(self):
        self.gravity_direction *= -1
        self.velocity_y = 0


async def game_loop():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Gravity Reversal Game")
    font = pygame.font.Font(None, 74)

    def restart_game():
        player.rect.x = 50
        player.rect.y = HEIGHT // 2 - 25
        player.velocity_y = 0
        player.gravity_direction = 1
        obstacles = create_obstacles(10, 2)  # Recreate obstacles
        all_sprites.empty() # Clear old sprites
        all_sprites.add(player)
        all_sprites.add(obstacles)
        return 0, set(), obstacles # Return new obstacles

    def show_game_over_screen(score):
        game_over_text = font.render("Game Over", True, RED)
        restart_text = font.render("Click to Restart", True, RED)
        score_text = font.render(f"Score: {score}", True, RED)
        screen.fill(WHITE)
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 4))
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2))
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 + 60))
        pygame.display.flip()

    player = Player(50, HEIGHT // 2 - 25, 50, 50)  # Start in the middle
    all_sprites = pygame.sprite.Group(player)

    obstacles = create_obstacles(10, 2)
    all_sprites.add(obstacles)

    score = 0
    passed_obstacles = set()

    clock = pygame.time.Clock()
    FPS = 60

    game_over = False
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if not game_over:  # Only allow space if not game over
                        player.reverse_gravity()
                    elif game_over:
                        score, passed_obstacles, obstacles = restart_game()
                        game_over = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not game_over:
                        player.reverse_gravity()
                    elif game_over:
                        score, passed_obstacles = restart_game() # Corrected restart_game call
                        game_over = False

        if not game_over:
            all_sprites.update()

            for obstacle in obstacles:
                if obstacle.rect.right < player.rect.left and obstacle not in passed_obstacles:
                    score += 1
                    passed_obstacles.add(obstacle)

            if pygame.sprite.spritecollideany(player, obstacles):
                game_over = True
                show_game_over_screen(score)  # Show game over screen immediately

        if not game_over: # Only draw and update if game is running
            screen.fill(WHITE)
            text_surface = font.render(f"Score: {score}", True, RED)
            screen.blit(text_surface, (20, 20))
            all_sprites.draw(screen)
            pygame.display.flip()

        clock.tick(FPS)
        await asyncio.sleep(0)

    pygame.quit()


async def main():
    await game_loop()
    sys.exit()


if __name__ == "__main__":
    asyncio.run(main())