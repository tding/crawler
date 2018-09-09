import csv
import os
from os import listdir
from os.path import isfile, join
import random
import time
from collections import Counter

dir = "D:\\Dropbox\\DrugAbuse\\HashTag\\"
file_names = onlyfiles = [f for f in listdir(dir) if isfile(join(dir, f))]
letters_nums = set(range(48,58)+range(65,91)+range(97,123))

def extract_csv():
    result = []
    i = 1
    for f in file_names:
        if "_rank" not in f and "csv" in f:
            print dir+f
            with open(dir+f, 'rb') as csv_f:
                reader = csv.reader(csv_f)
                for row in reader:
                    tmp = ""
                    for c in row[2]:
                        if ord(c) in letters_nums:
                            tmp += c
                        else:
                            tmp += " "
                    result.append([i, row[1], tmp])
                    i = i+1
                    
    return result

def rankSearch():
    distribution_file = "D:\\Dropbox\\DrugAbuse\\data1\\lda-70417a07-20-293e697b\\document-topic-distributions-rank.csv"
    with open(distribution_file, 'rb') as csv_f:
        reader = csv.reader(csv_f)
        i = -1 
        relatedColumn = []
        matrix = []
        for row in reader:
            if i == -1:
                for index, column in enumerate(row):
                    if "related" in column:
                        relatedColumn.append(index)
                        matrix.append([])
                i = 0
                continue
            
            for index,j in enumerate(relatedColumn):
                matrix[index].append(float(row[j]))
            i = i + 1
        
        precent = 0.4
        num = int(i * precent)
        theshold = []
        for column in matrix:
            theshold.append(sorted(column,reverse=True)[num])
        
        docs = []
        for index in range(i):
            flag = True
            for j,row in enumerate(matrix):
                if matrix[j][index] < theshold[j]:
                    flag = False
            
            if flag:
                docs.append(index)
        print len(docs)
        return docs

def timeTracking(docs, keyword):
    conentet_file = "D:\\Dropbox\\DrugAbuse\\timePost\\result_new.csv"
    retrievedDocs = []
    with open(conentet_file, 'rb') as csv_f:
        reader = csv.reader(csv_f)
        for row in reader:
            if int(row[0]) in docs and keyword in row[2].lower() and len(row) > 6:
                if len(row[5]) > 2:
                    retrievedDocs.append(row[5].split("T")[0])
                else:
                    date = randomDate("5/1/2016 1:30 PM", "8/27/2009 4:50 AM", random.random())
                    retrievedDocs.append(date.split(" ")[0])
                    
    retrievedDocs = Counter(retrievedDocs)
    sorted_word_counts = sorted(retrievedDocs.items(), key=lambda item: item[0],reverse=True)
    
    print retrievedDocs
                
def strTimeProp(start, end, format, prop):
    """Get a time at a proportion of a range of two formatted times.

    start and end should be strings specifying times formated in the
    given format (strftime-style), giving an interval [start, end].
    prop specifies how a proportion of the interval to be taken after
    start.  The returned time will be in the specified format.
    """

    stime = time.mktime(time.strptime(start, format))
    etime = time.mktime(time.strptime(end, format))

    ptime = stime + prop * (etime - stime)

    return time.strftime(format, time.localtime(ptime))


def randomDate(start, end, prop):
    return strTimeProp(start, end, '%m/%d/%Y %I:%M %p', prop)

if __name__ == '__main__':
    docs = rankSearch()
    timeTracking(docs, "heroin")
    
    '''
    with open("result.csv", "wb") as result_csv:
        writer = csv.writer(result_csv)
        writer.writerows(extract_csv())
    '''