import datetime
import os
from functools import wraps

import jwt
from flask import request, jsonify
from flask_restful import Resource
from werkzeug.utils import import_string

from app import create_app
from app.manejo_de_usuarios.modelo.enum.enums import TipoUsuario
from app.manejo_de_usuarios.modelo.modelos import Usuario

settings_module = os.getenv('APP_SETTINGS_MODULE')

def obtener_secret_key():
    objeto_configuracion = import_string(settings_module)
    try:
        key = objeto_configuracion.SECRET_KEY
        return key
    except AttributeError:
        return None

def token_requerido(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            error = {'error': 'token_faltante',
                     'mensaje': 'La cabecera http no lleva el token en el campo \'x-access-token\''}
            return error, 401
        try:
            secret_key = obtener_secret_key()
            if secret_key is None:
                return {}, 500
            datos = jwt.decode(token, secret_key)
            usuario_actual = Usuario.obtener_usuario_por_id(datos['id_usuario'])
        except:
            error = {'error': 'token_invalido',
                     'mensaje': 'El token no es valido, ya sea por que se modifico o el tiempo de vida expiro'}
            return error, 401
        return f(*args, usuario_actual, **kwargs)

    return decorated


def solo_creador_de_contenido(f):
    @wraps(f)
    def decorador(*args, **kwargs):
        usuario_actual = args[1]
        if TipoUsuario(usuario_actual.tipo_usuario) != TipoUsuario.CreadorDeContenido:
            error = {'error': 'operacion_no_permitida',
                     'mensaje': 'El usuario con el que se encuentra autenticado no tiene permisos para realizar dicha '
                                'operación'}
            return error, 403
        return f(*args, **kwargs)

    return decorador

class LoginControlador(Resource):

    def get(self):
        """
        Se encarga de generar un token para autenticar a un usuario
        :return: Un token de autenticacion o un diccionario con el error y mensaje del error si ocurrio uni
        """
        login = request.authorization
        error = {'error': 'parametros_faltantes', 'mensaje': 'Los siguientes parametros faltan en tu solicitud: '}
        if login is None or (not login.username and not login.password):
            error['mensaje'] += '<username>, <password>'
            return error, 400
        elif not login.username:
            error['mensaje'] += '<username>'
            return error, 400
        elif not login.password:
            error['mensaje'] += '<password>'
            return error, 400

        usuario = Usuario.validar_credenciales(login.username, login.password)
        if usuario is None:
            error = {'error': 'credenciales_invalidas', 'mensaje': 'No existe un usuario con la combinación de usuario '
                                                                   'y contrasena indicada'}
            return error, 400
        secret_key = obtener_secret_key()
        if secret_key is None:
            return {}, 500
        token = jwt.encode({'id_usuario': usuario.id_usuario,
                            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60)}, secret_key)
        return jsonify({'token': token.decode('UTF-8')})

    @staticmethod
    def token_requerido_grpc(token):
        app = create_app(settings_module)
        if token is not None:
            try:
                with app.app_context():
                    secret_key = obtener_secret_key()
                    datos = jwt.decode(token, secret_key)
                    usuario_actual = Usuario.obtener_usuario_por_id(datos['id_usuario'])
                    return usuario_actual
            except Exception:
                return None
