import json
import pandas as pd

with open("cars.json", "r", encoding="utf-8") as f:
    data = json.load(f)

df = pd.json_normalize(data["listings"])
df.to_csv("cars.csv", index=False)
print(df.shape)