import pickle

class Model:
    model = None

    def __new__(cls, *args, **kwargs):
        if not cls.model:
            cls.model = super(Model, cls).__new__(cls, *args, **kwargs)
        return cls.model

    def __init__(self):
        with open('data/temperature.pkl', 'rb') as pkl:
            self.temperature_model = pickle.load(pkl)

        with open('data/humidity.pkl', 'rb') as pkl:
            self.humidity_model = pickle.load(pkl)

    def predict(self, periods):
        return {
            'temperature': self.temperature_model.predict(n_periods=periods, return_conf_int=False).tolist(),
            'humidity': self.humidity_model.predict(n_periods=periods, return_conf_int=False).tolist()
        }
