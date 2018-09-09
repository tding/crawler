import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.common.by import By
import csv
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
'''
Created on Sep 19, 2016

@author: Tao Ding
'''

def instagramCrawlerByPost():
    dir = "D:/Dropbox/DrugAbuse/User/"
    driver = webdriver.Firefox()
    driver.implicitly_wait(10)
    
    textWriter = csv.writer(open(dir+'chrismastracchio.csv', 'wb'))
    textWriter.writerow(["time", "like", "interaction","commenter"])
    with open(dir+'chrismastracchio_1473437909.csv', 'rb') as csvfile:
        spamreader = csv.reader(csvfile)
        for row in spamreader:
            print row[0]
            driver.get(row[1])
            try:
                time = driver.find_element_by_class_name('_379kp')
                like = driver.find_element_by_class_name('_tf9x3')
                
                likeNum = like.find_element_by_css_selector('span').get_attribute('innerHTML')
                listOfCommenters = "";
                try:
                    interaction = 0;
                    comments = driver.find_elements_by_css_selector('._4zhc5.notranslate._iqaka')
                    interaction = len(comments)
                    commenters = [];
                    commenters_counts = {};
                   
                    for comment in comments:
                        commenters.append(comment.get_attribute('title'));
                    commenters_counts = Counter(commenters)
                    
                    for item in commenters_counts.items():
                        listOfCommenters = listOfCommenters + item[0] + ":"+str(item[1])+","
                except NoSuchElementException:
                        listOfCommenters = "0";
            except NoSuchElementException:
                likeNum = 0
            finally:
                time = time.get_attribute('datetime')
                textWriter.writerow([time, likeNum, interaction,listOfCommenters])
        #print like.find_element_by_css_selector('span').get_attribute('innerHTML')
        #driver.close()     
    #html_source = driver.page_source
    #data = html_source.encode('utf-8')

def StatisticsFriendsInteraction():
    dir = "D:/Dropbox/DrugAbuse/User/"
    
    users = []
    with open(dir+'chrismastracchio.csv', 'rb') as csvfile:
        spamreader = csv.reader(csvfile)
        for row in spamreader:
            for user in row[3].split(","):
                user = user.split(":")[0].strip();
                if user == "chrismastracchio":
                    continue
                if user:
                    users.append(user);
    
    
    G=nx.star_graph(20)
    pos=nx.spring_layout(G)
    colors=range(20)
    

    users_count = Counter(users)
    index = 2
    for user_count in users_count:
        print users_count[user_count]
        index = index + 1
    
    plt.savefig("edge_colormap.png") # save as png
    plt.show() # display
    
    '''
    sorted_users_count = sorted(users_count.items(), key=lambda item: item[1],reverse=True)
    #print sorted_users_count
    thredshold = 20
    frequentUsers = []
    for value in sorted_users_count:
        if value[1] < thredshold:
            break
        frequentUsers.append(value[0])
    orderedUsers= sorted(frequentUsers)
    #print 
    
    
    arr = [0] * len(orderedUsers)
    textWriter = csv.writer(open(dir+'axis.csv', 'wb'))
    textWriter.writerow(orderedUsers)
    X = []
    Y = []
    colors = []
    i = 0
    with open(dir+'chrismastracchio.csv', 'rb') as csvfile:
        spamreader = csv.reader(csvfile)
        for row in spamreader:
            i = i + 1
            arr = [0] * len(orderedUsers)
            for user in row[3].split(","):
                user = user.split(":")[0]; 
                print user
                if user not in orderedUsers:
                    continue;
                arr[orderedUsers.index(user)] = 1
                
                Y.append(orderedUsers.index(user))
                X.append(i)
                if orderedUsers.index(user) % 2 ==0 :
                    colors.append("red")
                else:
                    colors.append("blue")
                textWriter.writerow([orderedUsers.index(user),i]) 
            #textWriter.writerow(arr)        
            
    area = np.pi * 4  # 0 to 15 point radiuses
    plt.xlabel("Posts (2012-11-08 to 2016-08-24)",fontsize=18)
    plt.ylabel("Friends",fontsize=18)
    plt.scatter(X, Y, s=area, c=colors, alpha=0.5)
    #plt.scatter(X, Y, s=area, c=colors, alpha=0.5)
    plt.show()
    '''

def StatisticsComments():
    dir = "D:/Dropbox/DrugAbuse/User/"
    index = 0
    X = []
    Y = []
    colors = []
    max = 0
    with open(dir+'chrismastracchio.csv', 'rb') as csvfile:
        spamreader = csv.reader(csvfile)
        for row in spamreader:
            if index == 0: 
                index = 1
                continue
            Y.insert(0, row[2])  # num of comments
            if max < row[2]:
                max = row[2]
            X.insert(0, index)
            index = index + 1
    
    X.append(index)
    Y.append(int(max)+50)
    colors.append("blue")    
    area = np.pi * 4  # 0 to 15 point radiuses
    plt.xlabel("Posts (2012-11-08 to 2016-08-24)",fontsize=18)
    plt.ylabel("Comments",fontsize=18)
    plt.scatter(X, Y, s=area, c=colors, alpha=0.5)
    #plt.scatter(X, Y, s=area, c=colors, alpha=0.5)
    plt.show()

def StatisticsLikes():
    dir = "D:/Dropbox/DrugAbuse/User/"
    index = 0
    X = []
    Y = []
    colors = []
    max = 0
    with open(dir+'chrismastracchio.csv', 'rb') as csvfile:
        spamreader = csv.reader(csvfile)
        for row in spamreader:
            if index == 0: 
                index = 1
                continue
            Y.append(row[1])  # num of comments
            X.append(index)
            index = index + 1
    
    
    colors.append("blue")    
    area = np.pi * 4  # 0 to 15 point radiuses
    plt.xlabel("Post (2012-11-08 to 2016-08-24)",fontsize=18)
    plt.ylabel("Likes",fontsize=18)
    plt.scatter(X, Y, s=area, c=colors, alpha=0.5)
    #plt.scatter(X, Y, s=area, c=colors, alpha=0.5)
    plt.show()
            
def StatisticsPostByMonth():
    dir = "D:/Dropbox/DrugAbuse/User/"
    X = []
    Y = []
    colors = []
    index = 0
    tags = []
    for i in range(2012,2017):
        for j in range(1,13):
            if i == 2016 and j > 8:
                continue;
            if i == 2012 and j < 11:
                continue;
            if j < 10:
                tags.append(str(i)+"0"+str(j))
            else:
                tags.append(str(i)+str(j))
                
    months = []
    with open(dir+'chrismastracchio.csv', 'rb') as csvfile:
        spamreader = csv.reader(csvfile)
        for row in spamreader:
            if index == 0: 
                index = 1
                continue
        
            timeStr = row[0].split("T")[0]
            
            month = timeStr.split("-")[0] + timeStr.split("-")[1];
            months.append(month)
            i = i + 1
        
        count_month = dict(Counter(months))
        for i in range(len(tags)):
            tag = tags[i];
            num = 0
            if tag in count_month.keys():
                num = count_month[tag]
                
            Y.append(num)
            X.append(i)
      
    plt.xlabel("Month (2012-11 to 2016-08)",fontsize=18)
    plt.ylabel("Posts",fontsize=18)
    plt.plot(X, Y)
    #plt.scatter(X, Y, s=area, c=colors, alpha=0.5)
    plt.show()
    
    
if __name__ == '__main__':
    StatisticsFriendsInteraction()