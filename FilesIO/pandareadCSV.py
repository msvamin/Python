__author__ = 'amin'

import pandas as pd

# Reading a csv file
filename = "C:/Amin/Python/FilesIO/" + "flowrate.csv"
with open(filename, 'r') as csvfile:
    readframe = pd.read_csv(csvfile)
    #readvalue = list(readfile)

print(readfile)
