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
import unicodecsv as csv
from nltk.tokenize import RegexpTokenizer
from collections import Counter
import time
import json as json
import re
from os import remove,path,makedirs,listdir
from os.path import isfile, join
import urllib
import sys


def instagramCrawler(keyword, dir, driver):
    base_url = "https://www.instagram.com"
    SearchTime = str(int(time.time()))
    driver.get(base_url + "/explore/tags/"+keyword+"/")
    try:
        driver.find_element_by_link_text("Load more").click()
        
    except NoSuchElementException:
        print keyword+" is not enought to load."
    finally:
        lastHeight = driver.execute_script("return document.body.scrollHeight")
        print "starting:"+keyword
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
            
        divs = driver.find_elements_by_class_name('_myci9')
        i = 0
        textWriter = csv.writer(open(dir+keyword+'_'+SearchTime+'.csv', 'wb'))
        tokenizer = RegexpTokenizer(r'\w+')
        words = []
        for div in divs:
            hrefs = div.find_elements_by_css_selector('a')
            images = div.find_elements_by_css_selector('img')
            for index, href in enumerate(hrefs):
                link = href.get_attribute('href')
                content = images[index].get_attribute('alt');
                tokens = tokenizer.tokenize(content)
                hashtag = ""
                i = i +1
                for token in tokens:
                    if token.startswith("#"):
                        key = token.lower()
                        words.append(key)
                        hashtag = hashtag+key+","
                textWriter.writerow([i, link, content.encode('utf-8'), hashtag])
        
        word_counts = Counter(words)
        sorted_word_counts = sorted(word_counts.items(), key=lambda item: item[1],reverse=True)
        
        rankWriter = csv.writer(open(dir+keyword+'_'+SearchTime+'_rank.csv', 'wb'))
        for value in sorted_word_counts:
            rankWriter.writerow([value[0],value[1]])
        print keyword + ":" + str(i)
        #driver.close()     
    #html_source = driver.page_source
    #data = html_source.encode('utf-8')

def crawlePostDetail():
    driver = webdriver.Firefox()
    driver.implicitly_wait(10)
    TAG_RE = re.compile(r'<.*?>')
    
    with open("Output", "w") as text_file:
        with open('D:/Dropbox/DrugAbuse/data/result.csv', 'rb') as csvfile:
            spamreader = csv.reader(csvfile)
            for row in spamreader:
                driver.get(row[1])
                try:
                    user = driver.find_element_by_class_name('_f95g7').find_element_by_css_selector('a').get_attribute('title')
                    time = driver.find_element_by_class_name('_379kp').get_attribute('datetime')
                    like = driver.find_element_by_class_name('_tf9x3')
                    likeNum = like.find_element_by_css_selector('span').get_attribute('innerHTML')
                    
                    interaction = -1
                    
                    try:
                        comments = driver.find_elements_by_class_name('_nk46a')
                        interaction = len(comments)
                        user_comments = "["
                        
                        for comment in comments:
                            commenter = comment.find_element_by_xpath("//a[@class='_4zhc5 notranslate _ook48']").get_attribute('title')
                            content = comment.find_element_by_css_selector('span')
                            cleanContent = json.dumps(TAG_RE.sub('', content.get_attribute('innerHTML')))
                          
                            tag = "";
                            try:
                                hashtags = comment.find_elements_by_css_selector('a')
                                tag = "["
                                i = 0
                                for hashtag in hashtags: 
                                    if i == 0:
                                        i = 1
                                        continue;
                                    tag = tag + "'"+hashtag.get_attribute('innerHTML')+"',"
                                
                                tag = tag[:-1] + "]"
                            except NoSuchElementException:
                                tag = ""
                            if  tag =="" or tag =="]" :
                                user_comment = "{'user' : '"+commenter+"', 'comment' : "+cleanContent + "}"
                            else:
                                user_comment = "{'user' : '"+commenter+"', 'comment' : "+cleanContent + ", 'hashtag':"+tag+"}"
                            
                            user_comment = user_comment + ","
                            user_comments = user_comments + user_comment
                            
                        user_comments = user_comments[:-1] + "]"
                    except NoSuchElementException:
                        interaction = 0;
                    
                except NoSuchElementException:
                    likeNum = 0
                finally:
                    content = '{\'user\': \''+user+'\', \'time\':\''+time+'\', \'like\':\''+str(likeNum)+'\', \'count_of_comments\': \''+str(interaction)+'\''
                    if interaction == 0:
                        content = content + "}"
                    else:
                        content = content + ", 'comments':" + user_comments +"}"
                    print content.encode("UTF-8")
                    '''
                    if interaction > 0:
                        content = content + 
                    text_file.write("{'user':user, 'time':time, 'like':likeNum}")
                    text_file.write("\n")
                    '''
                    break;
                   
                             
def crawlePostTime(dir,skipwords):
    files = [f for f in listdir(dir) if isfile(join(dir,f)) and "rank" not in f and "result_time" not in f]
    textWriter = csv.writer(open(dir+'result_time.csv', 'wb'))
    driver = webdriver.Firefox()
    driver.implicitly_wait(10)
    id = 1
    
    for file in files:
        pretag = file.split("_")[0]
        if pretag in skipwords:
            continue;
        
            
        with open(dir+file, 'rb') as csvfile:
            spamreader = csv.reader(csvfile)
            for row in spamreader:
                if pretag == "hashish" and int(row[0]) < 5787:
                    continue;
                driver.get(row[1])
                try:
                    user = driver.find_element_by_class_name('_f95g7').find_element_by_css_selector('a').get_attribute('title')
                    time = driver.find_element_by_class_name('_379kp').get_attribute('datetime')
                    like = driver.find_element_by_class_name('_tf9x3')
                    likeNum = like.find_element_by_css_selector('span').get_attribute('innerHTML')
                    
                    interaction = -1
                    
                    try:
                        comments = driver.find_elements_by_class_name('_nk46a')
                        interaction = len(comments)
                        
                    except NoSuchElementException:
                        interaction = 0;
                    
                except NoSuchElementException:
                    likeNum = 0
                finally:
                    textWriter.writerow([id,row[1],row[1].split("?")[0],row[1].split("=")[1],row[2],user,time,likeNum,interaction])
                    id = id + 1
                    
def crawlePostPic():
    sourceDir = "D:\\Dropbox\\DrugAbuse\\HashTag\\Fentanyl\\"
    targetDir = "D:\\InstagramPic\\"
    files = [f for f in listdir(sourceDir) if isfile(join(sourceDir,f)) and "rank" not in f and "result_time" not in f]
    driver = webdriver.Firefox()
    driver.implicitly_wait(10)
    flag = False
    for file in files:
        directory = targetDir + file.split(".")[0]
        
        if not path.exists(directory):
            makedirs(directory)
        with open(sourceDir+file, 'rb') as csvfile:
            spamreader = csv.reader(csvfile,encoding='utf-8')
            for row in spamreader:
                id = row[0]
                if "Norcos_1473179602" in file and int(id) < 80:
                    continue;
                
                driver.get(row[1])
                try:
                    images = driver.find_elements_by_tag_name('img') 
                    for image in images:
                        try:
                            src = image.get_attribute("src")
                            if "ig_cache_key" in src:
                                urllib.urlretrieve(src,directory+"\\"+id+".jpg")
                        except:
                            print "no element"
                except NoSuchElementException:
                    print "no image"
                
    
def margedAllPost():
    sourceDir = "D:\\Dropbox\\DrugAbuse\\HashTag\\"
    targetDir = "D:\\Dropbox\\DrugAbuse\\All\\"
    
    files = [f for f in listdir(sourceDir) if isfile(join(sourceDir,f)) and "rank" not in f and "post" not in f]
    textWriter = csv.writer(open(targetDir+'allPosts.csv', 'wb'),encoding='utf-8')
    i = 1
    for file in files:
        print file
        with open(sourceDir+file, 'rb') as csvfile:
            spamreader = csv.reader(csvfile,encoding='utf-8')
            for row in spamreader:
                textWriter.writerow([i,row[1],row[2]])
                i = i+1
                
def mergePostDetail():
    targetDir = "D:\\Dropbox\\DrugAbuse\\All\\"
    textWriter = csv.writer(open(targetDir+'posts_details.csv', 'wb'),encoding='utf-8')
    with open(targetDir+"details.csv", 'rb') as f1, open(targetDir+"allPosts.csv", 'rb') as f2:
        rdr1 = csv.reader(f2,encoding='utf-8')
        rdr2 = csv.reader(f1,encoding='utf-8')
        for file1_line in rdr1:
            file2_line = rdr2.next()
            if file1_line[1] == file2_line[1]:
                textWriter.writerow([file1_line[0],file1_line[1],file1_line[1].split("=")[1],file1_line[2],file2_line[2],file2_line[3],file2_line[4],file2_line[5]])
    
def FilterFentanyl(source_file):
    with open(source_file, 'rb') as csvfile:
        spamreader = csv.reader(csvfile)
        next(spamreader, None)
        hashtags = []
        for row in spamreader:
            count = int(row[1])
            street_name = row[3].strip()
            type = row[4].strip()
            
            if count < 5 and (not street_name or not type):
                hashtags.append(row[0].lower())
        
        print hashtags
        dir = "D:\\Dropbox\\DrugAbuse\\HashTag\\Fentanyl\\"
        for f in listdir(dir):
            if isfile(join(dir,f)) and f.split("_")[0] in hashtags:
                print join(dir,f)
                remove(join(dir,f))
            
      
def crawlerForFentanyl(keywords, target_dir, source_file):
    keywords = [x.lower() for x in keywords]
    driver = webdriver.Firefox()
    driver.implicitly_wait(10)
    
    with open(source_file, 'rb') as csvfile:
        spamreader = csv.reader(csvfile)
        next(spamreader, None)
        for row in spamreader:
            street_name = row[3].strip()
            type = row[4].strip()
            frequencies = int(row[1])
            if street_name:
                if "," in street_name:
                    street_names = street_name.split(",")
                    for name in street_names:
                        name = name.replace(" ","")
                        name = name.replace("-","")
                        if not name:
                            continue;
                        if name.lower() not in keywords:
                            instagramCrawler(name.lower(),target_dir,driver)
                            keywords.append(name.lower());
                else:
                    street_name = street_name.replace(" ","")
                    street_name = street_name.replace("-","")
                    if not street_name:
                        continue;
                    if street_name.lower() not in keywords:
                        instagramCrawler(street_name.lower(),target_dir,driver)
                        keywords.append(street_name.lower());
                    
                    
            tag = row[0].lower().strip()
            if tag in keywords or not tag: 
                continue;
            if frequencies >= 5 or type:
                instagramCrawler(tag,target_dir,driver)
                keywords.append(tag);
               
def filterRedundancy():
    dir = "D:/Dropbox/DrugAbuse/docs/"
    files = [f for f in listdir(dir) if isfile(join(dir,f))]
    textWriter = csv.writer(open('D:/Dropbox/DrugAbuse/LDA/docs.csv', 'wb'),encoding='utf-8')
    
    urls = []
    id = 1
    for file in files:
        with open(dir+file, 'rb') as csvfile:
            spamreader = csv.reader(csvfile)
            for row in spamreader:
                url = row[1].split("?")[0].split("p/")[1][:-1]
                if url not in urls:
                    urls.append(url)
                    if len(row) > 8:
                        textWriter.writerow([id,row[1].split("?")[0],row[3],row[4],row[5],row[6],row[7],row[8]])
                    else:
                        textWriter.writerow([id,row[1].split("?")[0],row[2],row[3],row[4],row[5],row[6],row[7]])
                    id = id + 1
        
    
if __name__ == "__main__":
    keywords = [
                    "Murder8", #22
                    "Apache", #259662
                    "ChinaGirl", #66084
                    "ChinaWhite", #18718
                    "DanceFever", #26825
                    "Friend", #43042599
                    "Goodfella", #279331
                    "Jackpot", #347429
                    "TNT", #766944
                    "TangoCash", #117
                    "GreatBear", #6004
                    "ChinaTown", #2,178,345
                    "HeMan", #184,296
                    "KingIvory", #38
                    "morphine",#57,942
                    "heroin",#119,553 
                    "propofol",#3,785
                    "versed",#1,452
                    "midazolam",
                    "opiates",
                    "opiate",
                    "opioid",
                    "dilaudid",
                    "oxycodone",
                    "oxycontin",
                    "oxy",
                    "MDMA",
                    "percocet",#29771
                    "xanax",#
                    "ecstacy",#25463
                    "lidocaine",#4393
                    "adderall",#37980
                    "Hydrocodone",
                    "RoxyCodone",#8964
                    "Molly",#1493267
                    "Norcos",#22157 
                    "ketamine",#22688
                    "opiate", #12,174
                    "oxycodone", #40883
                    "fentanyl",
                    "chronicpain",
                     "drugs",
                     "pain",
                     "surgery",
                     "hospital",
                     "chronicpain",
                     "chronicillness",
                     "anesthesia",
                     "overdose",
                     "hash",
                     "Hemp"
                    ]
    
    '''
    dir = "D:\\Dropbox\\DrugAbuse\\HashTag\\Fentanyl\\"
    files = [f for f in listdir(dir) if isfile(join(dir,f)) and "result_time" in f]
    
    skipwords = []
    for file in files:
        with open(dir+file, 'rb') as csvfile:
                spamreader = csv.reader(csvfile)
                for row in spamreader:
                    if row[3] not in skipwords:
                        skipwords.append(row[3])
                    else:
                        continue
    
    keywords = ["hashish", "marijuana", "obey"];
    for keyword in keywords:
        if keyword in skipwords:
            skipwords.remove(keyword)
    crawlePostTime(dir,skipwords)
    '''
    
    filterRedundancy()
    #margedAllPost()
    #mergePostDetail()
    
    #crawlePostPic()s
    '''
    files = [f.split("_")[0] for f in listdir(dir) if isfile(join(dir,f)) and not "rank" in f]
    keywords = keywords + files
    keywords = [x.lower() for x in keywords]
    #print keywords
    crawlerForFentanyl(keywords,"D:\\Dropbox\\DrugAbuse\\HashTag\\Fentanyl\\","D:\\Dropbox\\DrugAbuse\\fentanyl_withAnnotation.csv")
    '''
    #instagramCrawler("ChinaTown");
    #StatisticsFriendsInteraction();
    #crawlePostTime("D:\\Dropbox\\DrugAbuse\\time\\")
    #crawlePostTime();
    
    #instagramCrawlerByPost();
    #for keyword in keywords:
    #   instagramCrawler(keyword);