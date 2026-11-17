import io
import os
import shutil
import tempfile
import unittest
from unittest import mock

import gestor


class PruebasGestor(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.carpeta_patch = mock.patch.object(gestor, "carpeta", self.tmp)
        self.carpeta_patch.start()

    def tearDown(self):
        self.carpeta_patch.stop()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def correr(self, func, entradas):
        salida = io.StringIO()
        with mock.patch("builtins.input", side_effect=entradas):
            with mock.patch("sys.stdout", salida):
                func()
        return salida.getvalue()

    def test_crear_dir(self):
        salida = self.correr(gestor.crear_dir, ["cosas"])
        self.assertIn("carpeta creada", salida)
        self.assertTrue(os.path.isdir(os.path.join(self.tmp, "cosas")))

    def test_crear_dir_repetido(self):
        os.mkdir(os.path.join(self.tmp, "cosas"))
        salida = self.correr(gestor.crear_dir, ["cosas"])
        self.assertIn("ya existe esa carpeta", salida)

    def test_crear_arch_agrega_txt(self):
        salida = self.correr(gestor.crear_arch, ["notas"])
        self.assertIn("archivo creado", salida)
        self.assertTrue(os.path.exists(os.path.join(self.tmp, "notas.txt")))

    def test_crear_arch_repetido(self):
        open(os.path.join(self.tmp, "notas.txt"), "w").close()
        salida = self.correr(gestor.crear_arch, ["notas.txt"])
        self.assertIn("ya existe ese archivo", salida)

    def test_escribir(self):
        open(os.path.join(self.tmp, "notas.txt"), "w").close()
        salida = self.correr(gestor.escribir, ["notas.txt", "hola"])
        self.assertIn("listo se guardo", salida)
        f = open(os.path.join(self.tmp, "notas.txt"), "r")
        self.assertEqual(f.read(), "hola\n")
        f.close()

    def test_escribir_no_existe(self):
        salida = self.correr(gestor.escribir, ["falta.txt", "hola"])
        self.assertIn("no existe ese archivo", salida)

    def test_leer(self):
        f = open(os.path.join(self.tmp, "notas.txt"), "w")
        f.write("contenido\n")
        f.close()
        salida = self.correr(gestor.leer, ["notas.txt"])
        self.assertIn("contenido", salida)

    def test_leer_no_existe(self):
        salida = self.correr(gestor.leer, ["falta.txt"])
        self.assertIn("no existe ese archivo", salida)

    def test_renombrar(self):
        open(os.path.join(self.tmp, "viejo.txt"), "w").close()
        salida = self.correr(gestor.renombrar, ["viejo.txt", "nuevo.txt"])
        self.assertIn("renombrado", salida)
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "viejo.txt")))
        self.assertTrue(os.path.exists(os.path.join(self.tmp, "nuevo.txt")))

    def test_renombrar_no_existe(self):
        salida = self.correr(gestor.renombrar, ["falta.txt", "nuevo.txt"])
        self.assertIn("no existe ese archivo", salida)

    def test_copiar(self):
        f = open(os.path.join(self.tmp, "orig.txt"), "w")
        f.write("datos")
        f.close()
        salida = self.correr(gestor.copiar, ["orig.txt", "copia.txt"])
        self.assertIn("copiado", salida)
        self.assertTrue(os.path.exists(os.path.join(self.tmp, "orig.txt")))
        self.assertTrue(os.path.exists(os.path.join(self.tmp, "copia.txt")))

    def test_copiar_no_existe(self):
        salida = self.correr(gestor.copiar, ["falta.txt", "copia.txt"])
        self.assertIn("no existe ese archivo", salida)

    def test_eliminar_si(self):
        open(os.path.join(self.tmp, "borrar.txt"), "w").close()
        salida = self.correr(gestor.eliminar, ["borrar.txt", "s"])
        self.assertIn("eliminado", salida)
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "borrar.txt")))

    def test_eliminar_cancelado(self):
        open(os.path.join(self.tmp, "borrar.txt"), "w").close()
        salida = self.correr(gestor.eliminar, ["borrar.txt", "n"])
        self.assertIn("cancelado", salida)
        self.assertTrue(os.path.exists(os.path.join(self.tmp, "borrar.txt")))

    def test_eliminar_no_existe(self):
        salida = self.correr(gestor.eliminar, ["falta.txt"])
        self.assertIn("no existe ese archivo", salida)

    def test_listar_vacio(self):
        salida = self.correr(gestor.listar, [])
        self.assertIn("no hay nada", salida)

    def test_listar_con_cosas(self):
        open(os.path.join(self.tmp, "a.txt"), "w").close()
        salida = self.correr(gestor.listar, [])
        self.assertIn("a.txt", salida)

    def test_info(self):
        f = open(os.path.join(self.tmp, "datos.txt"), "w")
        f.write("12345")
        f.close()
        salida = self.correr(gestor.info, ["datos.txt"])
        self.assertIn("nombre: datos.txt", salida)
        self.assertIn("tamano: 5 bytes", salida)
        self.assertIn("modificado:", salida)

    def test_info_no_existe(self):
        salida = self.correr(gestor.info, ["falta.txt"])
        self.assertIn("no existe ese archivo", salida)


if __name__ == "__main__":
    unittest.main()
