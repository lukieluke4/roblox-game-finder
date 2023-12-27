import pickle as pkl
import pandas as pd
with open("test.pkl", "rb") as f:
    object = pkl.load(f)

df = pd.DataFrame(object)
df = df.drop_duplicates(subset=["UniverseID"], keep='last')
df = df.reset_index(drop=True)
df.to_csv('test.csv')
df.to_pickle('test.pkl')