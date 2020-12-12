import json
import re
from collections import Counter
from operator import itemgetter
from progress.bar import IncrementalBar
import itertools 
import array
import pandas as pd
import csv

matrix = []
final_matrix = {}
accounts = []

def process():
    bar = IncrementalBar('Processing', max=len(matrix))
    for index,user in enumerate(matrix):
        final_matrix[accounts[index]] = {word:key for word,key in user.items()}
        bar.next()
    bar.finish()
    
    table = pd.DataFrame(final_matrix).T
    print(table)

    #with open('matrix.txt',"w") as f:
        #f.write(table.to_string())  
        
def readInData():
    global matrix
    with open("MatrixData.json","r") as f:
        data=json.load(f)
        
    for item in data:
        matrix.append(item)
        
    with open("100Accounts.txt",'r') as a:
        for line in a:
            line = line.rstrip('\n')
            accounts.append(line)

if __name__ == '__main__':
    readInData()
    process()
