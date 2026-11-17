import os
import shutil
import datetime

carpeta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "GESTOR_SO")


def preparar():
    if os.path.islink(carpeta):
        print("GESTOR_SO no puede ser un enlace")
        return False
    if os.path.exists(carpeta):
        if not os.path.isdir(carpeta):
            print("GESTOR_SO existe pero no es una carpeta")
            return False
    else:
        os.mkdir(carpeta)
    return True


def ruta_segura(nom, vacio=False):
    nom = nom.strip()
    if os.path.islink(carpeta) or not os.path.isdir(carpeta):
        print("la carpeta de trabajo no esta lista")
        return None
    if nom == "":
        if vacio:
            return carpeta
        print("falta el nombre")
        return None
    if os.path.isabs(nom) or "\\" in nom or ":" in nom or "\0" in nom or nom.startswith("~"):
        print("usa una ruta dentro de GESTOR_SO")
        return None

    ruta = carpeta
    for parte in nom.split("/"):
        if parte == "" or parte.endswith(".") or parte.endswith(" "):
            print("nombre no valido")
            return None
        ruta = os.path.join(ruta, parte)
        if os.path.islink(ruta):
            print("no se permiten enlaces")
            return None

    if not os.path.isdir(os.path.dirname(ruta)):
        print("no existe la carpeta indicada")
        return None
    return ruta


def crear_dir():
    nom = input("nombre de la carpeta: ")
    ruta = ruta_segura(nom)
    if ruta is None:
        return
    if os.path.exists(ruta):
        print("ya existe algo con ese nombre")
    else:
        os.mkdir(ruta)
        print("carpeta creada")


def crear_arch():
    nom = input("nombre del archivo: ").strip()
    ruta = ruta_segura(nom)
    if ruta is None:
        return
    if not nom.lower().endswith(".txt"):
        nom = nom + ".txt"
        ruta = ruta_segura(nom)
        if ruta is None:
            return
    if os.path.exists(ruta):
        print("ya existe algo con ese nombre")
    else:
        with open(ruta, "x", encoding="utf-8") as f:
            f.write("")
        print("archivo creado")


def escribir():
    nom = input("en que archivo escribo: ")
    ruta = ruta_segura(nom)
    if ruta is None:
        return
    if os.path.isfile(ruta):
        txt = input("que quieres escribir: ")
        with open(ruta, "a", encoding="utf-8") as f:
            f.write(txt + "\n")
        print("listo se guardo")
    else:
        print("no existe ese archivo o no es un archivo")


def leer():
    nom = input("que archivo leo: ")
    ruta = ruta_segura(nom)
    if ruta is None:
        return
    if os.path.isfile(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            txt = f.read()
        if txt == "":
            print("el archivo esta vacio")
        else:
            print(txt)
    else:
        print("no existe ese archivo o no es un archivo")


def renombrar():
    viejo = input("archivo a renombrar: ")
    ruta1 = ruta_segura(viejo)
    if ruta1 is None:
        return
    if not os.path.isfile(ruta1):
        print("no existe ese archivo o no es un archivo")
        return
    nuevo = input("nuevo nombre: ")
    ruta2 = ruta_segura(nuevo)
    if ruta2 is None:
        return
    if os.path.exists(ruta2):
        print("ya existe algo con ese nombre")
    else:
        os.rename(ruta1, ruta2)
        print("renombrado")


def copiar():
    orig = input("archivo a copiar: ")
    ruta1 = ruta_segura(orig)
    if ruta1 is None:
        return
    if not os.path.isfile(ruta1):
        print("no existe ese archivo o no es un archivo")
        return
    dest = input("nombre de la copia: ")
    ruta2 = ruta_segura(dest)
    if ruta2 is None:
        return
    if os.path.exists(ruta2):
        print("ya existe algo con ese nombre")
    else:
        shutil.copy2(ruta1, ruta2)
        print("copiado")


def eliminar():
    nom = input("archivo a eliminar: ")
    ruta = ruta_segura(nom)
    if ruta is None:
        return
    if os.path.isfile(ruta):
        resp = input("seguro que quieres borrarlo? (s/n): ").strip().lower()
        if resp == "s":
            os.remove(ruta)
            print("eliminado")
        else:
            print("cancelado")
    else:
        print("no existe ese archivo o no es un archivo")


def listar():
    nom = input("carpeta a listar (enter para GESTOR_SO): ")
    ruta = ruta_segura(nom, True)
    if ruta is None:
        return
    if not os.path.isdir(ruta):
        print("eso no es una carpeta")
        return
    cosas = sorted(os.listdir(ruta))
    if len(cosas) == 0:
        print("no hay nada")
    else:
        for c in cosas:
            dato = os.path.join(ruta, c)
            if os.path.islink(dato):
                print("[enlace]", c)
            elif os.path.isdir(dato):
                print("[carpeta]", c)
            else:
                print("[archivo]", c)


def info():
    nom = input("de que archivo quieres la info: ")
    ruta = ruta_segura(nom)
    if ruta is None:
        return
    if os.path.isfile(ruta):
        datos = os.stat(ruta)
        tam = datos.st_size
        fecha = datetime.datetime.fromtimestamp(datos.st_mtime)
        print("nombre:", os.path.basename(ruta))
        print("tamano:", tam, "bytes")
        print("modificado:", fecha.strftime("%Y-%m-%d %H:%M:%S"))
    else:
        print("no existe ese archivo o no es un archivo")


def menu():
    print("\n===== GESTOR DE ARCHIVOS =====")
    print("1. crear un directorio")
    print("2. crear un archivo de texto")
    print("3. escribir en un archivo")
    print("4. leer un archivo")
    print("5. renombrar un archivo")
    print("6. copiar un archivo")
    print("7. eliminar un archivo")
    print("8. listar archivos y carpetas")
    print("9. info de un archivo")
    print("0. salir")


def main():
    try:
        if not preparar():
            return
    except OSError as error:
        print("no se pudo preparar GESTOR_SO:", error)
        return

    op = ""
    while op != "0":
        menu()
        try:
            op = input("elige una opcion: ").strip()
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
            elif op == "0":
                print("chao")
            else:
                print("opcion no valida")
        except UnicodeError:
            print("no se pudo leer o guardar el texto, usa archivos utf-8")
        except OSError as error:
            print("no se pudo hacer la operacion:", error)
        except (KeyboardInterrupt, EOFError):
            print("\nchao")
            break


if __name__ == "__main__":
    main()
