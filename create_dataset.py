import pandas as pd
import random

def dataset_creator():

    items = ['bread', 'cheese', 'egg', 'juice', 'milk', 'yogurt']
    items_set = []

    for i in range(5):
        temp = random.sample(items, k = random.randint(2, 5))
        items_set.append(temp)

    df = pd.DataFrame({"T_Id": range(1, len(items_set)+1), "Items": items_set})
    df.to_csv('Dataset.csv', index=False)

    return df


if __name__ == "__main__":
    df = dataset_creator()