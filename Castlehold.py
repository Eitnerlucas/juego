import pygame
import sys
import random
import os
from datetime import datetime

# ====== Configuración ======
ANCHO, ALTO = 1400, 800
FPS = 75
COLOR_TEXTO = (255, 255, 255)
COLOR_TEXTO_REGISTRO = (255, 205, 0)

# ====== Inicialización ======
pygame.init()
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Juego de Eitner - registro de usuario")
clock = pygame.time.Clock()
# === RUTA BASE ===
BASE_DIR = os.path.dirname(__file__)  # directorio donde está Castlehold.py


def ruta(relativa):
    """Devuelve la ruta absoluta del archivo, partiendo de Castlehold.py"""
    return os.path.join(BASE_DIR, relativa)


# === FONDOS ===
fondo_inicio = pygame.image.load(ruta("fondo_galdor.png")).convert()
fondo_juego = pygame.image.load(ruta("dungeon.png")).convert()
fuente = pygame.font.Font(ruta("QuinqueFive.ttf"), 10)
fuente_R = pygame.font.Font(ruta("QuinqueFive.ttf"), 15)


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
        # proteger si no hay frames
        if self.frames:
            self.image = self.frames[self.indice_frame]
            self.rect = self.image.get_rect(center=pos_inicial)
        else:
            # placeholder si no hay imágenes
            self.image = pygame.Surface((50, 50))
            self.image.fill((255, 0, 255))
            self.rect = self.image.get_rect(center=pos_inicial)

        # Temporizador de animación (ms)
        self.timer_animacion = 0
        # milisegundos por frame (valor por defecto)
        self.velocidad_animacion = 120
        self.escala = escala

    def cambiar_accion(self, nueva_accion):
        if nueva_accion != self.accion_actual and nueva_accion in self.animaciones:
            self.accion_actual = nueva_accion
            self.frames = self.animaciones[nueva_accion]
            self.indice_frame = 0
            self.timer_animacion = 0

            # velocidad distinta por acción (ms por frame)
            if nueva_accion == "shoot":
                self.velocidad_animacion = 60  # anima más rápido el disparo
            elif nueva_accion == "run":
                self.velocidad_animacion = 100
            elif nueva_accion == "dead":
                self.velocidad_animacion = 180
            else:
                self.velocidad_animacion = 140

            # actualizar imagen inicial de la nueva acción (si hay frames)
            if self.frames:
                self.image = self.frames[0]

    def update_animacion(self, dt):
        if not self.frames:
            return
        self.timer_animacion += dt
        if self.timer_animacion >= self.velocidad_animacion:
            self.timer_animacion = 0
            # avanzar frame
            self.indice_frame = (self.indice_frame + 1) % len(self.frames)
            self.image = self.frames[self.indice_frame]


class Bala(pygame.sprite.Sprite):
    def __init__(self, x, y, direccion):
        super().__init__()
        self.frames = []
        self.cargar_animacion("Sprite/bala")
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=(x, y))
        self.velocidad = 15 
        self.anim_speed = 0.9  # qué tan rápido cambia de frame
        self.contador_anim = 0

    def cargar_animacion(self, carpeta):
        """Carga todas las imágenes de la carpeta de animación"""
        for nombre in sorted(os.listdir(carpeta)):
            if nombre.endswith(".png"):
                ruta = os.path.join(carpeta, nombre)
                imagen = pygame.image.load(ruta).convert_alpha()
                self.frames.append(imagen)

    def update(self):
        # Movimiento
        self.rect.x += self.velocidad

        # Animación
        self.contador_anim += self.anim_speed
        if self.contador_anim >= 1:
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.image = self.frames[self.frame_index]
            self.contador_anim = 0

        # Si sale de la pantalla, eliminar
        if self.rect.right < 0 or self.rect.left > 1400:
            self.kill()


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
        pantalla.blit(instruccion, (ANCHO // 2 - instruccion.get_width() // 2, ALTO // 2))
        pantalla.blit(salir, (ANCHO // 2 - salir.get_width() // 2, ALTO // 2 + 40))
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

        pantalla.blit(fondo_inicio, (0, 0))
        msg = fuente_R.render("Ingresar: codigo, nombre, apodo, clave", True, COLOR_TEXTO_REGISTRO)
        pantalla.blit(msg, (340, 230))
        render = fuente_R.render(texto, True,(255, 205, 0))
        pantalla.blit(render, (350, 280))
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
        super().__init__(animaciones, (x, y), escala=escala)

        # Movimiento
        self.vel_y = 0
        self.velocidad = 10

        # Disparo
        self.direccion = "derecha"  # "derecha" o "izquierda"
        self.disparando = False
        self.tiempo_recarga = 300  # milisegundos entre disparos
        self.ultimo_disparo = 0
        self.accion_previa = "quieto"  # para recordar en qué estado estaba antes de disparar
        self.bala_disparada = False  # aseguranos que solo salga 1 bala por animación

        # referencia al juego (se asigna desde Juego.__init__)
        self.juego = None

    def manejar_input(self, teclas):
        # mov vertical
        self.vel_y = 0
        if teclas[pygame.K_UP]:
            self.vel_y = -self.velocidad
            desired_action = "run"
        elif teclas[pygame.K_DOWN]:
            self.vel_y = self.velocidad
            desired_action = "run"
        else:
            desired_action = "quieto"

        # guardo la acción previa (la que debe retomarse al terminar el shoot)
        self.accion_previa = desired_action

        # Si está disparando no sobreescribo la animación actual (shoot),
        # pero sí actualizo la accion_previa para volver a ella después.
        if not self.disparando:
            self.cambiar_accion(desired_action)

    def disparar(self):
        """Inicia la animación de disparo y controla el cooldown.
           No crea la bala inmediatamente: la bala sale en el frame clave."""
        if not self.juego:
            return
        tiempo_actual = pygame.time.get_ticks()
        if tiempo_actual - self.ultimo_disparo >= self.tiempo_recarga:
            # iniciar animación de disparo
            self.disparando = True
            self.bala_disparada = False
            self.cambiar_accion("shoot")
            self.ultimo_disparo = tiempo_actual

    def update(self, *args):
        dt = clock.get_time()
        teclas = pygame.key.get_pressed()

        # manejar movimiento (incluso mientras dispara)
        self.manejar_input(teclas)
        self.rect.y += self.vel_y
        self.rect.clamp_ip(pantalla.get_rect())

        # si mantiene SPACE y puede disparar -> inicia la animación (el proyectil sale en el frame clave)
        if teclas[pygame.K_SPACE] and not self.juego.game_over:
            self.disparar()

        # actualizar animación
        self.update_animacion(dt)

        # Lógica de disparo sincronizada con la animación
        if self.disparando and self.frames:
            # elegir frame clave: el frame 1 si existe, sino el último disponible
            key_frame = 1 if len(self.frames) > 1 else len(self.frames) - 1
            key_frame = max(0, min(key_frame, len(self.frames) - 1))

            if self.indice_frame == key_frame and not self.bala_disparada:
                # crear la bala en el momento exacto del frame
                # usamos crear_bala del juego para que la bala quede en ambos grupos
                self.juego.crear_bala(self.rect.centerx + 50, self.rect.centery, self.direccion)
                self.bala_disparada = True

            # cuando termina la animación de disparo volvemos a la acción previa
            if self.indice_frame == len(self.frames) - 1:
                self.disparando = False
                self.bala_disparada = False
                self.cambiar_accion(self.accion_previa)





class Enemigo(SpriteAnimado):
    def __init__(self, y, velocidad, escala=0.5):
        animaciones = {
            "enemy run": cargar_frames(ruta("Sprite/enemigo/enemy run")),
            "enemy down": cargar_frames(ruta("Sprite/enemigo/enemy down"))
        }
        super().__init__(animaciones, (ANCHO, y), accion_inicial="enemy run")
        self.vel_x = velocidad
        self.vida = 1
        self.max_vida = 1
        self.muerto = False

    def recibir_dano(self, cantidad):
        self.vida -= cantidad
        if self.vida <= 0 and not self.muerto:
            self.cambiar_accion("enemy down")
            self.muerto = True
            self.vel_x = 0  # detener el movimiento

    def update(self):
        dt = clock.get_time()
        self.update_animacion(dt)
        if not self.muerto:
            self.rect.x += self.vel_x
            if self.rect.right < 50:
                self.kill()
                return "castillo"
        else:
            # esperar a que termine la animación antes de eliminar
            if self.indice_frame == len(self.frames) - 1:
                self.kill()
        return None


import pygame
import os

class Jefe(pygame.sprite.Sprite):
    def __init__(self, x, y, escala=3):
        super().__init__()
        self.escala = escala
        self.animaciones = {
            'caminar': self.cargar_animacion('Sprite/jefe/caminar'),
            'danio': self.cargar_animacion('Sprite/jefe/danio'),
            'muerte': self.cargar_animacion('Sprite/jefe/muerte')
        }

        self.estado = 'caminar'
        self.frame = 0
        self.image = self.animaciones[self.estado][self.frame]
        self.rect = self.image.get_rect(topleft=(x, y))

        self.vida = 5
        self.tiempo_danio = 0
        self.vivo = True

    def cargar_animacion(self, ruta):
        imagenes = []
        for nombre in sorted(os.listdir(ruta)):
            img = pygame.image.load(os.path.join(ruta, nombre)).convert_alpha()
            ancho = int(img.get_width() * self.escala)
            alto = int(img.get_height() * self.escala)
            img = pygame.transform.scale(img, (ancho, alto))
            imagenes.append(img)
        return imagenes


    def recibir_dano(self, cantidad):
        if not self.vivo:
            return
        self.vida -= cantidad
        if self.vida > 0:
            self.estado = 'danio'
            self.frame = 0
            self.tiempo_danio = pygame.time.get_ticks()
        else:
            self.estado = 'muerte'
            self.frame = 0
            self.vivo = False

    def update(self):
        ahora = pygame.time.get_ticks()

        # Volver a caminar después de recibir daño
        if self.estado == 'danio' and ahora - self.tiempo_danio > 300:
            if self.vivo:
                self.estado = 'caminar'

        # Avanzar frames de animación
        self.frame += 0.2
        if self.frame >= len(self.animaciones[self.estado]):
            if self.estado == 'muerte':
                self.kill()
                return
            self.frame = 0

        self.image = self.animaciones[self.estado][int(self.frame)]

        # Movimiento si está caminando
        if self.estado == 'caminar':
            self.rect.x -= 2


class GestionMatriz:
    def __init__(self, MAX_JUGADAS=500, NUM_OBJETOS=2, DIAS=31, MES=12, PARTIDAS=100):
        # PRIMERA MATRIZ (JUGADAS X OBJETOS)
        self.matriz_jugadas = [[0 for _ in range(NUM_OBJETOS)] for _ in range(MAX_JUGADAS)]
        # SEGUNDA MATRIZ (DIAS X OBJETOS)
        self.matriz_dias = [[0 for _ in range(NUM_OBJETOS)] for _ in range(DIAS)]
        # TERCERA MATRIZ (PARTIDA X MES X OBJETOS)
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
    # dividir el texto ingresado por comas y asignar el nombre de usuario
    def __init__(self, texto):
        campos = texto.split(",")
        if len(campos) >= 2:
            self.nombre_jugador = campos[2].strip()
        else:  # si no hay suficientes campos, usar el texto completo
            self.nombre_jugador = texto

        self.partidas_jugadas = acumulador_partidas()  # llama a la funcion para contar las partidas jugadas
        guardar_partida(self.partidas_jugadas)  # guarda la cantidad de partidas jugadas en el archivo
        self.jugador = Jugador(60, ALTO // 2)
        self.jugador.juego = self  # ← referencia para que el jugador acceda a self.balas

        self.sprites = pygame.sprite.Group(self.jugador)
        self.grupo_balas = pygame.sprite.Group()
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
        # selfs para manejar jefes
        self.nivel = 1
        self.enemigos_para_jefe = 5  # cantidad de enemigos a eliminar para que aparezca el jefe
        self.jefe_activo = False  # indica si el jefe está activo en pantalla
        self.jefe = None  # referencia al jefe
        self.max_nivel = 5  # Nivel máximo para limitar la dificultad
        self.barras_vidas = cargar_frames(ruta("Sprite/barra"), escala = 3)

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
                if evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

    def crear_bala(self, x, y, direccion):
        bala = Bala(x, y, direccion)
        self.grupo_balas.add(bala)
        self.sprites.add(bala)


    def actualizar(self, dt):
        if self.game_over:
            return

        # spawn
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            enemigo = Enemigo(random.randint(40, ALTO - 40), self.enemigo_velocidad)
            self.enemigos.add(enemigo)

        # actualizaciones
        self.sprites.update()
        self.grupo_balas.update()

        # revisar enemigos (solo una vez por frame)
        for enemigo in list(self.enemigos):
            resultado = enemigo.update()  # Enemigo.update() maneja movimiento y animación

            # si es jefe tratamos distinto
            if isinstance(enemigo, Jefe):
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
                # enemigo normal
                if resultado == "castillo":
                    self.vidas -= 1
                    self.puntaje_B += 1
                    self.matriz.cargar_matriz_jugadas(self.contador_jugadas, 1)
                    self.contador_jugadas += 1
                    cod_usuario = obtener_codigo_usuario()[0]
                    Guardar_colisiones(cod_usuario, self.partidas_jugadas, enemigo.rect.x, enemigo.rect.y,
                                      "enemigo llegó al castillo")
                    if self.vidas <= 0:
                        self.game_over = True

        # Colisiones entre balas y enemigos
        colisiones = pygame.sprite.groupcollide(self.grupo_balas, self.enemigos, True, False)
        if colisiones:
            kills = len(colisiones)
            self.puntaje_A += kills
            self.matriz.cargar_matriz_jugadas(self.contador_jugadas, 0)
            self.contador_jugadas += 1

            for bala, enemigos in colisiones.items():
                for enemigo in enemigos:
                    if isinstance(enemigo, Jefe):
                        enemigo.recibir_dano(1)  # cada bala le quita 1 de vida al jefe
                    else:
                        enemigo.recibir_dano(1)  # cada bala le quita 1 de vida al enemigo normal

                    cod_usuario = obtener_codigo_usuario()[0]
                    Guardar_colisiones(cod_usuario, self.partidas_jugadas, enemigo.rect.x, enemigo.rect.y,)

            # aumentar dificultad por puntaje
            if self.puntaje_A % 25 == 0:
                self.enemigo_velocidad -= 0.5
                if self.spawn_interval > 600:
                    self.spawn_interval -= 200

        # verificar si toca invocar al jefe
        if self.puntaje_A >= self.enemigos_para_jefe * self.nivel and not self.jefe_activo:
            self.jefe = Jefe(ANCHO -200 ,ALTO // 2)
            self.enemigos.add(self.jefe)
            self.jefe_activo = True
            
            
    def dibujar_barra_vida(self, surf):
            if not self.barras_vidas:
                return  # si no cargaron las imágenes, no hacer nada
            # Elegir la imagen correcta según la vida actual (0 a 5)
            vida_index = max(0, min(self.vidas, 5))  # asegura que no salga de rango
            barra = self.barras_vidas[vida_index]
            surf.blit(barra, (60, 0))  # posición de la barra
            # posición de la barra

    def dibujar(self, surf):
        surf.blit(fondo_juego, (0, 0))

        self.sprites.draw(surf)
        self.grupo_balas.draw(surf)
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
    print(__file__)
    pantalla_registro()
    pantalla_inicio()
    Juego("jugador").run()
    
    