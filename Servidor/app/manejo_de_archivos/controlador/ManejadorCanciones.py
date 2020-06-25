import hashlib
import pathlib
import time

import app.manejo_de_archivos.protos.ManejadorDeArchivos_pb2 as ManejadorDeArchivos_pb2
import eyed3

from app.manejo_de_archivos.modelo.enums.enums import Calidad
from app.manejo_de_archivos.modelo.modelos import ArchivoAudio

from Servidor.app.administracion_de_contenido.modelo.modelos import Cancion, CancionPersonal
from Servidor.app.manejo_de_archivos.Cliente import ConvertidorDeArchivosCliente
from Servidor.app.manejo_de_archivos.controlador.ManejadorDeArchivos import ManejadorDeArchivos
from Servidor.app.manejo_de_archivos.modelo.enums.enums import FormatoAudio


class ManejadorCanciones:

    @staticmethod
    def guardar_cancion(informacion_cancion, bytes_de_la_cancion):
        pass

    @staticmethod
    def obtener_sha256_de_byte_array(array_de_bytes):
        """
        Calcula el hash del arreglo de bytes con el algoritmo sha256
        :param array_de_bytes: El arreglo de bytes a calcular el hash
        :return: Un string con el hash256 del arreglo de bytes
        """
        hash256_cancion_calidad_alta = hashlib.sha3_256(array_de_bytes).hexdigest()
        return hash256_cancion_calidad_alta

    @staticmethod
    def validar_existe_cancion(id_cancion, calidad):
        """
        Valida si se encuentra registrado el ArchivoAudio de la cancion con el id_cancion en la calidad
        :param id_cancion: El id de la cancion
        :param calidad: La calidad de la cancion
        :return: True si se encuentra registrada o False si no
        """
        if calidad == ManejadorDeArchivos_pb2.Calidad.ALTA:
            calidad = Calidad.ALTA
        elif calidad == ManejadorDeArchivos_pb2.Calidad.MEDIA:
            calidad = Calidad.MEDIA
        elif calidad == ManejadorDeArchivos_pb2.Calidad.BAJA:
            calidad = Calidad.BAJA
        archivo_cancion = ArchivoAudio.obtener_archivo_audio_cancion(id_cancion, calidad)
        return archivo_cancion is not None

    @staticmethod
    def validar_existe_archivo_cancion(id_cancion, calidad):
        """
        Valida si el archivo de la cancion con el id cancion existe
        :param id_cancion: El id de la cancion a validar si su archivo existe
        :param calidad: La calidad de la cancion
        :return: True si existe o false si no
        """
        if calidad == ManejadorDeArchivos_pb2.Calidad.ALTA:
            calidad = Calidad.ALTA
        elif calidad == ManejadorDeArchivos_pb2.Calidad.MEDIA:
            calidad = Calidad.MEDIA
        elif calidad == ManejadorDeArchivos_pb2.Calidad.BAJA:
            calidad = Calidad.BAJA
        archivo_cancion = ArchivoAudio.obtener_archivo_audio_cancion(id_cancion, calidad)
        if archivo_cancion is None:
            return None
        existe_archivo = ManejadorCanciones.validar_existe_archivo(archivo_cancion.ruta)
        return existe_archivo

    @staticmethod
    def validar_existe_cancion_original(id_cancion):
        """
        Valida si existe el ArchivoAudio de la cancion original en la base de datos
        :param id_cancion: El id de la cancion a validar si existe su ArchivoAudio
        :return: True si existe o False si no
        """
        archivo_audio = ArchivoAudio.obtener_archivo_audio_cancion(id_cancion, Calidad.ORIGINAL)
        return archivo_audio is None

    @staticmethod
    def validar_existe_archivo_cancion_original(id_cancion):
        """
        Valida si existe el archivo de la cancion original
        :param id_cancion: El id de la cancion a validar si existe su archivo
        :return: True si existe o False si no
        """
        archivo_audio = ArchivoAudio.obtener_archivo_audio_cancion(id_cancion, Calidad.ORIGINAL)
        if archivo_audio is None:
            return False
        existe_archivo_cancion = ManejadorCanciones.validar_existe_archivo(archivo_audio.ruta)
        return existe_archivo_cancion

    @staticmethod
    def validar_existe_archivo(ubicacion):
        """
        Valida si existe un archivo en la ubicacion indicada
        :param ubicacion: La ubicacion en donde se buscara el archivo
        :return: True si el archivo existe o False si no
        """
        archivo = pathlib.Path(ubicacion)
        return archivo.is_file()

    @staticmethod
    def reconvertir_cancion(id_cancion):
        """
        Se encarga de reconvertir la cancion con el id cancion a mp3 en todas sus calidades
        :param id_cancion: El id de la cancion a reconvertir
        :return: None
        """
        archivo_cancion_original = ArchivoAudio.obtener_archivo_audio_cancion(id_cancion, Calidad.ORIGINAL)
        cliente_convertidor = ConvertidorDeArchivosCliente(id_cancion=archivo_cancion_original.id_cancion,
                                                           ubicacion_archivo=archivo_cancion_original.ruta,
                                                           extension=archivo_cancion_original.formato.value)
        cantidad_intentos = 0
        while cantidad_intentos < 3:
            try:
                cliente_convertidor.enviar_cancion()
                ManejadorCanciones._crear_archivo_audio_canciones_convertidas(id_cancion, cliente_convertidor)
                break
            except Exception as ex:
                # Mostrar log
                time.sleep(10)
                cantidad_intentos += 1

    @staticmethod
    def _colocar_metadata_cancion(cancion, ruta):
        """
        Coloca la informacion de la cancion al archivo
        :param ruta: La ruta en donde se encuentra el archivo de la cancion
        :param cancion: La cancion con la informacion de la cancion
        :return: None
        """
        creadores_de_cotenido = ""
        for creador_de_cotenido in cancion.creadores_de_contenido:
            creadores_de_cotenido += creador_de_cotenido.nombre + ", "
        creadores_de_cotenido = creadores_de_cotenido[:-2]
        archivo_de_audio = eyed3.load(ruta)
        archivo_de_audio.tag.artist = creadores_de_cotenido
        archivo_de_audio.tag.album = cancion.album.nombre
        archivo_de_audio.tag.title = cancion.nombre
        archivo_de_audio.tag.save()

    @staticmethod
    def _crear_archivo_audio_canciones_convertidas(id_cancion, cliente_convertidor):
        """
        Se encarga de crear los tres ArchivoAudio de la cancion convertida en sus tres calidades
        :param id_cancion: El id de la cancion convertida
        :param cliente_convertidor: El cliente del convertidor de archivos que contiene las tres canciones convertidas
        :return: None
        """
        ManejadorCanciones._crear_archivo_audio_cancion_calidades(id_cancion, cliente_convertidor, Calidad.ALTA,
                                                                  FormatoAudio.MP3)
        ManejadorCanciones._crear_archivo_audio_cancion_calidades(id_cancion, cliente_convertidor, Calidad.MEDIA,
                                                                  FormatoAudio.MP3)
        ManejadorCanciones._crear_archivo_audio_cancion_calidades(id_cancion, cliente_convertidor, Calidad.BAJA,
                                                                  FormatoAudio.MP3)

    @staticmethod
    def _crear_archivo_audio_cancion_calidades(id_cancion, cliente_convertidor, calidad, formato):
        """
        Crea un ArchivoAudio de la cancion
        :param id_cancion: El id de la cancion que se convirtio
        :param cliente_convertidor: El cliente del convertidor de archivos que contiene la informacion de las canciones
        convertidas
        :param calidad: La calidad del ArchivoAudio a guardar
        :param formato: El formato de la cancion
        :return: None
        """
        hash256 = ""
        tamano_cancion = 0
        ruta = ""
        if calidad == Calidad.BAJA:
            hash256 = cliente_convertidor.informacion_archivo_calidad_baja.hash256
            tamano_cancion = len(cliente_convertidor.cancion_calidad_baja)
            ruta = ManejadorDeArchivos.guardar_cancion(id_cancion, Calidad.BAJA, formato,
                                                       cliente_convertidor.cancion_calidad_baja)
        elif calidad == Calidad.MEDIA:
            hash256 = cliente_convertidor.informacion_archivo_calidad_media.hash256
            tamano_cancion = len(cliente_convertidor.cancion_calidad_media)
            ruta = ManejadorDeArchivos.guardar_cancion(id_cancion, Calidad.MEDIA, formato,
                                                       cliente_convertidor.cancion_calidad_media)
        elif calidad == Calidad.ALTA:
            hash256 = cliente_convertidor.informacion_archivo_calidad_alta.hash256
            tamano_cancion = len(cliente_convertidor.cancion_calidad_alta)
            ruta = ManejadorDeArchivos.guardar_cancion(id_cancion, Calidad.ALTA, formato,
                                                       cliente_convertidor.cancion_calidad_alta)
        cancion = Cancion.obtener_cancion_por_id(id_cancion)
        ManejadorCanciones._colocar_metadata_cancion(cancion, ruta)
        cancion_calidad = ArchivoAudio.obtener_archivo_audio_cancion(id_cancion, calidad)
        if cancion_calidad is not None:
            cancion_calidad.editar_archivo_audio(False, FormatoAudio.MP3, ruta, hash256, tamano_cancion)
        else:
            cancion_calidad = ArchivoAudio(calidad, FormatoAudio.MP3, ruta, hash256, tamano_cancion,
                                           id_cancion=id_cancion)
            cancion_calidad.guardar()

    @staticmethod
    def validar_existe_cancion_personal_original(id_cancion):
        """
        Se encarga de validar si existe el ArchivoAudio con el id_cancion_personal
        :param id_cancion: El id de la cancion personal a validar si existe
        :return: True si el ArchivoAudio de la cancion personal con la calidad ORIGINAL o False si no
        """
        archivo_audio = ArchivoAudio.obtener_archivo_audio_cancion_personal(id_cancion, Calidad.ORIGINAL)
        return archivo_audio is None

    @staticmethod
    def validar_existe_archivo_cancion_personal_original(id_cancion):
        """
        Se encarga de validar si el archico de la cancion personal con el id existe
        :param id_cancion: El id cancion personal a validar si existe su archivo
        :return: True si existe el archivo o False si no
        """
        archivo_audio = ArchivoAudio.obtener_archivo_audio_cancion_personal(id_cancion, Calidad.ORIGINAL)
        if archivo_audio is None:
            return False
        existe_archivo_cancion = ManejadorCanciones.validar_existe_archivo(archivo_audio.ruta)
        return existe_archivo_cancion

    @staticmethod
    def validar_existe_cancion_personal(id_cancion, calidad):
        """
        Valida si existe el ArchivoAudio de una cancion personal con la calidad indicada
        :param id_cancion: El id de la cancion personal a validar si existe
        :param calidad: La caliad del ArchivoAudio a validar si existe
        :return: True si existe el ArchivoAudio de la cancion personal con la calidad indicada
        """
        if calidad == ManejadorDeArchivos_pb2.Calidad.ALTA:
            calidad = Calidad.ALTA
        elif calidad == ManejadorDeArchivos_pb2.Calidad.MEDIA:
            calidad = Calidad.MEDIA
        elif calidad == ManejadorDeArchivos_pb2.Calidad.BAJA:
            calidad = Calidad.BAJA
        archivo_cancion = ArchivoAudio.obtener_archivo_audio_cancion_personal(id_cancion, calidad)
        return archivo_cancion is not None

    @staticmethod
    def validar_existe_archivo_cancion_personal(id_cancion, calidad):
        """
        Se encarga de validar si el archico de la cancion personal con el id y la calidad indicada existe
        :param id_cancion: El id cancion personal a validar si existe su archivo
        :param calidad: La calidad de la cancion a validar si existe su archivo
        :return: True si existe el archivo o False si no
        """
        if calidad == ManejadorDeArchivos_pb2.Calidad.ALTA:
            calidad = Calidad.ALTA
        elif calidad == ManejadorDeArchivos_pb2.Calidad.MEDIA:
            calidad = Calidad.MEDIA
        elif calidad == ManejadorDeArchivos_pb2.Calidad.BAJA:
            calidad = Calidad.BAJA
        archivo_cancion = ArchivoAudio.obtener_archivo_audio_cancion_personal(id_cancion, calidad)
        if archivo_cancion is None:
            return None
        existe_archivo = ManejadorCanciones.validar_existe_archivo(archivo_cancion.ruta)
        return existe_archivo

    @staticmethod
    def reconvertir_cancion_personal(id_cancion):
        """
        Reconvierte una cancion personal a mp3 en todas las calidades
        :param id_cancion: El id de la cancion personal a reconvertir el archivo a todas sus calidades
        :return: None
        """
        archivo_cancion_original = ArchivoAudio.obtener_archivo_audio_cancion_personal(id_cancion, Calidad.ORIGINAL)
        cliente_convertidor = ConvertidorDeArchivosCliente(id_cancion=archivo_cancion_original.id_cancion,
                                                           ubicacion_archivo=archivo_cancion_original.ruta,
                                                           extension=archivo_cancion_original.formato.value)
        cantidad_intentos = 0
        while cantidad_intentos < 3:
            try:
                cliente_convertidor.enviar_cancion()
                ManejadorCanciones._crear_archivo_audio_canciones_personales_convertidas(id_cancion,
                                                                                         cliente_convertidor)
                break
            except Exception as ex:
                # Mostrar log
                time.sleep(10)
                cantidad_intentos += 1

    @staticmethod
    def _colocar_metadata_cancion_personal(cancion_personal, ruta):
        """
        Coloca la informacion de la cancion al archivo
        :param ruta: La ruta en donde se encuentra el archivo de la cancion
        :param cancion: La cancion con la informacion de la cancion
        :return: None
        """
        archivo_de_audio = eyed3.load(ruta)
        archivo_de_audio.tag.artist = cancion_personal.artistas
        archivo_de_audio.tag.album = cancion_personal.album
        archivo_de_audio.tag.title = cancion_personal.nombre
        archivo_de_audio.tag.save()

    @staticmethod
    def _crear_archivo_audio_canciones_personales_convertidas(id_cancion, cliente_convertidor):
        """
        Se encarga de crear los tres ArchivoAudio de la cancion personal convertida en sus tres calidades
        :param id_cancion: El id de la cancion personal convertida
        :param cliente_convertidor: El cliente del convertidor de archivos que contiene las tres canciones personales
        convertidas
        :return: None
        """
        ManejadorCanciones._crear_archivo_audio_cancion_personal_calidades(id_cancion, cliente_convertidor,
                                                                           Calidad.ALTA, FormatoAudio.MP3)
        ManejadorCanciones._crear_archivo_audio_cancion_personal_calidades(id_cancion, cliente_convertidor,
                                                                           Calidad.MEDIA, FormatoAudio.MP3)
        ManejadorCanciones._crear_archivo_audio_cancion_personal_calidades(id_cancion, cliente_convertidor,
                                                                           Calidad.BAJA, FormatoAudio.MP3)

    @staticmethod
    def _crear_archivo_audio_cancion_personal_calidades(id_cancion, cliente_convertidor, calidad, formato):
        """
        Crea un ArchivoAudio de la cancion personal
        :param id_cancion: El id de la cancion personal que se convirtio
        :param cliente_convertidor: El cliente del convertidor de archivos que contiene la informacion de las canciones
        convertidas
        :param calidad: La calidad del ArchivoAudio a guardar
        :param formato: El formato de la cancion personal
        :return: None
        """
        hash256 = ""
        tamano_cancion = 0
        ruta = ""
        if calidad == Calidad.BAJA:
            hash256 = cliente_convertidor.informacion_archivo_calidad_baja.hash256
            tamano_cancion = len(cliente_convertidor.cancion_calidad_baja)
            ruta = ManejadorDeArchivos.guardar_cancion_personal(id_cancion, Calidad.BAJA, formato,
                                                                cliente_convertidor.cancion_calidad_baja)
        elif calidad == Calidad.MEDIA:
            hash256 = cliente_convertidor.informacion_archivo_calidad_media.hash256
            tamano_cancion = len(cliente_convertidor.cancion_calidad_media)
            ruta = ManejadorDeArchivos.guardar_cancion_personal(id_cancion, Calidad.MEDIA, formato,
                                                                cliente_convertidor.cancion_calidad_media)
        elif calidad == Calidad.ALTA:
            hash256 = cliente_convertidor.informacion_archivo_calidad_alta.hash256
            tamano_cancion = len(cliente_convertidor.cancion_calidad_alta)
            ruta = ManejadorDeArchivos.guardar_cancion_personal(id_cancion, Calidad.ALTA, formato,
                                                                cliente_convertidor.cancion_calidad_alta)
        cancion_personal = CancionPersonal.obtener_cancion_por_id(id_cancion)
        ManejadorCanciones._colocar_metadata_cancion(cancion_personal, ruta)
        cancion_calidad = ArchivoAudio.obtener_archivo_audio_cancion_personal(id_cancion, calidad)
        if cancion_calidad is not None:
            cancion_calidad.editar_archivo_audio(False, FormatoAudio.MP3, ruta, hash256, tamano_cancion)
        else:
            cancion_calidad = ArchivoAudio(calidad, FormatoAudio.MP3, ruta, hash256, tamano_cancion,
                                           id_cancion_pesonal=id_cancion)
            cancion_calidad.guardar()