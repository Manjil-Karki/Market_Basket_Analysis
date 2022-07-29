import numpy as np
import pandas as pd
from create_dataset import dataset_creator


def calculate_priority(df, min_support):
    min_no_of_transactions = min_support * df.shape[0]
    all_items = df["Items"].sum()
    item, count = np.unique(all_items, return_counts = True)
    freq_df = pd.DataFrame({"Items": item, "Count": count})
    filter = freq_df[freq_df["Count"] < min_no_of_transactions].index
    freq_df.drop(filter, inplace = True)
    freq_df.sort_values(by = ["Count"], inplace = True, ascending = False)
    freq_df.reset_index(inplace = True)
    return freq_df


def calc_order(unordered, priority):
    ordered = []
    [ordered.append(item) for item in priority if item in unordered]
    return ordered


def order_items(df, priority):
    df["Order_Items"] = df["Items"].apply(calc_order, args = [priority])
    return df


def create_graph_structure(df, order):
    ordered_df = pd.DataFrame()
    max_width = df["Order_Items"].apply(lambda x : len(x)).max()
    cols = [f"order_{i}" for i in range(0, max_width)]
    ordered_df[cols] = pd.DataFrame(df.Order_Items.to_list(), index = df.index)
    ordered_df.replace(order, range(0, len(order)), inplace = True)
    ordered_df.sort_values(cols, inplace = True)
    ordered_df.replace(range(0, len(order)), order, inplace = True)
    ordered_df.reset_index(inplace = True)
    return ordered_df


if __name__ == "__main__":
    sample_df = dataset_creator()
    print(sample_df.head())
    does_have = input("Do you have dataset in shown format(y/n):")
    if does_have.lower()[0] == "y":
        path = input("Enter Dataset path(.../*.csv):")
        df = pd.read_csv(path)
        df["Items"] = df["Items"].apply(lambda x : x[1:-1].replace(" ", "").replace("'", "").split(","))
    else:
        print("Working with sample shown above.")
        df = sample_df
    
    min_support = int(input("Enter value for minimum support in percentage: "))
    min_support = min_support / 100

    freq_df = calculate_priority(df, min_support)
    # print(freq_df)
    df = order_items(df, freq_df["Items"].to_list())

    # print(df)
    final_structure_df = create_graph_structure(df, freq_df["Items"].to_list())
    print(final_structure_df)