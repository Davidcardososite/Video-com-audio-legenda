# __init__.py
from flask import Flask
from app.funcoes import configure_moviepy
from app.extensions import csrf




def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'mysecretkey'

    # Configurar o MoviePy para usar ImageMagick
    configure_moviepy()

    csrf.init_app(app)
    
    from app.routes import main
    app.register_blueprint(main)

    return app


