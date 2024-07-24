import requests, json, random
import pandas as pd
from prophet import Prophet
import datetime
from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource
import warnings
from prophet.plot import plot_plotly, plot_components_plotly
import matplotlib.pyplot as plt
import time
import configparser
warnings.simplefilter("ignore", category=FutureWarning)


def create_config():
    config = configparser.ConfigParser()
 
    # Add sections and key-value pairs
    config['General'] = {'debug': True, 'log_level': 'info'}
    config['Database'] = {'api1': 'CG-1NHiCVCJ4RMM8z3a7bMDBUtu',
                          'api2': 'CG-wZ9oi4agWw3VvpuavQxDcoJH',
                          'api3': 'CG-wzfTQkUNqMM7efmTJ4GWP6JA',
                          'api4': 'CG-akiT1sAUbxQcBRJEDb7ik2iD',
                          'api5': 'CG-wZ9oi4agWw3VvpuavQxDcoJH',
                          'api6': 'CG-7gJCPGwpa5pWc4hm1LzzEtfx',
                          'api7': 'CG-C8KQc8UCnWoDVPL154cSrL48'}
 
    # Write the configuration to a file
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
 
 
if __name__ == "__main__":
    create_config()
