"""
    Se encarga de representar a un CreadorDeContenido y manejar el acceso del objeto a la base de datos
"""
from app import base_de_datos
from app.util.JsonBool import JsonBool


class CreadorDeContenido(base_de_datos.Model):
    """
    Se encarga de representar el modelo CreadorDeContenido y su acceso a la base de datos
    """
    id_creador_de_contenido = base_de_datos.Column(base_de_datos.Integer, primary_key=True)
    nombre = base_de_datos.Column(base_de_datos.String(70), nullable=False)
    biografia = base_de_datos.Column(base_de_datos.String(500), nullable=True)
    es_grupo = base_de_datos.Column(base_de_datos.Boolean, nullable=False)
    usuario_nombre_usuario = base_de_datos.Column(base_de_datos.String(20),
                                                  nullable=False, index=True)
    artistas = base_de_datos.relationship('Artista', backref='creador_de_contenido', lazy=True)
    albumes = base_de_datos.relationship('Album', backref='creador_de_contenido', lazy=True)

    def guardar(self):
        """
        Guarda en la base de datos los atributos del CreadorDeContenido
        :return:
        """
        base_de_datos.session.add(self)
        base_de_datos.session.commit()

    def actualizar_informacion(self, nombre, biografia, es_grupo):
        """
        Actauliza la informacion de los atributos de nombre, biografia y es_grupo en la base de datos
        :param nombre: El nombre a actualizar
        :param biografia: La biografia a actualizar
        :param es_grupo: El es_grupo a actualizar
        """
        if nombre is not None:
            self.nombre = nombre
        if biografia is not None:
            self.biografia = biografia
        if es_grupo is not None:
            self.es_grupo = JsonBool.obtener_boolean_de_valor_json(es_grupo)

        base_de_datos.session.commit()

    def obtener_json(self):
        """
        Crea un diccionario con los datos de la clase para poder devolverse como un json
        :return: Un diccionario con los datos de los atributos
        """
        json = {'id': self.id_creador_de_contenido, 'nombre': self.nombre, 'biografia': self.biografia,
                'es_grupo': self.es_grupo}
        return json

    @staticmethod
    def verificar_usuario_tiene_creador_contenido_registrado(nombre_usuario):
        """
        Verifica si el nombre de usuario ya tiene un creador de contenido asociado
        :param nombre_usuario: El nombre del usuario a verificar
        :return: Verdadero si el nombre de usuario ya tiene un creador de contenido registrado, falso si no
        """
        perfiles_con_el_mismo_usuario = CreadorDeContenido.query. \
            filter_by(usuario_nombre_usuario=nombre_usuario).count()
        return perfiles_con_el_mismo_usuario > 0

    @staticmethod
    def verificar_existe_creador_contenido(id_creador_contenido):
        """
        Verifica si id_creador_cotenido pertence a un creador de contenido
        :param id_creador_contenido: El id del CreadorDeContenido a validar si existe
        :return: Verdadero si el id_creador_cotenido es de un CreadorDeContenido o falso si no
        """
        cantidad_creadores_contenido_con_mismo_id = \
            CreadorDeContenido.query.filter_by(id_creador_de_contenido=id_creador_contenido).count()
        return cantidad_creadores_contenido_con_mismo_id > 0

    @staticmethod
    def obtener_creador_de_contenido_por_id(id_creador_contenido):
        """
        Recupera el creador de contenido que tenga el id indicado
        :param id_creador_contenido: El id del creador de contenido a recuperar
        :return: El creador de contenido que tiene ese id
        """
        creador_de_contenido = CreadorDeContenido.query.filter_by(id_creador_de_contenido=id_creador_contenido).first()
        return creador_de_contenido

    @staticmethod
    def obtener_creador_de_contenido_por_usuario(nombre_usuario):
        """
        Recupera el creador de contenido que sea del nombre de usuario
        :param nombre_usuario: El nombre del usuario al que esta asociado el creador de contenido
        :return: El creador de contenido que pertenezca al usuario
        """
        creador_de_contenido = CreadorDeContenido.query.filter_by(usuario_nombre_usuario=nombre_usuario).first()
        return creador_de_contenido

    @staticmethod
    def obtener_creador_de_contenido_por_busqueda(cadena_busqueda):
        """
        Busca a los creadores de contenido que su nombre contenga la candena de busqueda
        :param cadena_busqueda: La cadena de se utilizara para realizar la busqueda
        :return: Una lista con los creadores que consisten con la cadena de busqueda
        """
        expresion_regular_de_busqueda = "%" + cadena_busqueda + "%"
        creadores_de_contenido = CreadorDeContenido.query. \
            filter(CreadorDeContenido.nombre.ilike(expresion_regular_de_busqueda)).all()
        return creadores_de_contenido


class Artista(base_de_datos.Model):
    """
    Representa a un artista de un CreadorDeContenido que es grupo
    """
    id_artista = base_de_datos.Column(base_de_datos.Integer, primary_key=True)
    nombre = base_de_datos.Column(base_de_datos.String(70), nullable=False)
    creador_de_contenido_id = base_de_datos.Column(base_de_datos.Integer,
                                                   base_de_datos.
                                                   ForeignKey('creador_de_contenido.id_creador_de_contenido'),
                                                   nullable=False)

    def guardar(self):
        """
        Se encarga de guardar en la base de datos la informacion del objeto
        """
        base_de_datos.session.add(self)
        base_de_datos.session.commit()

    def actualizar_informacion(self, nombre):
        """
        Actualiza la informacion del nombre del objeto y lo guarda en la base de datos
        :param nombre: El nombre actualizado
        """
        self.nombre = nombre
        base_de_datos.session.commit()

    def eliminar(self):
        """
        Se encarga de eliminar al objeto actual de la base de datos
        """
        base_de_datos.session.delete(self)
        base_de_datos.session.commit()

    def obtener_json(self):
        """
        Genera un diccionario con los datos del objeto, el cual se utilizara para serializar la información a un JSON
        :return: Un diccionario con los datos del artista
        """
        diccionario = {'id': self.id_artista,
                       'nombre': self.nombre}
        return diccionario

    @staticmethod
    def obtener_artistas_de_creador_de_contenido(id_creador_de_cotenido):
        """
        Recupera de la base de datos todos artistas que pertenecen al creador de contenido
        :param id_creador_de_cotenido: El id del creador de contenido al que pertencen los artistas
        :return: Los artistas que pertenecen al creador de contenido
        """
        artistas = Artista.query.filter_by(creador_de_contenido_id=id_creador_de_cotenido).all()
        return artistas

    @staticmethod
    def obtener_artista_por_id(id_artista):
        """
        Recupera de la base de datos el artista que tiene el id_artista
        :param id_artista: El id del artista a recuperar
        :return: El artista que coincide con el id_artista o None si ningun artista tiene el id_artista
        """
        artista = Artista.query.filter_by(id_artista=id_artista).first()
        return artista

    @staticmethod
    def verificar_artista_existe(id_artista):
        """
        Verifica si un artista existe en la base de datos
        :param id_artista: El id del artista a verificar si existe
        :return: Verdadero si el usuario existe, falso si no
        """
        cantidad_de_artistas_con_el_id = Artista.query.filter_by(id_artista=id_artista).count()
        return cantidad_de_artistas_con_el_id > 0

    @staticmethod
    def verificar_creador_de_contenido_es_dueno_de_artista(id_creador_de_contenido, id_artista):
        """
        Verifica si la combinacion de id_artista e id_creador_de_contenido tiene  algun registro en la base de dato
        :param id_creador_de_contenido: El id del creador de contenido que es dueño del artista
        :param id_artista: El id del artista a validar si es dueña del creador de contenido
        :return: Verdadero si el creador de contenido es dueño del artista o falso si no
        """
        cantidad_de_artistas_duenos_del_creador = Artista.query \
            .filter_by(id_artista=id_artista, creador_de_contenido_id=id_creador_de_contenido).count()
        return cantidad_de_artistas_duenos_del_creador > 0


class Genero(base_de_datos.Model):
    """
    Representa a un Genero que agrupa canciones y creadores de contenido
    """
    id_genero = base_de_datos.Column(base_de_datos.Integer, primary_key=True, autoincrement=True)
    genero = base_de_datos.Column(base_de_datos.String(30), nullable=False)

    @staticmethod
    def recuperar_todos_los_generos():
        """
        Recupera de la base de datos todos los generos registrados
        :return: Una lista con los generos registrados
        """
        generos = Genero.query.all()
        return generos

    def obtner_json(self):
        """
        Crea un diccionario con los atributos del objeto
        :return: Un diccionario con los atributos del objeto
        """
        diccionario_de_los_atributos = {'id': self.id_genero, 'genero': self.genero}
        return diccionario_de_los_atributos


class Disquera(base_de_datos.Model):
    """
    Se encarga de representar una Disquera a la que pertenece un artista
    """
    id_disquera = base_de_datos.Column(base_de_datos.Integer, primary_key=True, autoincrement=True)
    nombre = base_de_datos.Column(base_de_datos.String(70), nullable=False)
    direccion = base_de_datos.Column(base_de_datos.String(200), nullable=False)
    email = base_de_datos.Column(base_de_datos.String(100), nullable=False)
    telefono = base_de_datos.Column(base_de_datos.String(30), nullable=True)
    es_empresa = base_de_datos.Column(base_de_datos.Boolean, nullable=False)
    nombre_usuario_creador = base_de_datos.Column(base_de_datos.String(20), nullable=False)

    def guardar(self):
        """
        Se encarga de guardar el objeto actual en la base de datos
        """
        if self.es_empresa is None:
            self.es_empresa = False
        base_de_datos.session.add(self)
        base_de_datos.session.commit()

    def obtner_json(self):
        """
        Crea un diccionario con los atributos del objeto
        :return: Un diccionario con los atributos del objeto
        """
        diccionario_de_los_atributos = {'id': self.id_disquera, 'nombre': self.nombre, 'direccion': self.direccion,
                                        'email': self.email, 'telefono': self.telefono, 'es_empresa': self.es_empresa}
        return diccionario_de_los_atributos


class Album(base_de_datos.Model):
    id_album = base_de_datos.Column(base_de_datos.Integer, primary_key=True)
    nombre = base_de_datos.Column(base_de_datos.String(70), nullable=False)
    anio_lanzamiento = base_de_datos.Column(base_de_datos.String(4), nullable=False)
    duracion_total_segundos = base_de_datos.Column(base_de_datos.Float)
    eliminado = base_de_datos.Column(base_de_datos.Boolean, nullable=False, default=False)
    creador_de_contenido_id = base_de_datos.Column(base_de_datos.Integer,
                                                   base_de_datos.
                                                   ForeignKey('creador_de_contenido.id_creador_de_contenido'),
                                                   nullable=False)

    def guardar(self):
        """
        Se encarga de guardar el objeto actual en la base de datos
        """
        base_de_datos.session.add(self)
        base_de_datos.session.commit()

    def actualizar_informacion(self, nombre, anio_lanzamiento):
        """
        Actualiza la informacion del nombre del objeto y lo guarda en la base de datos
        :param nombre: El nombre actualizado
        :param anio_lanzamiento: El año de lanzamiento actualizado
        """
        self.nombre = nombre
        self.anio_lanzamiento = anio_lanzamiento
        base_de_datos.session.commit()

    def eliminar_informacion(self, eliminado):
        """
        Actualiza la informacion del valor eliminado del objeto y lo guarda en la base de datos
        :param eliminado: El valor eliminado actualizado
        """
        self.eliminado = eliminado
        base_de_datos.session.commit()


    @staticmethod
    def obtener_abumes_creador_de_contenido(id_creador_de_contenido):
        """
        Obtener un listado de álbumes pertenecientes a un
        creador de contenido
        :param id_creador_de_contenido: El id del creador de contenido que es dueño del álbum
        :return: Una lista de álbumes o una lista vacía
        """
        albumes = Album.query.filter_by(creador_de_contenido_id = id_creador_de_contenido, eliminado=False).all()
        if albumes is None:
            return []
        return albumes

    @staticmethod
    def obtener_album_por_id(id_album):
        """
        Recupera de la base de datos el álbum que tiene el id_album
        :param id_album: El id del álbum a recuperar
        :return: El álbum que coincide con el id_album o None si ningún álbum tiene el id_album
        """
        album = Album.query.filter_by(id_album=id_album).first()
        return album

    @staticmethod
    def obtener_album_por_nombre(nombre):
        """
        Recupera de la base de datos el álbum que tiene el nombre
        :param nombre: El nombre del álbum a recuperar
        :return: El álbum que coincide con el nombre o None si ningún álbum tiene el nombre
        """
        album = Album.query.filter_by(nombre=nombre).first()
        return album

    @staticmethod
    def verificar_album_existe(id_album):
        """
        Verifica si un álbum existe en la base de datos
        :param id_album: El id del álbum a verificar si existe
        :return: Verdadero si el álbum existe, falso si no
        """
        cantidad_de_albumes_con_el_id = Album.query.filter_by(id_album=id_album).count()
        return cantidad_de_albumes_con_el_id > 0

    def obtener_json(self):
        """
        Crea un diccionario con los atributos del objeto
        :return: Un diccionario con los atributos del objeto
        """
        diccionario_del_objeto = {'id': self.id_album, 'nombre': self.nombre, 'anio_lanzamiento': self.anio_lanzamiento,
                                  'duracion_total': self.duracion_total_segundos}
        return diccionario_del_objeto