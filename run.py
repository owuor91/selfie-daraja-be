from flask import Flask
from flask_restful import Api
from app.resources import Selfie, Daraja, PaymentCallBack


def create_app():
    app = Flask(__name__)

    api = Api(app)

    api.add_resource(Selfie, "/selfie")
    api.add_resource(Daraja, "/payments")
    api.add_resource(PaymentCallBack, "/daraja-callback")

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=6160)