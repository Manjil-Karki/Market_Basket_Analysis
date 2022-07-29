import pandas as pd
import numpy as np
from itertools import combinations, permutations
from create_dataset import dataset_creator


ALL_DF = pd.DataFrame(columns=["Items", "Total_Count", "Support"])

def merge_all(df):
    global ALL_DF
    ALL_DF = pd.concat([ALL_DF, df], ignore_index = True)


def generate_frequent_itemset(df, min_support):
    all_items = []
    number_of_tuples = df.shape[0]
    min_support_number = min_support * number_of_tuples / 100
    
    all_items = df["Items"].sum()
    items, count = np.unique(all_items, return_counts = True)

    frequent_itemset = pd.DataFrame({"Items": items, "Total_Count": count, "Support": np.nan})
    frequent_itemset = frequent_itemset.loc[frequent_itemset["Total_Count"] >= min_support_number]
    frequent_itemset["Support"] = frequent_itemset["Total_Count"] / number_of_tuples

    frequent_itemset.reset_index(inplace = True)
    frequent_itemset.drop(["index"], axis = 1, inplace = True)

    return frequent_itemset


def get_support(tuple_items, actual_items, total_count):
    count = 0
    for item in actual_items:
        if all(tuple_item in item for tuple_item in tuple_items):
            count += 1 
    support = count/total_count
    return count, support


def generate_nextlevel_tuples(PrevItr_df, df, min_support):

    level = 2
    min_support = min_support / 100
    items = PrevItr_df["Items"].to_list()
    while True:
        items = list(combinations(items, level))
        
        if not items:
            return PrevItr_df
        
        nextLevelTuple_df = pd.DataFrame(columns = ["Items", "Total_Count", "Support"])
        nextLevelTuple_df["Items"] = items
        support_count = nextLevelTuple_df["Items"].apply(get_support, args = [df["Items"], df.shape[0]])

        nextLevelTuple_df[["Total_Count", "Support"]] = support_count.apply(pd.Series)

        nextLevelTuple_df.drop(nextLevelTuple_df[nextLevelTuple_df["Support"] < min_support].index, inplace = True)
        merge_all(nextLevelTuple_df)

        if nextLevelTuple_df.empty:
            if level == 2:
                print("No next level tuples formed there is no association!!")
                exit()
            return PrevItr_df
        
        PrevItr_df = nextLevelTuple_df.copy()
        items = set(PrevItr_df["Items"].sum())
        level += 1




def calculate_confidence(target, item, items):
    count_of_target = ALL_DF.loc[ALL_DF["Items"] == target, "Total_Count"].squeeze()
    filter = ALL_DF["Items"] == set(items)
    number_of_tuples_with_items = ALL_DF[filter]["Total_Count"].squeeze()
    confidence = number_of_tuples_with_items / count_of_target
    row = pd.DataFrame(columns = ["Items", "Target", "Confidence"])
    row.loc[0] =[list(item), list(target), confidence]
    return row



def finalize_association(df):
    association_df = pd.DataFrame(columns = ["Items", "Target", "Confidence"])
    for items in df["Items"]:
        perms = []
        temp = list(permutations(items, len(items) - 1))
        temp = [set(t) for t in temp]
        [perms.append(t) for t in temp if t not in perms]
        for item in perms:
            target = set(items) - item
            item = set(item)
            row = calculate_confidence(target, item, items)
            association_df = pd.concat([association_df, row], ignore_index = True)
            if len(items) > 2:
                row = calculate_confidence(item, target, items)
                association_df = pd.concat([association_df, row], ignore_index = True)

    return association_df
            

def filter_by_confidence(df, min_confidence):
    min_confidence = min_confidence / 100
    filter = (df.loc[df["Confidence"] < min_confidence]).index
    df.drop(filter, inplace = True)
    df.reset_index(inplace = True)
    return df


if __name__ == '__main__':
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
       
    min_support = int(input("Enter value for minimum support in percent: "))
    min_confidence = int(input("Enter value for minimum confidence in percent: "))

    frequent_itemset = generate_frequent_itemset(df, min_support)
    merge_all(frequent_itemset)
    finalItems_df = generate_nextlevel_tuples(frequent_itemset, df, min_support)
    # ALL_DF.reset_index(inplace = True)
    ALL_DF["Items"] = ALL_DF["Items"].apply(lambda x : set([x]) if type(x) is str else set(x))
    # print(ALL_DF)
    association_df = finalize_association(finalItems_df)
    # print(association_df)
    final_asocation = filter_by_confidence(association_df, min_confidence)
    print("Thus the final association is: ")
    print(final_asocation.loc[:, ["Items", "Target", "Confidence"]])