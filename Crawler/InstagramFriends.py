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
import time
import json
import re
import unicodecsv as csv
from nltk.tokenize import RegexpTokenizer
from os import remove,path,makedirs,listdir
from collections import Counter
import operator
import sys, traceback
import pickle
from genericpath import isdir
from multiprocessing import Process


TAG_RE = re.compile(r'<.*?>')
USER_DIR = "D:/Dropbox/DrugAbuse/User/"

def get_userinfo(user_id):
    driver = webdriver.Firefox()
    driver.implicitly_wait(10)
    url = "https://www.instagram.com/"+user_id
    driver.get(url)
    
       
    user_info = {}
    
    user_info["username"] = ""
    user_info["full_name"] = ""
    user_info["profile_picture"]=""
    user_info["bio"]=""
    user_info["website"]=""
    user_info["count"]= {}
    user_info["count"]["media"]=0
    user_info["count"]["follows"]=0
    user_info["count"]["followed_by"]=0
    
    user_info["username"] = get_attribute_of_element_by_xpath(driver,"//h1[@class='_i572c notranslate']","title")
    user_info["full_name"] = get_attribute_of_element_by_xpath(driver,"//h2[@class='_79dar']","innerHTML")
    user_info["profile_picture"] = get_attribute_of_element_by_xpath(driver,"//img[@class='_8gpiy _r43r5']","src")
    bio = get_attribute_of_element_by_xpath(driver,"//div[@class='_bugdy']/span","innerHTML")
    if bio is not None:
        user_info["bio"] = TAG_RE.sub('', bio)
        
    user_info["website"] = get_attribute_of_element_by_xpath(driver,"//a[@class='_56pjv']","innerHTML")
    
    counts = driver.find_elements_by_xpath("//span[@class='_bkw5z']")
    
    user_info["count"]["media"] = counts[0].get_attribute("innerHTML")
    user_info["count"]["follows"] = counts[1].get_attribute("innerHTML")
    user_info["count"]["followed_by"] = counts[2].get_attribute("innerHTML")
    
    json_data = json.dumps(user_info)
    
    
def get_friends(user_id,driver,outputfile,sessionfile):
    for cookie in pickle.load(open(sessionfile, "rb")):
        driver.add_cookie(cookie)
    
    url = "https://www.instagram.com/"+user_id
    print url
    driver.get(url)
    
    user_info = {}
    user_info["user_id"] = user_id
    try:
        content = get_attribute_of_element_by_xpath(driver, "//div[@class='_76rrx _yo2b4']/h2[@class='_glq0k']","innerHTML")
        if content != None: # if user is private account
            return
        
        counters = driver.find_elements_by_xpath("//a[@class='_s53mj']/span[@class='_bkw5z']")
        if counters[0].get_attribute("innerHTML") != "0":
            f1 = counters[0].get_attribute("innerHTML")
            user_info["follower_count_real"] = f1
            follower = get_follower(user_id, driver)
            user_info["follower_count"] = len(follower)
            user_info["follower"] = follower
            
        if counters[1].get_attribute("innerHTML") != "0":
            f2 = counters[1].get_attribute("innerHTML")
            user_info["followering_count_real"] = f2
            followering = get_following(user_id, driver)
            user_info["followering_count"] = len(followering)
            user_info["followering"] = followering
    
    except:
        print user_id,"get_friends Unexpected error",sys.exc_info()[0]
        traceback.print_exc(file=sys.stdout)
    
    finally:
        outputfile.write(json.dumps(user_info)+"\n")
        outputfile.flush()

def get_follower(user_id, driver):
    follower = driver.find_element_by_xpath("//a[@class='_s53mj']")
    follower.click()
    
    element = driver.find_element_by_xpath("//div[@class='_4gt3b']")
    lastHeight = driver.execute_script("return arguments[0].scrollHeight",element)
    
    followers = []
    start = 0
    
    while True:
        try:
            driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);",element)
            users = driver.find_elements_by_xpath("//a[@class='_4zhc5 notranslate _j7lfh']")
            time.sleep(3)
            for i in range(start,len(users)):
                name = users[i].get_attribute("title")
                if name != None:
                    followers.append(name)
            newHeight = driver.execute_script("return arguments[0].scrollHeight",element)
            
            if newHeight == lastHeight:
                break
            lastHeight = newHeight
            start = len(users)
        except:
            print user_id,"Follower Unexpected error",sys.exc_info()[0]
            
    try:
        driver.find_element_by_xpath("//button[@class='_3eajp']").click()
    except:
        print "no button"
        
    return followers

def get_following(user_id, driver):
    following = driver.find_elements_by_xpath("//a[@class='_s53mj']")[1]
    following.click()
    
    element = driver.find_element_by_xpath("//div[@class='_4gt3b']")
    lastHeight = driver.execute_script("return arguments[0].scrollHeight",element)
    
    followerings = []
    start = 0
    while True:
        try:
            driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);",element)
            users = driver.find_elements_by_xpath("//a[@class='_4zhc5 notranslate _j7lfh']")
            time.sleep(3)
            for i in range(start,len(users)):
                name = users[i].get_attribute("title")
                if name != None:
                    followerings.append(name)
            newHeight = driver.execute_script("return arguments[0].scrollHeight",element)
            
            if newHeight == lastHeight:
                break
            lastHeight = newHeight
            start = len(users)
        except:
            print user_id,"Following Unexpected error",sys.exc_info()[0]
    
    return followerings

def get_post_link(user_id):
    driver = webdriver.Firefox()
    driver.implicitly_wait(10)
    url = "https://www.instagram.com/"+user_id
    driver.get(url)
    
    directory = USER_DIR+user_id+"/"
    if not path.exists(directory):
        makedirs(directory)
        
    try:
        driver.find_element_by_link_text("Load more").click()
    except NoSuchElementException:
        print " No loading"
    finally:
        lastHeight = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            newHeight = driver.execute_script("return document.body.scrollHeight")
            if newHeight == lastHeight:
                time.sleep(20)
                newHeight = driver.execute_script("return document.body.scrollHeight")
                if newHeight == lastHeight:
                    break
            lastHeight = newHeight
        
        
        textWriter = csv.writer(open(directory+'PostLink.csv', 'wb'))
        textWriter.writerow(["index", "url", "content","hashtag"])
        divs = driver.find_elements_by_class_name('_myci9')
        i = 0
        tokenizer = RegexpTokenizer(r'\w+')
        for div in divs:
            print "div",i
            hrefs = div.find_elements_by_css_selector('a')
            images = div.find_elements_by_css_selector('img')
            for index, href in enumerate(hrefs):
                link = href.get_attribute('href')
                print link
                content = images[index].get_attribute('alt');
                tokens = tokenizer.tokenize(content)
                hashtag = ""
                i = i +1
                for token in tokens:
                    if token.startswith("#"):
                        key = token.lower()
                        hashtag = hashtag+key+","
                textWriter.writerow([i, link, content.encode('utf-8'), hashtag])
        
        
def post_commenter(user_id):
    directory = USER_DIR+user_id+"/"
    postLinkFile = directory+'PostLink.csv'
    
    driver = webdriver.Firefox()
    driver.implicitly_wait(10)
    
    myFile = open(directory+'Commenters.csv', 'wb')
    textWriter = csv.writer(myFile)
    textWriter.writerow(["index","url","time", "like", "interaction","commenter"])
    
    with open(postLinkFile, 'rb') as csvfile:
        spamreader = csv.reader(csvfile)
        next(spamreader, None)  # skip the headers
        for row in spamreader:
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
                textWriter.writerow([row[0],row[1],time, likeNum, interaction,listOfCommenters])
                myFile.flush()
            
def get_comment_account(user_id):
    directory = USER_DIR+user_id+"/"
    commenterFile = directory+'Commenters.csv'
    users = {}
    
    with open(commenterFile, 'rb') as csvfile:
        spamreader = csv.reader(csvfile)
        next(spamreader, None)  # skip the headers
        for row in spamreader:
            for user in row[5].split(","):
                user = user.split(":")[0].strip();
                if user == user_id:
                    continue
                if user == "":
                    continue
                if user in users:
                    users[user] = users[user] +1
                else:
                    users[user] = 1
    
    sorted_users = sorted(users.items(), key=operator.itemgetter(1), reverse=True)
    print sorted_users
    driver = webdriver.Firefox()
    driver.implicitly_wait(10)
    
    myfile = open(directory+'Commenters_Access.csv', 'wb')
    textWriter = csv.writer(myfile)
    textWriter.writerow(["index","username","url","count","access"])
    
    index = 1
    for key, value in sorted_users:
        if value > 1:
            url = "https://www.instagram.com/"+key
            driver.get(url)
            content = get_attribute_of_element_by_xpath(driver, "//div[@class='_76rrx _yo2b4']/h2[@class='_glq0k']","innerHTML")
            content = "public" if content != None else "private"
            print index,key,url,value,content
            textWriter.writerow([index,key,url,value,content])
            index = index + 1
            myfile.flush()
    
def get_attribute_of_element_by_xpath(driver, path, attribute):
    try:
        result = driver.find_element_by_xpath(path).get_attribute(attribute)
        if result != None:
            return result
        else:
            return None
    except:
        return None

def login(sessionFile):
    driver = webdriver.Firefox()
    driver.implicitly_wait(10)
    url = "https://www.instagram.com/accounts/login/"
    driver.get(url)
    
    username = driver.find_element_by_name("username")
    password = driver.find_element_by_name("password")

    username.send_keys("tding1927")
    password.send_keys("D851123t")

    driver.find_element_by_tag_name('button').click()
    
    pickle.dump(driver.get_cookies() , open(sessionFile,"wb"))
    
    return driver

def get_follower_start_with_seed(inputFile, outputFile, sessionFile):
    driver = login(sessionFile)
    while driver.current_url != "https://www.instagram.com/":
        driver.close()
        driver = login(sessionFile)
        time.sleep(10)
    
    writer_output = open(outputFile,'w')
    with open(inputFile) as f:
        users = f.readlines()
        for user in users:
            get_friends(user.rstrip('\n'),driver,writer_output,sessionFile)



if __name__ == '__main__':
    processes = []
    input = sys.argv[1] # seed 
    output = sys.argv[2] #result  
    
    if isdir(input) and isdir(output):
        for file in listdir(input):
            if path.isfile(input+file):
                print file
                inputFile = input + file
                outputFile = output + file
                sessionFile = file+"_cookie.pkl"
                p = Process(target=get_follower_start_with_seed,args=(inputFile, outputFile, sessionFile))
                p.start()
                processes.append(p)
                
    
        for p in processes:
            p.join()
            
    if path.isfile(input):
        file = path.basename(input)
        outputFile = output + file
        sessionFile = file+"_cookie.pkl"
        get_follower_start_with_seed(input, outputFile, sessionFile)
        
    