import os
import shutil
from pathlib import Path
import datetime

carpeta = "GESTOR_SO"

if not os.path.exists(carpeta):
    os.mkdir(carpeta)


def crear_dir():
    nom = input("nombre de la carpeta: ")
    ruta = os.path.join(carpeta, nom)
    if os.path.exists(ruta):
        print("ya existe esa carpeta")
    else:
        os.mkdir(ruta)
        print("carpeta creada")


def crear_arch():
    nom = input("nombre del archivo: ")
    if not nom.endswith(".txt"):
        nom = nom + ".txt"
    ruta = os.path.join(carpeta, nom)
    if os.path.exists(ruta):
        print("ya existe ese archivo")
    else:
        f = open(ruta, "w")
        f.close()
        print("archivo creado")


def escribir():
    nom = input("en que archivo escribo: ")
    ruta = os.path.join(carpeta, nom)
    if os.path.exists(ruta):
        txt = input("que quieres escribir: ")
        f = open(ruta, "a")
        f.write(txt + "\n")
        f.close()
        print("listo se guardo")
    else:
        print("no existe ese archivo")


def leer():
    nom = input("que archivo leo: ")
    ruta = os.path.join(carpeta, nom)
    if os.path.exists(ruta):
        f = open(ruta, "r")
        print(f.read())
        f.close()
    else:
        print("no existe ese archivo")


def renombrar():
    viejo = input("archivo a renombrar: ")
    ruta1 = os.path.join(carpeta, viejo)
    if os.path.exists(ruta1):
        nuevo = input("nuevo nombre: ")
        ruta2 = os.path.join(carpeta, nuevo)
        os.rename(ruta1, ruta2)
        print("renombrado")
    else:
        print("no existe ese archivo")


def copiar():
    orig = input("archivo a copiar: ")
    ruta1 = os.path.join(carpeta, orig)
    if os.path.exists(ruta1):
        dest = input("nombre de la copia: ")
        ruta2 = os.path.join(carpeta, dest)
        shutil.copy(ruta1, ruta2)
        print("copiado")
    else:
        print("no existe ese archivo")


def eliminar():
    nom = input("archivo a eliminar: ")
    ruta = os.path.join(carpeta, nom)
    if os.path.exists(ruta):
        resp = input("seguro que quieres borrarlo? (s/n): ")
        if resp == "s":
            os.remove(ruta)
            print("eliminado")
        else:
            print("cancelado")
    else:
        print("no existe ese archivo")


def listar():
    cosas = os.listdir(carpeta)
    if len(cosas) == 0:
        print("no hay nada")
    else:
        for c in cosas:
            print(c)


def info():
    nom = input("de que archivo quieres la info: ")
    ruta = os.path.join(carpeta, nom)
    if os.path.exists(ruta):
        p = Path(ruta)
        tam = p.stat().st_size
        fecha = datetime.datetime.fromtimestamp(p.stat().st_mtime)
        print("nombre: " + p.name)
        print("tamano: " + str(tam) + " bytes")
        print("modificado: " + str(fecha))
    else:
        print("no existe ese archivo")


op = ""
while op != "10":
    print("")
    print("1. crear un directorio")
    print("2. crear un archivo de texto")
    print("3. escribir en un archivo")
    print("4. leer un archivo")
    print("5. renombrar un archivo")
    print("6. copiar un archivo")
    print("7. eliminar un archivo")
    print("8. listar archivos")
    print("9. info de un archivo")
    print("10. salir")
    op = input("elige una opcion: ")

    if op == "1":
        crear_dir()
    elif op == "2":
        crear_arch()
    elif op == "3":
        escribir()
    elif op == "4":
        leer()
    elif op == "5":
        renombrar()
    elif op == "6":
        copiar()
    elif op == "7":
        eliminar()
    elif op == "8":
        listar()
    elif op == "9":
        info()
    elif op == "10":
        print("chao")
    else:
        print("opcion no valida")
