from flask_restplus import Namespace, Resource
from model import Model

api = Namespace(name='prediccion')


@api.route('prediccion/24horas')
class Hour24(Resource):
    @staticmethod
    def get():
        return Model().predict(24), 200


@api.route('prediccion/48horas')
class Hour48(Resource):
    @staticmethod
    def get():
        return Model().predict(48), 200


@api.route('prediccion/72horas')
class Hour72(Resource):
    @staticmethod
    def get():
        return Model().predict(72), 200
