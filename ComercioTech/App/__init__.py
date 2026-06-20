#Librerias
from flask import Flask
from flask_cors import CORS # Permite peticiones al backend sin problemas de CORS
from .config.database_config import init_db

def crear_app():
    app = flask(__name__)
    