import pygame
import sys
import random
import os
from datetime import datetime

# ====== Configuración ======
ANCHO, ALTO = 1400, 800
FPS = 60
COLOR_FONDO = (20, 20, 30)
COLOR_CASTILLO = (80, 80, 200)
COLOR_JUGADOR = (200, 200, 240)
COLOR_ENEMIGO = (200, 80, 80)
COLOR_BALA = (250, 250, 100)
COLOR_BARRA_VIDA = (80, 200, 80)
COLOR_BARRA_VACIA = (200, 50, 50)
COLOR_TEXTO = (220, 220, 220)
COLOR_JEFE = (150, 0, 0)

pygame.init()
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Juego de Eitner - registro de usuario")
clock = pygame.time.Clock()
fuente = pygame.font.SysFont("consolas", 20)

# === RUTA BASE ===
BASE_DIR = os.path.dirname(__file__)

def ruta(relativa):
    """Devuelve la ruta absoluta del archivo, partiendo de Castlehold.py"""
    return os.path.join(BASE_DIR, relativa)

# === FONDOS ===
fondo_inicio = pygame.image.load(ruta("fondo_galdor.png")).convert()
fondo_juego = pygame.image.load(ruta("dungeon.png")).convert()

def cargar_frames(carpeta, escala=3):
    frames = []
    if not os.path.exists(carpeta):
        print(f" Carpeta no encontrada: {carpeta}")
        return frames
    for nombre in sorted(os.listdir(carpeta)):
        if nombre.lower().endswith(".png"):
            img = pygame.image.load(os.path.join(carpeta, nombre)).convert_alpha()
            if escala != 1:
                ancho = int(img.get_width() * escala)
                alto = int(img.get_height() * escala)
                img = pygame.transform.scale(img, (ancho, alto))
            frames.append(img)
    return frames



# ====== Clase base animada ======
class SpriteAnimado(pygame.sprite.Sprite):
    def __init__(self, animaciones, pos_inicial, escala=1, accion_inicial=None):
        super().__init__()
        self.animaciones = animaciones
        # Si no se pasa una acción inicial, usa la primera que haya
        if accion_inicial and accion_inicial in animaciones:
            self.accion_actual = accion_inicial
        else:
            self.accion_actual = list(animaciones.keys())[0]
        self.frames = self.animaciones[self.accion_actual]
        self.indice_frame = 0
        self.image = self.frames[self.indice_frame]
        self.rect = self.image.get_rect(center=pos_inicial)
        self.timer_animacion = 0
        self.velocidad_animacion = 120
        self.escala = escala


    def cambiar_accion(self, nueva_accion):
        if nueva_accion != self.accion_actual:
            self.accion_actual = nueva_accion
            self.frames = self.animaciones[nueva_accion]
            self.indice_frame = 0
            self.timer_animacion = 0

    def update_animacion(self, dt):
        self.timer_animacion += dt
        if self.timer_animacion >= self.velocidad_animacion:
            self.timer_animacion = 0
            self.indice_frame = (self.indice_frame + 1) % len(self.frames)
            self.image = self.frames[self.indice_frame]


# ====== Pantalla de inicio ======
def pantalla_inicio():
    activo = True
    while activo:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                else:
                    return

        pantalla.blit(fondo_inicio, (0, 0))
        instruccion = fuente.render("Presiona cualquier tecla para comenzar", True, (180, 180, 180))
        salir = fuente.render("Presiona ESC para salir", True, (180, 100, 100))
        pantalla.blit(instruccion, (ANCHO//2 - instruccion.get_width()//2, ALTO//2))
        pantalla.blit(salir, (ANCHO//2 - salir.get_width()//2, ALTO//2 + 40))
        pygame.display.flip()
        clock.tick(FPS)


# ====== Registro ======
def pantalla_registro():
    texto = ""
    activo = True
    while activo:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN and texto.strip() != "":
                    with open(ruta("usuarios.txt"), "a") as archivo:
                        archivo.write(f"{texto}\n")
                    return texto
                elif evento.key == pygame.K_BACKSPACE:
                    texto = texto[:-1]
                else:
                    texto += evento.unicode

        pantalla.fill(COLOR_FONDO)
        msg = fuente.render("Ingresar: código, nombre, apodo, clave", True, COLOR_TEXTO)
        pantalla.blit(msg, (0, 30))
        render = fuente.render(texto, True, (200, 200, 200))
        pantalla.blit(render, (0, 60))
        pygame.display.flip()
        clock.tick(FPS)


def obtener_codigo_usuario():
    with open(ruta("usuarios.txt"), "r") as archivo:
        for linea in archivo:
            campos = linea.strip().split(",")
            if len(campos) < 4:
                continue  # salta líneas incompletas
            cod_usuario = campos[0]
            nombre = campos[1]
            apodo = campos[2]
            clave = campos[3]
    return cod_usuario, nombre, apodo, clave



# ====== Archivos ======
def acumulador_partidas():
    archivo_path = ruta("acumulador_partidas.txt")
    if not os.path.exists(archivo_path):
        with open(archivo_path, "w") as archivo:
            archivo.write("0")
        return 1
    else:
        with open(archivo_path, "r") as archivo:
            linea = archivo.readline()
            if linea:
                num = int(linea.strip())
                return num + 1
            else:
                return 1


def guardar_partida(num):
    with open(ruta("acumulador_partidas.txt"), "w") as archivo:
        archivo.write(str(num))


def guardar_detalle_partida(cod_usuario, num_partida, puntaje_a, puntaje_b):
    archivo_path = ruta("detalle_partidas.txt")
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if not os.path.exists(archivo_path):
        id_jugador = 1
        with open(archivo_path, "w") as f:
            f.write(f"{id_jugador},{cod_usuario},{num_partida},{puntaje_a},{puntaje_b},{fecha}\n")
    else:
        with open(archivo_path, "r") as f:
            lineas = f.readlines()
        if lineas:
            ultima_linea = lineas[-1].strip()
            ultimo_id = int(ultima_linea.split(",")[0])
            id_jugador = ultimo_id + 1
        else:
            id_jugador = 1
        with open(archivo_path, "a") as f:
            f.write(f"{id_jugador},{cod_usuario},{num_partida},{puntaje_a},{puntaje_b},{fecha}\n")


def Guardar_colisiones(cod_usuario, num_partida, x, y, obs="enemigo eliminado"):
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(ruta("colisiones.txt"), "a") as f:
        f.write(f"{cod_usuario},{num_partida},{x},{y},{obs},{fecha}\n")


# ====== Clases ======
class Jugador(SpriteAnimado):
    def __init__(self, x, y, escala=2):
        animaciones = {
            "quieto": cargar_frames(ruta("Sprite/jugador/quieto")),
            "run": cargar_frames(ruta("Sprite/jugador/run")),
            "shoot": cargar_frames(ruta("Sprite/jugador/shoot")),
            "dead": cargar_frames(ruta("Sprite/jugador/dead"))
        }
        super().__init__(animaciones, (x, y), escala=1)
        self.vel_y = 0
        self.velocidad = 10
        self.disparando = False
        self.tiempo_disparo = 0

    def manejar_input(self, teclas):
        self.vel_y = 0
        self.disparando = False
        if teclas[pygame.K_UP]:
            self.vel_y = -self.velocidad
            self.cambiar_accion("run")
        elif teclas[pygame.K_DOWN]:
            self.vel_y = self.velocidad
            self.cambiar_accion("run")
        else:
            self.cambiar_accion("quieto")
        if teclas[pygame.K_SPACE]:
            self.disparando = True
            self.cambiar_accion("shoot")

    def update(self):
        teclas = pygame.key.get_pressed()
        self.manejar_input(teclas)
        self.rect.y += self.vel_y
        self.rect.clamp_ip(pantalla.get_rect())
        dt = clock.get_time()
        self.update_animacion(dt)

    def disparar(self, balas):
        ahora = pygame.time.get_ticks()
        if self.disparando and ahora - self.tiempo_disparo > 300:  # 0.3 seg entre disparos
            bala = Bala(self.rect.right, self.rect.centery)
            balas.add(bala)
            self.tiempo_disparo = ahora


class Bala(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((15, 6), pygame.SRCALPHA)
        pygame.draw.rect(self.image, COLOR_BALA, (0, 0, 15, 6))
        self.rect = self.image.get_rect(center=(x, y))
        self.vel_x = 15

    def update(self):
        self.rect.x += self.vel_x
        if self.rect.left > ANCHO:
            self.kill()


class Enemigo(SpriteAnimado):
    def __init__(self, y, velocidad, escala = 0.5):
        animaciones = {
            "enemy run": cargar_frames(ruta("Sprite/enemigo/enemy run")),
            "enemy down": cargar_frames(ruta("Sprite/enemigo/enemy down"))
        }
        super().__init__(animaciones, (ANCHO, y), accion_inicial="enemy run")
        self.vel_x = velocidad
        self.vida = 3
        self.max_vida = 3

    def update(self):
        dt = clock.get_time()
        self.update_animacion(dt)
        self.rect.x += self.vel_x
        if self.rect.right < 50:
            self.kill()
            return "castillo"
        return None

    def recibir_dano(self, cantidad):
        self.vida -= cantidad
        if self.vida <= 0:
            self.cambiar_accion("enemy down")

    def dibujar_barra_vida(self, surf):
        ancho_total = 40
        alto = 5
        x = self.rect.centerx - ancho_total // 2
        y = self.rect.top - 10
        pygame.draw.rect(surf, (200, 50, 50), (x, y, ancho_total, alto))
        ancho_actual = int(ancho_total * (self.vida / self.max_vida))
        pygame.draw.rect(surf, (50, 200, 50), (x, y, ancho_actual, alto))


class jefe(pygame.sprite.Sprite):
    def __init__(self, y):
        super().__init__()
        self.image = pygame.Surface((120, 120))
        self.image.fill(COLOR_JEFE)
        self.rect = self.image.get_rect(midright=(ANCHO, y)) #toma el punto medio del lado derecho como referencia
        self.vel_x = -2
        self.vida = 10
        
    def update(self):
        self.rect.x += self.vel_x
        if self.rect.right < 50:  # tocó el castillo
            self.kill()
            return "castillo"
        if self.vida <= 0:
            self.kill()
            return "muerto"
        return None
    
    def recibir_dano(self, cantidad):
        self.vida -= cantidad
        


class GestionMatriz:
    def __init__(self, MAX_JUGADAS=100, NUM_OBJETOS=2, DIAS =31, MES=12, PARTIDAS=100):
        #PRIMERA MATRIZ (JUGADAS X OBJETOS)
        self.matriz_jugadas = [[0 for _ in range(NUM_OBJETOS)] for _ in range(MAX_JUGADAS)]
        #SEGUNDA MATRIZ (DIAS X OBJETOS)
        self.matriz_dias = [[0 for _ in range(NUM_OBJETOS)] for _ in range(DIAS)]
        #TERCERA MATRIZ (PARTIDA X MES X OBJETOS)
        self.matriz_3D = [[[0 for _ in range(NUM_OBJETOS)] for _ in range(MES)] for _ in range(PARTIDAS)]
        
    def cargar_matriz_jugadas(self, fila, objeto):
        self.matriz_jugadas[fila][objeto] += 1
        
    def cargar_matriz_dias(self, dia, objeto):
        self.matriz_dias[dia][objeto] += 1
        
    def cargar_matriz_3D(self, partida, mes, objeto):
        self.matriz_3D[partida][mes][objeto] += 1
        
    def mostrar_matriz(self, matriz):
        for fila in matriz:
            for valor in fila:
                print(f"|{valor}|", end="")
            print()
        print()


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
        self.matriz = GestionMatriz()
        self.spawn_timer = 0
        self.spawn_interval = 2000 
        self.enemigo_velocidad = -3

        self.puntaje_A = 0
        self.puntaje_B = 0
        self.vidas = 5
        self.game_over = False
        self.contador_jugadas = 0
        #selfs para manejar jefes
        self.nivel = 1
        self.enemigos_para_jefe = 25 # cantidad de enemigos a eliminar para que aparezca el jefe
        self.jefe_activo = False # indica si el jefe está activo en pantalla
        self.jefe = None # referencia al jefe
        self.max_nivel = 5  # Nivel máximo para limitar la dificultad

    def subir_nivel(self):
        if self.nivel < self.max_nivel:
            self.nivel += 1
            print(f"Nivel {self.nivel} alcanzado!")
            # reinciar enemigos y puntaje parcial si queres
            self.spawn_interval = max(500, self.spawn_interval - 300)  # reducir el intervalo de spawn
            self.enemigo_velocidad -= 0.5  # aumentar la velocidad de los enemigos
            self.jefe_activo = False
            self.jefe = None
        else:
            print("¡¡ JUEGO COMPLETADO !!")        
            self.game_over = True
            
            
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
        # disparar
        self.jugador.disparar(self.balas)
        self.balas.update()


        for enemigo in list(self.enemigos):
            resultado = enemigo.update()
            if resultado == "castillo":
                self.vidas -= 1
                self.puntaje_B += 1
                self.matriz.cargar_matriz_jugadas(self.contador_jugadas, 1)
                self.contador_jugadas += 1
                cod_usuario = obtener_codigo_usuario()[0]
                Guardar_colisiones(cod_usuario, self.partidas_jugadas, enemigo.rect.x, enemigo.rect.y, "enemigo llegó al castillo")
                if self.vidas <= 0:
                    self.game_over = True

        colisiones = pygame.sprite.groupcollide(self.balas, self.enemigos, True, False)
        if colisiones:
            kills = len(colisiones)
            self.puntaje_A += kills
            self.matriz.cargar_matriz_jugadas(self.contador_jugadas, 0)
            self.contador_jugadas += 1
            
            
            for bala, enemigos in colisiones.items():
                for enemigo in enemigos:
                    if isinstance(enemigo, jefe):
                        enemigo.recibir_dano(1) #cada bala le quita 1 de vida al jefe
                    else:
                        enemigo.kill()
                         #
                        
                        
                    cod_usuario = obtener_codigo_usuario()[0]
                    Guardar_colisiones(cod_usuario, self.partidas_jugadas, enemigo.rect.x, enemigo.rect.y,)
            if self.puntaje_A % 25 == 0:
                self.enemigo_velocidad -= 0.5
                if self.spawn_interval > 600:
                    self.spawn_interval -= 200
                    
        #verificaar si toca invocar al jefe
        if self.puntaje_A >= self.enemigos_para_jefe * self.nivel and not self.jefe_activo:
            self.jefe = jefe(ALTO // 2 )
            self.enemigos.add(self.jefe)
            self.jefe_activo = True
            
        #actualizar el jefe
        for enemigo in list(self.enemigos):
            resultado = enemigo.update()
    
            if isinstance(enemigo, jefe):
                if resultado == "castillo":
                    self.vidas -= 3
                    self.puntaje_B += 3
                    self.enemigos.remove(enemigo)
                    self.jefe_activo = False
                    self.jefe = None
                    if self.vidas <= 0:
                        self.game_over = True
            elif resultado == "muerto":
                self.enemigos.remove(enemigo)
                self.jefe_activo = False
                self.jefe = None
                self.subir_nivel()
            else:
                if resultado == "castillo":
                    self.vidas -= 1
                    self.puntaje_B += 1
                    self.matriz.cargar_matriz_jugadas(self.contador_jugadas, 1)
                    self.contador_jugadas += 1
                    cod_usuario = obtener_codigo_usuario()[0]
                    Guardar_colisiones(cod_usuario, self.partidas_jugadas, enemigo.rect.x, enemigo.rect.y, "enemigo llegó al castillo")
                    if self.vidas <= 0:
                        self.game_over = True

                    
                    
                    

    def dibujar_barra_vida(self, surf):
        max_ancho = 150
        alto = 20
        x = 60
        y = 20
        pygame.draw.rect(surf, COLOR_BARRA_VACIA, (x, y, max_ancho, alto))
        ancho_actual = int(max_ancho * (self.vidas / 5))
        pygame.draw.rect(surf, COLOR_BARRA_VIDA, (x, y, ancho_actual, alto))
        pygame.draw.rect(surf, (255, 255, 255), (x, y, max_ancho, alto), 2)

    def dibujar(self, surf):
        
        surf.blit(fondo_juego, (0, 0))  # Usa la imagen de fondo cargada
        #  pygame.draw.rect(surf, COLOR_CASTILLO, (0, 0, 50, ALTO))

        self.sprites.draw(surf)
        self.balas.draw(surf)
        self.enemigos.draw(surf)
        
        for e in self.enemigos:
            if hasattr(e, "dibujar_barra_vida"):
                e.dibujar_barra_vida(surf)

        
        
        texto_nivel = fuente.render(f"Nivel: {self.nivel}", True, COLOR_TEXTO)
        surf.blit(texto_nivel, (1100, 10))


        texto = fuente.render(f"Puntaje: {self.puntaje_A}", True, COLOR_TEXTO)
        surf.blit(texto, (1250, 10))

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
                print("jugas|objetos")   
                self.matriz.mostrar_matriz(self.matriz.matriz_jugadas)
                cod_usuario, nombre, apodo, clave = obtener_codigo_usuario()
                guardar_detalle_partida(cod_usuario, self.partidas_jugadas, self.puntaje_A, self.puntaje_B)
                pygame.quit()
                sys.exit()
            self.actualizar(dt)
            self.dibujar(pantalla)
            pygame.display.flip()
            

# ====== Ejecutar ======
if __name__ == "__main__":
    pantalla_inicio()
    Juego("jugador").run()
