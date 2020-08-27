import pandas as pd
import requests
import os
os.environ['NO_PROXY'] = '127.0.0.1'





def get_data():
    data_source = 'http://127.0.0.1:8000/thermoglobe/data'
    data = requests.get(data_source).json()
    df = pd.DataFrame(data['data'])
    df.columns = data['headers']
    return df

def check_last_update():
    data_source = 'http://127.0.0.1:8000/thermoglobe/data'
    data = requests.get(data_source).json()
    


if __name__ == '__main__':
    data = get_data()
    print(data.head())
