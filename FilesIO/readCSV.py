__author__ = 'amin'

import csv

# Reading a csv file
filename = "C:/Amin/Python/FilesIO/" + "flowrate.csv"
with open (filename, 'r') as csvfile:
    readfile = csv.reader(csvfile)
    readvalue = list(readfile)

print(readvalue)
