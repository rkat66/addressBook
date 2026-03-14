import os
from flask import Flask
from config import config_map
from extensions import db


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config_map.get(config_name, config_map['development']))

    db.init_app(app)

    from routes.contacts import contacts_bp
    from routes.search import search_bp
    from routes.geocode import geocode_bp

    app.register_blueprint(contacts_bp)
    app.register_blueprint(search_bp, url_prefix='/search')
    app.register_blueprint(geocode_bp, url_prefix='/api')

    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
