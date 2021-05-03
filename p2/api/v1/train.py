import pandas as pd
import pmdarima as pm
import pickle

###############
# Temperature #
###############

temperatures = pd.read_csv('data/temperature.csv', names=['San Francisco'], header=0)
temperatures = temperatures.fillna(temperatures.mean())

temperature_model = pm.auto_arima(
    temperatures,
    start_p=1,
    start_q=1,
    test='adf',
    max_p=3,
    max_q=3,
    m=1,
    d=None,
    seasonal=False,
    start_P=0, 
    D=0, 
    trace=True,
    error_action='ignore',  
    suppress_warnings=True, 
    stepwise=True
)

with open('data/temperature.pkl', 'wb') as pkl:
    pickle.dump(temperature_model, pkl)

############
# Humidity #
############

humidity = pd.read_csv('data/humidity.csv', names=['San Francisco'], header=0)
humidity = humidity.fillna(humidity.mean())

humidity_model = pm.auto_arima(
    humidity,
    start_p=1,
    start_q=1,
    test='adf',
    max_p=3,
    max_q=3,
    m=1,
    d=None,
    seasonal=False,
    start_P=0, 
    D=0, 
    trace=True,
    error_action='ignore',  
    suppress_warnings=True, 
    stepwise=True
)

with open('data/humidity.pkl', 'wb') as pkl:
    pickle.dump(humidity_model, pkl)
