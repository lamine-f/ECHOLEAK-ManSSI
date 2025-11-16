"""
Routes for EchoLeak application
"""
from .main_routes import create_main_blueprint
from .admin_routes import create_admin_blueprint

__all__ = ['create_main_blueprint', 'create_admin_blueprint']
