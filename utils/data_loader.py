import pandas as pd

def load_data():
    df = pd.read_csv("data/arbol.csv")
    return df