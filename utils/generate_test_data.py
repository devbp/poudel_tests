import pandas as pd
import random

def generate_random_data(n=5):
    data = {
        "battery_level": [round(random.uniform(0.0, 1.0), 2) for _ in range(n)],
        "wind_speed": [random.randint(10, 50) for _ in range(n)]
    }
    df= pd.DataFrame(data)
    df.to_csv("test_data/test_data.csv", index=False)


generate_random_data(20)   