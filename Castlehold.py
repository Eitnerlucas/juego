import pygame #herramientas para el juego
import sys # para manejar las salidas del programa
import random #para obtener valores random (obtener numeros aleatorios)
import os  #para operaciones del sistema 
from datetime import datetime #para obtener fechas

# ====== Configuración ======
ANCHO, ALTO = 1400, 800 #cambio el tamaño de la ventana
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
pygame.display.set_caption("Juego de Eitner- registro de usuario")
clock = pygame.time.Clock()
fuente = pygame.font.SysFont("consolas", 20)
fondo_inicio = pygame.image.load("fondo_galdor.png").convert() #carga la imagen de fondo y la convierte para optimizar el rendimiento
fondo_juego = pygame.image.load("dungeon.png").convert() #carga la imagen de fondo y la convierte para optimizar el rendimiento


#========= pantalla de inicio ========
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
                    return  # cualquier otra tecla continúa

        pantalla.blit(fondo_inicio,(0,0))

        # Mensajes
       # titulo = fuente.render("COMENZAR", True, COLOR_TEXTO)
        instruccion = fuente.render("Presiona cualquier tecla para comenzar", True, (180, 180, 180))
        salir = fuente.render("Presiona ESC para salir", True, (180, 100, 100))

        #pantalla.blit(titulo, (ANCHO//2 - titulo.get_width()//2, ALTO//2 - 60))
        pantalla.blit(instruccion, (ANCHO//2 - instruccion.get_width()//2, ALTO//2)) # centra el texto
        pantalla.blit(salir, (ANCHO//2 - salir.get_width()//2, ALTO//2 + 40)) # centra el texto

        pygame.display.flip()
        clock.tick(FPS)



# =============== Registro de jugador en pantalla ====== AHORA SE EJECUTA AL FINALIZAR LA PARTIDA    
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


def Guardar_colisiones(cod_usuario, num_partida, x, y, obs="enemigo eliminado"):
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("colisiones.txt", "a") as f:
        f.write(f"{cod_usuario},{num_partida},{x},{y},{obs},{fecha}\n")
        



# ====== Clases ======
class Jugador(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__() # super() llama al constructor de la clase padre (pygame.sprite.Sprite)
        self.image = pygame.Surface((70, 70)) #crea una superficie de 40x40 pixeles
        self.image.fill(COLOR_JUGADOR) #rellena la superficie con el color definido
        self.rect = self.image.get_rect(center=(x, y)) #obtiene el rectángulo que rodea la imagen y lo centra en (x, y)
        self.vel_y = 0 #velocidad vertical inicial
        self.velocidad = 10 #velocidad de movimiento

    def manejar_input(self, teclas): #maneja el input del teclado
        self.vel_y = 0 #resetea la velocidad vertical
        if teclas[pygame.K_UP]: #si la tecla arriba está presionada
            self.vel_y = -self.velocidad #mueve hacia arriba
        if teclas[pygame.K_DOWN]: #si la tecla abajo está presionada
            self.vel_y = self.velocidad #mueve hacia abajo

    def update(self): #actualiza la posición del jugador
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
        self.vel_x = 15

    def update(self):
        self.rect.x += self.vel_x
        if self.rect.left > ANCHO:
            self.kill()


class Enemigo(pygame.sprite.Sprite):
    def __init__(self, y, velocidad):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill(COLOR_ENEMIGO)
        self.rect = self.image.get_rect(midright=(ANCHO, y))
        self.vel_x = velocidad

    def update(self):
        self.rect.x += self.vel_x
        if self.rect.right < 50:  # tocó el castillo
            self.kill()
            return "castillo"
        return None

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
    def __init__(self, MAX_JUGADAS=150, NUM_OBJETOS=2, DIAS =31, MES=12, PARTIDAS=100):
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

        # --- QUITÉ la primera pasada que llamaba enemigo.update() aquí ---
        # Procesamos colisiones primero (esto permite gestionar daño/muerte inmediatamente)
        colisiones = pygame.sprite.groupcollide(self.balas, self.enemigos, True, False)
        if colisiones:
            kills = len(colisiones)
            self.puntaje_A += kills
            self.matriz.cargar_matriz_jugadas(self.contador_jugadas, 0)
            self.contador_jugadas += 1

            for bala, lista_enemigos in colisiones.items():
                for enemigo in lista_enemigos:
                    if isinstance(enemigo, jefe):
                        enemigo.recibir_dano(1)  # cada bala le quita 1 al jefe
                        # comprobar muerte inmediatamente
                        if enemigo.vida <= 0:
                            # removerlo y gestionar subida de nivel AHORA
                            enemigo.kill()
                            if enemigo in self.enemigos:
                                self.enemigos.remove(enemigo)
                            self.jefe_activo = False
                            self.jefe = None
                            self.subir_nivel()
                    else:
                        enemigo.kill()
                        # guardar colisión de enemigo eliminado
                    cod_usuario = obtener_codigo_usuario()[0]
                    Guardar_colisiones(cod_usuario, self.partidas_jugadas, enemigo.rect.x, enemigo.rect.y)

            # ajustar dificultad en base a puntaje
            if self.puntaje_A % 25 == 0:
                self.enemigo_velocidad -= 0.5
                if self.spawn_interval > 600:
                    self.spawn_interval -= 200

        # verificar si toca invocar al jefe (si no está activo)
        if self.puntaje_A >= self.enemigos_para_jefe * self.nivel and not self.jefe_activo:
            self.jefe = jefe(ALTO // 2)
            self.enemigos.add(self.jefe)
            self.jefe_activo = True

        # UNA SOLA pasada para actualizar enemigos y procesar "castillo"
        for enemigo in list(self.enemigos):
            resultado = enemigo.update()
            if resultado == "castillo":
                if isinstance(enemigo, jefe):
                    self.vidas -= 3
                    self.puntaje_B += 3
                    # ya que llegó al castillo, lo removemos
                    if enemigo in self.enemigos:
                        self.enemigos.remove(enemigo)
                    self.jefe_activo = False
                    self.jefe = None
                else:
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
