import pandas as pd
import pmdarima as pm
import pickle

###############
# Temperature #
###############

temperatures = pd.read_csv('data/temperature.csv', names=['San Francisco'], header=0)
temperatures.dropna(subset=['San Francisco'], inplace=True)
temperatures.rename(columns={'San Francisco': 'temperature'}, inplace=True)

temperatures_model = pm.auto_arima(
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

with open('data/temperatures.pkl', 'wb') as pkl:
    pickle.dump(temperatures_model, pkl)

############
# Humidity #
############

humidity = pd.read_csv('data/humidity.csv', names=['San Francisco'], header=0)
humidity.dropna(subset=['San Francisco'], inplace=True)
humidity.rename(columns={'San Francisco': 'humidity'}, inplace=True)

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
