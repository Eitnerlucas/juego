import pygame
import sys
import random
import os
from pygame.sprite import LayeredUpdates
from datetime import datetime

# ====== Configuración ============================================================================================================
ANCHO, ALTO = 1400, 800
FPS = 75
COLOR_TEXTO = (255, 255, 255)
COLOR_TEXTO_REGISTRO = (255, 205, 0)

# ====== Inicialización ==================================================================================================
pygame.init()
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Juego de Eitner")
clock = pygame.time.Clock()

# === RUTA BASE ==========================================================================================================
BASE_DIR = os.path.dirname(__file__)

def ruta(relativa):
    return os.path.join(BASE_DIR, relativa)

def colision_mask_segura(sprite1, sprite2):
    if sprite1.mask is None or sprite2.mask is None:
        return False  # no hay colisión posible
    return pygame.sprite.collide_mask(sprite1, sprite2) #funcion de deteccion de colisiones por pixel

# =============== FONDOS ===============================================================================================
fondo_inicio = pygame.image.load(ruta("fondo_galdor.png")).convert()
fondo_inicio = pygame.transform.scale(fondo_inicio, (ANCHO, ALTO))
fondo_juego = pygame.image.load(ruta("dungeon.png")).convert()
fondo_juego = pygame.transform.scale(fondo_juego, (ANCHO, ALTO))
fuente = pygame.font.Font(ruta("QuinqueFive.ttf"), 10)
fuente_R = pygame.font.Font(ruta("QuinqueFive.ttf"), 15)

# ====== Funciones de carga de frames ============================================================================================
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

# ====== Clases ============================================================================================================
class SpriteAnimado(pygame.sprite.Sprite):
    def __init__(self, animaciones, pos_inicial, escala=1, accion_inicial=None):
        super().__init__()
        self.animaciones = animaciones
        self.accion_actual = accion_inicial if accion_inicial and accion_inicial in animaciones else list(animaciones.keys())[0]
        self.frames = self.animaciones[self.accion_actual]
        self.indice_frame = 0
        if self.frames:
            self.image = self.frames[self.indice_frame]
            self.rect = self.image.get_rect(center=pos_inicial)
            self.mask = pygame.mask.from_surface(self.image)
        else:
            self.image = pygame.Surface((50, 50))
            self.image.fill((255, 0, 255))
            self.rect = self.image.get_rect(center=pos_inicial)
            self.mask = pygame.mask.from_surface(self.image)
        self.timer_animacion = 0
        self.velocidad_animacion = 120
        self.escala = escala

    def cambiar_accion(self, nueva_accion):
        if nueva_accion != self.accion_actual and nueva_accion in self.animaciones:
            self.accion_actual = nueva_accion
            self.frames = self.animaciones[nueva_accion]
            self.indice_frame = 0
            self.timer_animacion = 0
            if nueva_accion == "shoot":
                self.velocidad_animacion = 60
            elif nueva_accion == "run":
                self.velocidad_animacion = 100
            elif nueva_accion == "dead":
                self.velocidad_animacion = 180
            else:
                self.velocidad_animacion = 140
            if self.frames:
                self.image = self.frames[0]

    def update_animacion(self, dt):
        if not self.frames:
            return
        self.timer_animacion += dt
        if self.timer_animacion >= self.velocidad_animacion:
            self.timer_animacion = 0
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
        self.mask = pygame.mask.from_surface(self.image)
        self.velocidad = 15 
        self.anim_speed = 0.9
        self.contador_anim = 0

    def cargar_animacion(self, carpeta):
        for nombre in sorted(os.listdir(carpeta)):
            if nombre.endswith(".png"):
                ruta_img = os.path.join(carpeta, nombre)
                self.frames.append(pygame.image.load(ruta_img).convert_alpha())

    def update(self):
        self.rect.x += self.velocidad
        self.contador_anim += self.anim_speed
        if self.contador_anim >= 1:
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.image = self.frames[self.frame_index]
            self.contador_anim = 0
        if self.rect.right < 0 or self.rect.left > ANCHO:
            self.kill()


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
        render = fuente_R.render(texto, True, COLOR_TEXTO_REGISTRO)
        pantalla.blit(render, (350, 280))
        pygame.display.flip()
        clock.tick(FPS)

def obtener_codigo_usuario():
    with open(ruta("usuarios.txt"), "r") as archivo:
        for linea in archivo:
            campos = linea.strip().split(",")
            if len(campos) < 4:
                continue
            cod_usuario, nombre, apodo, clave = campos[0], campos[1], campos[2], campos[3]
    return cod_usuario, nombre, apodo, clave

# ====== Gestión de partidas y colisiones ======
def acumulador_partidas():
    archivo_path = ruta("acumulador_partidas.txt")
    if not os.path.exists(archivo_path):
        with open(archivo_path, "w") as archivo:
            archivo.write("0")
        return 1
    else:
        with open(archivo_path, "r") as archivo:
            linea = archivo.readline()
            return int(linea.strip()) + 1 if linea else 1

def guardar_partida(num):
    with open(ruta("acumulador_partidas.txt"), "w") as archivo:
        archivo.write(str(num))

def guardar_detalle_partida(cod_usuario, num_partida, puntaje_a, puntaje_b):
    archivo_path = ruta("detalle_partidas.txt")
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    id_jugador = 1
    if os.path.exists(archivo_path):
        with open(archivo_path, "r") as f:
            lineas = f.readlines()
        if lineas:
            ultima_linea = lineas[-1].strip()
            id_jugador = int(ultima_linea.split(",")[0]) + 1
    with open(archivo_path, "a") as f:
        f.write(f"{id_jugador},{cod_usuario},{num_partida},{puntaje_a},{puntaje_b},{fecha}\n")

def Guardar_colisiones(cod_usuario, num_partida, x, y, obs="enemigo eliminado"):
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(ruta("colisiones.txt"), "a") as f:
        f.write(f"{cod_usuario},{num_partida},{x},{y},{obs},{fecha}\n")

# ====== Clases de Jugador y Enemigos ======
class Jugador(SpriteAnimado):
    def __init__(self, x, y, escala=2):
        animaciones = {
            "quieto": cargar_frames(ruta("Sprite/jugador/quieto")),
            "run": cargar_frames(ruta("Sprite/jugador/run")),
            "shoot": cargar_frames(ruta("Sprite/jugador/shoot")),
            "dead": cargar_frames(ruta("Sprite/jugador/dead"))
        }
        super().__init__(animaciones, (x, y), escala=escala)
        self.vel_y = 0
        self.velocidad = 10
        self.direccion = "derecha"
        self.disparando = False
        self.tiempo_recarga = 150
        self.ultimo_disparo = 0
        self.accion_previa = "quieto"
        self.bala_disparada = False
        self.juego = None

    def manejar_input(self, teclas):
        self.vel_y = 0
        if teclas[pygame.K_UP]:
            self.vel_y = -self.velocidad
            desired_action = "run"
        elif teclas[pygame.K_DOWN]:
            self.vel_y = self.velocidad
            desired_action = "run"
        else:
            desired_action = "quieto"
        self.accion_previa = desired_action
        if not self.disparando:
            self.cambiar_accion(desired_action)

    def disparar(self):
        if not self.juego:
            return
        tiempo_actual = pygame.time.get_ticks()
        if tiempo_actual - self.ultimo_disparo >= self.tiempo_recarga:
            self.disparando = True
            self.bala_disparada = False
            self.cambiar_accion("shoot")
            self.ultimo_disparo = tiempo_actual

    def update(self, *args):
        dt = clock.get_time()
        teclas = pygame.key.get_pressed()
        self.manejar_input(teclas)
        self.rect.y += self.vel_y
        self.rect.clamp_ip(pantalla.get_rect())
        if teclas[pygame.K_SPACE] and not self.juego.game_over:
            self.disparar()
        self.update_animacion(dt)
        if self.disparando and self.frames:
            key_frame = 1 if len(self.frames) > 1 else len(self.frames) - 1
            key_frame = max(0, min(key_frame, len(self.frames) - 1))
            if self.indice_frame == key_frame and not self.bala_disparada:
                self.juego.crear_bala(self.rect.centerx + 50, self.rect.centery, self.direccion)
                self.bala_disparada = True
            if self.indice_frame == len(self.frames) - 1:
                self.disparando = False
                self.bala_disparada = False
                self.cambiar_accion(self.accion_previa)

class Enemigo(SpriteAnimado):
    def __init__(self, y, velocidad, escala=1):
        animaciones = {
            "enemy run": cargar_frames(ruta("Sprite/enemigo/enemy run"), escala=2.75),
            "enemy down": cargar_frames(ruta("Sprite/enemigo/enemy down"), escala=2.75)
        }
        super().__init__(animaciones, (ANCHO, y), accion_inicial="enemy run")
        self.vel_x = velocidad
        self.vida = 1
        self.max_vida = 1
        self.muerto = False
        self.escala = escala

    def recibir_dano(self, cantidad):
        self.vida -= cantidad
        if self.vida <= 0 and not self.muerto:
            self.cambiar_accion("enemy down")
            self.muerto = True
            self.vel_x = 0
            self.mask =  None

    def update(self):
        dt = clock.get_time()
        self.update_animacion(dt)
        if not self.muerto:
            self.rect.x += self.vel_x
            if self.rect.right < 50:
                return "castillo"
        else:
            if self.indice_frame == len(self.frames) - 1:
                self.kill()
        return None

# ====== Nuevo enemigo a partir del nivel 2 ======
class Enemigo2(SpriteAnimado):
    def __init__(self, y, velocidad, escala=6):
        animaciones = {
            "run": cargar_frames(ruta("Sprite/enemidos/caminata"), escala=3.75),
            "down": cargar_frames(ruta("Sprite/enemidos/esquelemuerte"), escala=3.75)
        }
        super().__init__(animaciones, (ANCHO, y), accion_inicial="run")
        self.vel_x = velocidad
        self.vida = 1
        self.max_vida = 1
        self.escala = escala
        self.muerto = False
        

    def recibir_dano(self, cantidad):
        self.vida -= cantidad
        if self.vida <= 0 and not self.muerto:
            self.cambiar_accion("down")
            self.muerto = True
            self.vel_x = 0
            self.mask = None
            

    def update(self):
        dt = clock.get_time()
        self.update_animacion(dt)
        if not self.muerto:
            self.rect.x += self.vel_x
            if self.rect.right < 50:
                return "castillo"
        else:
            if self.indice_frame == len(self.frames) - 1:
                self.kill()
        return None


# ====== Clase Jefe ======
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
        self.mask = pygame.mask.from_surface(self.image)

    def cargar_animacion(self, ruta_carpeta):
        imagenes = []
        for nombre in sorted(os.listdir(ruta_carpeta)):
            img = pygame.image.load(os.path.join(ruta_carpeta, nombre)).convert_alpha()
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
            self.mask = None

    def update(self):
        ahora = pygame.time.get_ticks()
        if self.estado == 'danio' and ahora - self.tiempo_danio > 300:
            if self.vivo:
                self.estado = 'caminar'
        self.frame += 0.2
        if self.frame >= len(self.animaciones[self.estado]):
            if self.estado == 'muerte':
                self.kill()
                return "muerto"
            self.frame = 0
        self.image = self.animaciones[self.estado][int(self.frame)]
        if self.estado == 'caminar':
            self.rect.x -= 2
            if self.rect.right < 50:
                return "castillo"
        return None

# ====== Jefe2 para nivel >=2 ======
class Jefe2(Jefe):
    def __init__(self, x, y, escala=4):
        super().__init__(x, y, escala)
        self.animaciones = {
            "caminar": cargar_frames(ruta("Sprite/jefedos/walk"), escala),
            "danio": cargar_frames(ruta("Sprite/jefedos/danio"), escala),
            "muerte": cargar_frames(ruta("Sprite/jefedos/muerte"), escala)
        }
        self.estado = "caminar"
        self.frame = 0
        self.image = self.animaciones[self.estado][self.frame]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vida = 8
        self.tiempo_danio = 0
        self.vivo = True
        self.mask = pygame.mask.from_surface(self.image)


    def cargar_animacion(self, ruta_carpeta):
        imagenes = []
        for nombre in sorted(os.listdir(ruta_carpeta)):
            img = pygame.image.load(os.path.join(ruta_carpeta, nombre)).convert_alpha()
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
            self.mask = None

    def update(self):
        ahora = pygame.time.get_ticks()
        if self.estado == 'danio' and ahora - self.tiempo_danio > 300:
            if self.vivo:
                self.estado = 'caminar'
        self.frame += 0.2
        if self.frame >= len(self.animaciones[self.estado]):
            if self.estado == 'muerte':
                return "muerto"
            self.frame = 0
        self.image = self.animaciones[self.estado][int(self.frame)]
        if self.estado == 'caminar':
            self.rect.x -= 1
            if self.rect.right < 50:
                self.kill()
                return "castillo"
        return None


# ====== Clase Juego ======
class GestionMatriz:
    def __init__(self, MAX_JUGADAS=50, NUM_OBJETOS=2, DIAS =31, MES=12, PARTIDAS=10):
        #PRIMERA MATRIZ (JUGADAS X OBJETOS)
        self.matriz_jugadas = [[0 for _ in range(NUM_OBJETOS)] for _ in range(MAX_JUGADAS)] #[[cuantos elementos en cada fila] cuantas filas en cada matriz]
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
        
    def calcular_totales(self):
        # Totales por fila (por jugada)
        totales_filas = [sum(fila) for fila in self.matriz_jugadas]

        # Totales por columna (por tipo de objeto/evento)
        totales_columnas = [sum(col) for col in zip(*self.matriz_jugadas)]

        # Total general (suma de todo)
        total_general = sum(totales_filas)
    
        return totales_filas, totales_columnas, total_general

        
    def mostrar_matriz(self):
        print("\n=== MATRIZ DE JUGADAS ===")
        for i, fila in enumerate(self.matriz_jugadas):
            print(f"Fila {i + 1}: {fila} | Total Fila: {sum(fila)}")

        # Totales por columna
        totales_columnas = [sum(col) for col in zip(*self.matriz_jugadas)]
        print(f"Totales por objeto: {totales_columnas}")
        print(f"Total general: {sum(totales_columnas)}")

    
    def mostrar_matriz_dias(self):
        print("=== MATRIZ DE INTERVENCIÓN POR DÍA ===")
        print("Día | Objeto 0 | Objeto 1 | Total Día")
        print("--------------------------------------")

        totales_dia = []
        for i, fila in enumerate(self.matriz_dias):
            total_dia = sum(fila)
            totales_dia.append(total_dia)
            print(f"{i+1:3} | " + " | ".join(f"{v:8}" for v in fila) + f" | {total_dia:9}")

        print("--------------------------------------")
        totales_objetos = [sum(col) for col in zip(*self.matriz_dias)]
        total_general = sum(totales_dia)
        print("Totales objetos:", " | ".join(f"{v:8}" for v in totales_objetos), "|", total_general)

        # Mejor y peor día
        if any(totales_dia):
            mejor_dia = totales_dia.index(max(totales_dia)) + 1
            peor_dia = totales_dia.index(min(totales_dia)) + 1
            print(f"\nEl Mejor Día: {mejor_dia} (Total: {max(totales_dia)})")
            print(f"El Peor Día: {peor_dia} (Total: {min(totales_dia)})")
        else:
            print("\nSin registros de días aún.")
            

    def mostrar_matriz_3D(self):
        print("=== MATRIZ 3D (SOLO PARTIDAS CON MOVIMIENTO) ===")
        hay_partidas_con_movimiento = False  # bandera para saber si hay alguna partida válida

        for idx_partida, partida in enumerate(self.matriz_3D):
            # Calcular el total de la partida (suma de todos los objetos y meses)
            total_partida = sum(sum(mes) for mes in partida)

            if total_partida == 0:
                continue  # si no hubo movimientos, no se muestra esta partida

            hay_partidas_con_movimiento = True
            print(f"\nPartida {idx_partida + 1}")
            print("Mes | Obj0 | Obj1 | Total Mes")
            print("------------------------------")

            # mostrar todos los meses, aunque tengan ceros
            for idx_mes, mes in enumerate(partida):
                total_mes = sum(mes)
                print(f"{idx_mes + 1:3} | " + " | ".join(f"{v:5}" for v in mes) + f" | {total_mes:10}")

            print("------------------------------")
            print(f"Total partida {idx_partida + 1}: {total_partida}")

        # Si ninguna partida tuvo movimiento
        if not hay_partidas_con_movimiento:
            print("\nNo hay partidas registradas con movimiento aún.")

        # Totales generales (solo si hubo partidas con datos)
        if hay_partidas_con_movimiento:
            totales_obj = [
                sum(sum(mes[j] for mes in partida) for partida in self.matriz_3D)
                for j in range(len(self.matriz_3D[0][0]))
            ]
            total_general = sum(totales_obj)
            print("\nTotales generales por objeto:",
                  " | ".join(f"Obj {j} : {v}" for j, v in enumerate(totales_obj)))
            print("Total 3D general:", total_general)

    
    def mostrar_matriz_con_puntero(self):
        print("\n=== MATRIZ DE JUGADAS (MÉTODO DEL PUNTERO) ===")
        fila_puntero = 0
        while fila_puntero < len(self.matriz_jugadas):
            fila = self.matriz_jugadas[fila_puntero]
            col_puntero = 0
            total_fila = 0

            print(f"Fila {fila_puntero + 1} -> ", end="")
            while col_puntero < len(fila):
                valor = fila[col_puntero]
                print(f"[Obj{col_puntero}:{valor}]", end=" ")
                total_fila += valor
                col_puntero += 1

            print(f" | Total Fila: {total_fila}")
            fila_puntero += 1
            
    def mostrar_matriz_dias_con_puntero(self):
        print("\n=== MATRIZ DE DÍAS (MÉTODO DEL PUNTERO) ===")
        dia_puntero = 0
        while dia_puntero < len(self.matriz_dias):
            fila = self.matriz_dias[dia_puntero]
            objeto_puntero = 0
            total_dia = 0

            print(f"Día {dia_puntero + 1}: ", end="")
            while objeto_puntero < len(fila):
                valor = fila[objeto_puntero]
                print(f"Obj{objeto_puntero}={valor}", end=" ")
                total_dia += valor
                objeto_puntero += 1

            print(f"| Total día: {total_dia}")
            dia_puntero += 1

    def mostrar_matriz_3D_con_puntero(self):
        print("\n=== MATRIZ 3D (MÉTODO DEL PUNTERO) ===")

        partida_puntero = 0
        total_general = 0  # total de todas las partidas

        while partida_puntero < len(self.matriz_3D):
            partida = self.matriz_3D[partida_puntero]
            total_partida = 0

            print(f"\nPartida {partida_puntero + 1}:")
            print("Mes | Obj0 | Obj1 | Total Mes")
            print("-------------------------------")

            mes_puntero = 0
            while mes_puntero < len(partida):
                mes = partida[mes_puntero]
                objeto_puntero = 0
                total_mes = 0
                fila_datos = []

                # recorrer objetos (Obj0, Obj1)
                while objeto_puntero < len(mes):
                    valor = mes[objeto_puntero]
                    fila_datos.append(valor)
                    total_mes += valor
                    objeto_puntero += 1

                # imprimir la fila con totales
                if total_mes > 0:  # mostrar solo meses con datos
                    print(f"{mes_puntero + 1:3} | " + " | ".join(f"{v:5}" for v in fila_datos) + f" | {total_mes:10}")

                total_partida += total_mes
                mes_puntero += 1

            print("-------------------------------")
            print(f"Total partida {partida_puntero + 1}: {total_partida}")
            total_general += total_partida
            partida_puntero += 1

        # Mostrar totales por objeto
        objetos = len(self.matriz_3D[0][0]) if self.matriz_3D and self.matriz_3D[0] else 0
        tot_obj = [0] * objetos
        partida_puntero = 0

        # recorrer todo el 3D para sumar objetos
        while partida_puntero < len(self.matriz_3D):
            partida = self.matriz_3D[partida_puntero]
            mes_puntero = 0
            while mes_puntero < len(partida):
                mes = partida[mes_puntero]
                objeto_puntero = 0
                while objeto_puntero < len(mes):
                    tot_obj[objeto_puntero] += mes[objeto_puntero]
                    objeto_puntero += 1
                mes_puntero += 1
            partida_puntero += 1

        print("\nTotales generales por objeto:", " | ".join(f"Obj{j}:{v}" for j, v in enumerate(tot_obj)))
        print("Total 3D general:", total_general)




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

        self.sprites = LayeredUpdates()
        self.sprites.add(self.jugador, layer=3)
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
        self.fecha = datetime.now()
        self.dia = self.fecha.day - 1
        self.mes = self.fecha.month - 1

        self.partida_idx = self.partidas_jugadas - 1

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

        # Spawn de enemigos
        # Spawn de enemigos
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0

            # A partir del nivel 3, mezclamos ambos tipos de enemigos
            if self.nivel >= 3:
                if random.random() < 0.5:  # 50% de probabilidad de cada tipo
                    enemigo = Enemigo(random.randint(40, ALTO - 40), self.enemigo_velocidad)
                else:
                    enemigo = Enemigo2(random.randint(40, ALTO - 40), self.enemigo_velocidad)
            elif self.nivel == 2:
                enemigo = Enemigo2(random.randint(40, ALTO - 40), self.enemigo_velocidad)
            else:
                enemigo = Enemigo(random.randint(40, ALTO - 40), self.enemigo_velocidad)

            self.enemigos.add(enemigo)
            self.sprites.add(enemigo, layer = 1)


        # Actualización de todos los sprites (jugador, enemigos, balas)
        self.sprites.update()
        self.grupo_balas.update()

        # Revisar enemigos
        for enemigo in list(self.enemigos):
            resultado = None

            # Solo comprobaciones de estado sin llamar update otra vez
            if isinstance(enemigo, (Jefe, Jefe2)):
                # Jefe: revisar si llegó al castillo
                if enemigo.estado == "caminar" and enemigo.rect.right < 50:
                    resultado = "castillo"
                elif enemigo.estado == "muerte" and enemigo.frame >= len(enemigo.animaciones["muerte"]) - 1:
                    resultado = "muerto"
            else:
                # Enemigo normal: revisar si llegó al castillo
                if enemigo.rect.right < 50:
                    resultado = "castillo"

            # Aplicar resultados
            if resultado == "castillo":
                if isinstance(enemigo, (Jefe, Jefe2)):
                    self.vidas -= 3
                    self.puntaje_B += 3
                    self.jefe_activo = False
                    self.jefe = None
                else:
                    self.vidas -= 1
                    self.puntaje_B += 1
                    self.matriz.cargar_matriz_3D(self.partida_idx, self.mes, 1)
                    self.matriz.cargar_matriz_dias(self.dia, 1)
                    self.matriz.cargar_matriz_jugadas(self.contador_jugadas, 1)
                    self.contador_jugadas += 1
                    cod_usuario = obtener_codigo_usuario()[0]
                    Guardar_colisiones(cod_usuario, self.partidas_jugadas, enemigo.rect.x, enemigo.rect.y,
                                      "enemigo llegó al castillo")
                enemigo.kill()
                if self.vidas <= 0:
                    self.game_over = True

            elif resultado == "muerto":
                enemigo.kill()
                self.jefe_activo = False
                self.jefe = None
                self.subir_nivel()

        # Colisiones balas-enemigos
        colisiones = pygame.sprite.groupcollide(self.grupo_balas, self.enemigos, True, False, colision_mask_segura)
        if colisiones:
            kills = len(colisiones)
            self.puntaje_A += kills
            self.matriz.cargar_matriz_3D(self.partida_idx, self.mes, 0)
            self.matriz.cargar_matriz_dias(self.dia, 0)
            self.matriz.cargar_matriz_jugadas(self.contador_jugadas, 0)
            self.contador_jugadas += 1

            for bala, enemigos in colisiones.items():
                for enemigo in enemigos:
                    enemigo.recibir_dano(1)
                    cod_usuario = obtener_codigo_usuario()[0]
                    Guardar_colisiones(cod_usuario, self.partidas_jugadas, enemigo.rect.x, enemigo.rect.y)

        # Invocar jefe según nivel
# Invocar jefe según nivel
        if self.puntaje_A >= self.enemigos_para_jefe * self.nivel and not self.jefe_activo:
            pos_y = random.randint(100, ALTO - 400)  # posición vertical aleatoria

            # A partir del nivel 3, vuelve el jefe principal
            if self.nivel == 1:
                self.jefe = Jefe(ANCHO + 150, pos_y)
            elif self.nivel == 2:
                self.jefe = Jefe2(ANCHO + 150, pos_y)
            elif self.nivel == 3:
                self.jefe = Jefe(ANCHO + 150, pos_y)
            else:
                self.jefe = Jefe2(ANCHO + 150, pos_y)

            self.enemigos.add(self.jefe)
            self.sprites.add(self.jefe, layer=5)
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

        for e in self.enemigos:
            if hasattr(e, "dibujar_barra_vida"):
                e.dibujar_barra_vida(surf)

        texto_nivel = fuente.render(f"Nivel: {self.nivel}", True, COLOR_TEXTO)
        surf.blit(texto_nivel, (1100, 10))

        texto = fuente.render(f"Puntaje: {self.puntaje_A}", True, COLOR_TEXTO)
        surf.blit(texto, (1250, 10))
        self.dibujar_barra_vida(surf)

    


        if self.game_over:
            msg = fuente.render("Presiona ESC para ver los resultados", True, (COLOR_TEXTO_REGISTRO))
            rect = msg.get_rect(center=(ANCHO // 2, ALTO // 2 + 60))
            pantalla.blit(msg, rect)
            pygame.display.flip()

            # Esperar a que el jugador presione ESC
            esperando = True
            while esperando:
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        esperando = False
            print()
            self.matriz.mostrar_matriz()
            self.matriz.mostrar_matriz_dias()
            self.matriz.mostrar_matriz_3D()
            self.matriz.mostrar_matriz_con_puntero()
            self.matriz.mostrar_matriz_dias_con_puntero()
            self.matriz.mostrar_matriz_3D_con_puntero()
            filas, columnas, total = self.matriz.calcular_totales()
            # Mostrar resumen
            print("\n=== RESUMEN DE TOTALES ===")
            print(f"Total por jugada: {filas}")
            print(f"Total por objeto: {columnas}")
            print(f"Total general: {total}")
            # Identificar “mejor” y “peor” jugada
            if filas:
                mejor_jugada = filas.index(max(filas)) + 1
                peor_jugada = filas.index(min(filas)) + 1
                print(f"\nMejor jugada: {mejor_jugada} (total {max(filas)})")
                print(f"Peor jugada: {peor_jugada} (total {min(filas)})")

            

    def run(self):
        while True:
            dt = clock.tick(FPS)
            self.manejar_eventos()
            teclas = pygame.key.get_pressed()
            if self.game_over and teclas[pygame.K_ESCAPE]:
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
    