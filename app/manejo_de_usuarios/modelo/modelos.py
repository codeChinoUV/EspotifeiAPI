"""
    Se encarga de representar a un USUARIO y manejar el acceso del objeto a la base de datos
"""
from werkzeug.security import generate_password_hash, check_password_hash

from app import base_de_datos
from app.manejo_de_usuarios.modelo.enum.enums import TipoUsuario


class Usuario(base_de_datos.Model):
    """
    Se encarga de representar el modelo usuario y define su estructura en la base de datos
    """
    nombre_usuario = base_de_datos.Column(base_de_datos.String(20), primary_key=True)
    nombre = base_de_datos.Column(base_de_datos.String(70), nullable=False)
    contrasena = base_de_datos.Column(base_de_datos.String(80), nullable=False)
    tipo_usuario = base_de_datos.Column(base_de_datos.Integer, nullable=False)

    def guardar(self):
        """
        Guarda la informacion del objeto en la base de datos
        :return: None
        """
        self.contrasena = generate_password_hash(self.contrasena, method='sha256')
        base_de_datos.session.add(self)
        base_de_datos.session.commit()

    def actualizar_informacion(self, nombre, contrasena):
        """
        Actualiza la información de los atributos nombre y contrasena y guarda los cambios realizados
        en la base de datos
        """
        if nombre is not None:
            self.nombre = nombre
        if contrasena is not None:
            contrasena_hasheada = generate_password_hash(contrasena, method='sha256')
            self.contrasena = contrasena_hasheada

        base_de_datos.session.commit()

    @staticmethod
    def obtener_todos_los_usuario():
        """
        Recupera todos los usuarios registrados en la base de datps
        :return: Una lista con los usuarios en la base de datos
        """
        return Usuario.query.all()

    @staticmethod
    def verificar_nombre_usuario_en_uso(nombre_usuario):
        """
        Verifica si el nombre de usuario ya se encuentra en uso
        :return: Verdadero si el nombre de usuario se encuentra disponible o falso si no
        """
        usuarios_con_el_mismo_nombre = Usuario.query.filter_by(nombre_usuario=nombre_usuario).count()
        return usuarios_con_el_mismo_nombre > 0

    def obtener_json(self):
        """
        Crea un diccionario que representa al objeto a partir de la información del mismo
        :return: Un diccionario con la información del objeto
        """
        json = {'nombre_usuario': self.nombre_usuario, 'nombre': self.nombre, 'tipo_usuario': self.tipo_usuario}
        return json

    @staticmethod
    def validar_usuario_creador_de_contenido(nombre_usuario):
        """
        Valida que el usuario sea de tipo creador de contenido
        :return: Verdadero si el usuario es creador de contenido o falso si no
        """
        usuario = Usuario.query.filter_by(nombre_usuario=nombre_usuario).first()
        return TipoUsuario(usuario.tipo_usuario) == TipoUsuario.CreadorDeContenido

    @staticmethod
    def obtener_usuario(nombre_usuario):
        """
        Recupera al usuario de la base de datos que tiene el nombre_usuario
        :param nombre_usuario: El nombre del usuario a recueprar
        :return: El usuario que tiene el nombre de usuario
        """
        usuario = Usuario.query.filter_by(nombre_usuario=nombre_usuario).first()
        return usuario

    @staticmethod
    def validar_credenciales(nombre_usuario, contrasena):
        """
        Valida que las credenciales de un usuario sean correctas
        :param nombre_usuario: El nombre del usuario a validar que sea correcto
        :param contrasena: La contrasena que pertenece al nombre de usuario
        :return: El usuario al que pertenecen las credenciaels o None si las credenciales no pertenecen a nadie
        """
        usuario = Usuario.query.filter_by(nombre_usuario=nombre_usuario).first()
        if usuario is None:
            return None
        if check_password_hash(usuario.contrasena, contrasena):
            return usuario
