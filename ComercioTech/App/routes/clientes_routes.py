from flask import Blueprint, request, jsonify
from app.config.database_config import db_sql
from app.models.sql_models import Cliente, Direccion
from datetime import datetime

