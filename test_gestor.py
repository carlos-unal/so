import os
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import main


class pruebas(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name) / "GESTOR_SO"
        self.base.mkdir()
        self.fuera = Path(self.temp.name) / "fuera.txt"
        self.fuera.write_text("no tocar", encoding="utf-8")
        self.cambio = patch("main.carpeta", str(self.base))
        self.cambio.start()

    def tearDown(self):
        self.cambio.stop()
        self.temp.cleanup()

    def hacer(self, funcion, entradas):
        salida = StringIO()
        with patch("builtins.input", side_effect=entradas):
            with redirect_stdout(salida):
                funcion()
        return salida.getvalue()

    def test_preparar_carpeta(self):
        self.base.rmdir()
        self.hacer(main.main, ["0"])
        self.assertTrue(self.base.is_dir())

    def test_base_no_puede_ser_archivo(self):
        self.base.rmdir()
        self.base.write_text("no tocar", encoding="utf-8")
        salida = self.hacer(main.main, [])
        self.assertIn("no es una carpeta", salida)
        self.assertEqual(self.base.read_text(encoding="utf-8"), "no tocar")

    def test_crear_directorio(self):
        salida = self.hacer(main.crear_dir, ["tareas"])
        self.assertTrue((self.base / "tareas").is_dir())
        self.assertIn("carpeta creada", salida)
        salida = self.hacer(main.crear_dir, ["tareas"])
        self.assertIn("ya existe", salida)

    def test_crear_archivo(self):
        salida = self.hacer(main.crear_arch, ["nota.txt"])
        ruta = self.base / "nota.txt"
        self.assertTrue(ruta.is_file())
        self.assertEqual(ruta.read_text(encoding="utf-8"), "")
        self.assertIn("archivo creado", salida)

    def test_agregar_extension(self):
        self.hacer(main.crear_arch, ["nota"])
        self.hacer(main.crear_arch, ["otra.TXT"])
        self.assertTrue((self.base / "nota.txt").is_file())
        self.assertTrue((self.base / "otra.TXT").is_file())
        self.assertFalse((self.base / "otra.TXT.txt").exists())

    def test_no_reemplazar_al_crear(self):
        ruta = self.base / "nota.txt"
        ruta.write_text("original", encoding="utf-8")
        salida = self.hacer(main.crear_arch, ["nota"])
        self.assertIn("ya existe", salida)
        self.assertEqual(ruta.read_text(encoding="utf-8"), "original")

    def test_nombres_vacios(self):
        salida = self.hacer(main.crear_arch, ["   "])
        self.assertIn("falta el nombre", salida)
        salida = self.hacer(main.crear_dir, [""])
        self.assertIn("falta el nombre", salida)
        self.assertEqual(os.listdir(self.base), [])

    def test_archivo_en_subcarpeta(self):
        self.hacer(main.crear_dir, ["tareas"])
        self.hacer(main.crear_arch, ["tareas/nota"])
        self.assertTrue((self.base / "tareas" / "nota.txt").is_file())

    def test_carpeta_destino_no_existe(self):
        salida = self.hacer(main.crear_arch, ["falta/nota.txt"])
        self.assertIn("no existe la carpeta indicada", salida)
        self.assertFalse((self.base / "falta").exists())

    def test_escribir_sin_borrar(self):
        ruta = self.base / "nota.txt"
        ruta.write_text("primera\n", encoding="utf-8")
        salida = self.hacer(main.escribir, ["nota.txt", "segunda, con ñ y tildes: áéíóú"])
        self.assertIn("listo se guardo", salida)
        self.assertEqual(ruta.read_text(encoding="utf-8"), "primera\nsegunda, con ñ y tildes: áéíóú\n")

    def test_leer_archivo(self):
        ruta = self.base / "nota.txt"
        ruta.write_text("hola mundo", encoding="utf-8")
        salida = self.hacer(main.leer, ["nota.txt"])
        self.assertIn("hola mundo", salida)

    def test_leer_archivo_vacio(self):
        (self.base / "nota.txt").touch()
        salida = self.hacer(main.leer, ["nota.txt"])
        self.assertIn("el archivo esta vacio", salida)

    def test_archivo_que_no_existe(self):
        for funcion in [main.escribir, main.leer, main.renombrar, main.copiar, main.eliminar, main.info]:
            salida = self.hacer(funcion, ["falta.txt"])
            self.assertIn("no existe ese archivo", salida)

    def test_no_tratar_carpeta_como_archivo(self):
        (self.base / "tareas").mkdir()
        for funcion in [main.escribir, main.leer, main.renombrar, main.copiar, main.eliminar, main.info]:
            salida = self.hacer(funcion, ["tareas"])
            self.assertIn("no es un archivo", salida)
        self.assertTrue((self.base / "tareas").is_dir())

    def test_renombrar_archivo(self):
        ruta = self.base / "nota.txt"
        ruta.write_text("hola", encoding="utf-8")
        salida = self.hacer(main.renombrar, ["nota.txt", "nueva.txt"])
        self.assertIn("renombrado", salida)
        self.assertFalse(ruta.exists())
        self.assertEqual((self.base / "nueva.txt").read_text(encoding="utf-8"), "hola")

    def test_copiar_archivo(self):
        ruta = self.base / "nota.txt"
        ruta.write_text("hola", encoding="utf-8")
        salida = self.hacer(main.copiar, ["nota.txt", "copia.txt"])
        self.assertIn("copiado", salida)
        self.assertTrue(ruta.is_file())
        self.assertEqual((self.base / "copia.txt").read_text(encoding="utf-8"), "hola")

    def test_no_reemplazar_al_copiar_o_renombrar(self):
        ruta1 = self.base / "nota.txt"
        ruta2 = self.base / "otra.txt"
        ruta1.write_text("original", encoding="utf-8")
        ruta2.write_text("conservar", encoding="utf-8")
        for funcion in [main.copiar, main.renombrar]:
            salida = self.hacer(funcion, ["nota.txt", "otra.txt"])
            self.assertIn("ya existe", salida)
            self.assertEqual(ruta1.read_text(encoding="utf-8"), "original")
            self.assertEqual(ruta2.read_text(encoding="utf-8"), "conservar")

    def test_cancelar_borrado(self):
        ruta = self.base / "nota.txt"
        ruta.write_text("hola", encoding="utf-8")
        for resp in ["n", "", "otra cosa"]:
            salida = self.hacer(main.eliminar, ["nota.txt", resp])
            self.assertIn("cancelado", salida)
            self.assertEqual(ruta.read_text(encoding="utf-8"), "hola")

    def test_confirmar_borrado(self):
        ruta = self.base / "nota.txt"
        ruta.write_text("hola", encoding="utf-8")
        salida = self.hacer(main.eliminar, ["nota.txt", " S "])
        self.assertIn("eliminado", salida)
        self.assertFalse(ruta.exists())

    def test_listar(self):
        (self.base / "tareas").mkdir()
        (self.base / "nota.txt").touch()
        salida = self.hacer(main.listar, [""])
        self.assertIn("[carpeta] tareas", salida)
        self.assertIn("[archivo] nota.txt", salida)

    def test_listar_vacio(self):
        salida = self.hacer(main.listar, [""])
        self.assertIn("no hay nada", salida)

    def test_listar_subcarpeta(self):
        (self.base / "tareas").mkdir()
        (self.base / "tareas" / "nota.txt").touch()
        salida = self.hacer(main.listar, ["tareas"])
        self.assertIn("[archivo] nota.txt", salida)

    def test_listar_no_acepta_archivo(self):
        (self.base / "nota.txt").touch()
        salida = self.hacer(main.listar, ["nota.txt"])
        self.assertIn("eso no es una carpeta", salida)

    def test_info(self):
        ruta = self.base / "nota.txt"
        ruta.write_text("hola", encoding="utf-8")
        salida = self.hacer(main.info, ["nota.txt"])
        self.assertIn("nombre: nota.txt", salida)
        self.assertIn("tamano: 4 bytes", salida)
        self.assertIn("modificado:", salida)

    def test_bloquear_rutas_fuera(self):
        nombres = [
            "../fuera.txt",
            str(self.fuera),
            "C:/fuera.txt",
            "..\\fuera.txt",
            "~/fuera.txt",
            "tareas/../../fuera.txt",
            ".. /fuera.txt",
            "nota\0.txt"
        ]
        for nom in nombres:
            salida = self.hacer(main.leer, [nom])
            self.assertTrue("ruta dentro" in salida or "nombre no valido" in salida)
        self.assertEqual(self.fuera.read_text(encoding="utf-8"), "no tocar")

    def test_bloquear_salidas_en_todas_las_opciones(self):
        for funcion in [main.crear_dir, main.crear_arch, main.escribir, main.leer, main.renombrar, main.copiar, main.eliminar, main.listar, main.info]:
            salida = self.hacer(funcion, ["../fuera.txt"])
            self.assertIn("nombre no valido", salida)
        self.assertEqual(self.fuera.read_text(encoding="utf-8"), "no tocar")

    def test_bloquear_destino_fuera(self):
        (self.base / "nota.txt").write_text("original", encoding="utf-8")
        for funcion in [main.copiar, main.renombrar]:
            salida = self.hacer(funcion, ["nota.txt", "../fuera.txt"])
            self.assertIn("nombre no valido", salida)
        self.assertEqual(self.fuera.read_text(encoding="utf-8"), "no tocar")
        self.assertEqual((self.base / "nota.txt").read_text(encoding="utf-8"), "original")

    def test_bloquear_enlaces(self):
        enlace = self.base / "enlace.txt"
        try:
            enlace.symlink_to(self.fuera)
        except (OSError, NotImplementedError):
            self.skipTest("no se pueden crear enlaces en este equipo")
        for funcion in [main.crear_arch, main.escribir, main.leer, main.renombrar, main.copiar, main.eliminar, main.info]:
            salida = self.hacer(funcion, ["enlace.txt"])
            self.assertIn("no se permiten enlaces", salida)
        salida = self.hacer(main.listar, [""])
        self.assertIn("[enlace] enlace.txt", salida)
        self.assertEqual(self.fuera.read_text(encoding="utf-8"), "no tocar")

    def test_bloquear_enlace_en_subcarpeta(self):
        enlace = self.base / "atajo"
        try:
            enlace.symlink_to(self.temp.name, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("no se pueden crear enlaces en este equipo")
        salida = self.hacer(main.leer, ["atajo/fuera.txt"])
        self.assertIn("no se permiten enlaces", salida)
        self.assertEqual(self.fuera.read_text(encoding="utf-8"), "no tocar")

    def test_bloquear_base_enlace(self):
        self.base.rmdir()
        try:
            self.base.symlink_to(self.temp.name, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("no se pueden crear enlaces en este equipo")
        salida = self.hacer(main.main, [])
        self.assertIn("GESTOR_SO no puede ser un enlace", salida)
        self.assertEqual(self.fuera.read_text(encoding="utf-8"), "no tocar")

    def test_error_de_permisos_no_cierra_el_menu(self):
        (self.base / "nota.txt").touch()
        with patch("main.os.rename", side_effect=PermissionError("sin permiso")):
            salida = self.hacer(main.main, ["5", "nota.txt", "otra.txt", "0"])
        self.assertIn("no se pudo hacer la operacion", salida)
        self.assertIn("chao", salida)
        self.assertTrue((self.base / "nota.txt").is_file())

    def test_error_de_texto_no_cierra_el_menu(self):
        (self.base / "nota.txt").write_bytes(b"\xff\xfe")
        salida = self.hacer(main.main, ["4", "nota.txt", "0"])
        self.assertIn("usa archivos utf-8", salida)
        self.assertIn("chao", salida)

    def test_menu_completo(self):
        entradas = [
            "1", "tareas",
            "2", "tareas/nota",
            "3", "tareas/nota.txt", "hola mundo",
            "4", "tareas/nota.txt",
            "5", "tareas/nota.txt", "tareas/nueva.txt",
            "6", "tareas/nueva.txt", "copia.txt",
            "8", "",
            "9", "copia.txt",
            "7", "copia.txt", "n",
            "7", "copia.txt", "s",
            "99",
            " 0 "
        ]
        salida = self.hacer(main.main, entradas)
        self.assertIn("carpeta creada", salida)
        self.assertIn("archivo creado", salida)
        self.assertIn("hola mundo", salida)
        self.assertIn("renombrado", salida)
        self.assertIn("copiado", salida)
        self.assertIn("cancelado", salida)
        self.assertIn("eliminado", salida)
        self.assertIn("opcion no valida", salida)
        self.assertIn("chao", salida)
        self.assertFalse((self.base / "copia.txt").exists())
        self.assertEqual((self.base / "tareas" / "nueva.txt").read_text(encoding="utf-8"), "hola mundo\n")


if __name__ == "__main__":
    unittest.main()
