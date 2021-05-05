from dotenv import dotenv_values
import requests

ENV_PATH = '.env'

def get_url(period, key):
    return 'https://api.weatherapi.com/v1/forecast.json?key=%s&q=San Francisco&days=%i&aqi=no&alerts=no' % (key, period)

class Manager:
    manager = None

    def __new__(cls, *args, **kwargs):
        if not cls.manager:
            cls.manager = super(Manager, cls).__new__(cls, *args, **kwargs)
        return cls.manager

    def __init__(self):
        config = dotenv_values(ENV_PATH)
        self.api_key = config['API_KEY']

    def __perform_request_and_get_forecast(self, period):
        url = get_url(period, self.api_key)
        response = requests.get(url)
        data = response.json()
        forecast = data['forecast']['forecastday']
        forecasts = []

        for day in forecast:
            forecasts += day['hour']

        return [
            {
                'hour': item['time'],
                'temp': item['temp_c'],
                'hum': item['humidity']
            } for item in forecasts
        ]

    def predict(self, periods):

        return {
            'periods': periods,
            'prediction': self.__perform_request_and_get_forecast(periods / 24)
        }
