'''
Created on Oct 14, 2016

@author: Tao Ding
'''
import json, os
if __name__ == '__main__':
    all = []
    myfile = open("D:/Eclipse_Workspace/CRAFT/34/all.json", 'wb')
    myfile.write("[")
    for file in os.listdir("D:/Eclipse_Workspace/CRAFT/34/"):
        print file
        if "all" not in file:
            with open("D:/Eclipse_Workspace/CRAFT/34/"+file) as data_file:
                data = json.load(data_file)
                all = all + data
        
    for i in all:
        myfile.write(str(i)+",\n")
    myfile.write("]")
        