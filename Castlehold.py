import pygame #herramientas para el juego
import sys # para manejar las salidas del programa
import random #para obtener valores random (obtener numeros aleatorios)
import os  #para operaciones del sistema 
from datetime import datetime #para obtener fechas

# ====== Configuración ======
#variables en mayuscula por convención 
ANCHO, ALTO = 800, 450
FPS = 60
COLOR_FONDO = (20, 20, 30)
COLOR_CASTILLO = (80, 80, 200)
COLOR_JUGADOR = (200, 200, 240)
COLOR_ENEMIGO = (200, 80, 80)
COLOR_BALA = (250, 250, 100)
COLOR_BARRA_VIDA = (80, 200, 80)
COLOR_BARRA_VACIA = (200, 50, 50)

pygame.init() #inicia pygame
pantalla = pygame.display.set_mode((ANCHO, ALTO)) #establece pantalla con valores ya establecidos
pygame.display.set_caption("Defiende el castillo") #nombre
clock = pygame.time.Clock() #establece la velocidad a la que va a correr el juego 
fuente = pygame.font.SysFont("consolas", 20)


# ====== Clases ======
class Jugador(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill(COLOR_JUGADOR)
        self.rect = self.image.get_rect(center=(x, y))
        self.vel_y = 0
        self.velocidad = 5

    def manejar_input(self, teclas):
        self.vel_y = 0
        if teclas[pygame.K_UP]:
            self.vel_y = -self.velocidad
        if teclas[pygame.K_DOWN]:
            self.vel_y = self.velocidad

    def update(self):
        teclas = pygame.key.get_pressed()
        self.manejar_input(teclas)

        # mover
        self.rect.y += self.vel_y

        # límites
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > ALTO:
            self.rect.bottom = ALTO

    def disparar(self, balas):
        bala = Bala(self.rect.right, self.rect.centery)
        balas.add(bala)


class Bala(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((12, 6))
        self.image.fill(COLOR_BALA)
        self.rect = self.image.get_rect(center=(x, y))
        self.vel_x = 10

    def update(self):
        self.rect.x += self.vel_x
        if self.rect.left > ANCHO:
            self.kill()


class Enemigo(pygame.sprite.Sprite):
    def __init__(self, y, velocidad):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(COLOR_ENEMIGO)
        self.rect = self.image.get_rect(midright=(ANCHO, y))
        self.vel_x = velocidad

    def update(self):
        self.rect.x += self.vel_x
        if self.rect.right < 50:  # tocó el castillo
            self.kill()
            return "castillo"
        return None


# ====== Juego ======
class Juego:
    def __init__(self):
        self.jugador = Jugador(60, ALTO // 2)
        self.sprites = pygame.sprite.Group(self.jugador)
        self.balas = pygame.sprite.Group()
        self.enemigos = pygame.sprite.Group()

        self.spawn_timer = 0
        self.spawn_interval = 2000  # ms entre enemigos
        self.enemigo_velocidad = -2  # velocidad inicial de enemigos

        self.puntaje = 0
        self.vidas = 5
        self.game_over = False

    def manejar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE and not self.game_over:
                    self.jugador.disparar(self.balas)

    def actualizar(self, dt):
        if self.game_over:
            return

        # spawnear enemigos
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            enemigo = Enemigo(random.randint(40, ALTO - 40), self.enemigo_velocidad)
            self.enemigos.add(enemigo)

        # actualizar sprites
        self.sprites.update()
        self.balas.update()

        for enemigo in list(self.enemigos):
            resultado = enemigo.update()
            if resultado == "castillo":
                self.vidas -= 1
                if self.vidas <= 0:
                    self.game_over = True

        # colisiones balas-enemigos
        colisiones = pygame.sprite.groupcollide(self.balas, self.enemigos, True, True)
        if colisiones:
            kills = len(colisiones)
            self.puntaje += kills

            # Cada 5 kills aumenta dificultad
            if self.puntaje % 5 == 0:
                self.enemigo_velocidad -= 0.5  # más rápido
                if self.spawn_interval > 600:  # máximo de dificultad
                    self.spawn_interval -= 200

    def dibujar_barra_vida(self, surf):
        max_ancho = 150
        alto = 20
        x = ANCHO - max_ancho - 20
        y = 20

        pygame.draw.rect(surf, COLOR_BARRA_VACIA, (x, y, max_ancho, alto))
        ancho_actual = int(max_ancho * (self.vidas / 5))
        pygame.draw.rect(surf, COLOR_BARRA_VIDA, (x, y, ancho_actual, alto))
        pygame.draw.rect(surf, (255, 255, 255), (x, y, max_ancho, alto), 2)

    def dibujar(self, surf):
        surf.fill(COLOR_FONDO)
        pygame.draw.rect(surf, COLOR_CASTILLO, (0, 0, 50, ALTO))

        self.sprites.draw(surf)
        self.balas.draw(surf)
        self.enemigos.draw(surf)

        # HUD
        texto = fuente.render(f"Puntaje: {self.puntaje}", True, (220, 220, 220))
        surf.blit(texto, (10, 10))

        self.dibujar_barra_vida(surf)

        if self.game_over:
            msg = fuente.render("GAME OVER - Presiona ESC para salir", True, (255, 50, 50))
            rect = msg.get_rect(center=(ANCHO // 2, ALTO // 2))
            surf.blit(msg, rect)

    def run(self):
        while True:
            dt = clock.tick(FPS)
            self.manejar_eventos()

            teclas = pygame.key.get_pressed()
            if self.game_over and teclas[pygame.K_ESCAPE]:
                pygame.quit()
                sys.exit()

            self.actualizar(dt)
            self.dibujar(pantalla)
            pygame.display.flip()


# ====== Ejecutar ======
if __name__ == "__main__":
    Juego().run()
98