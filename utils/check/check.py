from check_functions import *

import sys

range_to_load = None
try:
    range_to_load = (sys.argv[1].zfill(3), sys.argv[2].zfill(3))
except:
    pass

dataset_directory = "./xfund/"

dataset = load_uflaforms(dataset_directory, range_to_load=range_to_load)

print("Checking")
print()
print("Samples:")
print([sample["id"] for sample in dataset])
print()
print("Labels:")
check_labels(dataset)
print()
print("Links:")
check_links(dataset)
print()
print("Duplications:")
check_duplications(dataset)
print()
print("Texts:")
check_texts(dataset)
print()
