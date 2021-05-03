from flask import Flask
from flask_restplus import Api

from routes import api as routes

app = Flask(__name__)
api = Api(app, title='Weather v1')

api.add_namespace(routes, path='/servicio/v1/')