from flask import Flask
from flask_restful import Api
from app.resources import Selfie


def create_app():
    app = Flask(__name__)

    api = Api(app)

    api.add_resource(Selfie, "/selfie")

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=6160)