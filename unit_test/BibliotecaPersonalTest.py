from app.administracion_de_contenido.modelo.modelos import CancionPersonal
from app.util.validaciones.modelos.ValidacionCancionPersonal import ValidacionCancionPersonal
from . import BaseTestClass


class CancionPersonalTest(BaseTestClass):

    def test_guardar_cancion_personal(self):
        with self.app.app_context():
            cancion_a_registrar = CancionPersonal(nombre="Cancion prueba", artistas="Hola como", album="album 1",
                                                  id_usuario=1)
            cancion_a_registrar.guardar()
            caciones_registradas = CancionPersonal.obtener_canciones_de_usuario(1)
            cantidad_de_canciones = 1
            self.assertEqual(cantidad_de_canciones, len(caciones_registradas))

    def test_obtener_canciones_de_personas(self):
        with self.app.app_context():
            cancion_a_registrar = CancionPersonal(nombre="Cancion prueba", artistas="Hola como", album="album 1",
                                                  id_usuario=1)
            cancion_a_registrar.guardar()
            caciones_registradas = CancionPersonal.obtener_canciones_de_usuario(1)
            cantidad_de_canciones = 1
            self.assertEqual(cantidad_de_canciones, len(caciones_registradas))

    def test_obtener_cantidad_canciones(self):
        with self.app.app_context():
            cancion_a_registrar = CancionPersonal(nombre="Cancion prueba", artistas="Hola como", album="album 1",
                                                  id_usuario=1)
            cancion_a_registrar.guardar()
            cantidad_canciones_en_bd = CancionPersonal.obtener_cantidad_de_canciones(1)
            cantidad_de_canciones = 1
            self.assertEqual(cantidad_de_canciones, cantidad_canciones_en_bd)


class ValidacionCancionPersonalTest(BaseTestClass):

    def test_parametros_requeridos(self):
        with self.app.app_context():
            cancion_personal = CancionPersonal(nombre=None, artistas=None, id_usuario=1)
            errores_validacion = ValidacionCancionPersonal.validar_registro_cancion_personal(cancion_personal)
            codigo_error = "parametros_faltantes"
            self.assertEqual(codigo_error, errores_validacion['error'])

    def test_nombre_demasido_largo(self):
        with self.app.app_context():
            cancion_a_registrar = CancionPersonal(
                nombre="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                artistas="hola como estas", id_usuario=1)
            errores_validacion = ValidacionCancionPersonal.validar_registro_cancion_personal(cancion_a_registrar)
            codigo_error = "nombre_demasiado_largo"
            self.assertEqual(codigo_error, errores_validacion[0]['error'])

    def test_registro_correcto(self):
        with self.app.app_context():
            cancion_a_registrar = CancionPersonal(nombre="asdfgh", artistas="asdfgh", id_usuario=1)
            validacion_registro = ValidacionCancionPersonal.validar_registro_cancion_personal(cancion_a_registrar)
            codigo_error = None
            self.assertEqual(codigo_error, validacion_registro)

    def test_validar_no_existe_cancion_personal(self):
        with self.app.app_context():
            validacion_no_existe = ValidacionCancionPersonal.validar_existe_cancion_personal(1)
            codigo_error = "cancion_personal_inexistente"
            self.assertEqual(codigo_error, validacion_no_existe['error'])

    def test_validar_no_es_dueno(self):
        with self.app.app_context():
            cancion_a_registrar = CancionPersonal(nombre="asdfgh", artistas="asdfgh", id_usuario=1)
            cancion_a_registrar.guardar()
            validacion_registro = ValidacionCancionPersonal.validar_es_dueno_cancion_personal(2, 1)
            codigo_error = "cancion_persona_no_es_de_usuario"
            self.assertEqual(codigo_error, validacion_registro['error'])

    def test_cancion_personal_existe(self):
        with self.app.app_context():
            cancion_a_registrar = CancionPersonal(nombre="asdfgh", artistas="asdfgh", id_usuario=1)
            cancion_a_registrar.guardar()
            validacion_no_existe = ValidacionCancionPersonal.validar_existe_cancion_personal(1)
            codigo_error = None
            self.assertEqual(codigo_error, validacion_no_existe)

    def test_cancion_es_dueno(self):
        with self.app.app_context():
            cancion_a_registrar = CancionPersonal(nombre="asdfgh", artistas="asdfgh", id_usuario=1)
            cancion_a_registrar.guardar()
            validacion_registro = ValidacionCancionPersonal.validar_es_dueno_cancion_personal(1, 1)
            codigo_error = None
            self.assertEqual(codigo_error, validacion_registro)
