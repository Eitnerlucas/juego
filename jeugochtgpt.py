import pygame #herramientas para el juego
import sys # para manejar las salidas del programa
import random #para obtener valores random (obtener numeros aleatorios)
import os  #para operaciones del sistema 
from datetime import datetime #para obtener fechas

# ====== Configuración ======
ANCHO, ALTO = 800, 450
FPS = 60
COLOR_FONDO = (20, 20, 30)
COLOR_CASTILLO = (80, 80, 200)
COLOR_JUGADOR = (200, 200, 240)
COLOR_ENEMIGO = (200, 80, 80)
COLOR_BALA = (250, 250, 100)
COLOR_BARRA_VIDA = (80, 200, 80)
COLOR_BARRA_VACIA = (200, 50, 50)
COLOR_TEXTO = (220, 220, 220)

pygame.init()
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Juego de Eitner- registro de usuario")
clock = pygame.time.Clock()
fuente = pygame.font.SysFont("consolas", 20)


# ====== Registro de jugador en pantalla ======
def pantalla_registro():
    texto = "" 
    activo = True

    while activo:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT: #se fija si el usuario quiere saalir 
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN and texto.strip() != "": #si presiona enter y el texto no está vacío 
                    with open("usuarios.txt", "a") as archivo:
                        archivo.write(f"{texto}\n")
                    return texto  # vuelve al juego 
                elif evento.key == pygame.K_BACKSPACE: #si el usuario presiona backspace (borrar) 
                    texto = texto[:-1] #se borra el último caracter
                else:
                    texto += evento.unicode #agrega el caracter que se presionó

        pantalla.fill(COLOR_FONDO)
        msg = fuente.render("ingresar: código de usuario, nombre, apodo, clave", True, COLOR_TEXTO)
        pantalla.blit(msg, (0, 30)) #posicion del titulo

        render = fuente.render(texto, True, (200, 200, 200))#color del texto
        pantalla.blit(render, (0, 60)) #posicion del texto

        pygame.display.flip()
        clock.tick(FPS)
        
def obtener_codigo_usuario():
    with open("usuarios.txt", "r") as archivo:
        for linea in archivo:
            campos = linea.strip().split(",")
            cod_usuario = campos[0]
            nombre = campos[1]
            apodo = campos[2]
            clave = campos[3]
    return cod_usuario, nombre, apodo, clave
    
# ====== Funciones para manejo de archivos ======    
            
def acumulador_partidas(): #funcion para contar la cantidad de partidas jugadas
    if not os.path.exists("acumulador_partidas.txt"): #si no existe el archivo, se crea y se inicializa en 0
        with open("acumulador_partidas.txt", 'w') as archivo:
            archivo.write("0")
        return 1 #si es la primera partida retorna 1 
    else: #si ya existe el archivo, se lee el valor, se incrementa en 1 y se guarda       
        with open("acumulador_partidas.txt", 'r') as archivo:
            linea = archivo.readline()
            if linea:
                num = int(linea.strip())
                return num + 1
            else:
                return 1
    
    
def guardar_partida(num): #funcion para guardar la cantidad de partidas jugadas
    with open("acumulador_partidas.txt", 'w') as archivo:
        archivo.write(str(num))


def guardar_detalle_partida(cod_usuario, num_partida, puntaje_a, puntaje_b):
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if not os.path.exists("detalle_partidas.txt"): #pregunta si el archivo existe si no existe lo crea y asigna el id 1
        id_jugador = 1
        with open("detalle_partidas.txt", "w") as f:
            f.write(f"{id_jugador},{cod_usuario},{num_partida},{puntaje_a},{puntaje_b},{fecha}\n")
    else: #si ya existe 
        with open("detalle_partidas.txt", "r") as f: #lee todas las lineas del archivo
            lineas = f.readlines() 
        if lineas: #corrobora que no esté vació
            ultima_linea = lineas[-1].strip() #obtiene la última línea
            ultimo_id = int(ultima_linea.split(",")[0]) #extrae el ID del jugador
            id_jugador = ultimo_id + 1
        else:#asigna el 1 si el archivo está vació
            id_jugador = 1
        with open("detalle_partidas.txt", "a") as f:
            f.write(f"{id_jugador},{cod_usuario},{num_partida},{puntaje_a},{puntaje_b},{fecha}\n")

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
        self.rect.y += self.vel_y
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
    #dividir el texto ingresado por comas y asignar el nombre de usuario
    def __init__(self, texto):
        campos = texto.split(",")
        if len(campos) >= 2:
            self.nombre_jugador = campos[2].strip() 
        else: # si no hay suficientes campos, usar el texto completo 
            self.nombre_jugador =  texto
        
        self.partidas_jugadas = acumulador_partidas()#llama a la funcion para contar las partidas jugadas
        guardar_partida(self.partidas_jugadas)#guarda la cantidad de partidas jugadas en el archivo   
        self.jugador = Jugador(60, ALTO // 2)
        self.sprites = pygame.sprite.Group(self.jugador)
        self.balas = pygame.sprite.Group()
        self.enemigos = pygame.sprite.Group()

        self.spawn_timer = 0
        self.spawn_interval = 2000
        self.enemigo_velocidad = -2

        self.puntaje_A = 0
        self.puntaje_B = 0
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
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            enemigo = Enemigo(random.randint(40, ALTO - 40), self.enemigo_velocidad)
            self.enemigos.add(enemigo)

        self.sprites.update()
        self.balas.update()

        for enemigo in list(self.enemigos):
            resultado = enemigo.update()
            if resultado == "castillo":
                self.vidas -= 1
                self.puntaje_B += 1
                if self.vidas <= 0:
                    self.game_over = True

        colisiones = pygame.sprite.groupcollide(self.balas, self.enemigos, True, True)
        if colisiones:
            kills = len(colisiones)
            self.puntaje_A += kills
            if self.puntaje_A % 5 == 0:
                self.enemigo_velocidad -= 0.5
                if self.spawn_interval > 600:
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

        texto = fuente.render(f"{self.nombre_jugador} | Puntaje: {self.puntaje_A} | Puntaje enemigo {self.puntaje_B}", True, COLOR_TEXTO)
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
    nombre = pantalla_registro()
    Juego(nombre).run()