import argparse
import hashlib
import logging
from concurrent import futures

import grpc
from convertidor.ConvertidorDeCanciones import ConvertidorDeCanciones
from convertidor.ConvertidorDeImagenes import ConvertidorDeImagenes
from protos import ConvertidorDeArchivos_pb2_grpc, ConvertidorDeArchivos_pb2

global logger


class ConvertidorDeCancionesServicer(ConvertidorDeArchivos_pb2_grpc.ConvertidorDeCancionesServicer):

    def ConvertirCancionAMP3(self, request_iterator, context):
        """
        Se encarga de convertir una cancion mp3 a los 3 calidades disponibles:
        :param request_iterator: Un iterador de solicitudes por parte del cliente
        :param context: El contexto del cliente
        :return: Un objeto de tipo RespuestaCancionesConvertidas que contiene la informacion de las canciones
        convertidas
        """
        hash256_archivo_original = ""
        convertidor_de_canciones = ConvertidorDeCanciones(logger)
        try:
            for solicitud in request_iterator:
                convertidor_de_canciones.escribir_fichero(solicitud.informacionArchivo.idElemento,
                                                          solicitud.informacionArchivo.extension,
                                                          solicitud.data)
                hash256_archivo_original = solicitud.informacionArchivo.hash256
            logger.info("Se recibio la cancion " + str(convertidor_de_canciones.id_cancion))
            respuesta = ConvertidorDeArchivos_pb2.RespuestaCancionesConvertidas()
            if convertidor_de_canciones.obtener_sha256_de_cancion_original() != hash256_archivo_original:
                logger.error("integridad_archivo_no_definida_" + str(convertidor_de_canciones.id_cancion))
                respuesta.error.error = "integridad_archivo_no_definida"
                respuesta.error.mensaje = "El Hash 256 del archivo recibido no coincide con el del archivo enviado"
                return respuesta
            cancion_calidad_alta = convertidor_de_canciones.convertir_a_wav_calidad_alta()
            cancion_calidad_media = convertidor_de_canciones.convertir_a_wav_calidad_media()
            cancion_calidad_baja = convertidor_de_canciones.convertir_a_mp3_calidad_baja()
            bytes_del_chunk_baja = leer_archivo_por_bloques(cancion_calidad_baja,
                                                            convertidor_de_canciones.TAMANO_CHUNK)
            bytes_del_chunk_media = leer_archivo_por_bloques(cancion_calidad_media,
                                                             convertidor_de_canciones.TAMANO_CHUNK)
            bytes_del_chunk_alta = leer_archivo_por_bloques(cancion_calidad_alta,
                                                            convertidor_de_canciones.TAMANO_CHUNK)
            hash256_cancion_calidad_baja = obtener_has256_de_archivo(cancion_calidad_baja)
            hash256_cancion_calidad_media = obtener_has256_de_archivo(cancion_calidad_media)
            hash256_cancion_calidad_alta = obtener_has256_de_archivo(cancion_calidad_alta)
            log_baja_enviada = False
            log_media_enviada = False
            while True:
                try:
                    respuesta.cancionCalidadBaja.data = next(bytes_del_chunk_baja)
                    respuesta.cancionCalidadBaja.informacionArchivo.hash256 = str(hash256_cancion_calidad_baja)
                    respuesta.cancionCalidadBaja.informacionArchivo.extension = convertidor_de_canciones.FORMATO_MP3
                except StopIteration:
                    respuesta.cancionCalidadBaja.data = bytes()
                    if not log_baja_enviada:
                        logger.info("Se envio la cancion " + str(convertidor_de_canciones.id_cancion) + "."
                                    + convertidor_de_canciones.FORMATO_MP3 + " en calidad baja")
                        log_baja_enviada = True
                try:
                    respuesta.cancionCalidadMedia.data = next(bytes_del_chunk_media)
                    respuesta.cancionCalidadMedia.informacionArchivo.hash256 = hash256_cancion_calidad_media
                    respuesta.cancionCalidadMedia.informacionArchivo.extension = convertidor_de_canciones.FORMATO_MP3
                except StopIteration:
                    respuesta.cancionCalidadMedia.data = bytes()
                    if not log_media_enviada:
                        logger.info("Se envio la cancion " + str(convertidor_de_canciones.id_cancion) + "."
                                    + convertidor_de_canciones.FORMATO_MP3 + " en calidad media")
                        log_media_enviada = True
                try:
                    respuesta.cancionCalidadAlta.data = next(bytes_del_chunk_alta)
                    respuesta.cancionCalidadAlta.informacionArchivo.hash256 = hash256_cancion_calidad_alta
                    respuesta.cancionCalidadAlta.informacionArchivo.extension = convertidor_de_canciones.FORMATO_MP3
                except StopIteration:
                    logger.info("Se envio la cancion " + str(convertidor_de_canciones.id_cancion) + "."
                                + convertidor_de_canciones.FORMATO_MP3 + " en calidad alta")
                    break
                yield respuesta
            convertidor_de_canciones.limpiar_archivos()
            logger.info("Se limpiaron los archivos generados de la cancion con el id "
                        + str(convertidor_de_canciones.id_cancion))
        except Exception:
            convertidor_de_canciones.limpiar_archivos()
            logger.error("Ocurrio un error y se limpiaron los archivos generados de la cancion con el id "
                         + str(convertidor_de_canciones.id_cancion))


class ConvertidorDeImagenesServicer(ConvertidorDeArchivos_pb2_grpc.ConvertidorDeImagenesServicer):

    def ConvertirImagenAPng(self, request_iterator, context):
        convertidor_imagenes = ConvertidorDeImagenes(logger)
        try:
            for solicitud in request_iterator:
                convertidor_imagenes.escribir_fichero(solicitud.informacionImagen.idElemento,
                                                      solicitud.informacionImagen.extension,
                                                      solicitud.data)

            logger.info("Se recibio la portada " + str(convertidor_imagenes.id_portada))
            respuesta = ConvertidorDeArchivos_pb2.RespuestaImagenesConvertidas()
            portada_calidad_alta = convertidor_imagenes.convertir_a_calidad_alta()
            portada_calidad_media = convertidor_imagenes.convertir_a_calidad_media()
            portada_calidad_baja = convertidor_imagenes.convertir_a_calidad_baja()
            bytes_del_chunk_baja = leer_archivo_por_bloques(portada_calidad_baja,
                                                            convertidor_imagenes.TAMANO_CHUNK)
            bytes_del_chunk_media = leer_archivo_por_bloques(portada_calidad_media,
                                                             convertidor_imagenes.TAMANO_CHUNK)
            bytes_del_chunk_alta = leer_archivo_por_bloques(portada_calidad_alta,
                                                            convertidor_imagenes.TAMANO_CHUNK)
            log_baja_enviada = False
            log_media_enviada = False
            while True:
                try:
                    respuesta.imagenCalidadBaja.data = next(bytes_del_chunk_baja)
                    respuesta.imagenCalidadBaja.informacionImagen.extension = convertidor_imagenes.FORMATO_PNG
                except StopIteration:
                    respuesta.imagenCalidadBaja.data = bytes()
                    if not log_baja_enviada:
                        logger.info("Se envio la portada " + str(convertidor_imagenes.id_portada) + "."
                                    + convertidor_imagenes.FORMATO_PNG + " en calidad baja")
                        log_baja_enviada = True
                try:
                    respuesta.imagenCalidadMedia.data = next(bytes_del_chunk_media)
                    respuesta.imagenCalidadMedia.informacionImagen.extension = convertidor_imagenes.FORMATO_PNG
                except StopIteration:
                    respuesta.imagenCalidadMedia.data = bytes()
                    if not log_media_enviada:
                        logger.info("Se envio la portada " + str(convertidor_imagenes.id_portada) + "."
                                    + convertidor_imagenes.FORMATO_PNG + " en calidad media")
                        log_media_enviada = True
                try:
                    respuesta.imagenCalidadAlta.data = next(bytes_del_chunk_alta)
                    respuesta.imagenCalidadAlta.informacionImagen.extension = convertidor_imagenes.FORMATO_PNG
                except StopIteration:
                    logger.info("Se envio la portada " + str(convertidor_imagenes.id_portada) + "."
                                + convertidor_imagenes.FORMATO_PNG + " en calidad alta")
                    break
                yield respuesta
            convertidor_imagenes.limpiar_archivos()
            logger.info("Se limpiaron los archivos generados de la portada con el id "
                        + str(convertidor_imagenes.id_portada))

        except Exception:
            convertidor_imagenes.limpiar_archivos()
            logger.error("Ocurrio un error y se limpiaron los archivos generados de la portada con el id "
                         + str(convertidor_imagenes.id_portada))


def leer_archivo_por_bloques(ruta_archivo, tamano_chunk):
    """
    Se encarga de leer una cancion por bloques
    :param ruta_archivo: La ruta en donde se encuentra el archivo
    :param tamano_chunk: El tamaño que tendra cada bloque
    :return: El bloque leido
    """
    with open(ruta_archivo, 'rb') as archivo:
        for bloque in iter(lambda: archivo.read(tamano_chunk), b""):
            yield bloque


def obtener_has256_de_archivo(ruta_archivo):
    """
    Se encargar de calcular el sha256 de un archivo
    :param ruta_archivo: La ruta del archivo a encargar el sha256
    :return: El hash 256 del archivo
    """
    hash256 = hashlib.sha3_256()
    with open(ruta_archivo, 'rb') as archivo:
        for bloque in iter(lambda: archivo.read(1000 * 64), b""):
            hash256.update(bloque)
    return hash256.hexdigest()


def serve(puerto):
    """
    Se encarga de levantar el servidor
    :param puerto: El puerto donde se expondra el api
    :return: None
    """
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    ConvertidorDeArchivos_pb2_grpc.add_ConvertidorDeCancionesServicer_to_server(ConvertidorDeCancionesServicer(),
                                                                                server)
    ConvertidorDeArchivos_pb2_grpc.add_ConvertidorDeImagenesServicer_to_server(ConvertidorDeImagenesServicer(),
                                                                               server)
    try:
        server.add_insecure_port('[::]:' + str(puerto))
        server.add_insecure_port('0.0.0.0:' + str(puerto))
        server.start()
        logger.info("Se ha iniciado el servidor en el puerto: " + str(puerto))
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Se ha cerrado el servidor")


def manejar_parametros():
    """
    Se encarga de manejar los parametros introducidos en consola
    :return: Un objeto de tipo ArgumentParser
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--puerto", help="El puerto a exponer")
    args = parser.parse_args()
    return args


def verbose_formatter():
    """
    Crea el formato para las salidas del logger
    :return: Un objeto de tipo Formatter
    """
    return logging.Formatter(
        '[%(asctime)s.%(msecs)d]\t %(levelname)s \t[%(name)s.%(funcName)s:%(lineno)d]\t %(message)s',
        datefmt='%d/%m/%Y %H:%M:%S'
    )


def configurar_logger():
    """
    Realiza crea un logger y realiza las configuraciones necesarias
    :return: Un logger
    """
    logger_local = logging.getLogger('logger')
    logger_local.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    fh = logging.FileHandler('EspotifeiConvertidorDeArchivos.log')
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(verbose_formatter())
    fh.setLevel(logging.INFO)
    fh.setFormatter(verbose_formatter())
    logger_local.addHandler(fh)
    logger_local.addHandler(console_handler)
    return logger_local


if __name__ == '__main__':
    """
    El main
    """
    argumentos = manejar_parametros()
    if argumentos.puerto:
        puerto = argumentos.puerto
    else:
        puerto = 5002
    logger = configurar_logger()
    serve(puerto)
