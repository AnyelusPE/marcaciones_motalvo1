import pandas as pd
import os

def leer_csv_seguro(path):
    if os.path.exists(path):
        return pd.read_csv(path)
    else:
        return pd.DataFrame()