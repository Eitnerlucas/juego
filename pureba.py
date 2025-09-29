#def obtener():
#    with open("usuarios.txt", "r") as archivo:
#        linea = archivo.readlines()
#        print(linea)
#        
#obtener()
import os
def obtener_codigo_usuario():
    with open("usuarios.txt", "r") as archivo:
        for linea in archivo:
            campos = linea.strip().split(",")
            cod_usuario = campos[0]
            nombre = campos[1]
            apodo = campos[2]
            clave = campos[3]
    print(cod_usuario, nombre, apodo, clave)
            
def probar():
    if not os.path.exists("prueba.txt"):
        with open("prueba.txt", 'w') as archivo:
            archivo.write("0")
    else:
        with open("prueba.txt", 'r') as archivo:
            linea = archivo.readlines()
            
            if linea:
                print(linea)
            else:
                print("vacio")
                
proba = probar()
print(proba)