import pygame #herramientas para el juego
import sys # para manejar las salidas del programa
import random #para obtener valores random (obtener numeros aleatorios)
import os  #para operaciones del sistema 
from datetime import datetime #para obtener fechas

# ====== Configuración ==================================================================================================================================================================================================
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


# ====== Registro de jugador en pantalla ================================================================================================================================================================================
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
    
# ====== Funciones para manejo de archivos ===============================================================================================================================================================================
            
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
        

# ====== Clases ==========================================================================================================================================================================================================
class Jugador(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__() # super() llama al constructor de la clase padre (pygame.sprite.Sprite)
        self.image = pygame.Surface((40, 40)) #crea una superficie de 40x40 pixeles
        self.image.fill(COLOR_JUGADOR) #rellena la superficie con el color definido
        self.rect = self.image.get_rect(center=(x, y)) #obtiene el rectángulo que rodea la imagen y lo centra en (x, y)
        self.vel_y = 0 #velocidad vertical inicial
        self.velocidad = 5 #velocidad de movimiento

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


#========= MATRICES CON FOR Y CON PUNTERO===============================================================================================================================================================================================
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

        
    def mostrar_matriz(self, matriz):
        print("=== MATRIZ DE JUGADAS ===")
        print("Fila | Objeto 0 | Objeto 1 | Total Fila")
        print("----------------------------------------")
        for i, fila in enumerate(matriz):
            total_fila = sum(fila)
            print(f"{i+1:4} | " + " | ".join(f"{v:8}" for v in fila) + f" | {total_fila:10}")
        print("----------------------------------------")

        # Totales por columna
        totales_columnas = [sum(col) for col in zip(*matriz)]
        total_general = sum(totales_columnas)
        print("Totales columnas:", " | ".join(f"{v:8}" for v in totales_columnas), "|", total_general)
    
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
        while partida_puntero < len(self.matriz_3D):
            partida = self.matriz_3D[partida_puntero]
            total_partida = 0
            print(f"\nPartida {partida_puntero + 1}:")
            mes_puntero = 0
            while mes_puntero < len(partida):
                mes = partida[mes_puntero]
                objeto_puntero = 0
                total_mes = 0
                while objeto_puntero < len(mes):
                    valor = mes[objeto_puntero]
                    total_mes += valor
                    objeto_puntero += 1
                print(f"  Mes {mes_puntero + 1} -> Total: {total_mes}")
                total_partida += total_mes
                mes_puntero += 1
            print(f"Total partida: {total_partida}")
            partida_puntero += 1





# ====== Juego ======================================================================================================================================================================================================
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
        self.enemigo_velocidad = -2

        self.puntaje_A = 0
        self.puntaje_B = 0
        self.vidas = 5
        self.game_over = False
        self.contador_jugadas = 0
        self.fecha = datetime.now()
        self.dia = self.fecha.day - 1
        self.mes = self.fecha.month - 1
        self.partida_idx = self.partidas_jugadas - 1

        
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
                self.matriz.cargar_matriz_3D(self.partida_idx, self.mes, 1)
                self.matriz.cargar_matriz_dias(self.dia, 1)
                self.matriz.cargar_matriz_jugadas(self.contador_jugadas, 1)
                self.contador_jugadas += 1
                cod_usuario = obtener_codigo_usuario()[0]
                Guardar_colisiones(cod_usuario, self.partidas_jugadas, enemigo.rect.x, enemigo.rect.y, "enemigo llegó al castillo")
                if self.vidas <= 0:
                    self.game_over = True

        colisiones = pygame.sprite.groupcollide(self.balas, self.enemigos, True, True)
        if colisiones:
            kills = len(colisiones)
            self.puntaje_A += kills
            self.matriz.cargar_matriz_3D(self.partida_idx, self.mes, 0)
            self.matriz.cargar_matriz_jugadas(self.contador_jugadas, 0)
            self.matriz.cargar_matriz_dias(self.dia, 0)
            self.contador_jugadas += 1
            for bala, enemigos in colisiones.items():
                for enemigo in enemigos:
                    cod_usuario = obtener_codigo_usuario()[0]
                    Guardar_colisiones(cod_usuario, self.partidas_jugadas, enemigo.rect.x, enemigo.rect.y,)
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
                print()
                self.matriz.mostrar_matriz_3D()
                self.matriz.mostrar_matriz_dias()
                self.matriz.mostrar_matriz(self.matriz.matriz_jugadas)
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
                


                cod_usuario, nombre, apodo, clave = obtener_codigo_usuario()
                guardar_detalle_partida(cod_usuario, self.partidas_jugadas, self.puntaje_A, self.puntaje_B)
                pygame.quit()
                sys.exit()
            self.actualizar(dt)
            self.dibujar(pantalla)
            pygame.display.flip()
            

# ====== Ejecutar ========================================================================================================================================================================================================
if __name__ == "__main__":
    nombre = pantalla_registro()
    Juego(nombre).run()