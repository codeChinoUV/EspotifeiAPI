from app.administracion_de_contenido.modelo.modelos import CreadorDeContenido
from app.util.JsonBool import JsonBool
from app.util.validaciones.ValidacioCadenas import ValidacionCadenas


class ValidacionCreadorDeContenido:
    """
    Se encarga de realizar las validaciones necesarias para el modelo CreadorDeContenido
    """

    @staticmethod
    def _validar_campos_requeridos(creador_de_contenido):
        """
        Valida que el creador_de_contenido tenga los campos requeridos
        :param creador_de_contenido: El creador de contenido a validar
        :return: None si el creador de contenido tiene los atributos requeridos o un diccionario con el error y el
        mensaje si al creador de contenido no tiene los campos requeridos
        """
        parametros_faltantes = ""
        if creador_de_contenido.nombre is None:
            parametros_faltantes += "<nombre> "
        if creador_de_contenido.es_grupo is None:
            parametros_faltantes += "<es_grupo>"

        if len(parametros_faltantes) > 0:
            mensaje = "Los siguientes parametros faltan en tu solicitud: " + parametros_faltantes
            errores = {'error': 'parametros_faltantes', 'mensaje': mensaje}
            return errores

    @staticmethod
    def _validar_booleano_valido(creador_de_contenido):
        """
        Valida que los campos que son de tipo booleano del creador de contenido sean validos
        :param creador_de_contenido: El creador de contenido al que se le validara los campos booleanos
        :return: None si los booleanos son validos o un diccionario con el error y el mensaje si los booleanos no son
        validos
        """
        if JsonBool.obtener_boolean_de_valor_json(creador_de_contenido.es_grupo) is None:
            error = {'error': 'es_grupo_no_es_booleano',
                     'mensaje': 'El atributo <es_grupo> debe de ser booleano'}
            return error

    @staticmethod
    def _validar_tamano_modelo_creador_de_contenido(creador_de_contenido):
        """
        Valida que el tamaño de las cadenas de los atributos del creador_de_contenido sean correctos
        :param creador_de_contenido: El creador de contenido a validar
        :return: Una lista de diccionarios que contienen el error y el mensaje del error ocurrido
        """
        tamano_minimo_general = 5
        tamano_maximo_nombre = 70
        tamano_maximo_biografia = 500
        lista_de_errores = []
        if creador_de_contenido.nombre is not None:
            error = ValidacionCadenas.validar_tamano_parametro(creador_de_contenido.nombre, "nombre",
                                                               tamano_minimo_general, tamano_maximo_nombre)
            if error is not None:
                lista_de_errores.append(error)
        if creador_de_contenido.biografia is not None:
            error = ValidacionCadenas.validar_tamano_parametro(creador_de_contenido.biografia, "biografia",
                                                               tamano_minimo_general, tamano_maximo_biografia)
            if error is not None:
                lista_de_errores.append(error)
        return lista_de_errores

    @staticmethod
    def validar_registro_creador_de_contenido(creador_de_contenido):
        """
        Valida que el creador de contenido sea valido para poder registrarlo
        :param creador_de_contenido: El creador de contenido a validar
        :return: Un diccionario con los errores del modelo
        """
        lista_de_errores = []
        error = ValidacionCreadorDeContenido._validar_campos_requeridos(creador_de_contenido)
        if error is not None:
            lista_de_errores.append(error)
        errores = ValidacionCreadorDeContenido._validar_tamano_modelo_creador_de_contenido(creador_de_contenido)
        if len(errores) > 0:
            for error in errores:
                lista_de_errores.append(error)
        error = ValidacionCreadorDeContenido._validar_booleano_valido(creador_de_contenido)
        if error is not None:
            lista_de_errores.append(error)
        return lista_de_errores

    @staticmethod
    def validar_edicion_creador_de_contenido(creador_de_contenido):
        """
        Se encarga de validar si los elementos que se editaran del creador de contenido son validos
        :param creador_de_contenido: El creador de contenido que contiene los campos a validar
        :return: Una lista con los errores que cuentan los campos a modificar
        """
        lista_de_errores = []
        if creador_de_contenido.nombre is None and creador_de_contenido.biografia is None \
                and creador_de_contenido.es_grupo is None:
            error = {'error': 'solicitud_sin_parametros_a_modificar',
                     'mensaje': 'La solicitud no contiene ningun parametro a modificar, los parametros que puedes '
                                'modificar son: <nombre> <biografia> <es_grupo>'}
            lista_de_errores.append(error)
        errores_del_tamano = ValidacionCreadorDeContenido. \
            _validar_tamano_modelo_creador_de_contenido(creador_de_contenido)
        if errores_del_tamano is not None:
            for error in errores_del_tamano:
                lista_de_errores.append(error)
        if creador_de_contenido.es_grupo is not None:
            error_boolean_no_valido = ValidacionCreadorDeContenido._validar_booleano_valido(creador_de_contenido)
            if error_boolean_no_valido is not None:
                lista_de_errores.append(error_boolean_no_valido)
        return lista_de_errores

    @staticmethod
    def validar_usuario_tiene_creador_de_contenido_asociado(usuario):
        """
        Valida si el usuario tiene un creador de contenido registrado
        :param usuario: El usuario a validar si ya tiene un creador de contenido registrado
        :return: Un diccionario con el error y el mensaje del error si ya tiene un creador de contenido registrado o
        None si no tiene un creador de contenido registrado
        """
        if CreadorDeContenido.verificar_usuario_tiene_creador_contenido_registrado(usuario.id_usuario):
            error = {'error': 'usuario_tiene_un_creador_de_contenido_registrado',
                     'mensaje': 'El usuario con el cual se autentico ya cuenta con un creador de contenido registrado'}
            return error

    @staticmethod
    def validar_creador_de_contenido_existe_a_partir_de_usuario(usuario):
        """
        Valida si el usuario tiene a un CreadorDeContenido registrado
        :param usuario: El usuario a validar si tiene un CreadorDeContenido
        :return: Un diccionario con el codigo del error y el mensaje del error o None si existe el CreadorDeContenido
        """
        creador_de_contenido = CreadorDeContenido.obtener_creador_de_contenido_por_id_usuario(usuario.id_usuario)
        if creador_de_contenido is None:
            error = {'error': 'usuario_no_tiene_un_creador_de_contenido',
                     'mensaje': 'El usuario con el cual se autentico no tiene ningun CreadorDeContenido registrado'}
            return error

    @staticmethod
    def validar_usuario_no_tiene_creador_de_contenido_asociado(usuario):
        """
        Valida que el usuario no tiene un creador de contenido asoca¿iado
        :param usuario: El usuario a validar si no tiene registrado un creador de contenido
        :return: Un diccionario que indica el error y el mensaje del mismo o None si el usuario tiene un
        creador de contenido asociado
        """
        if not CreadorDeContenido. \
                verificar_usuario_tiene_creador_contenido_registrado(usuario.id_usuario):
            error = {'error': 'usuario_no_ha_registrado_un_creador_de_contenido',
                     'mensaje': 'El usuario con el cual se autentico no ha registrado el creador de contenido'}
            return error

    @staticmethod
    def validar_existe_creador_de_contenido(id_creador_de_contenido):
        """
        Valida si el id_creador_de_contenido pertence a un CreadorDeContenido
        :param id_creador_de_contenido: El id del creador de contenido a valdiar si existe
        :return: None si el existe un CreadorDeContenido con el id indicado o un diccionario con el error y el mensaje
        si no existe un CreadorDeContenido con el id indicado
        """
        if not CreadorDeContenido.verificar_existe_creador_contenido(id_creador_de_contenido):
            error = {'error': 'creador_de_contenido_inexistente',
                     'mensaje': 'No existe ningun CreadorDeContenido registrado con el id indicado'}
            return error

    @staticmethod
    def _validar_parametros_requeridos_agregar_creador_de_contenido(id_creador):
        """
        Valida si el id_creador es None
        :param id_creador: El id a validar
        :return: None si el id_creador no es None o un diccionario indicando el error si lo es
        """
        parametros_faltantes = ""
        if id_creador is None:
            parametros_faltantes += "<id> "
        if len(parametros_faltantes) > 0:
            mensaje = "Los siguientes parametros faltan en tu solicitud: " + parametros_faltantes
            errores = {'error': 'parametros_faltantes', 'mensaje': mensaje}
            return errores

    @staticmethod
    def _validar_id_creador_es_entero(id_creador):
        """
        Valida que el id_creador sea de tipo int
        :param id_creador: EL id a validar
        :return: None si es de tipo entero o un diccionario indicando el error si no es de tipo entero
        """
        try:
            int(id_creador)
        except ValueError:
            error = {'error': 'id_no_es_entero', 'mensaje': 'El id del creador de contenido a agregar debe de ser '
                                                            'entero'}
            return error

    @staticmethod
    def validar_agregar_creador_de_contenido(id_creador):
        """
        Realiza las validaciones sobre el id_creador para poder ser agregado a una cancion
        :param id_creador: El id_creador a validar
        :return: None si el id es valido y existe un creador de contenido con el id o un diccionario indicando el error
        """
        error_parametros_requeridos = ValidacionCreadorDeContenido.\
            _validar_parametros_requeridos_agregar_creador_de_contenido(id_creador)
        if error_parametros_requeridos is not None:
            return error_parametros_requeridos
        error_no_entero = ValidacionCreadorDeContenido._validar_id_creador_es_entero(id_creador)
        if error_no_entero is not None:
            return error_no_entero
        error_no_existe = ValidacionCreadorDeContenido.validar_existe_creador_de_contenido(id_creador)
        if error_no_existe is not None:
            return error_no_existe
