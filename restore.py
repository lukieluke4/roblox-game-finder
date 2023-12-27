import pickle as pkl
import pandas as pd

df = pd.read_csv('test.csv')

df.to_pickle('test.pkl')