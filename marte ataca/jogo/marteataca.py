import pygame
import time
from random import randint

# Inicializando pygame
pygame.init()

# Configuração da Janela
LARGURA, ALTURA = 638, 368
WINDOW = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("MARTE ATACA")

# Configuração de cor
PRETO = (0, 0, 0)
VERDE = (0, 255, 0)
BRANCO = (255, 255, 255)
VERMELHO = (255, 0, 0)
AZUL = (0, 0, 255)
LARANJA = (255, 165, 0)

# Carregar imagens e sons
menu_image = pygame.image.load("jogo/img menu teste 3.jpg")
gameplay_image = pygame.image.load("jogo/img gameplay DFN.jpg")
player_image = pygame.image.load("jogo/nave jogador green.PNG")
enemy_image = pygame.image.load("jogo/nave do inimigo.png")
img_gameover = pygame.image.load("jogo/img gameouver DFN 2.jpg")
menu_sound = pygame.mixer.Sound("jogo/musica menu.ogg")
gameplay_sound = pygame.mixer.Sound("jogo/musica gameplay.mp3")

# Classe Base para Entidades
class Entity:
    def __init__(self, name, width, height, x, y, color_or_image):
        self.name = name
        if isinstance(color_or_image, pygame.Surface):  # Caso seja uma imagem
            self.surf = pygame.transform.scale(color_or_image, (width, height))
        else:  # Caso seja uma cor
            self.surf = pygame.Surface((width, height))
            self.surf.fill(color_or_image)
        self.rect = self.surf.get_rect(topleft=(x, y))

    def move(self):
        pass

    def draw(self, window):
        window.blit(self.surf, self.rect)

# Jogador
class Player(Entity):
    def __init__(self):
        super().__init__("Player", 50, 50, LARGURA // 2, ALTURA - 60, player_image)
        self.speed = 5
        self.lives = 3

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < LARGURA:
            self.rect.x += self.speed
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < ALTURA:
            self.rect.y += self.speed

    def shoot(self, entity_list):
        shot = PlayerShot(self.rect.centerx, self.rect.top)
        entity_list.append(shot)

# Tiro do Jogador
class PlayerShot(Entity):
    def __init__(self, x, y):
        super().__init__("PlayerShot", 5, 10, x - 2.5, y, VERDE)
        self.speed = -10

    def move(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            return False  # Remove do jogo
        return True

# Inimigo
class Enemy(Entity):
    def __init__(self, x, y):
        super().__init__("Enemy", 40, 40, x, y, enemy_image)
        self.speed = 1

    def move(self):
        self.rect.y += self.speed
        if self.rect.top > ALTURA:
            return False  # Remove do jogo
        return True

    def shoot(self, entity_list):
        if randint(2, 100) > 97:  # Pequena chance de atirar
            shot = EnemyShot(self.rect.centerx, self.rect.bottom)
            entity_list.append(shot)

# Tiro do Inimigo
class EnemyShot(Entity):
    def __init__(self, x, y):
        super().__init__("EnemyShot", 5, 10, x - 2.5, y, VERMELHO)
        self.speed = 5
        self.direction = 0  # 0 = reta, -1 = esquerda, 1 = direita

    def move(self):
        self.rect.y += self.speed
        self.rect.x += self.direction * 5
        if self.rect.top > ALTURA or self.rect.left < 0 or self.rect.right > LARGURA:
            return False  # Remove do jogo
        return True

# Gerenciador de Entidades
class EntityMediator:
    @staticmethod
    def detect_collisions(entity_list, player):
        for entity in entity_list:
            if isinstance(entity, EnemyShot) and player.rect.colliderect(entity.rect):
                player.lives -= 1
                entity_list.remove(entity)
                if player.lives <= 0:
                    return "Game Over"
            if isinstance(entity, Enemy) and player.rect.colliderect(entity.rect):
                player.lives -= 1
                entity_list.remove(entity)
                if player.lives <= 0:
                    return "Game Over"
        return "Playing"

# Tela de Níveis
class Level:
    def __init__(self, window):
        self.window = window
        self.entity_list = []
        self.last_spawn_time = time.time()
        self.spawn_interval = 1
        self.score = 0
        self.start_time = time.time()

    def spawn_enemies(self, count=1):
        for _ in range(count):
            x = randint(50, LARGURA - 50)
            y = -50
            self.entity_list.append(Enemy(x, y))

    def run(self, player):
        current_time = time.time()
        if current_time - self.start_time >= 1:
            self.score += 10
            self.start_time = current_time

        if current_time - self.last_spawn_time >= self.spawn_interval:
            self.spawn_enemies()
            self.last_spawn_time = current_time

        for entity in self.entity_list[:]:
            if not entity.move():
                self.entity_list.remove(entity)
            if isinstance(entity, Enemy):
                entity.shoot(self.entity_list)

        for entity in self.entity_list[:]:
            if isinstance(entity, PlayerShot):
                for target in self.entity_list[:]:
                    if isinstance(target, Enemy) and target.rect.colliderect(entity.rect):
                        self.entity_list.remove(target)
                        self.entity_list.remove(entity)
                        break

        return EntityMediator.detect_collisions(self.entity_list, player)

    def draw(self):
        for entity in self.entity_list:
            entity.draw(self.window)

# Tela do Menu
class Menu:
    def __init__(self, window):
        self.window = window

    def run(self):
        menu_sound.play(-1)
        font = pygame.font.Font(None, 50)
        title_font = pygame.font.Font(None, 80)

        title_text = title_font.render("MARTE ATACA", True, LARANJA)
        self.window.fill(PRETO)
        self.window.blit(menu_image, (0, 0))
        self.window.blit(title_text, (LARGURA // 2 - title_text.get_width() // 2, 50))

        text = font.render("PLay:  ENTER   ", True, BRANCO)
        self.window.blit(text, (LARGURA // 2 - text.get_width() // 2, ALTURA // 2 - text.get_height() // 2))
        pygame.display.flip()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    menu_sound.stop()
                    return

# Tela de Game Over
class GameOver:
    def __init__(self, window, score):
        self.window = window
        self.score = score

    def run(self):
        font = pygame.font.Font(None, 74)
        small_font = pygame.font.Font(None, 50)

        self.window.fill(PRETO)
        text = font.render("Game Over", True, BRANCO)
        score_text = small_font.render(f"Pontuação: {self.score:.2f}", True, BRANCO)

        self.window.blit(text, (LARGURA // 2 - text.get_width() // 2, ALTURA // 4))
        self.window.blit(score_text, (LARGURA // 2 - score_text.get_width() // 2, ALTURA // 2))
        pygame.display.flip()

        time.sleep(3)
        return

# Classe Principal do Jogo
class Game:
    def __init__(self):
        self.window = WINDOW
        self.clock = pygame.time.Clock()
        self.player = Player()
        self.level = Level(self.window)

    def run(self):
        while True:
            keys = pygame.key.get_pressed()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.player.shoot(self.level.entity_list)

            self.window.fill(PRETO)
            
            self.window.blit( gameplay_image, (0, 0))
            self.level.draw()
            self.player.move(keys)
            self.player.draw(self.window)

            status = self.level.run(self.player)
            if status == "Game Over":
                return self.level.score

            gameplay_sound.play(-1)
            font = pygame.font.Font(None, 36)
            score_text = font.render(f"Score: {self.level.score:.2f}", True, BRANCO)
            lives_text = font.render(f"Lives: {self.player.lives}", True, BRANCO)

            self.window.blit(score_text, (10, 10))
            self.window.blit(lives_text, (10, 50))

            pygame.display.flip()
            self.clock.tick(60)

# Executando o Jogo
def main():
    while True:
        menu = Menu(WINDOW)
        menu.run()

        game = Game()
        final_score = game.run()

        game_over = GameOver(WINDOW, final_score)
        game_over.run()

if __name__ == "__main__":
    main()
